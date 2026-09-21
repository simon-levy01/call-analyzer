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


def test_indirect_happy_event_uses_clear_contact_cues_but_not_a_vague_prompt(
    tmp_path, monkeypatch
):
    def fake_vectors(texts, _cache_dir):
        vectors = np.zeros((len(texts), 384), dtype=np.float32)
        for index, text in enumerate(texts):
            lowered = text.casefold()
            if "moved into" in lowered or "carrying so much weight" in lowered:
                vectors[index, 0] = 1
            elif "strength-training class" in lowered:
                vectors[index, 0] = 0.99
                vectors[index, 3] = (1 - 0.99**2) ** 0.5
            elif "pepper died" in lowered or "meant a lot to me" in lowered:
                vectors[index, 4] = 1
            elif "pottery course" in lowered:
                vectors[index, 4] = 0.99
                vectors[index, 5] = (1 - 0.99**2) ** 0.5
            elif "lost her job" in lowered:
                vectors[index, 1] = 1
            elif "blue walls" in lowered:
                vectors[index, 6] = 1
            else:
                vectors[index, 2] = 1
        return vectors

    monkeypatch.setattr(semantic_module, "embed_texts_if_ready", fake_vectors)
    turns = _turns([
        ("user", "How are you feeling after the whole thing?"),
        ("selected_contact", "Honestly, really happy, but completely exhausted."),
        ("user", "What wore you out so much?"),
        ("selected_contact", "I spent all day carrying so much weight up the stairs."),
        ("selected_contact", "My back is sore, but I am glad it is finally done."),
    ])
    with MemoryStore(tmp_path / "indirect-happy-event.sqlite3") as store:
        maya = store.create_contact("Maya")
        noa = store.create_contact("Noa")
        move = store.create_memory(
            maya.id,
            "Maya moved into a new apartment on August 28, 2026",
            memory_type="event_date",
        )
        wall_color = store.create_memory(
            maya.id, "Maya likes blue walls", memory_type="preference"
        )
        store.connect_memories(move, wall_color)
        store.create_memory(maya.id, "Maya lost her job", memory_type="event_date")
        store.create_memory(
            maya.id, "Maya started a pottery course", memory_type="recurring_topic"
        )
        store.create_memory(
            maya.id, "Maya's dog Pepper died", memory_type="event_date"
        )
        store.create_memory(
            noa.id, "Noa moved into a new apartment", memory_type="event_date"
        )
        store.backfill_semantic_embeddings()

        for count in (2, 3):
            visible = turns[:count]
            query, date_query = _memory_retrieval_inputs(visible)
            assert store.retrieve(
                maya.id,
                query,
                for_cloud=True,
                date_query=date_query,
                semantic_query=_memory_semantic_input(visible),
                contact_cue_query=_memory_semantic_input(
                    visible, speaker_role=SpeakerRole.SELECTED_CONTACT
                ),
            ).matches == ()

        query, date_query = _memory_retrieval_inputs(turns)
        result = store.retrieve(
            maya.id,
            query,
            for_cloud=True,
            date_query=date_query,
            semantic_query=_memory_semantic_input(turns),
            contact_cue_query=_memory_semantic_input(
                turns, speaker_role=SpeakerRole.SELECTED_CONTACT
            ),
        )
        assert not result.ambiguous
        assert [item.memory_id for item in result.matches] == [move]
        context = result.matches[0]
        request = prepare_interpretation_request(build_snapshot(
            turns,
            snapshot_id=1,
            generation=1,
            contact_id=maya.id,
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
        ))
        assert request.memory_count == 1
        assert "moved into a new apartment" in request.input_text

        training = store.create_memory(
            maya.id,
            "Maya attends a weekly strength-training class",
            memory_type="recurring_topic",
        )
        store.backfill_semantic_embeddings()
        possibilities = store.retrieve(
            maya.id,
            query,
            for_cloud=True,
            date_query=date_query,
            semantic_query=_memory_semantic_input(turns),
            contact_cue_query=_memory_semantic_input(
                turns, speaker_role=SpeakerRole.SELECTED_CONTACT
            ),
        )
        assert possibilities.ambiguous and possibilities.status == "possibilities"
        assert {move, training} == {
            item.memory_id for item in possibilities.matches
        }
        possible_contexts = [RetrievedMemoryContext(
            memory_id=item.memory_id,
            revision_id=item.revision_id,
            excerpt=item.content,
            memory_type=item.memory_type,
            confidence=item.confidence,
            sensitivity_safe=item.cloud_eligible,
            rank=item.rank,
            relevance=item.reason,
        ) for item in possibilities.matches]
        withheld = prepare_interpretation_request(build_snapshot(
            turns,
            snapshot_id=2,
            generation=1,
            contact_id=maya.id,
            retrieved_memories=[],
        ))
        assert withheld.memory_count == 0
        display = format_interpretation_body(
            InterpretationUpdate(
                status="insufficient_evidence",
                explanation="The current words do not identify one event.",
            ),
            "Waiting for interpretation",
            possible_contexts,
        )
        assert "moved into a new apartment" in display
        assert "weekly strength-training class" in display

        misleading_loss = _turns([
            ("user", "How have you been?"),
            ("selected_contact", "I missed her call yesterday."),
            ("user", "How are you feeling after the whole thing?"),
            ("selected_contact", "That really meant a lot to me yesterday."),
        ])
        loss_query, loss_date_query = _memory_retrieval_inputs(misleading_loss)
        assert store.retrieve(
            maya.id,
            loss_query,
            for_cloud=True,
            date_query=loss_date_query,
            semantic_query=_memory_semantic_input(misleading_loss),
            contact_cue_query=_memory_semantic_input(
                misleading_loss, speaker_role=SpeakerRole.SELECTED_CONTACT
            ),
        ).matches == ()

        wrong_query, wrong_date_query = _memory_retrieval_inputs(turns)
        wrong = store.retrieve(
            noa.id,
            wrong_query,
            for_cloud=True,
            date_query=wrong_date_query,
            semantic_query=_memory_semantic_input(turns),
            contact_cue_query=_memory_semantic_input(
                turns, speaker_role=SpeakerRole.SELECTED_CONTACT
            ),
        )
        assert wrong.matches
        assert all(item.contact_id == noa.id for item in wrong.matches)
        assert move not in {item.memory_id for item in wrong.matches}

        vague = _turns([
            ("user", "How have you been?"),
            ("selected_contact", "I have been getting by."),
            ("user", "How are you feeling after the whole thing?"),
            ("selected_contact", "It has been a lot."),
        ])
        query, date_query = _memory_retrieval_inputs(vague)
        assert store.retrieve(
            maya.id,
            query,
            for_cloud=True,
            date_query=date_query,
            semantic_query=_memory_semantic_input(vague),
            contact_cue_query=_memory_semantic_input(
                vague, speaker_role=SpeakerRole.SELECTED_CONTACT
            ),
        ).matches == ()


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
            ) or ("died" in lowered and ("dog" in lowered or "cat" in lowered))
            if "robin died" in lowered:
                vectors[index, 0] = 0.93
                vectors[index, 1] = (1 - 0.93**2) ** 0.5
            elif grief:
                vectors[index, 0] = 1
            elif lowered.startswith("maya") or lowered.startswith("other maya"):
                vectors[index, 1] = 1
            else:
                vectors[index, 2] = 1
        return vectors

    monkeypatch.setattr(semantic_module, "embed_texts_if_ready", fake_vectors)

    def retrieve(store, contact_id, turns, *, for_cloud=True):
        query, date_query = _memory_retrieval_inputs(turns)
        return store.retrieve(
            contact_id,
            query,
            for_cloud=for_cloud,
            date_query=date_query,
            semantic_query=_memory_semantic_input(turns),
            contact_cue_query=_memory_semantic_input(
                turns, speaker_role=SpeakerRole.SELECTED_CONTACT
            ),
        )

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
        pottery = store.create_memory(
            selected.id, "Maya is learning pottery", memory_type="recurring_topic"
        )
        tea = store.create_memory(selected.id, "Maya prefers mint tea", memory_type="preference")
        store.create_memory(selected.id, "Maya recently lost her job", memory_type="event_date")
        store.create_memory(selected.id, "Maya moved apartment recently", memory_type="event_date")
        store.create_memory(selected.id, "Maya's laptop died last week", memory_type="event_date")
        store.create_memory(selected.id, "Maya's friend loves death metal", memory_type="preference")
        store.create_memory(
            other.id,
            "Other Maya's dog Pepper died on August 20, 2026",
            memory_type="event_date",
        )
        store.connect_memories(pepper, tea)
        store.backfill_semantic_embeddings()

        for raw in scenarios:
            turns = _turns(raw)
            cue_at = 4 if len(raw) == 4 else 5
            before = retrieve(store, selected.id, turns[: cue_at - 1])
            assert pepper not in {item.memory_id for item in before.matches}

            result = retrieve(store, selected.id, turns)
            assert not result.ambiguous
            assert [item.memory_id for item in result.matches] == [pepper]
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

            wrong = retrieve(store, other.id, turns)
            assert pepper not in {item.memory_id for item in wrong.matches}

        implicit = _turns([
            ("user", "Hey, how have you been?"),
            ("selected_contact", "I have been trying to manage."),
            ("user", "How are you feeling after the whole thing?"),
            ("selected_contact", "Honestly, it has been difficult."),
            ("selected_contact", "She meant a lot to me."),
            ("selected_contact", "I miss her every day."),
        ])
        for length, expected in ((4, []), (5, [pepper]), (6, [pepper])):
            visible = implicit[:length]
            result = retrieve(store, selected.id, visible)
            assert not result.ambiguous
            assert [item.memory_id for item in result.matches] == expected
            if length == 4:
                assert result.status == "none"

        grief_only = _turns([
            ("user", "Hey, how have you been?"),
            ("selected_contact", "I have been trying to manage."),
            ("user", "How are you feeling after the whole thing?"),
            ("selected_contact", "I miss her every day."),
        ])
        result = retrieve(store, selected.id, grief_only)
        assert [item.memory_id for item in result.matches] == [pepper]

        dated_vague = _turns([
            ("user", "Hey, how have you been?"),
            ("selected_contact", "I have been trying to manage."),
            ("user", "How are you feeling after the whole thing?"),
            ("selected_contact", "It has been difficult since August 18, 2026."),
        ])
        result = retrieve(store, selected.id, dated_vague)
        assert not result.matches and result.status == "abstain"

        user_spoken_cues = _turns([
            ("user", "Hey, how have you been?"),
            ("selected_contact", "I have been trying to manage."),
            ("user", "After the whole thing, she meant a lot and I miss her."),
            ("selected_contact", "It has been difficult."),
        ])
        result = retrieve(store, selected.id, user_spoken_cues)
        assert not result.matches and result.status == "none"

        mundane_cues = _turns([
            ("user", "Hey, how have you been after the whole thing?"),
            ("selected_contact", "I missed her call."),
            ("user", "Did it matter?"),
            ("selected_contact", "That really meant a lot."),
        ])
        result = retrieve(store, selected.id, mundane_cues)
        assert not result.matches and result.status == "none"

        mixed_topic = _turns([
            ("user", "Hey, how have you been?"),
            ("selected_contact", "I have been trying to manage."),
            ("user", "How are you feeling after the whole thing?"),
            ("selected_contact", "Honestly, it has been difficult."),
            ("selected_contact", "She meant a lot to me."),
            ("selected_contact", "I miss her every day."),
            ("user", "How is the pottery class going?"),
        ])
        result = retrieve(store, selected.id, mixed_topic)
        assert {item.memory_id for item in result.matches} == {pepper, pottery}

        direct_loss = store.retrieve(
            selected.id,
            "Pepper dog",
            for_cloud=True,
            semantic_query="",
            contact_cue_query="",
        )
        assert [item.memory_id for item in direct_loss.matches] == [pepper]
        direct_tea = store.retrieve(
            selected.id,
            "mint tea",
            for_cloud=True,
            semantic_query="",
            contact_cue_query="",
        )
        assert [item.memory_id for item in direct_tea.matches] == [tea]

        robin = store.create_memory(
            selected.id,
            "Maya's cat Robin died two weeks ago",
            memory_type="event_date",
        )
        store.backfill_semantic_embeddings()
        result = retrieve(store, selected.id, implicit)
        assert result.ambiguous and result.status == "possibilities"
        assert {item.memory_id for item in result.matches} == {pepper, robin}

        private = store.create_contact("Private Maya")
        private_loss = store.create_memory(
            private.id,
            "Private Maya's dog Clover died last month",
            memory_type="event_date",
            sensitivity="sensitive",
        )
        store.backfill_semantic_embeddings()
        automatic = retrieve(store, private.id, implicit)
        local = retrieve(store, private.id, implicit, for_cloud=False)
        assert [item.memory_id for item in automatic.matches] == [private_loss]
        assert [item.memory_id for item in local.matches] == [private_loss]

        dated = store.create_contact("Dated Maya")
        older = store.create_memory(
            dated.id,
            "Dated Maya's grandfather died years ago",
            memory_type="event_date",
            normalized_date_start=datetime(2011, 5, 1, tzinfo=timezone.utc),
        )
        newest = store.create_memory(
            dated.id,
            "Dated Maya's dog Pepper died recently",
            memory_type="event_date",
            normalized_date_start=datetime(2026, 8, 18, tzinfo=timezone.utc),
        )
        store.backfill_semantic_embeddings()
        result = retrieve(store, dated.id, implicit)
        assert not result.ambiguous
        assert [item.memory_id for item in result.matches] == [newest]
        direct_old = store.retrieve(
            dated.id,
            "grandfather",
            for_cloud=True,
            semantic_query="",
            contact_cue_query="",
        )
        assert [item.memory_id for item in direct_old.matches] == [older]

    monkeypatch.setattr(
        semantic_module, "embed_texts_if_ready", lambda *_args, **_kwargs: None
    )
    with MemoryStore(tmp_path / "progressive-grief-no-model.sqlite3") as store:
        selected = store.create_contact("Maya")
        store.create_memory(
            selected.id,
            "Maya's dog Pepper died on August 18, 2026",
            memory_type="event_date",
        )
        result = retrieve(store, selected.id, implicit)
        assert not result.matches and result.status == "none"
        assert not result.semantic_available


def test_financial_wording_focuses_retrieval_without_inventing_a_cause(tmp_path, monkeypatch):
    queries = []
    def embed(texts, cache):
        queries.extend(texts)
        return np.array([np.eye(384, dtype=np.float32)[0 if "lost his job" in text or "Financial hardship." in text else 1]
                         for text in texts])
    monkeypatch.setattr(semantic_module, "embed_texts_if_ready", embed)
    with MemoryStore(tmp_path / "financial.sqlite3") as store:
        contact = store.create_contact("Sam")
        job = store.create_memory(contact.id, "Sam lost his job at McDonalds.", memory_type="event_date")
        store.backfill_semantic_embeddings()
        def retrieve(text):
            turns = _turns([("user", "How have you been?"), ("selected_contact", "A rough week."),
                            ("user", "What happened?"), ("selected_contact", text)])
            query, dates = _memory_retrieval_inputs(turns)
            return store.retrieve(contact.id, query, date_query=dates, for_cloud=True,
                semantic_query=_memory_semantic_input(turns),
                contact_cue_query=_memory_semantic_input(turns, speaker_role=SpeakerRole.SELECTED_CONTACT))
        assert [m.memory_id for m in retrieve("It's hard money-wise.").matches] == [job]
        assert "It's hard money-wise. Financial hardship." in queries
        assert not retrieve("I'm stressed.").matches
        assert not retrieve("It's not hard money-wise.").matches
        assert not retrieve("Anyway, I finished a book.").matches
        assert not any("McDonalds" in query for query in queries[1:])


def test_implicit_lost_pet_reference_stays_possible_and_respects_context(tmp_path, monkeypatch):
    # Equal semantic vectors deliberately exercise the cue and ambiguity guards.
    monkeypatch.setattr(semantic_module, "embed_texts_if_ready",
        lambda texts, cache: np.tile(np.eye(1, 384, dtype=np.float32), (len(texts), 1)))
    def retrieve(store, contact, raw):
        turns = _turns(raw)
        query, dates = _memory_retrieval_inputs(turns)
        return store.retrieve(contact, query, for_cloud=True, date_query=dates,
            semantic_query=_memory_semantic_input(turns),
            contact_cue_query=_memory_semantic_input(turns, speaker_role=SpeakerRole.SELECTED_CONTACT))
    prefix = [("user", "How have you been?"), ("selected_contact", "A difficult few days."),
              ("user", "What has been on your mind?")]
    with MemoryStore(tmp_path / "lost-pet.sqlite3") as store:
        maya = store.create_contact("Maya").id
        other = store.create_contact("Nora").id
        pepper = store.create_memory(maya, "Maya lost her dog Pepper on August 18, 2026.", memory_type="event_date")
        store.backfill_semantic_embeddings()
        implicit = prefix + [("selected_contact", "I miss her every day. She meant a lot to me.")]
        result = retrieve(store, maya, implicit)
        assert [m.memory_id for m in result.matches] == [pepper]
        assert "possible-loss-reference" in result.matches[0].reason
        assert "died" not in result.matches[0].content
        assert not retrieve(store, other, implicit).matches
        assert not retrieve(store, maya, prefix + [("selected_contact", "It has been difficult.")]).matches
        user_only = prefix[:2] + [("user", "I miss her every day. She meant a lot to me."),
                                 ("selected_contact", "It has been difficult.")]
        assert not retrieve(store, maya, user_only).matches
        assert not retrieve(store, maya, implicit + [("user", "Okay."),
            ("selected_contact", "Changing the subject: I am enjoying The Hobbit.")]).matches
        direct = retrieve(store, maya, prefix + [("selected_contact", "I miss my dog Pepper.")])
        assert [m.memory_id for m in direct.matches] == [pepper]
        assert "possible-loss-reference" not in direct.matches[0].reason
        store.create_memory(maya, "Maya lost her cat Robin last month.", memory_type="event_date")
        store.backfill_semantic_embeddings()
        assert retrieve(store, maya, implicit).ambiguous


def test_generic_relationship_conflict_does_not_retrieve_bereavement_memory(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(
        semantic_module,
        "embed_texts_if_ready",
        lambda texts, _cache: np.pad(
            np.ones((len(texts), 1), dtype=np.float32), ((0, 0), (0, 383))
        ),
    )
    turns = _turns([
        ("user", "Synthetic prompt: describe the day."),
        ("selected_contact", "Synthetic reply: I will tell somebody else."),
        ("user", "Synthetic prompt: why not tell me?"),
        ("selected_contact", "Synthetic reply: I prefer not to discuss it."),
        ("user", "Synthetic prompt: is this about our friendship?"),
        ("selected_contact", "Synthetic reply: I no longer feel close to you."),
    ])
    with MemoryStore(tmp_path / "relationship-conflict.sqlite3") as store:
        contact = store.create_contact("Alex")
        store.create_memory(
            contact.id,
            "Alex's cat died on September 1, 2026",
            memory_type="event_date",
        )
        store.backfill_semantic_embeddings()
        query, date_query = _memory_retrieval_inputs(turns)
        result = store.retrieve(
            contact.id,
            query,
            date_query=date_query,
            semantic_query=_memory_semantic_input(turns),
            contact_cue_query=_memory_semantic_input(
                turns, speaker_role=SpeakerRole.SELECTED_CONTACT
            ),
        )

    assert result.matches == ()


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
        memory_ids=["authored-revision"] if memory_used else [],
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
                            memory_ids=[cloud_context[0].revision_id],
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
        max(index for index, turn in enumerate(fixture["turns"], 1) if turn["end_seconds"] <= first_update_at + 12 * offset)
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
            _authored_update(tone="sad_low_energy"),
            _authored_update(cue="uncertainty"),
            _authored_update(tone="positive_warm", cue="humor"),
            _authored_update(cue="sarcasm"),
            _authored_update(tone="positive_warm", cue="humor", memory_used=True),
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
            assert len(possibilities) == expected["request_memory_rows"]

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
            analysis_at = first_update_at + 12 * (snapshot_id - 1)
            card_at = 12.001 * (snapshot_id - 1)
            assert card.offer(returned, card_at) == expected.get("card_result", "replaced")
            memory_at = analysis_at + (0.001 if expected.get("after_hold_expiry") else 0)
            card.offer_memory_possibilities(possibilities, memory_at)
            display = format_interpretation_body(
                card.update, card.message, card.memory_possibilities
            )
            displays.append(display)
            for text in expected["memory_contains"]:
                assert text in display, (expected["through_turn"], text)
            for text in expected["memory_excludes"]:
                assert text not in display, (expected["through_turn"], text)
            if expected["request_memory_rows"]:
                assert "Evidence sources: conversation words, approved memory" in display
            else:
                assert "Evidence sources: conversation words, approved memory" not in display

        assert len(displays) == len(interpreter.calls) == len(fixture["progressive_checkpoints"])


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


def test_exact_lexical_memory_still_retrieves_during_a_semantic_topic_pause(tmp_path):
    changed_topic = _turns([
        ["user", "Besides that, what have you been drinking lately?"],
        ["selected_contact", "I have been making mint tea every evening."],
        ["user", "Does mint tea help you relax?"],
        ["selected_contact", "Yes, mint tea has been a pleasant routine."],
    ])
    with MemoryStore(tmp_path / "topic-pause-lexical.sqlite3") as store:
        maya = store.create_contact("Maya")
        tea = store.create_memory(
            maya.id, "Maya prefers mint tea", memory_type="preference"
        )
        query, date_query = _memory_retrieval_inputs(changed_topic)
        semantic_query = _memory_semantic_input(changed_topic)

        result = store.retrieve(
            maya.id, query, date_query=date_query, semantic_query=semantic_query
        )

        assert semantic_query == ""
        assert result.matches[0].memory_id == tea
        assert "lexical" in result.matches[0].reason


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
            model="gpt-5.6-terra",
            reasoning="low",
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
