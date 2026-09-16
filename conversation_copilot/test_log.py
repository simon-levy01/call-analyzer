"""Explicitly enabled, private numeric/text evidence; never accepts image/audio buffers."""
import atexit
import dataclasses
from datetime import datetime, timezone
from enum import Enum
import hashlib
import json
import os
from numbers import Real
from pathlib import Path
import queue
import sys
import threading
import time
import uuid

from pydantic import BaseModel


def _json(value):
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, (set, frozenset)):
        return sorted(value)
    if isinstance(value, Real):
        return float(value)
    if isinstance(value, BaseModel):
        return value.model_dump(mode="json")
    if dataclasses.is_dataclass(value):
        return dataclasses.asdict(value)
    if isinstance(value, datetime):
        return value.isoformat()
    raise TypeError(f"Unsupported test evidence: {type(value).__name__}")


class TestLog:
    __test__ = False

    def __init__(self, directory):
        self.path = Path(directory) / "events.jsonl"
        self.path.parent.mkdir(parents=True, exist_ok=False)
        self.stream = self.path.open("x", encoding="utf-8")
        self.lock = threading.Lock()
        self.error = None
        self.failed = False
        self.sequence = 0
        self.pending = queue.Queue(maxsize=2048)
        self.worker = threading.Thread(target=self._write_lines, daemon=True, name="private-test-log")
        self.worker.start()

    def write(self, event, **data):
        with self.lock:
            if self.failed:
                return
            self.sequence += 1
            envelope = dict(sequence=self.sequence, utc=datetime.now(timezone.utc).isoformat(),
                monotonic=time.perf_counter(), thread=threading.get_ident(), event=event)
            try:
                line = json.dumps(dict(envelope, data=data), default=_json, ensure_ascii=False, allow_nan=False)
            except (TypeError, ValueError) as exc:
                self.error = type(exc).__name__
                line = json.dumps(dict(envelope, serialization_error=self.error))
            try:
                self.pending.put_nowait(line)
            except queue.Full:
                self.error = "QueueFull: evidence missing"

    def _write_lines(self):
        try:
            while True:
                line = self.pending.get()
                try:
                    if line is None:
                        return
                    if not self.failed:
                        self.stream.write(line + "\n")
                        self.stream.flush()
                except (OSError, ValueError) as exc:
                    self.error = type(exc).__name__
                    self.failed = True
                    print(f"TEST LOG FAILED: {self.error}", file=sys.stderr, flush=True)
                finally:
                    self.pending.task_done()
        finally:
            self.stream.close()

    def close(self):
        try:
            self.pending.put(None, timeout=2)
        except queue.Full:
            self.error = "Shutdown backlog: evidence missing"
        self.worker.join(timeout=2)


active = None
startup_error = None


def start():
    global active, startup_error
    if active is not None or os.environ.get("COPILOT_TEST_LOG") != "1":
        return
    root = Path(__file__).resolve().parents[1]
    directory = root / "build" / ("live-evidence-" + datetime.now().strftime("%Y%m%d-%H%M%S-") + uuid.uuid4().hex[:8])
    try:
        candidate = TestLog(directory)
        # Preserve the exact running source, without unrelated files or private stores.
        source = directory / "source"
        source.mkdir()
        hashes = {}
        for path in Path(__file__).parent.glob("*.py"):
            content = path.read_bytes()
            (source / path.name).write_bytes(content)
            hashes[path.name] = hashlib.sha256(content).hexdigest()
    except OSError as exc:
        startup_error = type(exc).__name__
        if "candidate" in locals():
            candidate.close()
        print(f"TEST LOG START FAILED: {startup_error}", file=sys.stderr, flush=True)
        return
    active = candidate
    emit("app_start", source_sha256=hashes, python=sys.version,
         scope="numeric/text only; no raw frames, landmarks, audio, or credentials; no retrospective capture")
    atexit.register(active.close)
    print(f"PRIVATE TEST LOG: {active.path}", flush=True)


def emit(event, **data):
    if active is not None:
        active.write(event, **data)


def parse_response(client, **kwargs):
    if active is None:
        return client.responses.parse(**kwargs)
    request_id = uuid.uuid4().hex
    request = {key: kwargs[key] for key in ("model", "reasoning", "instructions", "input", "text", "max_output_tokens", "store") if key in kwargs}
    if kwargs.get("text_format") is not None:
        request["schema"] = kwargs["text_format"].model_json_schema()
    emit("api_request", request_id=request_id, request=request)
    started = time.perf_counter()
    try:
        response = client.responses.parse(**kwargs)
    except Exception as exc:
        emit("api_error", request_id=request_id, error_type=type(exc).__name__, seconds=time.perf_counter()-started)
        raise
    emit("api_response", request_id=request_id, response=response, seconds=time.perf_counter()-started)
    return response
