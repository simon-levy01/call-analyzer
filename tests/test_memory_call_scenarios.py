import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np

from conversation_copilot.interpretation import (
    Evidence,
    FakeInterpreter,
    InterpretationUpdate,
    RetrievedMemoryContext,
    SocialCue,
    StableInterpretationCard,
    ToneHypothesis,
    build_snapshot,
    format_interpretation_body,
    prepare_interpretation_request,
)
from conversation_copilot.memory import (
    ExtractionOutput,
    FakeMemoryExtractor,
    MemoryProposalInput,
    MemoryStore,
    analyze_record,
    memory_retrieval_inputs as _memory_retrieval_inputs,
    memory_semantic_input as _memory_semantic_input,
)
from conversation_copilot.models import ConversationTurn, SpeakerRole
import conversation_copilot.semantic as semantic_module


FIXTURE = (
    Path(__file__).parents[1]
    / "conversation_copilot"
    / "assets"
    / "f05"
    / "mock-memory-calls.json"
)
VIDEO_FIXTURE = Path(__file__).parents[1] / "conversation_copilot" / "assets" / "f04" / "basic-video-chat.json"


def test_progressive_indirect_employment_reference_reaches_f04_before_explicit_naming(
    tmp_path, monkeypatch
):
    def fake_vectors(texts, _cache_dir):
        vectors = np.zeros((len(texts), 384), dtype=np.float32)
        for index, text in enumerate(texts):
            lowered = text.casefold()
            axis = 0 if any(
                phrase in lowered
                for phrase in ("lost their job", "let you go", "make money", "newspaper", "rent is due")
            ) else 1
            vectors[index, axis] = 1
        return vectors

    monkeypatch.setattr(semantic_module, "embed_texts_if_ready", fake_vectors)
    raw = [
        ("user", "Has it only been a few days?"),
        ("selected_contact", "Yes. I was there for years."),
        ("selected_contact", "Now..."),
        ("user", "And then they let you go?"),
        ("selected_contact", "Yes. Now I need to work out how to make money."),
        ("user", "Do you think you will look for something new?"),
        ("selected_contact", "I do not know where to go."),
        ("user", "That sounds difficult."),
        ("selected_contact", "Maybe I should search online or in the newspaper."),
        ("selected_contact", "I need to find a new one."),
        ("selected_contact", "It is hard when rent is due."),
    ]
    turns = _turns(raw)
    with MemoryStore(tmp_path / "indirect-employment.sqlite3") as store:
        selected = store.create_contact("Test Contact")
        other = store.create_contact("Other Contact")
        employment = store.create_memory(
            selected.id,
            "Test Contact lost their job on August 25, 2026",
            memory_type="event_date",
        )
        store.create_memory(selected.id, "Test Contact is learning sign language", memory_type="recurring_topic")
        store.create_memory(other.id, "Other Contact lost their job", memory_type="event_date")
        store.backfill_semantic_embeddings()

        for count in (1, 2, 3):
            visible = turns[:count]
            query, date_query = _memory_retrieval_inputs(visible)
            assert store.retrieve(
                selected.id,
                query,
                for_cloud=True,
                date_query=date_query,
                semantic_query=_memory_semantic_input(visible),
            ).matches == ()

        for count in (4, 9, 11):
            visible = turns[:count]
            query, date_query = _memory_retrieval_inputs(visible)
            result = store.retrieve(
                selected.id,
                query,
                for_cloud=True,
                date_query=date_query,
                semantic_query=_memory_semantic_input(visible),
            )
            assert employment in {item.memory_id for item in result.matches}
            context = next(item for item in result.matches if item.memory_id == employment)
            request = prepare_interpretation_request(
                build_snapshot(
                    visible,
                    snapshot_id=count,
                    generation=1,
                    contact_id=selected.id,
                    retrieved_memories=[RetrievedMemoryContext(
                        memory_id=context.memory_id,
                        revision_id=context.revision_id,
                        excerpt=context.content,
                        memory_type=context.memory_type,
                        confidence=context.confidence,
                        sensitivity_safe=context.cloud_eligible,
                        rank=context.rank,
                        relevance=context.reason,
                    )],
                )
            )
            assert context.revision_id in request.input_text
            assert "lost their job" in request.input_text

        changed_topic = _turns([
            *raw,
            ("user", "Besides that, what did you do today?"),
            ("selected_contact", "I had practice and learned sign language."),
        ])
        query, date_query = _memory_retrieval_inputs(changed_topic)
        result = store.retrieve(
            selected.id,
            query,
            for_cloud=True,
            date_query=date_query,
            semantic_query=_memory_semantic_input(changed_topic),
        )
        assert employment not in {item.memory_id for item in result.matches}

        assert store.retrieve(
            other.id,
            "They let you go and now rent is due",
            semantic_query="They let you go and now rent is due",
        ).matches[0].contact_id == other.id


def test_progressive_grief_phrases_retrieve_tragedy_memory_cautiously(
    tmp_path, monkeypatch
):
    def fake_vectors(texts, _cache_dir):
        vectors = np.zeros((len(texts), 384), dtype=np.float32)
        for index, text in enumerate(texts):
            lowered = text.casefold()
            grief = any(
                phrase in lowered
                for phrase in (
                    "pepper died", "the tragedy", "recent sad event",
                    "meant a lot", "meant everything", "miss her", "miss him",
                    "miss them", "thinking about her",
                )
            )
            vectors[index, 0 if grief else 1] = 1
        return vectors

    monkeypatch.setattr(semantic_module, "embed_texts_if_ready", fake_vectors)
    scenarios = (
        [
            ("user", "How have the last few days been?"),
            ("selected_contact", "Harder than usual."),
            ("user", "Do you feel up to talking?"),
            ("selected_contact", "Maybe."),
            ("user", "Could this be about the tragedy?"),
            ("selected_contact", "She meant a lot to me and I miss her."),
        ],
        [
            ("user", "How are things?"),
            ("selected_contact", "Not great."),
            ("user", "What has been on your mind?"),
            ("selected_contact", "A lot."),
            ("user", "Is this about the recent sad event?"),
            ("selected_contact", "He meant a lot to me. I miss him all the time."),
        ],
        [
            ("user", "How have you been?"),
            ("selected_contact", "I have been quieter."),
            ("user", "Do you want to talk?"),
            ("selected_contact", "A little."),
            ("user", "Is this connected to the event?"),
            ("selected_contact", "They meant everything to me, and I miss them."),
        ],
        [
            ("user", "How are you?"),
            ("selected_contact", "I keep thinking about her."),
            ("user", "Do you want to tell me more?"),
            ("selected_contact", "She meant so much to me, and I miss her every day."),
        ],
    )
    with MemoryStore(tmp_path / "progressive-grief.sqlite3") as store:
        selected = store.create_contact("Maya")
        other = store.create_contact("Other Maya")
        pepper = store.create_memory(
            selected.id,
            "Maya's dog Pepper died on August 18, 2026",
            memory_type="event_date",
        )
        store.create_memory(selected.id, "Maya is learning pottery", memory_type="recurring_topic")
        store.create_memory(
            other.id,
            "Other Maya's dog Pepper died on August 20, 2026",
            memory_type="event_date",
        )
        store.backfill_semantic_embeddings()

        for raw in scenarios:
            turns = _turns(raw)
            cue_at = 4 if len(raw) == 4 else 5
            query, date_query = _memory_retrieval_inputs(turns[: cue_at - 1])
            before = store.retrieve(
                selected.id,
                query,
                for_cloud=True,
                date_query=date_query,
                semantic_query=_memory_semantic_input(turns[: cue_at - 1]),
            )
            assert pepper not in {item.memory_id for item in before.matches}

            query, date_query = _memory_retrieval_inputs(turns)
            result = store.retrieve(
                selected.id,
                query,
                for_cloud=True,
                date_query=date_query,
                semantic_query=_memory_semantic_input(turns),
            )
            assert not result.ambiguous
            assert result.matches[0].memory_id == pepper
            context = result.matches[0]
            snapshot = build_snapshot(
                turns,
                snapshot_id=1,
                generation=1,
                contact_id=selected.id,
                retrieved_memories=[RetrievedMemoryContext(
                    memory_id=context.memory_id,
                    revision_id=context.revision_id,
                    excerpt=context.content,
                    memory_type=context.memory_type,
                    confidence=context.confidence,
                    sensitivity_safe=context.cloud_eligible,
                    rank=context.rank,
                    relevance=context.reason,
                )],
            )
            assert "Pepper died" in prepare_interpretation_request(snapshot).input_text

            wrong = store.retrieve(
                other.id,
                query,
                for_cloud=True,
                date_query=date_query,
                semantic_query=_memory_semantic_input(turns),
            )
            assert pepper not in {item.memory_id for item in wrong.matches}


def _turns(raw_turns):
    started = datetime(2026, 8, 29, 12, tzinfo=timezone.utc)
    return [
        ConversationTurn(
            speaker_name="You" if role == "user" else "Maya",
            speaker_role=SpeakerRole(role),
            source="f05_mock_call",
            content=content,
            timestamp=started + timedelta(seconds=index * 5),
            display_order=index,
        )
        for index, (role, content) in enumerate(raw_turns, 1)
    ]


def _authored_update(*, tone=None, cue=None, memory_used=False):
    if tone is None and cue is None:
        return InterpretationUpdate(
            status="insufficient_evidence",
            explanation="The recent words do not support a conclusion",
        )
    evidence = Evidence(
        explanation="Independent authored replay response",
        modalities=["language", "memory"] if memory_used else ["language"],
    )
    return InterpretationUpdate(
        status="updated",
        tones=[ToneHypothesis(
            kind=tone, confidence="medium",
            hypothesis="The recent conversation may have this atmosphere", evidence=evidence,
        )] if tone else [],
        social_cues=[SocialCue(
            kind=cue, confidence="medium",
            hypothesis="The remote participant may show this cue", evidence=evidence,
        )] if cue else [],
    )


def test_fictional_mock_calls_cover_retrieval_request_and_visible_context(tmp_path):
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    assert fixture["fixture_id"] == "f05-mock-memory-calls-v1"
    assert fixture["fictional_data_only"] is True
    assert len(fixture["scenarios"]) == 8

    for scenario in fixture["scenarios"]:
        with MemoryStore(tmp_path / f"{scenario['id']}.sqlite3") as store:
            selected_id = None
            for contact_data in scenario["contacts"]:
                contact = store.create_contact(contact_data["name"])
                if contact_data.get("selected"):
                    selected_id = contact.id
                for memory_data in contact_data["memories"]:
                    memory_id = store.create_memory(
                        contact.id,
                        memory_data["content"],
                        memory_type=memory_data["type"],
                        confidence=memory_data["confidence"],
                        sensitivity=memory_data["sensitivity"],
                        normalized_date_start=datetime.fromisoformat(
                            memory_data["date"]
                        ).replace(tzinfo=timezone.utc),
                    )
                    if memory_data.get("cloud_allowed"):
                        store.set_cloud_permission(memory_id, True)

            turns = _turns(scenario["turns"])
            query, date_query = _memory_retrieval_inputs(turns)
            result = store.retrieve(
                selected_id, query, for_cloud=True, date_query=date_query
            )
            possibilities = [
                RetrievedMemoryContext(
                    memory_id=item.memory_id,
                    revision_id=item.revision_id,
                    excerpt=item.content,
                    memory_type=item.memory_type,
                    confidence=item.confidence,
                    sensitivity_safe=item.cloud_eligible,
                    rank=item.rank,
                    relevance=item.reason,
                )
                for item in result.matches[:3]
            ]
            cloud_context = [] if result.ambiguous else possibilities
            snapshot = build_snapshot(
                turns,
                snapshot_id=1,
                generation=1,
                contact_id=selected_id,
                retrieved_memories=cloud_context,
            )
            request = json.loads(prepare_interpretation_request(snapshot).input_text)
            update = InterpretationUpdate(
                status="updated",
                tones=[
                    ToneHypothesis(
                        kind="sad_low_energy",
                        confidence="medium",
                        hypothesis="The conversation may have a sad or reflective tone",
                        evidence=Evidence(
                            explanation="Current wording is subdued, and approved context may identify the indirect event",
                            modalities=["language", "memory"],
                        ),
                    )
                ],
            ) if scenario["id"] == "pepper-indirect-event-tone" else InterpretationUpdate(
                status="insufficient_evidence",
                explanation="The recent words do not support a confident interpretation",
            )
            display = format_interpretation_body(
                update, "Waiting for interpretation", possibilities
            )
            expected = scenario["expected"]

            assert result.ambiguous is expected["ambiguous"], scenario["id"]
            assert len(request.get("m", [])) == expected["request_memory_rows"], scenario["id"]
            for text in expected.get("display_contains", []):
                assert text in display, scenario["id"]
            for text in expected.get("display_excludes", []):
                assert text not in display, scenario["id"]


def test_progressive_video_transcript_replay_returns_expected_memory_and_tone_updates(tmp_path):
    fixture = json.loads(VIDEO_FIXTURE.read_text(encoding="utf-8"))
    started = datetime(2026, 8, 25, 12, tzinfo=timezone.utc)
    all_turns = [
        ConversationTurn(
            speaker_name="Alex" if item["speaker"] == "alex" else "Maya",
            speaker_role=SpeakerRole.USER if item["speaker"] == "alex" else SpeakerRole.SELECTED_CONTACT,
            source="f04_progressive_video_replay",
            content=item["text"],
            timestamp=started + timedelta(seconds=item["end_seconds"]),
            display_order=index,
        )
        for index, item in enumerate(fixture["turns"], 1)
    ]
    first_update_at = fixture["turns"][1]["end_seconds"]
    expected_turns = [
        max(index for index, turn in enumerate(fixture["turns"], 1) if turn["end_seconds"] <= first_update_at + 17 * offset)
        for offset in range(len(fixture["progressive_checkpoints"]))
    ]
    assert expected_turns == [item["through_turn"] for item in fixture["progressive_checkpoints"]]

    with MemoryStore(tmp_path / "progressive-video-replay.sqlite3") as store:
        maya = store.create_contact("Maya")
        for seed in fixture["seed_memories"]:
            memory_id = store.create_memory(
                maya.id,
                seed["content"],
                memory_type=seed["type"],
                sensitivity="sensitive" if seed["sensitive"] else "normal",
                normalized_date_start=datetime.fromisoformat(seed["date"]).replace(tzinfo=timezone.utc),
            )
            if seed["sensitive"]:
                store.set_cloud_permission(memory_id, True)

        card = StableInterpretationCard()
        interpreter = FakeInterpreter([
            _authored_update(tone="sad_low_energy", memory_used=True),
            _authored_update(cue="uncertainty"),
            _authored_update(tone="positive_warm", cue="humor"),
            _authored_update(cue="sarcasm"),
            _authored_update(tone="tense_negative", cue="uncertainty"),
            _authored_update(tone="positive_warm"),
        ])
        displays = []
        for snapshot_id, expected in enumerate(fixture["progressive_checkpoints"], 1):
            visible_turns = all_turns[:expected["through_turn"]]
            query, date_query = _memory_retrieval_inputs(visible_turns)
            result = store.retrieve(maya.id, query, for_cloud=True, date_query=date_query)
            assert not result.ambiguous
            possibilities = [
                RetrievedMemoryContext(
                    memory_id=item.memory_id,
                    revision_id=item.revision_id,
                    excerpt=item.content,
                    memory_type=item.memory_type,
                    confidence=item.confidence,
                    sensitivity_safe=item.cloud_eligible,
                    rank=item.rank,
                    relevance=item.reason,
                )
                for item in result.matches
            ]
            snapshot = build_snapshot(
                visible_turns,
                snapshot_id=snapshot_id,
                generation=1,
                contact_id=maya.id,
                retrieved_memories=possibilities,
            )
            request = json.loads(prepare_interpretation_request(snapshot).input_text)
            assert len(request.get("m", [])) == len(possibilities)

            returned = interpreter(snapshot)
            assert returned.status.value == expected["status"]
            assert [item.kind.value for item in returned.tones] == (
                [expected["tone"]] if expected.get("tone") else []
            )
            assert [item.kind.value for item in returned.social_cues] == (
                [expected["social_cue"]] if expected.get("social_cue") else []
            )
            returned_modalities = {
                modality.value
                for item in [*returned.tones, *returned.social_cues]
                for modality in item.evidence.modalities
            }
            assert returned_modalities == set(expected["evidence_modalities"])
            analysis_at = first_update_at + 17 * (snapshot_id - 1)
            assert card.offer(returned, analysis_at) == "replaced"
            display = format_interpretation_body(card.update, card.message, possibilities)
            displays.append(display)
            for text in expected["memory_contains"]:
                assert text in display, (expected["through_turn"], text)
            for text in expected["memory_excludes"]:
                assert text not in display, (expected["through_turn"], text)
            if possibilities:
                assert "Evidence sources: conversation words, approved memory" in display

        assert len(displays) == len(interpreter.calls) == 6


def test_progressive_multi_call_replay_switches_direct_indirect_dates_and_contacts(tmp_path):
    started = datetime(2026, 8, 29, 12, tzinfo=timezone.utc)
    with MemoryStore(tmp_path / "progressive-multi-call.sqlite3") as store:
        yaheli = store.create_contact("Yaheli")
        noa = store.create_contact("Noa")
        store.create_memory(
            yaheli.id, "Yaheli's dog Pepper died on July 10, 2026",
            memory_type="event_date", normalized_date_start=datetime(2026, 7, 10, tzinfo=timezone.utc),
        )
        store.create_memory(
            yaheli.id, "Yaheli lost his job on August 1, 2026",
            memory_type="event_date", normalized_date_start=datetime(2026, 8, 1, tzinfo=timezone.utc),
        )
        store.create_memory(
            yaheli.id, "Yaheli moved apartment on August 25, 2026",
            memory_type="event_date", normalized_date_start=datetime(2026, 8, 25, tzinfo=timezone.utc),
        )
        store.create_memory(
            noa.id, "Noa won a ceramics prize on August 28, 2026",
            memory_type="event_date", normalized_date_start=datetime(2026, 8, 28, tzinfo=timezone.utc),
        )

        calls = [
            (
                yaheli,
                [
                    ("Want to get lunch?", "Sure, that sounds good.", None, "neutral_calm"),
                    ("How are you doing after the event?", "I am still getting used to everything.", "moved apartment", "uncertainty"),
                    ("How are you feeling about Pepper?", "I still miss her.", "Pepper died", "sad_low_energy"),
                    ("Has the job loss been difficult?", "I am working through it.", "lost his job", "tense_negative"),
                    ("How is pottery class?", "I made a blue bowl today.", None, "positive_warm"),
                ],
            ),
            (
                noa,
                [
                    ("How are you doing after the event?", "I still cannot believe I won.", "ceramics prize", "positive_warm"),
                    ("How are you feeling about Pepper?", "I do not know who that is.", None, None),
                ],
            ),
            (
                yaheli,
                [
                    ("How have things been after that?", "Some days are easier than others.", "moved apartment", "uncertainty"),
                ],
            ),
        ]

        snapshot_id = 0
        interpreter = FakeInterpreter([
            _authored_update(tone="neutral_calm"),
            _authored_update(cue="uncertainty", memory_used=True),
            _authored_update(tone="sad_low_energy", memory_used=True),
            _authored_update(tone="tense_negative", memory_used=True),
            _authored_update(tone="positive_warm"),
            _authored_update(tone="positive_warm", memory_used=True),
            _authored_update(),
            _authored_update(cue="uncertainty", memory_used=True),
        ])
        seen = []
        for call_index, (contact, stages) in enumerate(calls):
            visible_turns = []
            for stage_index, (user_text, contact_text, expected_memory, expected_kind) in enumerate(stages):
                pair_started = started + timedelta(hours=call_index, seconds=stage_index * 18)
                visible_turns.extend([
                    ConversationTurn(
                        speaker_name="You", speaker_role=SpeakerRole.USER, source="progressive_multi_call",
                        content=user_text, timestamp=pair_started, display_order=stage_index * 2 + 1,
                    ),
                    ConversationTurn(
                        speaker_name=contact.display_name, speaker_role=SpeakerRole.SELECTED_CONTACT,
                        source="progressive_multi_call", content=contact_text,
                        timestamp=pair_started + timedelta(seconds=9), display_order=stage_index * 2 + 2,
                    ),
                ])
                query, date_query = _memory_retrieval_inputs(visible_turns)
                result = store.retrieve(contact.id, query, for_cloud=True, date_query=date_query)
                contents = [item.content for item in result.matches]
                if expected_memory:
                    assert not result.ambiguous
                    assert len(contents) == 1 and expected_memory in contents[0]
                else:
                    assert contents == []
                if contact.id == noa.id:
                    assert all("Pepper" not in content and "lost his job" not in content for content in contents)

                contexts = [
                    RetrievedMemoryContext(
                        memory_id=item.memory_id, revision_id=item.revision_id, excerpt=item.content,
                        memory_type=item.memory_type, confidence=item.confidence,
                        sensitivity_safe=item.cloud_eligible, rank=item.rank, relevance=item.reason,
                    )
                    for item in result.matches
                ]
                snapshot_id += 1
                snapshot = build_snapshot(
                    visible_turns, snapshot_id=snapshot_id, generation=1,
                    contact_id=contact.id, retrieved_memories=contexts,
                )
                assert len(json.loads(prepare_interpretation_request(snapshot).input_text).get("m", [])) == len(contexts)
                returned = interpreter(snapshot)
                actual_kind = (
                    returned.tones[0].kind.value if returned.tones
                    else returned.social_cues[0].kind.value if returned.social_cues
                    else None
                )
                assert actual_kind == expected_kind
                returned_modalities = {
                    modality.value
                    for item in [*returned.tones, *returned.social_cues]
                    for modality in item.evidence.modalities
                }
                assert ("memory" in returned_modalities) is bool(contexts)
                seen.append((contact.display_name, expected_memory, returned.status.value, actual_kind))

            store.create_record(
                source_kind="call", source_label=f"progressive call {call_index + 1}",
                timezone_name="UTC", contact_id=contact.id, turns=visible_turns, status="stopped",
            )

        assert len(seen) == len(interpreter.calls) == 8


def test_old_event_words_do_not_inject_memory_into_a_new_topic(tmp_path, monkeypatch):
    old_event_then_lunch = _turns([
        ["user", "How have you been since the event?"],
        ["selected_contact", "It has been difficult."],
        ["user", "I am glad we talked about it."],
        ["selected_contact", "Me too."],
        ["user", "Anyway, want to grab lunch?"],
        ["selected_contact", "Sure, lunch sounds good."],
    ])
    monkeypatch.setattr(
        semantic_module,
        "embed_texts_if_ready",
        lambda texts, _cache: np.pad(
            np.ones((len(texts), 1), dtype=np.float32), ((0, 0), (0, 383))
        ),
    )
    with MemoryStore(tmp_path / "stale-event.sqlite3") as store:
        maya = store.create_contact("Maya")
        store.create_memory(
            maya.id, "Maya's dog Pepper died on August 18", memory_type="event_date"
        )
        store.backfill_semantic_embeddings()
        query, date_query = _memory_retrieval_inputs(old_event_then_lunch)
        assert date_query == "anyway, want to grab lunch? sure, lunch sounds good."
        semantic_query = _memory_semantic_input(old_event_then_lunch)
        assert semantic_query == ""
        assert store.retrieve(
            maya.id, query, date_query=date_query, semantic_query=semantic_query
        ).matches == ()


def test_statement_form_event_reference_with_punctuation_retrieves(tmp_path):
    turns = _turns([
        ["user", "I have been thinking about the event."],
        ["selected_contact", "It has been difficult lately."],
    ])
    with MemoryStore(tmp_path / "statement-event.sqlite3") as store:
        maya = store.create_contact("Maya")
        memory_id = store.create_memory(
            maya.id,
            "Maya's dog Pepper died on August 18",
            memory_type="event_date",
            normalized_date_start=datetime(2026, 8, 18, tzinfo=timezone.utc),
        )
        query, date_query = _memory_retrieval_inputs(turns)
        assert date_query == "i have been thinking about the event. it has been difficult lately."
        result = store.retrieve(maya.id, query, date_query=date_query)
        assert not result.ambiguous and result.matches[0].memory_id == memory_id


def test_date_question_in_previous_turn_still_retrieves_after_contact_reply(tmp_path):
    date_exchange = _turns([
        ["user", "We talked about travel."],
        ["selected_contact", "Yes, that was useful."],
        ["user", "What happened on August 18?"],
        ["selected_contact", "I still do not want to name it."],
    ])
    with MemoryStore(tmp_path / "date-exchange.sqlite3") as store:
        maya = store.create_contact("Maya")
        memory_id = store.create_memory(
            maya.id,
            "Maya's dog Pepper died on August 18",
            memory_type="event_date",
            normalized_date_start=datetime(2026, 8, 18, tzinfo=timezone.utc),
        )
        query, date_query = _memory_retrieval_inputs(date_exchange)
        result = store.retrieve(maya.id, query, date_query=date_query)
        assert result.matches[0].memory_id == memory_id


def test_multiple_calls_prefer_newest_dated_event_indirectly_but_keep_direct_recall(tmp_path):
    calls = {
        "indirect_newest": [
            ["user", "How are you doing after the event?"],
            ["selected_contact", "I am still getting used to everything."],
        ],
        "indirect_after_that": [
            ["user", "How have things been after that?"],
            ["selected_contact", "Some days are easier than others."],
        ],
        "direct_oldest": [
            ["user", "How are you feeling about Pepper?"],
            ["selected_contact", "I still miss her."],
        ],
        "direct_middle": [
            ["user", "Has the job loss been difficult?"],
            ["selected_contact", "I am working through it."],
        ],
    }
    with MemoryStore(tmp_path / "dated-multi-call.sqlite3") as store:
        maya = store.create_contact("Maya", "friend")
        other = store.create_contact("Maya", "coworker")
        oldest = store.create_memory(
            maya.id,
            "Maya's dog Pepper died on July 10, 2026",
            memory_type="event_date",
            normalized_date_start=datetime(2026, 7, 10, tzinfo=timezone.utc),
        )
        middle = store.create_memory(
            maya.id,
            "Maya lost her job on August 1, 2026",
            memory_type="event_date",
            normalized_date_start=datetime(2026, 8, 1, tzinfo=timezone.utc),
        )
        newest = store.create_memory(
            maya.id,
            "Maya moved apartment on August 25, 2026",
            memory_type="event_date",
            normalized_date_start=datetime(2026, 8, 25, tzinfo=timezone.utc),
        )
        store.create_memory(maya.id, "Maya prefers mint tea", memory_type="preference")
        store.create_memory(
            other.id,
            "Maya started a new project on August 28, 2026",
            memory_type="event_date",
            normalized_date_start=datetime(2026, 8, 28, tzinfo=timezone.utc),
        )

        expected = {
            "indirect_newest": newest,
            "indirect_after_that": newest,
            "direct_oldest": oldest,
            "direct_middle": middle,
        }
        for label, raw_turns in calls.items():
            turns = _turns(raw_turns)
            store.create_record(
                source_kind="call",
                source_label=label,
                timezone_name="UTC",
                contact_id=maya.id,
                turns=turns,
                status="stopped",
            )
            query, date_query = _memory_retrieval_inputs(turns)
            result = store.retrieve(maya.id, query, date_query=date_query)
            assert not result.ambiguous, label
            assert [item.memory_id for item in result.matches] == [expected[label]], label

        query, date_query = _memory_retrieval_inputs(_turns(calls["indirect_newest"]))
        other_result = store.retrieve(other.id, query, date_query=date_query)
        assert len(other_result.matches) == 1
        assert "new project" in other_result.matches[0].content


def test_longitudinal_contact_history_covers_review_correction_future_calls_and_isolation(tmp_path):
    workflow = json.loads(FIXTURE.read_text(encoding="utf-8"))["longitudinal_workflow"]
    with MemoryStore(tmp_path / "contact-history.sqlite3") as store:
        contacts = {
            item["key"]: store.create_contact(item["name"], item["disambiguator"])
            for item in workflow["contacts"]
        }
        first = workflow["first_call"]
        first_turns = _turns(first["turns"])
        first_record = store.create_record(
            source_kind="call",
            source_label="fictional first call",
            timezone_name="UTC",
            contact_id=contacts[first["contact"]].id,
            turns=first_turns,
            status="stopped",
        )
        proposals = [
            MemoryProposalInput(
                content=item["content"],
                memory_type=item["type"],
                confidence=item["confidence"],
                evidence_turns=item["evidence_turns"],
            )
            for item in first["proposals"]
        ]
        analyze_record(
            store,
            first_record,
            FakeMemoryExtractor([ExtractionOutput(proposals=proposals)]),
            model="fake",
        )
        pending = {
            row["content"]: row["id"]
            for row in store.list_proposals(contacts[first["contact"]].id)
        }
        approved_items = [item for item in first["proposals"] if item["decision"] == "approve"]
        rejected_items = [item for item in first["proposals"] if item["decision"] == "reject"]
        approved_ids = store.review_proposals(
            [pending[item["content"]] for item in approved_items], approve=True
        )
        store.review_proposals(
            [pending[item["content"]] for item in rejected_items], approve=False
        )
        memories = dict(zip((item["content"] for item in approved_items), approved_ids))

        for item in first["proposals"]:
            evidence_text = " ".join(first_turns[index - 1].content for index in item["evidence_turns"])
            assert all(term in evidence_text for term in item["evidence_terms"])
        for memory_id in approved_ids:
            revision = store.current_revision(memory_id)
            source = store._connection.execute(
                "SELECT record_id,turn_sequences FROM memory_sources WHERE revision_id=?",
                (revision["id"],),
            ).fetchone()
            assert source["record_id"] == first_record
            assert json.loads(source["turn_sequences"])
        for item in rejected_items:
            retrieved = store.retrieve(
                contacts[first["contact"]].id, item["content"]
            ).matches
            assert all(match.content != item["content"] for match in retrieved)

        correction = workflow["correction"]
        old_revision = store.current_revision(memories[correction["from"]])["id"]
        new_revision = store.correct_memory(
            memories[correction["from"]], correction["to"]
        )
        assert new_revision != old_revision
        assert store.retrieve(
            contacts[first["contact"]].id, correction["from"]
        ).matches[0].revision_id == new_revision

        other_contact_memory = None
        for later in workflow["later_calls"]:
            contact = contacts[later["contact"]]
            if later.get("seed_memory"):
                other_contact_memory = store.create_memory(
                    contact.id, later["seed_memory"], memory_type="event_date"
                )
            later_turns = _turns(later["turns"])
            store.create_record(
                source_kind="call",
                source_label=later["id"],
                timezone_name="UTC",
                contact_id=contact.id,
                turns=later_turns,
                status="stopped",
            )
            query, date_query = _memory_retrieval_inputs(later_turns)
            result = store.retrieve(contact.id, query, for_cloud=True, date_query=date_query)
            contents = [item.content for item in result.matches]
            assert any(later["expected"] in content for content in contents), later["id"]
            if later.get("must_not_contain"):
                assert all(later["must_not_contain"] not in content for content in contents)

        assert other_contact_memory is not None
        to_delete = [
            memory_id
            for content, memory_id in memories.items()
            if any(term in content for term in workflow["bulk_delete"]["delete"])
        ]
        store.delete_memories(to_delete)
        pepper_contact = contacts[first["contact"]].id
        assert store.retrieve(pepper_contact, "mint tea").matches == ()
        assert store.retrieve(pepper_contact, "Pepper died").matches == ()
        assert store.retrieve(pepper_contact, "050-555-0101").matches
        assert store.retrieve(contacts["other_maya"].id, "Pepper prize").matches[0].memory_id == other_contact_memory
