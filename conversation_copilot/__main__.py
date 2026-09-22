import argparse
import json
import sys
from pathlib import Path

from pydantic import ValidationError

from .parser import parse_whatsapp_transcript
from .models import conversation_turn_from_audio as _conversation_turn_from_audio
from .models import vocal_observation_from_audio as _vocal_observation_from_audio

FIXTURE_PATH = Path(__file__).with_name("demo") / "lecturer_demo_chat.txt"


def foundation_summary() -> str:
    text = FIXTURE_PATH.read_text(encoding="utf-8-sig")
    turns = parse_whatsapp_transcript(text, source="demo")
    speaker_count = len({turn.speaker_name for turn in turns})
    if len(turns) != 500 or speaker_count != 2:
        raise ValueError(
            f"expected 500 Conversation Turns from 2 speakers, got {len(turns)} from {speaker_count}"
        )
    return f"Foundation ready\n{len(turns)} Conversation Turns\n{speaker_count} speakers"




def _relabel_contact_turns(turns, speaker_name: str) -> None:
    from .models import SpeakerRole

    for turn in turns:
        if turn.speaker_role == SpeakerRole.SELECTED_CONTACT:
            turn.speaker_name = speaker_name




def _needs_audio_selection(
    catalog, microphone_index: int, playback_index: int
) -> bool:
    return bool(
        catalog
        and catalog.microphones
        and catalog.playbacks
        and (microphone_index < 0 or playback_index < 0)
    )


def _keep_audio_after_video_end(audio_session) -> bool:
    return bool(audio_session and audio_session.snapshot().running)


def show_window(summary: str) -> None:
    from .desktop import run

    run()


def main(argv: list[str] | None = None) -> int:
    arg_parser = argparse.ArgumentParser(prog="python -m conversation_copilot")
    actions = arg_parser.add_mutually_exclusive_group()
    actions.add_argument("--check", action="store_true", help="validate the F01 fixture")
    actions.add_argument("--check-video", action="store_true", help="validate local face processing")
    actions.add_argument(
        "--check-video-capture",
        action="store_true",
        help="validate WGC using a local mock call",
    )
    actions.add_argument(
        "--benchmark-video",
        action="store_true",
        help="benchmark local face processing",
    )
    actions.add_argument(
        "--install-transcription-model",
        action="store_true",
        help="install the approved local transcription model",
    )
    actions.add_argument(
        "--install-memory-model",
        action="store_true",
        help="install the approved local indirect-memory retrieval model",
    )
    actions.add_argument(
        "--check-audio",
        action="store_true",
        help="replay the approved local audio corpus offline",
    )
    actions.add_argument(
        "--benchmark-audio",
        action="store_true",
        help="benchmark two-source transcription with the F02 loop",
    )
    actions.add_argument(
        "--evaluate-f04",
        action="store_true",
        help="run the capped paid F04 model comparison",
    )
    actions.add_argument(
        "--evaluate-f05-local",
        action="store_true",
        help="run the F05 fixed retrieval and 100k-revision local gates",
    )
    actions.add_argument(
        "--evaluate-f05-real",
        action="store_true",
        help="run the capped fictional-data F05 extraction profile comparison",
    )
    arg_parser.add_argument("--seconds", type=float, default=600)
    args = arg_parser.parse_args(argv)

    try:
        summary = foundation_summary()
    except ValidationError:
        print(
            "Foundation check failed: fixture produced an invalid Conversation Turn",
            file=sys.stderr,
        )
        return 1
    except (OSError, ValueError) as exc:
        print(f"Foundation check failed: {exc}", file=sys.stderr)
        return 1

    if args.check:
        print(summary)
    elif args.check_video:
        try:
            from .video import run_video_check

            print(run_video_check())
        except Exception as exc:
            print(f"Video check failed ({type(exc).__name__}): {exc}", file=sys.stderr)
            return 1
    elif args.check_video_capture:
        try:
            from .mock_call import run_video_capture_check

            print(run_video_capture_check())
        except Exception as exc:
            print(
                f"Video capture check failed ({type(exc).__name__}): {exc}",
                file=sys.stderr,
            )
            return 1
    elif args.benchmark_video:
        try:
            from .benchmark import run_benchmark

            print(run_benchmark(args.seconds))
        except Exception as exc:
            print(f"Video benchmark failed ({type(exc).__name__}): {exc}", file=sys.stderr)
            return 1
    elif args.install_transcription_model:
        try:
            from .audio import install_local_model

            install_local_model()
            print("Local transcription model installed")
        except Exception as exc:
            print(f"Model installation failed ({type(exc).__name__}): {exc}", file=sys.stderr)
            return 1
    elif args.install_memory_model:
        try:
            from .memory import MemoryStore
            from .semantic import install_model

            with MemoryStore() as store:
                details = install_model(store.semantic_cache_dir)
                details["embedded_memories"] = store.backfill_semantic_embeddings()
            print(json.dumps(details, sort_keys=True))
        except Exception as exc:
            print(f"Memory model installation failed ({type(exc).__name__}): {exc}", file=sys.stderr)
            return 1
    elif args.check_audio:
        try:
            from .audio import run_audio_replay

            print(run_audio_replay())
        except Exception as exc:
            print(f"Audio replay failed ({type(exc).__name__}): {exc}", file=sys.stderr)
            return 1
    elif args.benchmark_audio:
        try:
            from .audio import run_audio_benchmark

            print(run_audio_benchmark(args.seconds))
        except Exception as exc:
            print(f"Audio benchmark failed ({type(exc).__name__}): {exc}", file=sys.stderr)
            return 1
    elif args.evaluate_f04:
        try:
            from .f04_evaluation import run_real_evaluation

            print(run_real_evaluation())
        except Exception as exc:
            print(
                f"F04 evaluation stopped safely ({type(exc).__name__})",
                file=sys.stderr,
            )
            return 1
    elif args.evaluate_f05_local:
        try:
            from .f05_evaluation import run_local_evaluation

            print(run_local_evaluation())
        except Exception as exc:
            print(f"F05 local evaluation failed ({type(exc).__name__}): {exc}", file=sys.stderr)
            return 1
    elif args.evaluate_f05_real:
        try:
            from .f05_evaluation import run_real_extraction_evaluation

            print(run_real_extraction_evaluation())
        except Exception as exc:
            print(f"F05 real evaluation stopped safely ({type(exc).__name__})", file=sys.stderr)
            return 1
    else:
        show_window(summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
