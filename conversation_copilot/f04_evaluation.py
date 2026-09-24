from __future__ import annotations

import json
import math
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from .interpretation import (
    BudgetLimits,
    InterpretationUnavailable,
    InterpretationSnapshot,
    InterpretationUpdate,
    OpenAIInterpreter,
    TERRA_MODEL,
    UsageLedger,
    UsageRecord,
    VisualBucket,
    VocalObservation,
    build_snapshot,
)
from .models import ConversationTurn, SpeakerRole

MODES = ("transcript", "vocal", "visual", "all")
LUNA_MODEL = "gpt-5.6-luna"  # Preserve this historical evaluation's explicit profiles.
STAGE_A_MODES = ("transcript", "all")
PROFILES = (
    (LUNA_MODEL, "none"),
    (LUNA_MODEL, "low"),
    (TERRA_MODEL, "none"),
    (TERRA_MODEL, "low"),
)
FORBIDDEN_CLAIMS = (
    "definitely feels",
    "certainly feels",
    "is feeling",
    "true emotion",
    "intends to",
    "wants to manipulate",
)


@dataclass(frozen=True, slots=True)
class EvaluationScenario:
    identifier: str
    category: str
    user_text: str
    remote_text: str
    acceptable_tones: tuple[str, ...] = ()
    acceptable_cues: tuple[str, ...] = ()
    uplift_modality: str | None = None
    conflicting: bool = False
    relative_energy: float = 1.0
    words_per_voiced_second: float = 2.5
    gap_seconds: float = 0.5
    visual_movement: float = 0.03

    def expected_status(self, mode: str) -> str:
        if self.conflicting:
            return "conflicting_evidence"
        if self.uplift_modality and mode not in {self.uplift_modality, "all"}:
            return "insufficient_evidence"
        return "updated"

    def snapshot(self, mode: str, snapshot_id: int = 1) -> InterpretationSnapshot:
        if mode not in MODES:
            raise ValueError("unknown evaluation modality mode")
        started = datetime(2026, 8, 25, 12, 0, tzinfo=timezone.utc)
        turns = [
            ConversationTurn(
                speaker_name="You",
                speaker_role=SpeakerRole.USER,
                source="microphone",
                content=self.user_text,
                timestamp=started,
                display_order=1,
            ),
            ConversationTurn(
                speaker_name="Contact",
                speaker_role=SpeakerRole.SELECTED_CONTACT,
                source="system_audio_loopback",
                content=self.remote_text,
                timestamp=started + timedelta(seconds=8),
                display_order=2,
            ),
        ]
        vocal = (
            [
                VocalObservation(
                    turn_display_order=2,
                    available=True,
                    duration_seconds=2.0,
                    relative_energy=self.relative_energy,
                    voiced_ratio=0.72,
                    words_per_voiced_second=self.words_per_voiced_second,
                    gap_seconds=self.gap_seconds,
                    overlaps_user=False,
                )
            ]
            if mode in {"vocal", "all"}
            else []
        )
        visual = (
            [
                VisualBucket(
                    started_at=started + timedelta(seconds=6),
                    ended_at=started + timedelta(seconds=8),
                    availability=1.0,
                    reliability=0.95,
                    face_movement=self.visual_movement,
                    smile_movement=self.visual_movement,
                    brow_movement=self.visual_movement * 1.4,
                    eye_movement=self.visual_movement * 0.8,
                    mouth_movement=self.visual_movement * 1.2,
                )
            ]
            if mode in {"visual", "all"}
            else []
        )
        return build_snapshot(
            turns,
            snapshot_id=snapshot_id,
            generation=1,
            vocal_observations=vocal,
            visual_buckets=visual,
            created_at=started + timedelta(seconds=9),
        )


SCENARIOS = (
    EvaluationScenario(
        "neutral", "neutral", "Does Tuesday at ten work?", "Yes, Tuesday at ten works for me.",
        acceptable_tones=("neutral_calm",),
    ),
    EvaluationScenario(
        "warm", "positive", "Your presentation was really clear.", "Thank you, that means a lot to me!",
        acceptable_tones=("positive_warm",), acceptable_cues=("interest_engagement",),
    ),
    EvaluationScenario(
        "deadline", "negative", "The deadline was yesterday.", "I know. I am frustrated that the requirements changed again.",
        acceptable_tones=("tense_negative", "emotionally_intense"),
    ),
    EvaluationScenario(
        "launch", "high_energy", "The prototype finally works.", "Amazing! Let's show everyone today and plan the next version!",
        acceptable_tones=("energetic_high_energy", "positive_warm"),
        relative_energy=1.7, words_per_voiced_second=4.2,
    ),
    EvaluationScenario(
        "difficult_week", "low_energy", "How has your week been?", "It has been difficult. I am tired and I need a quiet weekend.",
        acceptable_tones=("sad_low_energy", "neutral_calm"),
        relative_energy=0.55, words_per_voiced_second=1.2, gap_seconds=2.4,
    ),
    EvaluationScenario(
        "urgent_change", "intense", "Can this wait until tomorrow?", "No, this change affects the whole release and we need to decide now.",
        acceptable_tones=("emotionally_intense", "tense_negative"),
        relative_energy=1.8, words_per_voiced_second=4.0,
    ),
    EvaluationScenario(
        "coffee_joke", "humor", "Did you finish the report?", "Almost. My coffee is doing most of the writing today.",
        acceptable_tones=("positive_warm",), acceptable_cues=("humor",),
    ),
    EvaluationScenario(
        "another_meeting", "sarcasm", "They added another meeting tomorrow.", "Oh great, exactly what my empty calendar needed.",
        acceptable_cues=("sarcasm",), uplift_modality="vocal",
        relative_energy=0.45, words_per_voiced_second=1.1, gap_seconds=1.8,
    ),
    EvaluationScenario(
        "follow_up", "interest", "I started learning pottery.", "What made you choose pottery, and what have you made so far?",
        acceptable_tones=("positive_warm",), acceptable_cues=("interest_engagement",),
    ),
    EvaluationScenario(
        "hedging", "uncertainty", "Should we book it now?", "Maybe. I think it could work, but I am not completely sure yet.",
        acceptable_cues=("uncertainty",),
    ),
    EvaluationScenario(
        "short_answers", "withdrawal", "Do you want to discuss what happened?", "Not really. It is fine. Can we talk later?",
        acceptable_cues=("discomfort", "disengagement_withdrawal"),
        uplift_modality="visual", visual_movement=0.18,
    ),
    EvaluationScenario(
        "mixed_signals", "conflict", "Are you comfortable with the plan?", "It is fine, but please stop asking me about it.",
        conflicting=True, relative_energy=1.8, visual_movement=0.2,
    ),
)


@dataclass(frozen=True, slots=True)
class EvaluationResult:
    scenario: EvaluationScenario
    mode: str
    update: InterpretationUpdate
    usage: UsageRecord
    latency_seconds: float


def _percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, math.ceil(len(ordered) * fraction) - 1)]


def _primary_ok(result: EvaluationResult) -> bool:
    expected = result.scenario.expected_status(result.mode)
    if result.update.status.value != expected:
        return False
    if expected != "updated":
        return True
    kinds = {
        item.kind.value for item in (*result.update.tones, *result.update.social_cues)
    }
    return bool(
        kinds
        & set(result.scenario.acceptable_tones + result.scenario.acceptable_cues)
    )


def _unacceptable_items(result: EvaluationResult) -> int:
    acceptable = set(
        result.scenario.acceptable_tones + result.scenario.acceptable_cues
    )
    return sum(
        item.kind.value not in acceptable
        for item in (*result.update.tones, *result.update.social_cues)
    )


def _quality_rates(results: list[EvaluationResult]) -> dict[str, float]:
    clear = [item for item in results if item.scenario.expected_status(item.mode) == "updated"]
    uncertain = [item for item in results if item.scenario.expected_status(item.mode) != "updated"]
    emitted = [
        (result, item)
        for result in results
        for item in (*result.update.tones, *result.update.social_cues)
    ]
    acceptable = [
        (result, item)
        for result, item in emitted
        if item.kind.value
        in set(result.scenario.acceptable_tones + result.scenario.acceptable_cues)
    ]
    high = [(result, item) for result, item in emitted if item.confidence.value == "high"]
    return {
        "primary_rate": sum(_primary_ok(item) for item in clear) / len(clear) if clear else 1.0,
        "abstention_rate": sum(_primary_ok(item) for item in uncertain) / len(uncertain) if uncertain else 1.0,
        "acceptable_emitted_rate": len(acceptable) / len(emitted) if emitted else 1.0,
        "acceptable_high_confidence_rate": sum(pair in acceptable for pair in high) / len(high) if high else 1.0,
    }


def score_results(results: list[EvaluationResult]) -> dict:
    emitted = [
        (result, item)
        for result in results
        for item in (*result.update.tones, *result.update.social_cues)
    ]
    acceptable = [
        (result, item)
        for result, item in emitted
        if item.kind.value
        in set(result.scenario.acceptable_tones + result.scenario.acceptable_cues)
    ]
    modalities_ok = all(
        {value.value for value in item.evidence.modalities}
        <= ({"language"} | ({"vocal"} if result.mode in {"vocal", "all"} else set())
            | ({"visual"} if result.mode in {"visual", "all"} else set()))
        for result, item in emitted
    )
    claims = sum(
        any(phrase in (item.hypothesis + " " + item.evidence.explanation).casefold() for phrase in FORBIDDEN_CLAIMS)
        for _result, item in emitted
    )
    confidence = {}
    for level in ("low", "medium", "high"):
        items = [(result, item) for result, item in emitted if item.confidence.value == level]
        accepted = sum(pair in acceptable for pair in items)
        confidence[level] = {
            "count": len(items),
            "acceptable_rate": accepted / len(items) if len(items) >= 5 else "insufficient sample",
        }
    rates = _quality_rates(results)
    model_results = [item for item in results if item.usage.input_tokens > 0]
    model_rates = _quality_rates(model_results)
    latencies = [item.latency_seconds for item in model_results]
    metrics = {
        "evaluations": len(results),
        "model_answered_evaluations": len(model_results),
        **rates,
        "model_only": model_rates,
        "evidence_modalities_valid": modalities_ok,
        "prohibited_claims": claims,
        "input_ceiling_valid": all(item.usage.input_tokens <= 1_650 for item in results),
        "latency_p50_seconds": _percentile(latencies, 0.5) if latencies else None,
        "latency_p95_seconds": _percentile(latencies, 0.95) if latencies else None,
        "cost_dollars": sum(item.usage.dollars for item in results),
        "calibration": confidence,
    }
    metrics["passes"] = bool(
        model_results
        and rates["primary_rate"] >= 0.80
        and rates["abstention_rate"] >= 0.80
        and rates["acceptable_emitted_rate"] >= 0.70
        and rates["acceptable_high_confidence_rate"] >= 0.85
        and model_rates["primary_rate"] >= 0.80
        and model_rates["abstention_rate"] >= 0.80
        and model_rates["acceptable_emitted_rate"] >= 0.70
        and model_rates["acceptable_high_confidence_rate"] >= 0.85
        and modalities_ok
        and claims == 0
        and metrics["input_ceiling_valid"]
        and metrics["latency_p95_seconds"] is not None
        and metrics["latency_p95_seconds"] <= 6
    )
    return metrics


def _run_profile(
    model: str,
    reasoning: str,
    modes: tuple[str, ...],
    ledger: UsageLedger,
    starting_snapshot_id: int,
) -> tuple[list[EvaluationResult], str | None]:
    results = []
    try:
        interpreter = OpenAIInterpreter(
            model=model, reasoning=reasoning, ledger=ledger
        )
    except InterpretationUnavailable as exc:
        return results, type(exc).__name__
    snapshot_id = starting_snapshot_id
    for scenario in SCENARIOS:
        for mode in modes:
            snapshot_id += 1
            before = len(ledger.records)
            started = time.perf_counter()
            try:
                update = interpreter(scenario.snapshot(mode, snapshot_id))
            except InterpretationUnavailable as exc:
                return results, type(exc).__name__
            latency = time.perf_counter() - started
            records = ledger.records
            request_records = records[before:]
            if not request_records:
                usage = UsageRecord(model, reasoning, 0, 0, 0, 0, 0, 0.0)
            else:
                last = request_records[-1]
                usage = UsageRecord(
                    model,
                    reasoning,
                    last.input_tokens,
                    last.cached_input_tokens,
                    last.cache_write_input_tokens,
                    last.output_tokens,
                    last.reasoning_tokens,
                    sum(item.dollars for item in request_records),
                )
            results.append(EvaluationResult(scenario, mode, update, usage, latency))
    return results, None


def run_real_evaluation() -> str:
    ledger = UsageLedger(BudgetLimits(0.15, 1.50, 1.50))
    stage_a: dict[tuple[str, str], list[EvaluationResult]] = {}
    snapshot_id = 0
    stopped = None
    for model, reasoning in PROFILES:
        results, stopped = _run_profile(
            model, reasoning, STAGE_A_MODES, ledger, snapshot_id
        )
        snapshot_id += len(results)
        stage_a[(model, reasoning)] = results
        if stopped:
            break
    summaries = {
        f"{model}:{reasoning}": score_results(results)
        for (model, reasoning), results in stage_a.items()
    }
    passing_luna = [
        profile
        for profile in ((LUNA_MODEL, "none"), (LUNA_MODEL, "low"))
        if f"{profile[0]}:{profile[1]}" in summaries
        and summaries[f"{profile[0]}:{profile[1]}"]["passes"]
    ]
    report = {
        "stage_a": summaries,
        "winner": None,
        "stage_b": None,
        "modality_uplift": None,
        "calls": len(ledger.records),
        "spent_dollars": ledger.total_dollars,
        "evaluation_cap_dollars": ledger.limits.hard_dollars,
        "stopped": stopped,
    }
    if stopped or not passing_luna:
        return json.dumps(report, indent=2, sort_keys=True)
    winner = min(
        passing_luna,
        key=lambda profile: summaries[f"{profile[0]}:{profile[1]}"]["cost_dollars"],
    )
    stage_b, stopped = _run_profile(
        winner[0], winner[1], ("vocal", "visual"), ledger, snapshot_id
    )
    stage_b_metrics = score_results(stage_b)
    if stopped:
        report.update(
            winner={"model": winner[0], "reasoning": winner[1]},
            stage_b=stage_b_metrics,
            calls=len(ledger.records),
            spent_dollars=ledger.total_dollars,
            stopped=stopped,
        )
        return json.dumps(report, indent=2, sort_keys=True)
    transcript = {
        item.scenario.identifier: item
        for item in stage_a[winner]
        if item.mode == "transcript"
    }
    added = {(item.scenario.identifier, item.mode): item for item in stage_b}
    recovery_pairs = [
        (scenario.identifier, scenario.uplift_modality)
        for scenario in SCENARIOS
        if scenario.uplift_modality
    ]
    recovered = sum(
        transcript[identifier].update.status.value != "updated"
        and _primary_ok(added[(identifier, mode)])
        for identifier, mode in recovery_pairs
    )
    added_unacceptable = sum(_unacceptable_items(item) for item in stage_b)
    baseline_unacceptable = 2 * sum(
        _unacceptable_items(item) for item in transcript.values()
    )
    additional_unacceptable = max(0, added_unacceptable - baseline_unacceptable)
    unsupported_high = sum(
        item.confidence.value == "high"
        and item.kind.value
        not in set(result.scenario.acceptable_tones + result.scenario.acceptable_cues)
        for result in stage_b
        for item in (*result.update.tones, *result.update.social_cues)
    )
    report.update(
        winner={"model": winner[0], "reasoning": winner[1]},
        stage_b=stage_b_metrics,
        modality_uplift={
            "designated_cases": len(recovery_pairs),
            "recovered_cases": recovered,
            "additional_unacceptable_items": additional_unacceptable,
            "unsupported_high_confidence_items": unsupported_high,
            "passes": recovered >= 2 and additional_unacceptable <= 1 and unsupported_high == 0,
        },
        calls=len(ledger.records),
        spent_dollars=ledger.total_dollars,
    )
    return json.dumps(report, indent=2, sort_keys=True)
