"""Offline evidence-integrity checks; no model inference."""
import pytest

from tools.evaluation.memory_evaluation import audit_corpus, audit_transcript, save_new


def test_saved_evidence_counts_chronology_and_no_overwrite(tmp_path):
    row = {"schema": "GuidanceOutput", "request": {
        "instructions": "Use only evidence", "input": {"m": [["m1", "Fictional fact"]]},
        "max_output_tokens": 1000}}
    result = audit_corpus([row, row])
    assert result["saved_requests"] == 2 and result["canonical_json_encodings"] == 1
    assert result["canonical_json_duplicate_rows"] == 1
    assert result["inference_performed_by_this_audit"] is False
    assert result["supplied_evidence"]["guidance_with_memory"] == 2
    turn = {"display_order": 1, "speaker_role": "selected_contact"}
    events = [{"event": "_conversation_turn_from_audio.result", "result": turn},
              {"event": "offer.start", "args": [{"turns": [turn], "memories": ["m1"]}]}]
    assert audit_transcript(events)["offers_with_supplied_memory"] == 1
    with pytest.raises(ValueError, match="Duplicate"):
        audit_transcript([events[0], events[0]])
    with pytest.raises(ValueError, match="missing"):
        audit_transcript([events[1]])
    with pytest.raises(ValueError, match="future"):
        audit_transcript(list(reversed(events)))
    target = tmp_path / "immutable.json"
    save_new(target, result)
    with pytest.raises(FileExistsError):
        save_new(target, {})


def test_paths_source_and_missing_evidence(tmp_path, monkeypatch):
    import json
    from types import SimpleNamespace
    from tools.evaluation import memory_evaluation as runner
    monkeypatch.setattr(runner, "ROOT", tmp_path)
    monkeypatch.setattr(runner.subprocess, "run", lambda *a, **k: SimpleNamespace(returncode=0))
    run = tmp_path / "build" / "run"
    with pytest.raises(ValueError, match="beneath"):
        runner.ignored_run(tmp_path / "outside")
    with pytest.raises(ValueError, match="beneath"):
        runner.ignored_run(tmp_path / "build" / ".." / "escape")
    assert runner.ignored_run(run) == run
    monkeypatch.setattr(runner.subprocess, "run", lambda *a, **k: SimpleNamespace(returncode=1))
    with pytest.raises(ValueError, match="not Git-ignored"):
        runner.ignored_run(run)
    monkeypatch.setattr(runner.subprocess, "run", lambda *a, **k: SimpleNamespace(returncode=0))
    with pytest.raises(FileNotFoundError, match="Required historical"):
        runner.preserve_history(run)
    (run / "source").mkdir(parents=True)
    source = run / "source" / "sample.py"
    source.write_text("original")
    (run / "source-manifest.json").write_text(json.dumps({"commit": "test", "files": {"sample.py": runner.digest(source)}}))
    assert runner.verify_source(run)["verified_files"] == 1
    extra = run / "source" / "extra.txt"
    extra.write_text("unexpected")
    with pytest.raises(ValueError, match="Unmanifested"):
        runner.verify_source(run)
    source.write_text("changed")
    with pytest.raises(ValueError, match="corrupted"):
        runner.verify_source(run)


def test_payload_absence_and_exact_encoding_are_explicit():
    import json
    from tools.evaluation.memory_evaluation import audit_corpus
    base = {"schema": "GuidanceOutput", "request": {"input": {"m": []}}}
    encoded = {"schema": "GuidanceOutput", "request": {"input": json.dumps({"m": []})}}
    missing = {"schema": "GuidanceOutput", "request": {"input": {}}}
    result = audit_corpus([base, encoded, missing])
    assert result["canonical_json_encodings"] == 3
    assert result["supplied_evidence"]["guidance_empty_memory"] == 2
    assert result["supplied_evidence"]["guidance_memory_field_absent"] == 1
    assert result["supplied_evidence"]["ask_with_evidence"] == 0
    assert result["observed_payload_keys"] == {"GuidanceOutput": ["m"]}
    with pytest.raises(ValueError, match="payload shape"):
        audit_corpus([{"schema": "GuidanceOutput", "request": {"input": []}}])
    assert audit_corpus([{"schema": "SummaryOutput", "request": {"input": []}}])["schemas"] == {"SummaryOutput": 1}


def test_actual_repository_ignore_rule():
    from tools.evaluation.memory_evaluation import ROOT, ignored_run
    assert ignored_run(ROOT / "build" / "memory-evaluation-ignore-check")
    with pytest.raises(ValueError, match="beneath"):
        ignored_run(ROOT / "docs" / "private-transcript.json")


def test_reaudit_checks_copies_and_preserves_prior_output(tmp_path, monkeypatch):
    import json
    from types import SimpleNamespace
    from tools.evaluation import memory_evaluation as runner
    monkeypatch.setattr(runner, "ROOT", tmp_path)
    monkeypatch.setattr(runner, "HISTORY", ("old/corpus.json",))
    monkeypatch.setattr(runner.subprocess, "run", lambda *a, **k: SimpleNamespace(returncode=0))
    run = tmp_path / "build" / "run"
    copy = run / "historical-evidence" / "old" / "corpus.json"
    copy.parent.mkdir(parents=True)
    for directory in (run, run / "historical-evidence"):
        (directory / "PRIVATE-DO-NOT-PUBLISH.txt").write_text("Private")
    copy.write_text("[]")
    (run / "historical-manifest.json").write_text(json.dumps([
        {"path": "old/corpus.json", "sha256": runner.digest(copy)}]))
    assert runner.audit_history(run, "historical-audit-check.json")["old/corpus.json"]["saved_requests"] == 0
    with pytest.raises(FileExistsError):
        runner.audit_history(run, "historical-audit-check.json")
    with pytest.raises(ValueError, match="filename"):
        runner.audit_history(run, "../escape.json")
    copy.write_text("changed")
    with pytest.raises(ValueError, match="copy changed"):
        runner.audit_history(run, "historical-audit-next.json")


def test_preservation_copies_journals_and_refuses_existing_destination(tmp_path, monkeypatch):
    import json
    from types import SimpleNamespace
    from tools.evaluation import memory_evaluation as runner
    monkeypatch.setattr(runner, "ROOT", tmp_path)
    monkeypatch.setattr(runner, "HISTORY", ("old/corpus.json",))
    monkeypatch.setattr(runner.subprocess, "run", lambda *a, **k: SimpleNamespace(returncode=0))
    original = tmp_path / "old" / "corpus.json"
    original.parent.mkdir()
    original.write_text("[]")
    run = tmp_path / "build" / "run"
    run.mkdir(parents=True)
    assert runner.preserve_history(run)["old/corpus.json"]["saved_requests"] == 0
    copied = run / "historical-evidence" / "old" / "corpus.json"
    assert copied.read_bytes() == original.read_bytes()
    assert (run / "PRIVATE-DO-NOT-PUBLISH.txt").is_file()
    journal = json.loads((run / "historical-evidence" / "copy-journal.jsonl").read_text())
    manifest = json.loads((run / "historical-manifest.json").read_text())
    assert journal["sha256"] == manifest[0]["sha256"] == runner.digest(original)
    with pytest.raises(FileExistsError):
        runner.preserve_history(run)
    # An interrupted/changed-source copy retains its intended hash and fails closed.
    next_run = tmp_path / "build" / "next"
    next_run.mkdir()
    copyfile = runner.shutil.copyfile
    def changing_copy(source, destination):
        assert (next_run / "historical-evidence" / "copy-journal.jsonl").is_file()
        copyfile(source, destination)
        original.write_text("changed")
    monkeypatch.setattr(runner.shutil, "copyfile", changing_copy)
    with pytest.raises(RuntimeError, match="Source changed"):
        runner.preserve_history(next_run)
