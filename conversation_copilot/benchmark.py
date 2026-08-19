from __future__ import annotations

import ctypes
import json
import math
import statistics
import subprocess
import sys
import threading
import time
from dataclasses import asdict, dataclass
from ctypes import wintypes

from .capture import FramePacket, LatestFrameSlot
from .video import FaceProcessor, replay_steps


class _ProcessMemoryCounters(ctypes.Structure):
    _fields_ = [
        ("cb", wintypes.DWORD),
        ("page_fault_count", wintypes.DWORD),
        ("peak_working_set_size", ctypes.c_size_t),
        ("working_set_size", ctypes.c_size_t),
        ("quota_peak_paged_pool_usage", ctypes.c_size_t),
        ("quota_paged_pool_usage", ctypes.c_size_t),
        ("quota_peak_non_paged_pool_usage", ctypes.c_size_t),
        ("quota_non_paged_pool_usage", ctypes.c_size_t),
        ("pagefile_usage", ctypes.c_size_t),
        ("peak_pagefile_usage", ctypes.c_size_t),
    ]


_kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
_psapi = ctypes.WinDLL("psapi", use_last_error=True)
_get_process = _kernel32.GetCurrentProcess
_get_process.restype = wintypes.HANDLE
_get_memory = _psapi.GetProcessMemoryInfo
_get_memory.argtypes = [
    wintypes.HANDLE,
    ctypes.POINTER(_ProcessMemoryCounters),
    wintypes.DWORD,
]
_get_memory.restype = wintypes.BOOL


def _working_set_mib() -> float:
    counters = _ProcessMemoryCounters()
    counters.cb = ctypes.sizeof(counters)
    if not _get_memory(_get_process(), ctypes.byref(counters), counters.cb):
        raise ctypes.WinError(ctypes.get_last_error())
    return counters.working_set_size / (1024 * 1024)


def _percentile(values: list[float], percentile: float) -> float:
    ordered = sorted(values)
    index = min(len(ordered) - 1, round((len(ordered) - 1) * percentile))
    return ordered[index]


@dataclass(frozen=True, slots=True)
class BenchmarkResult:
    delegate: str
    seconds: float
    signal_rate: float
    frame_age_p50_ms: float
    frame_age_p95_ms: float
    inference_p50_ms: float
    inference_p95_ms: float
    processed_count: int
    replaced_count: int
    peak_retained_frames: int
    final_retained_frames: int
    working_set_start_mib: float
    working_set_end_mib: float
    warm_growth_mib_per_min: float

    def lines(self) -> list[str]:
        return [
            f"{self.delegate.upper()} benchmark PASS ({self.seconds:.1f}s)",
            f"signal rate: {self.signal_rate:.2f}/s",
            f"frame age p50/p95: {self.frame_age_p50_ms:.1f}/{self.frame_age_p95_ms:.1f} ms",
            f"inference p50/p95: {self.inference_p50_ms:.1f}/{self.inference_p95_ms:.1f} ms",
            f"processed/replaced: {self.processed_count}/{self.replaced_count}",
            f"working set start/end: {self.working_set_start_mib:.1f}/{self.working_set_end_mib:.1f} MiB",
            f"post-warm-up growth: {self.warm_growth_mib_per_min:.2f} MiB/min",
            f"retained frames peak/final: {self.peak_retained_frames}/{self.final_retained_frames}",
        ]


def run_delegate_benchmark(seconds: float, delegate: str = "cpu") -> BenchmarkResult:
    if not math.isfinite(seconds) or seconds <= 0:
        raise ValueError("benchmark seconds must be positive")
    frames = [step.frame for step in replay_steps()]
    slot = LatestFrameSlot()
    stop = threading.Event()
    producer_done = threading.Event()
    start_memory = _working_set_mib()
    memory_samples: list[tuple[float, float]] = [(0.0, start_memory)]
    frame_ages: list[float] = []
    inference_times: list[float] = []
    signal_count = processed_count = peak_retained = 0
    processor = FaceProcessor(delegate)
    start = time.perf_counter()

    def produce() -> None:
        index = 0
        deadline = start
        try:
            while not stop.is_set():
                now = time.perf_counter()
                if now < deadline:
                    stop.wait(deadline - now)
                    continue
                slot.replace(FramePacket(frames[index % len(frames)], now, index + 1))
                index += 1
                deadline += 1 / 30
        finally:
            producer_done.set()

    producer = threading.Thread(target=produce, name="video-benchmark-producer")
    producer.start()
    last_memory_sample = start
    try:
        while time.perf_counter() - start < seconds:
            packet = slot.take(0.1)
            if packet is None:
                continue
            inference_start = time.perf_counter()
            result = processor.process(packet.pixels, int(packet.captured_at * 1_000))
            finished = time.perf_counter()
            inference_times.append((finished - inference_start) * 1_000)
            frame_ages.append((finished - packet.captured_at) * 1_000)
            processed_count += 1
            signal_count += int(result.signal is not None)
            peak_retained = max(peak_retained, slot.retained_count + 1)
            if processor.tracker.is_lost:
                processor.switch_face()
            if finished - last_memory_sample >= 1:
                memory_samples.append((finished - start, _working_set_mib()))
                last_memory_sample = finished
            packet = None
    finally:
        stop.set()
        slot.clear()
        producer.join(3)
        processor.close()
    if producer.is_alive() or not producer_done.is_set():
        raise RuntimeError("benchmark producer did not stop")
    if not frame_ages or not inference_times:
        raise RuntimeError("benchmark processed no frames")

    elapsed = time.perf_counter() - start
    end_memory = _working_set_mib()
    memory_samples.append((elapsed, end_memory))
    warm_samples = [sample for sample in memory_samples if sample[0] >= 120]
    if len(warm_samples) >= 2:
        span_minutes = (warm_samples[-1][0] - warm_samples[0][0]) / 60
        warm_growth = (warm_samples[-1][1] - warm_samples[0][1]) / span_minutes
        warm_baseline = warm_samples[0][1]
    else:
        warm_growth = 0.0
        warm_baseline = end_memory
    result = BenchmarkResult(
        delegate=delegate,
        seconds=elapsed,
        signal_rate=signal_count / elapsed,
        frame_age_p50_ms=statistics.median(frame_ages),
        frame_age_p95_ms=_percentile(frame_ages, 0.95),
        inference_p50_ms=statistics.median(inference_times),
        inference_p95_ms=_percentile(inference_times, 0.95),
        processed_count=processed_count,
        replaced_count=slot.replaced_count,
        peak_retained_frames=peak_retained,
        final_retained_frames=slot.retained_count,
        working_set_start_mib=start_memory,
        working_set_end_mib=end_memory,
        warm_growth_mib_per_min=warm_growth,
    )
    if result.signal_rate < 10:
        raise RuntimeError(f"CPU signal rate below 10/s: {result.signal_rate:.2f}")
    if result.frame_age_p95_ms >= 500:
        raise RuntimeError(f"CPU p95 frame age at least 500 ms: {result.frame_age_p95_ms:.1f}")
    if result.peak_retained_frames > 2 or result.final_retained_frames:
        raise RuntimeError("application retained too many frames")
    if elapsed >= 180 and (
        result.warm_growth_mib_per_min > 2
        or result.working_set_end_mib - warm_baseline > 100
    ):
        raise RuntimeError("working-set plateau threshold failed")
    return result


def run_benchmark(seconds: float) -> str:
    cpu = run_delegate_benchmark(seconds, "cpu")
    lines = cpu.lines()
    try:
        gpu_seconds = seconds
        completed = subprocess.run(
            [sys.executable, "-m", "conversation_copilot.benchmark", str(gpu_seconds)],
            check=False,
            capture_output=True,
            text=True,
            timeout=gpu_seconds + 10,
        )
        if completed.returncode:
            detail = completed.stderr.strip() or "no diagnostic"
            raise RuntimeError(f"GPU delegate unavailable: {detail}")
        gpu = BenchmarkResult(**json.loads(completed.stdout.strip()))
    except (OSError, RuntimeError, subprocess.TimeoutExpired, ValueError) as exc:
        lines.append(f"GPU skipped: unsupported ({type(exc).__name__}: {exc})")
    else:
        improvement = 1 - gpu.frame_age_p95_ms / cpu.frame_age_p95_ms
        if improvement >= 0.20:
            lines.extend(gpu.lines())
            lines.append(f"GPU retained: p95 improved {improvement:.0%}")
        else:
            lines.append(f"GPU not retained: p95 improvement {improvement:.0%} is below 20%")
    return "\n".join(lines)


if __name__ == "__main__":
    try:
        print(json.dumps(asdict(run_delegate_benchmark(float(sys.argv[1]), "gpu"))))
    except BaseException as exc:
        print(f"{type(exc).__name__}: {exc}", file=sys.stderr)
        raise SystemExit(1)
