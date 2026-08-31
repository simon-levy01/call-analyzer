import json

from conversation_copilot.f05_evaluation import (
    EXTRACTION_SCENARIOS,
    _score_extraction,
    run_local_evaluation,
)
from conversation_copilot.memory import EXTRACTION_INSTRUCTIONS, MemoryProposalInput


def test_fixed_f05_retrieval_and_safety_gates_pass_without_cloud_or_model_downloads():
    report = json.loads(run_local_evaluation(large_store=False, semantic_model=False))
    fixed = report["fixed"]

    assert fixed["recall_at_4"] >= 0.90
    assert fixed["mrr"] >= 0.80
    assert fixed["safety_pass_rate"] == 1.0
    assert all(fixed["safety"].values())
    assert all(fixed["coverage"].values())
    assert fixed["zero_unsupported_high_confidence_from_memory"] is True
    assert "BGE-small" in report["technology_gate"]["selected"]
    assert report["technology_gate"]["mem0"].startswith("rejected:")
    assert report["technology_gate"]["graphiti"].startswith("rejected:")
    assert report["semantic"] is None
    assert "not added" in report["technology_gate"]["cloud_rerank"]


def test_routine_one_off_activity_is_not_a_useful_memory_proposal():
    scenario = next(item for item in EXTRACTION_SCENARIOS if item.identifier == "routine_activity")
    walk = MemoryProposalInput(
        content="Test Contact took a walk yesterday",
        memory_type="other",
        confidence="high",
        evidence_turns=[2],
    )
    assert "one-off routine activities" in EXTRACTION_INSTRUCTIONS
    assert _score_extraction(scenario, []) is True
    assert _score_extraction(scenario, [walk]) is False
