"""Frozen fictional F06 question evaluation; no real contacts or media are loaded."""
from __future__ import annotations

import argparse
import json
import statistics
import time
from datetime import datetime, timezone
from pathlib import Path

from .ask_memory import AskSession, validate_sources
from .memory import MemoryStore, SummaryOutput, SummaryStatementInput, default_database_path
from .models import ConversationTurn, SpeakerRole
from .semantic import default_cache_dir, model_ready

FIXTURE = Path(__file__).parent / "assets" / "f06" / "questions.json"
HISTORY_FIXTURE = FIXTURE.with_name("history.json")


def seed_history(store):
    """Explicit fictional demo: three source calls and their hand-authored approved memories."""
    fixture = json.loads(HISTORY_FIXTURE.read_text(encoding="utf-8"))
    contact = store.create_contact(fixture["contact"], "Fictional three-call Ask test; no real person")
    ids = {}
    for call in fixture["calls"]:
        stamp = datetime.fromisoformat(call["date"] + "T12:00:00+03:00")
        turns = []
        for item in call["items"]:
            for role, name, text in ((SpeakerRole.USER, "You", item["you"]),
                                     (SpeakerRole.SELECTED_CONTACT, "Alex", item["said"])):
                turns.append(ConversationTurn(speaker_name=name, speaker_role=role,
                    source="fictional-ask-fixture", content=text, timestamp=stamp, display_order=len(turns)+1))
        record = store.create_record(source_kind="call", source_label="FICTIONAL: " + call["title"],
            timezone_name="Asia/Jerusalem", contact_id=contact.id, status="stopped", turns=turns)
        for i, item in enumerate(call["items"]):
            memory_id = store.create_memory(contact.id, item["memory"], record_id=record,
                evidence_turns=[2*i+1, 2*i+2], sensitivity="sensitive" if item.get("sensitive") else "normal",
                normalized_date_start=item.get("event"))
            if item.get("sensitive"):
                # Seed fictional permission without falsely labeling it a factual correction.
                with store.transaction() as db:
                    db.execute("UPDATE memory_revisions SET cloud_allowed=1 WHERE id=?",
                               (store.current_revision(memory_id)["id"],))
            ids[item["id"]] = memory_id
    return contact.id, ids, fixture


def seed_case(store, setup):
    contact = store.create_contact("Yaheli", "fictional F06 fixture")
    store.create_contact("Alex", "different fictional person")
    content = "Yaheli's dentist appointment is Tuesday at 3 PM at Cedar Clinic."
    if setup == "style":
        content = "Yaheli prefers direct, concise replies. This communication preference is approved."
    if setup == "missing_venue":
        content = "Yaheli's dentist appointment is Tuesday at 3 PM."
    record = store.create_record(source_kind="call", source_label="F06 fictional fixture",
        timezone_name="Asia/Jerusalem", contact_id=contact.id, status="stopped", turns=[ConversationTurn(
            speaker_name="Yaheli", speaker_role=SpeakerRole.SELECTED_CONTACT, source="fixture",
            content=content, timestamp=datetime(2026, 9, 7, 12, tzinfo=timezone.utc), display_order=1)])
    session = AskSession(contact.id)
    memory_id = None
    if setup != "empty":
        memory_id = store.create_memory(contact.id, content, memory_type="communication_style" if setup == "style" else "event_date",
            record_id=record, evidence_turns=[1])
    if setup in {"historical", "corrected"}:
        summary = store.create_summary_draft(record, SummaryOutput(statements=[SummaryStatementInput(
            section="plans", content=content, kind="fact", confidence="high", evidence_turns=[1])]), expected_generation=1)
        store.approve_summary(summary)
        statement = store.summary_statements(summary)[0]["id"]
        store.correct_memory(memory_id, content.replace("3 PM", "4 PM"), summary_choices={statement: "keep"})
    if setup == "deleted":
        store.delete_memory(memory_id)
    if setup == "ambiguous":
        store.create_memory(contact.id, "Yaheli's dentist appointment is Friday at 10 AM at Cedar Clinic.", memory_type="event_date")
    if setup in {"followup", "missing_venue"}:
        session.choose_event(memory_id)
    return session, statement if setup == "historical" else memory_id


def evaluate_local():
    cases = json.loads(FIXTURE.read_text(encoding="utf-8"))
    cache = default_cache_dir(default_database_path())
    original = MemoryStore.semantic_cache_dir
    MemoryStore.semantic_cache_dir = property(lambda _self: cache)
    results = []
    try:
        for semantic in (False, True):
            for case in cases:
                with MemoryStore(":memory:") as store:
                    session, expected_source = seed_case(store, case["setup"])
                    if semantic:
                        store.backfill_semantic_embeddings()
                    started = time.perf_counter()
                    result = session.answer(store, case["query"], semantic=semantic)
                    elapsed = 1000 * (time.perf_counter() - started)
                    passed = result.status == case["status"] and ("fact" not in case or case["fact"].casefold() in result.answer.casefold())
                    citations_ok = validate_sources(store, result.sources)
                    recall = expected_source in {source.id for source in result.sources[:4]} if case["status"] == "answered" else None
                    results.append({"id": case["id"], "semantic": semantic, "expected": case["status"],
                        "actual": result.status, "passed": passed and citations_ok, "citations_valid": citations_ok,
                        "answer": result.answer, "milliseconds": elapsed, "answerable": case["status"] == "answered", "recall_at_4": recall})
        return {"fixture": str(FIXTURE), "semantic_model_ready": model_ready(cache), "results": results,
            "profiles": {str(semantic): {
                "passed": sum(row["passed"] for row in results if row["semantic"] == semantic),
                "cases": len(cases),
                "answerable_correct": sum(row["passed"] for row in results if row["semantic"] == semantic and row["answerable"]),
                "answerable_total": sum(row["answerable"] for row in results if row["semantic"] == semantic),
                "recall_at_4": statistics.mean(row["recall_at_4"] for row in results if row["semantic"] == semantic and row["answerable"]),
                "p95_ms": sorted(row["milliseconds"] for row in results if row["semantic"] == semantic)[int(len(cases) * .95) - 1],
            } for semantic in (False, True)}}
    finally:
        MemoryStore.semantic_cache_dir = original


def evaluate_cloud(output_path, reasoning="none", group="all", ids=(), guidance_model="gpt-5.6-luna"):
    from .interpretation import BudgetLimits, UsageLedger, RetrievedMemoryContext
    from .guidance import interpret_guidance
    from .f04_evaluation import EvaluationScenario
    from .post_call import process_review
    from .memory import FakeMemoryExtractor, ExtractionOutput
    from .ask_memory import cloud_answer
    cache = default_cache_dir(default_database_path())
    original = MemoryStore.semantic_cache_dir
    try:
        MemoryStore.semantic_cache_dir = property(lambda _self: cache)
        # Persist every reservation before dispatch: an interrupted run remains conservatively charged.
        spend_path = output_path.parent / "f06-paid-spend.json"
        previous = json.loads(spend_path.read_text())["committed_dollars"] if spend_path.exists() else 0.0
        class EvaluationLedger(UsageLedger):
            def persist(self):
                temporary = spend_path.with_suffix(".tmp")
                temporary.write_text(json.dumps({"committed_dollars": previous + self.committed_dollars}), encoding="utf-8")
                temporary.replace(spend_path)
            def reserve(self, *args, **kwargs):
                result = super().reserve(*args, **kwargs)
                self.persist()
                return result
            def complete(self, *args):
                super().complete(*args)
                self.persist()
            def release(self, *args):
                super().release(*args)
                self.persist()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        if previous >= 2:
            raise ValueError("F06 aggregate paid allowance exhausted")
        ledger = EvaluationLedger(BudgetLimits(warning_dollars=(2 - previous) / 2, hard_dollars=2 - previous))
        fixtures = json.loads(FIXTURE.with_name("quality.json").read_text())
        results = []
        def record(case, started, result=None, error=None):
            text = json.dumps(result, ensure_ascii=False) if result is not None else ""
            passed = error is None and all(word.casefold() in text.casefold() for word in case.get("required", [])) and not any(
                word.casefold() in text.casefold() for word in case.get("forbidden", []))
            if isinstance(result, dict):
                import re
                passed = passed and not any(re.search(r"\[[^\]]+\]|<[^>]+>", item["text"])
                    for category in ("replies", "remember", "follow_up") for item in result.get(category, []))
            results.append({"id": case["id"], "milliseconds": (time.perf_counter() - started) * 1000,
                            "passed_automatic_checks": passed, "output": result, "error": error})
            output_path.write_text(json.dumps({"model": guidance_model if group == "guidance" else "gpt-5.6-luna", "guidance_model": guidance_model, "reasoning": reasoning, "results": results,
                "aggregate_committed_dollars": previous + ledger.committed_dollars}, indent=2), encoding="utf-8")
            print(case["id"], "checks passed" if passed else "needs review", flush=True)
            if error and ("credit_balance_exhausted" in error or "AuthenticationError" in error):
                raise RuntimeError("Controlled evaluation stopped: restore the configured API account before resuming")
        for case in fixtures["guidance"] if group in {"all", "guidance"} else []:
            if ids and case["id"] not in ids:
                continue
            started = time.perf_counter()
            try:
                snapshot = EvaluationScenario(case["id"], "f06", case["user"], case["remote"]).snapshot("transcript")
                memories = [RetrievedMemoryContext(memory_id="m-style", revision_id="r-style", excerpt=case["style"],
                    memory_type="communication_style", confidence="high", sensitivity_safe=True, rank=1, relevance="explicit style")] if "style" in case else []
                snapshot = snapshot.model_copy(update={"contact_id": "fictional-yaheli", "memories": memories})
                result = interpret_guidance(snapshot, ledger=ledger, model=guidance_model, reasoning=reasoning, live=False).model_dump(mode="json")
                record(case, started, result)
            except Exception as exc:
                record(case, started, error=f"{type(exc).__name__}: {exc}")
        for case in fixtures["summaries"] if group in {"all", "summaries"} else []:
            if ids and case["id"] not in ids:
                continue
            started = time.perf_counter()
            try:
                with MemoryStore(":memory:") as store:
                    contact = store.create_contact("Yaheli")
                    record_id = store.create_record(source_kind="call", source_label="F06 fictional controlled summary",
                        timezone_name="Asia/Jerusalem", contact_id=contact.id, status="stopped", turns=[ConversationTurn(
                            speaker_name="Yaheli", speaker_role=SpeakerRole.SELECTED_CONTACT, source="fixture", content=text,
                            timestamp=datetime(2026, 9, 7, 12, tzinfo=timezone.utc), display_order=i + 1) for i, text in enumerate(case["turns"])])
                    summary = process_review(store, record_id, ledger=ledger, extractor=FakeMemoryExtractor([ExtractionOutput()]))
                    result = [dict(row) for row in store.summary_statements(summary)]
                    record(case, started, result)
            except Exception as exc:
                record(case, started, error=f"{type(exc).__name__}: {exc}")
        for case in json.loads(FIXTURE.read_text()) if group in {"all", "ask"} else []:
            if ids and case["id"] not in ids:
                continue
            started = time.perf_counter()
            try:
                with MemoryStore(":memory:") as store:
                    session, _ = seed_case(store, case["setup"])
                    store.backfill_semantic_embeddings()
                    local = session.answer(store, case["query"])
                    # Cloud is an explicit grounded enhancement; no evidence remains a local abstention.
                    result = cloud_answer(store, case["query"], local.sources, ledger=ledger) if local.sources else local
                    check = {**case, "required": [case["fact"]] if "fact" in case else []}
                    compatible = result.status == case["status"] or case["status"] == "possibilities" and result.status in {"clarification", "conflict"}
                    compatible = compatible or case["status"] == "no_match" and result.status == "unavailable"
                    record(check, started, {"status": result.status, "answer": result.answer, "sources": [source.id for source in result.sources],
                        "citations_valid": validate_sources(store, result.sources), "backend": result.backend}, error=None if compatible else "wrong result status")
            except Exception as exc:
                record(case, started, error=f"{type(exc).__name__}: {exc}")
        return json.loads(output_path.read_text())
    finally:
        MemoryStore.semantic_cache_dir = original


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--seed-history", action="store_true", help="Create a NEW isolated SQLite demo, no API calls")
    parser.add_argument("--cloud", action="store_true", help="Explicit paid fictional evaluation; aggregate persisted cap $2")
    parser.add_argument("--reasoning", choices=("none", "low"), default="none")
    parser.add_argument("--guidance-model", choices=("gpt-5.6-luna", "gpt-5.6-terra"), default="gpt-5.6-luna")
    parser.add_argument("--group", choices=("all", "guidance", "ask", "summaries"), default="all")
    parser.add_argument("--ids", nargs="*", default=[])
    args = parser.parse_args()
    if args.seed_history:
        if args.output.exists():
            parser.error("Choose a new output path; existing databases are never overwritten.")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with MemoryStore(args.output) as store:
            contact, ids, fixture = seed_history(store)
        print(json.dumps({"database": str(args.output.resolve()), "contact": contact, "memories": len(ids)}))
        raise SystemExit(0)
    if args.cloud:
        evaluate_cloud(args.output, args.reasoning, args.group, args.ids, args.guidance_model)
        raise SystemExit(0)
    report = evaluate_local()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report["profiles"], indent=2))
    print("Failures:", [(row["id"], row["semantic"], row["actual"]) for row in report["results"] if not row["passed"]])
