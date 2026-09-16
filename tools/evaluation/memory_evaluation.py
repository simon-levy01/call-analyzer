"""Local-memory S0 evidence preparation. No provider calls or inference on import.

Run against a fresh ignored directory. Historical outputs are development evidence,
never new independent responses or held-out accuracy measurements.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import shutil
import subprocess


ROOT = Path(__file__).resolve().parents[2]
HISTORY = (
    "build/local-model-comparison-20260913/corpus.json",
    "build/local-model-comparison-20260913/recorded-call-manual-expectations.json",
    "build/live-test-20260913-121412/events.jsonl",
    "build/live-test-20260912-201026/events.jsonl",
    "build/f07-implementation-20260914/api-comparison-before-p1-v2/jobs.json",
    "build/f07-implementation-20260914/api-comparison-before-p1-v2/report.json",
    "conversation_copilot/assets/f06/questions.json",
    "conversation_copilot/assets/f06/history.json",
)


def digest(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def save_new(path, data):
    with Path(path).open("x", encoding="utf-8") as stream:
        json.dump(data, stream, ensure_ascii=False, indent=2)


def ignored_run(path):
    path = Path(path).resolve()
    if not path.is_relative_to((ROOT / "build").resolve()):
        raise ValueError("Evidence must stay beneath this checkout's ignored build directory")
    check = subprocess.run(["git", "check-ignore", "--", str(path)], cwd=ROOT, capture_output=True)
    if check.returncode:
        raise ValueError("Evidence directory is not Git-ignored")
    return path


def request_fingerprint(request, schema):
    # Exact recorded representation; no inference about omitted settings.
    wire = json.dumps([schema, request], sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(wire.encode()).hexdigest()


def audit_corpus(rows):
    fingerprints = [request_fingerprint(row["request"], row["schema"]) for row in rows]
    supplied = Counter({name: 0 for name in (
        "guidance_memory_field_absent", "guidance_with_memory", "guidance_empty_memory",
        "ask_evidence_field_absent", "ask_with_evidence", "ask_empty_evidence")})
    keys = {}
    for row in rows:
        if row["schema"] not in {"GuidanceOutput", "CloudAskOutput"}:
            continue  # Extraction/summary inputs have different historical schemas.
        payload = row["request"]["input"]
        payload = json.loads(payload) if isinstance(payload, str) else payload
        if not isinstance(payload, dict):
            raise ValueError("Unsupported historical payload shape: expected a JSON object")
        keys.setdefault(row["schema"], set()).update(payload)
        if row["schema"] == "GuidanceOutput":
            supplied["guidance_memory_field_absent" if "m" not in payload else
                     "guidance_with_memory" if payload["m"] else "guidance_empty_memory"] += 1
        elif row["schema"] == "CloudAskOutput":
            supplied["ask_evidence_field_absent" if "evidence" not in payload else
                     "ask_with_evidence" if payload["evidence"] else "ask_empty_evidence"] += 1
    return {
        "saved_requests": len(rows), "canonical_json_encodings": len(set(fingerprints)),
        "canonical_json_duplicate_rows": len(rows) - len(set(fingerprints)),
        "schemas": dict(Counter(row["schema"] for row in rows)),
        "supplied_evidence": dict(supplied), "inference_performed_by_this_audit": False,
        "observed_payload_keys": {schema: sorted(names) for schema, names in keys.items()},
        "limitation": "Presence does not establish relevance; supplied-evidence omissions must not be labeled retrieval failures.",
    }


def audit_transcript(events):
    turns = [row["result"] for row in events if row.get("event") == "_conversation_turn_from_audio.result"]
    offers = [row["args"][0] for row in events if row.get("event") == "offer.start"]
    orders = [turn["display_order"] for turn in turns]
    if len(orders) != len(set(orders)):
        raise ValueError("Duplicate finalized turn order requires investigation")
    available, all_orders = set(), set(orders)
    for event in events:
        if event.get("event") == "_conversation_turn_from_audio.result":
            available.add(event["result"]["display_order"])
        elif event.get("event") == "offer.start":
            referenced = {turn["display_order"] for turn in event["args"][0]["turns"]}
            if not referenced <= all_orders:
                raise ValueError("Snapshot refers to missing finalized turns")
            if not referenced <= available:
                raise ValueError("Snapshot refers to future finalized turns")
    return {"finalized_turns": len(turns), "saved_offers": len(offers),
            "offers_with_supplied_memory": sum(bool(offer.get("memories")) for offer in offers),
            "offers_memory_field_absent": sum("memories" not in offer for offer in offers),
            "offers_empty_memory": sum("memories" in offer and not offer["memories"] for offer in offers),
            "observed_offer_keys": sorted({key for offer in offers for key in offer}),
            "speaker_roles": dict(Counter(turn["speaker_role"] for turn in turns)),
            "inference_performed_by_this_audit": False,
            "limitation": "Saved offers preserve only supplied candidates, not the entire eligible database. No retrieval-recall claim."}


def preserve_history(run):
    run = ignored_run(run)
    missing = [name for name in HISTORY if not (ROOT / name).is_file()]
    if missing:
        raise FileNotFoundError(f"Required historical evidence missing: {missing}")
    destination = run / "historical-evidence"
    destination.mkdir(exist_ok=False)
    for directory in (run, destination):
        marker = directory / "PRIVATE-DO-NOT-PUBLISH.txt"
        if not marker.exists():
            with marker.open("x", encoding="utf-8") as stream:
                stream.write("Private source, transcripts and results. No files here are publishable.\n")
    entries, audits = [], {}
    for name in HISTORY:
        source = ROOT / name
        copied = ignored_run(destination / name)
        copied.parent.mkdir(parents=True, exist_ok=True)
        before = digest(source)
        # Append before copying so interrupted copies retain the intended provenance.
        with (destination / "copy-journal.jsonl").open("a", encoding="utf-8") as journal:
            journal.write(json.dumps({"path": name, "sha256": before}) + "\n")
            journal.flush()
        shutil.copyfile(source, copied)
        if digest(source) != before or digest(copied) != before:
            raise RuntimeError(f"Source changed during preservation: {name}")
        entries.append({"path": name, "sha256": before, "bytes": copied.stat().st_size})
    save_new(run / "historical-manifest.json", entries)
    # All copied-file hashes survive a later malformed-input/audit failure.
    for name in HISTORY:
        copied = destination / name
        if name.endswith("/corpus.json"):
            audits[name] = audit_corpus(json.loads(copied.read_text(encoding="utf-8")))
        elif name.endswith("/events.jsonl"):
            audits[name] = audit_transcript([json.loads(line) for line in copied.read_text(encoding="utf-8").splitlines()])
    save_new(run / "historical-audit.json", audits)
    return audits


def audit_history(run, output_name):
    """Re-audit immutable copies with current code; never replace a previous audit."""
    if Path(output_name).name != output_name or not output_name.startswith("historical-audit-") or not output_name.endswith(".json"):
        raise ValueError("Choose a new historical-audit-NAME.json filename")
    run = ignored_run(run)
    if not all((directory / "PRIVATE-DO-NOT-PUBLISH.txt").is_file()
               for directory in (run, run / "historical-evidence")):
        raise ValueError("Private evidence marker missing")
    entries = json.loads((run / "historical-manifest.json").read_text(encoding="utf-8"))
    if len(entries) != len(HISTORY) or {row["path"] for row in entries} != set(HISTORY):
        raise ValueError("Historical manifest does not cover the required evidence exactly")
    actual = {path.relative_to(run / "historical-evidence").as_posix()
              for path in (run / "historical-evidence").rglob("*") if path.is_file()}
    if actual - set(HISTORY) - {"PRIVATE-DO-NOT-PUBLISH.txt", "copy-journal.jsonl"}:
        raise ValueError("Unmanifested historical files")
    audits = {}
    for row in entries:
        source = ignored_run(run / "historical-evidence" / row["path"])
        if digest(source) != row["sha256"]:
            raise ValueError("Historical copy changed")
        if row["path"].endswith("/corpus.json"):
            audits[row["path"]] = audit_corpus(json.loads(source.read_text(encoding="utf-8")))
        elif row["path"].endswith("/events.jsonl"):
            audits[row["path"]] = audit_transcript([json.loads(line) for line in source.read_text(encoding="utf-8").splitlines()])
    save_new(run / output_name, audits)
    return audits


def verify_source(run):
    run = ignored_run(run)
    manifest = json.loads((run / "source-manifest.json").read_text(encoding="utf-8"))
    changed = [name for name, expected in manifest["files"].items()
               if not (run / "source" / name).is_file() or digest(run / "source" / name) != expected]
    if changed:
        raise ValueError(f"Frozen source corrupted: {changed}")
    actual = {path.relative_to(run / "source").as_posix() for path in (run / "source").rglob("*")
              if path.is_file() and "__pycache__" not in path.parts}
    extra = actual - set(manifest["files"])
    if extra:
        raise ValueError(f"Unmanifested source files: {sorted(extra)}")
    return {"commit": manifest["commit"], "verified_files": len(manifest["files"])}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", type=Path)
    parser.add_argument("--preserve-history", action="store_true")
    parser.add_argument("--audit-history", metavar="NEW_AUDIT_FILENAME")
    args = parser.parse_args()
    run = ignored_run(args.run)
    print(json.dumps(verify_source(run)))
    if args.preserve_history:
        print(json.dumps(preserve_history(run), indent=2))
    if args.audit_history:
        print(json.dumps(audit_history(run, args.audit_history), indent=2))
