"""Combined F06 guidance output and bounded display state."""
from __future__ import annotations

from . import test_log

import json
import hashlib
import re
from dataclasses import dataclass
from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict, Field

from .interpretation import (
    InterpretationUpdate, InterpretationStatus, _InterpretationWireUpdate, _canonical_interpretation,
    _calibrate_high_confidence, _restrict_evidence_to_present_modalities,
    f06_structured_request, prepare_interpretation_request,
    estimate_english_tokens, REQUEST_PROTOCOL_OVERHEAD_TOKENS, EvidenceModality,
    _cautious_policy, _ground_interpretation, LUNA_MODEL, LIVE_ASK_MODELS,
    LIVE_ASK_REASONING, LIVE_CATEGORY_LIMIT, visual_row_has_evidence,
)

CATEGORIES = ("replies", "remember", "follow_up")
LIVE_CATEGORIES = ("tones", "social_cues", *CATEGORIES)
GUIDANCE_RETAIN_SECONDS = 48.0
GUIDANCE_INPUT_LIMIT = 5_000  # Four-category-item schema plus explicit roles and source citations.

GUIDANCE_INSTRUCTIONS = """
Return optional replies, remember and follow_up candidates; empty lists are valid. Replies are alternatives for the USER, never automatic messages.
Never invent user feelings, reactions, knowledge, agreement or commitments. No placeholders, unprovided facts or filler. Return at most four useful items in each category.
Corrections are not acceptance: 'Got it—four PM', not 'Four PM works for me'. Use the user's voice, not assistant jargon.
Never answer the user's question as the contact; avoid questions already asked and statements already made.
Never infer call duration from this rolling context window. Replies are optional user speech, not answers addressed to the user. First-person factual claims need explicit user evidence; offering to show or clarify something now is an optional action, not a claim about feelings or availability.
reply_to_turn_id is the latest contact turn. Replies/follow_up must cite latest_turn_id and account for the user's words.
user_spoke_last is NOT a rule to wait; acknowledgments don't close a topic. Prefer concrete optional words for the next pause: clarification, support or a next step.
Wait only for the CONTACT to finish or answer an existing question. No duplicate waiting advice. If the USER is mid-sentence, don't tell the contact to finish it or invent its continuation.
Default to observed user phrasing. Approved communication_style/relationship_preference may refine style; cite preference_ids. Relationship labels imply no style; clarify conflicting preferences.
Cite up to 3 supplied turn_ids plus up to 3 memory revision IDs per candidate; use only relevant sources, with at least one citation overall. Remember requires relevant approved memory_ids. Ask rather than assume uncertain plans.
possible-loss-reference is unconfirmed. Offer 'Possibly related:' plus the memory's exact factual meaning. Keep uncertainty in the reminder, not an identity-check question.
Offer natural support without naming unconfirmed people/events or asking 'Is this about ...?'. 'I am sorry for your loss' can fit supported bereavement; 'lost' alone never establishes death.
No diagnosis, certain emotion, invented agreement or invented preference. Use only current evidence.
turn_ids maps each t row to its source turn ID. m row first field is its memory revision ID.

Current tone/cues concern the latest substantive contact contribution in the current topic. Past/negated feelings, user app commentary and filler are not present contact affect. A topic change is not withdrawal; a preference is not engagement.
Refusing to speak to a THIRD party is not withdrawal from THIS conversation.
When discriminating factual clues support a useful connection across the ongoing topic, return a Remember candidate; do not silently omit it. Copy its supplied ID exactly. Generic stress, sadness, relief or excitement alone cannot select an event; retrieval alone is not relevance. Match meanings without requiring names or shared keywords: a selected short and screening may connect to a film award. Prefer event clues over recency; use dates to distinguish plausible events. Begin 'Possibly related:' unless identity is established. Never recreate transcript facts as memories without supplied memory IDs.
An explicit refusal to discuss an event overrides relevance: omit its reminders/questions until the contact reopens it. After a topic switch, drop old-topic reminders and emotions.
Check each supplied memory against the current factual clues independently. If two facts are both relevant, retain both; if they are competing referents, present low-confidence alternatives or clarify. Do not silently choose, and do not add an irrelevant alternative.
Avoid repeating questions, answers or stated dependencies in meaning. An unfinished contact phrase calls for listening. Apparent greetings, names or other garbled fragments inconsistent with the surrounding topic are uncertain transcription, not a reason to reset the conversation. Never assume 'you must be thrilled'. Prefer one or two concise reply alternatives and at most one distinct follow_up; omit duplicate or unhelpful questions.
"""


def guidance_context_reset(text):
    from .memory import _TOPIC_BOUNDARY
    return bool(_TOPIC_BOUNDARY.search(text) or re.search(
        r"^\s*(?:correction|make that)\b|\b(?:don't|do not) want to (?:talk|discuss)|"
        r"\bstop (?:asking|talking)|\bleave (?:it|that) (?:there|alone)", text, re.I))


def reconcile_replies(update, turns, now=None):
    """Revalidate live content at delivery/render time without changing saved results."""
    now = now or datetime.now(timezone.utc)
    changed = [turn for turn in turns if turn.display_order > update.analyzed_order]
    expired = update.context_at is not None and (now - update.context_at).total_seconds() >= 24
    reset = any(guidance_context_reset(turn.content) for turn in changed)
    if reset or expired:
        return update.model_copy(update={**{key: [] for key in LIVE_CATEGORIES},
            "status": InterpretationStatus.INSUFFICIENT_EVIDENCE, "explanation": "The conversation moved on; waiting for current guidance."})
    return update.model_copy(update={key: [item for item in getattr(update, key)
        if not any(reply_superseded(item, turn) for turn in changed)]
        for key in ("replies", "follow_up")})


def normalized_words(text):
    return " " + re.sub(r"\W+", " ", text.casefold()).strip() + " "


def reply_superseded(item, turn):
    if turn.display_order <= max(item.turn_ids, default=0):
        return False
    # ponytail: conservative lexical supersession; paraphrases still need model evaluation.
    # Keep unrelated continuations, but retire a suggestion once the contact addresses its subject.
    stop = set("i you we they it that this the a an to of for is are was be have has do does can could would should will might think not so far about what which how your my me on in and or but just sure yes yeah no okay thanks like something anything say more now thing".split())
    def subjects(text):
        return {word.rstrip("s") for word in re.findall(r"[a-z]+", text.casefold()) if word not in stop and len(word) > 2}
    if turn.speaker_role.value == "user":
        if normalized_words(item.text) in normalized_words(turn.content):
            return True
        # ponytail: only retire same-subject questions, not arbitrary user continuations.
        # Semantic paraphrases beyond lexical overlap still need model evaluation.
        stop.update(('clarify', 'explain', 'please'))
        terms = subjects(item.text)
        return (item.text.rstrip().endswith('?') and turn.content.rstrip().endswith('?')
                and len(terms) >= 2 and terms <= subjects(turn.content))
    if (turn.content.rstrip().endswith(("?", "—", "-", "...", "…"))
        or re.search(r"\b(?:and|but|because|which|why|the|a|an)\s*$", turn.content, re.I)
        or re.match(r"\s*(?:who|what|when|where|why|how|can|could|would|should|do|does|did|is|are)\b",turn.content,re.I)):
        return False  # A question or unfinished continuation has not answered the suggestion.
    quantity = r"\b(?:\d+(?:\.\d+)?|a|an|half|quarter|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|thirty|forty|fifty|sixty)\s+(?:seconds?|minutes?|hours?)\b"
    if re.search(r"\b(?:so far|elapsed|call)\b",item.text,re.I) and re.search(quantity, item.text, re.I) and re.search(quantity, turn.content, re.I):
        return True
    distinguishing = subjects(item.text)
    return (len(distinguishing) >= 2 or any(len(word) >= 5 for word in distinguishing)) and distinguishing <= subjects(turn.content)


def selected_memory_context(memories, update):
    selected = {revision for item in update.remember for revision in item.memory_ids}
    return [memory for memory in memories if memory.revision_id in selected]


class GuidanceCandidate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    text: str = Field(min_length=1, max_length=180)
    confidence: str = Field(pattern="^(low|medium|high)$")
    turn_ids: list[int] = Field(default_factory=list, max_length=3)
    memory_ids: list[str] = Field(default_factory=list, max_length=3)
    preference_ids: list[str] = Field(default_factory=list, max_length=2)

    @property
    def id(self):
        return hashlib.sha256(self.model_dump_json().encode()).hexdigest()[:20]


class GuidanceOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    interpretation: _InterpretationWireUpdate
    replies: list[GuidanceCandidate] = Field(default_factory=list, max_length=LIVE_CATEGORY_LIMIT)
    remember: list[GuidanceCandidate] = Field(default_factory=list, max_length=LIVE_CATEGORY_LIMIT)
    follow_up: list[GuidanceCandidate] = Field(default_factory=list, max_length=LIVE_CATEGORY_LIMIT)


class GuidedInterpretation(InterpretationUpdate):
    replies: list[GuidanceCandidate] = Field(default_factory=list, max_length=LIVE_CATEGORY_LIMIT)
    remember: list[GuidanceCandidate] = Field(default_factory=list, max_length=LIVE_CATEGORY_LIMIT)
    follow_up: list[GuidanceCandidate] = Field(default_factory=list, max_length=LIVE_CATEGORY_LIMIT)
    snapshot_id: int
    generation: int
    manual: bool = False
    analyzed_order: int = 0
    context_at: datetime | None = None


def interpret_guidance(snapshot, *, ledger, client=None, model=LUNA_MODEL, reasoning=LIVE_ASK_REASONING, is_current=lambda _item: True, live=True):
    if model not in LIVE_ASK_MODELS or reasoning != LIVE_ASK_REASONING:
        raise ValueError("Live guidance requires a selectable model with low reasoning")
    policy = _cautious_policy(snapshot)
    test_log.emit("guidance_input", snapshot=snapshot, local_policy=policy)
    if not any(turn.speaker_role.value == "selected_contact" for turn in snapshot.turns):
        test_log.emit("guidance_empty", generation=snapshot.generation, snapshot_id=snapshot.snapshot_id, reason="no selected-contact speech")
        return GuidedInterpretation(**policy.model_dump(), snapshot_id=snapshot.snapshot_id,
            generation=snapshot.generation, manual=snapshot.manual,
            analyzed_order=max(turn.display_order for turn in snapshot.turns), context_at=snapshot.created_at)
    prepared = prepare_interpretation_request(snapshot, preserve_transcript=True)
    payload = json.loads(prepared.input_text)
    latest = max(snapshot.turns, key=lambda turn: turn.display_order)
    reply_to = max(turn.display_order for turn in snapshot.turns if turn.speaker_role.value == "selected_contact")
    payload["reply_to_turn_id"] = reply_to
    payload["latest_turn_id"] = latest.display_order
    payload["user_spoke_last"] = latest.speaker_role.value == "user"
    instructions = prepared.instructions + GUIDANCE_INSTRUCTIONS
    overhead = sum(estimate_english_tokens(text) for text in (
        instructions, json.dumps(GuidanceOutput.model_json_schema(), separators=(",", ":")))) + REQUEST_PROTOCOL_OVERHEAD_TOKENS
    while overhead + estimate_english_tokens(json.dumps(payload, ensure_ascii=False, separators=(",", ":"))) > GUIDANCE_INPUT_LIMIT:
        # Bound optional observations/memories without spending the transcript allowance on instructions.
        # Keep recent evidence from BOTH sensors before dropping an entire modality.
        key = next((key for key, floor in (("x", 4), ("v", 4), ("m", 1),
                                           ("x", 1), ("v", 1), ("m", 0), ("v", 0), ("x", 0))
                    if len(payload.get(key, [])) > floor), None)
        if key:
            payload[key].pop(-1 if key == "m" else 0)
        else:
            raise ValueError("bounded guidance speech exceeds its input ceiling")
    test_log.emit("guidance_supplied_evidence", generation=snapshot.generation, snapshot_id=snapshot.snapshot_id, payload=payload)
    parsed, _usage = f06_structured_request(GuidanceOutput, payload, instructions, ledger=ledger,
        input_limit=GUIDANCE_INPUT_LIMIT, output_limit=1800, live=live, client=client, model=model, reasoning=reasoning,
        priority=0 if snapshot.manual else 2, is_current=lambda: is_current(snapshot))
    turns = set(payload["turn_ids"])
    memories = {row[0] for row in payload.get("m", [])}
    styles = {item.revision_id for item in snapshot.memories if item.memory_type in {"communication_style", "relationship_preference"}}
    user_words = [normalized_words(turn.content)
                  for turn in snapshot.turns if turn.speaker_role.value == "user"]
    for category in CATEGORIES:
        accepted = []
        for item in getattr(parsed, category):
            words = normalized_words(item.text)
            already_said = any(words in turn for turn in user_words)
            if (not set(item.turn_ids) <= turns or not set(item.memory_ids) <= memories
                or not set(item.preference_ids) <= (styles & memories)):
                test_log.emit("guidance_rejected", generation=snapshot.generation, snapshot_id=snapshot.snapshot_id, category=category, item=item, reason="unavailable evidence")
                raise ValueError("guidance cites unavailable evidence")
            if category in {"replies", "follow_up"} and latest.display_order not in item.turn_ids:
                test_log.emit("guidance_filtered", generation=snapshot.generation, snapshot_id=snapshot.snapshot_id, category=category, item=item, reason="does not cite latest turn")
                continue
            if category in {"replies", "follow_up"} and already_said:
                test_log.emit("guidance_filtered", generation=snapshot.generation, snapshot_id=snapshot.snapshot_id, category=category, item=item, reason="already said")
                continue
            if (category in {"replies", "follow_up"} and latest.speaker_role.value == "user"
                and re.search(r"\b(?:how long|how many minutes)\b.*\b(?:call|talk|talking|conversation)\b", latest.content, re.I)
                and re.search(r"\b(?:seconds?|minutes?|hours?)\b", item.text, re.I)
                and not item.text.rstrip().endswith("?")):
                test_log.emit("guidance_filtered", generation=snapshot.generation, snapshot_id=snapshot.snapshot_id, category=category, item=item, reason="unverified answer to user call-duration question")
                continue
            if (not item.turn_ids and not item.memory_ids
                or (category == "remember" and not item.memory_ids)
                or re.search(r"\[[^\]]+\]|<[^>]+>", item.text)):
                test_log.emit("guidance_filtered", generation=snapshot.generation, snapshot_id=snapshot.snapshot_id, category=category, item=item, reason="evidence count, memory requirement or placeholder")
                continue
            personal_claims = re.finditer(r"\b(?:works? for me|see you|count me in|i(?:['’]ll| will)(?! (?:show(?! up\b)|clarify|rephrase)\b)|i(?: won['’]t| promise| agree| accept| feel| have(?! a question\b)| had| might have| don['’]t think i have)"
                r"|i can (?:make|attend|come|meet)|i(?:['’]m| am| was) (?:doing |feeling )?(?:okay|good|fine|tired|free|happy|glad|excited|sad|upset|angry|nervous|confused|not sure yet)\b|made me (?:laugh|smile))", item.text, re.I)
            unsupported_claim = any(not any(
                any(normalized_words(re.split(r"[,.!?;—]", item.text[claim.start():], maxsplit=1)[0]) == normalized_words(clause.split(",", 1)[0])
                    for clause in re.findall(r"[^.!?;—]+[.!?;—]?", turn.content)
                    if not clause.rstrip().endswith("?") and not re.search(r"[\"“”]", clause))
                for turn in snapshot.turns if turn.speaker_role.value == "user" and turn.display_order in item.turn_ids)
                for claim in personal_claims if not (
                    category in {"replies", "follow_up"} and (
                    (re.match(r"i(?:['’]ll| will) (?:bring (?:it|that|this) closer|check (?:that|it|this|whether|if|the)|look (?:at|up)|compare (?:these|those|the))\b", item.text[claim.start():], re.I)
                     and not re.search(r"\b(?:and|then|by|after|before|tomorrow|tonight|later|soon|weekend|next|monday|tuesday|wednesday|thursday|friday|saturday|sunday|this (?:morning|afternoon|evening))\b", item.text[claim.start():], re.I))
                    or re.search(r"\b(?:see|check) (?:whether|if) $", item.text[:claim.start()], re.I))))
            if unsupported_claim:
                test_log.emit("guidance_filtered", generation=snapshot.generation, snapshot_id=snapshot.snapshot_id, category=category, item=item, reason="unsupported personal claim")
                continue
            evidence_confidence = [memory.confidence.value for memory in snapshot.memories
                                   if memory.revision_id in {*item.memory_ids, *item.preference_ids}]
            if "low" in evidence_confidence:
                item.confidence = "low"
            elif "medium" in evidence_confidence and item.confidence == "high":
                item.confidence = "medium"
            accepted.append(item)
        setattr(parsed, category, accepted)
    if not parsed.replies:
        test_log.emit("guidance_empty", generation=snapshot.generation, snapshot_id=snapshot.snapshot_id, reason="no supported replies", last_speaker=latest.speaker_role)
    modalities = set(prepared.modalities)
    for key, modality in (("x", EvidenceModality.VISUAL), ("v", EvidenceModality.VOCAL), ("m", EvidenceModality.MEMORY)):
        if not payload.get(key):
            modalities.discard(modality)
    if not any(row[1] for row in payload.get("v", [])):
        modalities.discard(EvidenceModality.VOCAL)
    if not any(visual_row_has_evidence(row) for row in payload.get("x", [])):
        modalities.discard(EvidenceModality.VISUAL)
    if not any(row[0] == "c" for row in payload["t"]):
        modalities.discard(EvidenceModality.LANGUAGE)
    # Preserve the local tone/cue safety policy while independently allowing useful
    # word-supported replies. Abstention about tone does not forbid a factual question.
    interpretation = policy or _calibrate_high_confidence(_restrict_evidence_to_present_modalities(
        _ground_interpretation(_canonical_interpretation(parsed.interpretation), snapshot, payload["turn_ids"]), modalities), snapshot)
    if policy is not None and policy.status.value == "updated" and len(policy.tones) == 1:
        # Keep abstention/conflict gates authoritative; a positive rule match need
        # not hide a second supported model hypothesis.
        additional = _calibrate_high_confidence(_restrict_evidence_to_present_modalities(
            _ground_interpretation(_canonical_interpretation(parsed.interpretation), snapshot, payload["turn_ids"]), modalities), snapshot)
        room = LIVE_CATEGORY_LIMIT - len(policy.tones)
        extra = [tone for tone in additional.tones if tone.kind not in {t.kind for t in policy.tones}][:room]
        if extra:
            interpretation = policy.model_copy(update={"tones": [*policy.tones, *extra]})
    return GuidedInterpretation(**interpretation.model_dump(), snapshot_id=snapshot.snapshot_id,
        generation=snapshot.generation, manual=snapshot.manual, analyzed_order=latest.display_order,
        context_at=snapshot.created_at, **{key: getattr(parsed, key) for key in CATEGORIES})


@dataclass
class DisplayedGuidance:
    candidate: GuidanceCandidate
    shown_at: float
    supported_at: float
    snapshot_id: int


@dataclass(frozen=True)
class LiveSuggestionSnapshot:
    """A fixed live suggestion copy; UI lifetime is independent of live refresh."""
    contact_id: str
    category: str
    content: str
    confidence: str
    captured_at: datetime
    turn_ids: tuple[int, ...]
    memory_ids: tuple[str, ...]

    def sources_are_current(self, *, contact_id: str, turn_ids=(), memory_ids=()) -> bool:
        return (self.contact_id == contact_id
                and set(self.turn_ids) <= set(turn_ids)
                and set(self.memory_ids) <= set(memory_ids))


def capture_live_suggestion(update: GuidedInterpretation, category: str, index: int,
                            *, contact_id: str, captured_at: datetime | None = None) -> LiveSuggestionSnapshot:
    if category not in LIVE_CATEGORIES:
        raise ValueError("unknown live category")
    item = getattr(update, category)[index]
    evidence = item.evidence if category in {"tones", "social_cues"} else item
    return LiveSuggestionSnapshot(
        contact_id, category, item.hypothesis if hasattr(item, "hypothesis") else item.text,
        item.confidence.value if hasattr(item.confidence, "value") else item.confidence,
        captured_at or datetime.now(timezone.utc), tuple(evidence.turn_ids),
        tuple(evidence.memory_ids),
    )


class GuidanceDisplay:
    def __init__(self):
        self.reset()

    def reset(self):
        self.items = {key: [] for key in LIVE_CATEGORIES}
        self.local_remember = []
        self.dismissed: set[tuple] = set()
        self.expanded: set[str] = set()
        self.pending = None
        self.pending_categories = set()
        self.pending_at = 0.0
        self.pending_manual = False
        self.last_snapshot = 0

    @staticmethod
    def fingerprint(category, item):
        # ponytail: lexical meaning normalization; a local semantic matcher is only
        # warranted if measured paraphrases evade this bounded, non-cloud check.
        text = item.hypothesis if hasattr(item, "hypothesis") else item.text
        evidence = item.evidence if hasattr(item, "evidence") else item
        if category == 'remember' and evidence.memory_ids:
            return category, tuple(sorted(evidence.memory_ids))
        words = re.findall(r"\w+", text.casefold())
        meaning = tuple("clarify" if word in {"explain", "clarify", "elaborate"} else word
                        for word in words if word not in {"could", "would", "can", "you", "please", "that"})
        return category, tuple(sorted(evidence.memory_ids)), meaning

    def dismiss(self, category, index, *, update=None):
        if category in {"tones", "social_cues"} and not self.items[category] and update is not None:
            item = getattr(update, category)[index]
            if len(self.dismissed) < 256:
                self.dismissed.add(self.fingerprint(category, item))
            return
        item = self.all_items(category)[index]
        if item in self.local_remember:
            self.local_remember.remove(item)
        else:
            self.items[category].remove(item)
        if len(self.dismissed) < 256:
            self.dismissed.add(self.fingerprint(category, item.candidate))

    def filter_update(self, update):
        """Apply live dismissals without altering the accepted model result."""
        return update.model_copy(update={category: [
            item for item in getattr(update, category)
            if self.fingerprint(category, item) not in self.dismissed
        ] for category in LIVE_CATEGORIES})

    def visible(self, category):
        return self.all_items(category)[:LIVE_CATEGORY_LIMIT]

    def all_items(self, category):
        return (sorted(self.local_remember + self.items[category], key=lambda item: item.supported_at, reverse=True)[:LIVE_CATEGORY_LIMIT]
                if category == "remember" else self.items[category])

    def offer_local_remember(self, memories, snapshot_id, now):
        renewed = []
        for memory in memories[:LIVE_CATEGORY_LIMIT]:
            candidate = GuidanceCandidate(text=memory.excerpt, confidence=memory.confidence.value, memory_ids=[memory.revision_id])
            if self.fingerprint("remember", candidate) in self.dismissed:
                continue
            old = next((item for item in self.local_remember if item.candidate.memory_ids == candidate.memory_ids), None)
            if old and old.snapshot_id < snapshot_id:
                old.supported_at, old.snapshot_id = now, snapshot_id
            renewed.append(old or DisplayedGuidance(candidate, now, now, snapshot_id))
        retained = [item for item in self.local_remember if now - item.supported_at < GUIDANCE_RETAIN_SECONDS and item not in renewed]
        self.local_remember = (renewed + retained)[:LIVE_CATEGORY_LIMIT]

    def offer(self, update, now, *, manual=False, source_age=0):
        manual = manual or getattr(update, "manual", False)
        if update.snapshot_id < self.last_snapshot or (update.snapshot_id == self.last_snapshot and not manual):
            return
        if manual:
            self.dismissed.clear()
        self.last_snapshot = update.snapshot_id
        self.pending = update
        self.pending_categories = set(LIVE_CATEGORIES)
        if update.status == InterpretationStatus.CONFLICTING_EVIDENCE:
            self.items['tones'].clear()
            self.items['social_cues'].clear()
        self.pending_at = now - max(0, source_age)
        self.pending_manual = manual
        self.tick(now)

    def on_speech(self, turn):
        if guidance_context_reset(turn.content):
            self.invalidate(turn_ids=set(), memory_ids=set())
            return
        for category in ("replies", "follow_up"):
            self.items[category] = [item for item in self.items[category]
                if not reply_superseded(item.candidate, turn)]
            if self.pending:
                # Work on a copy: the accepted model result remains inspectable.
                self.pending = self.pending.model_copy(update={category: [item for item in getattr(self.pending, category)
                    if not reply_superseded(item, turn)]})

    def invalidate(self, *, turn_ids=None, memory_ids=None, new_topic=False):
        if new_topic or (turn_ids == set() and memory_ids == set()):
            if new_topic:
                self.dismissed.clear()
                self.expanded.clear()
            self.items = {key: [] for key in LIVE_CATEGORIES}
            self.local_remember.clear()
            self.pending = None
            self.pending_categories.clear()
            return
        for category in LIVE_CATEGORIES:
            self.items[category] = [item for item in self.items[category] if
                (turn_ids is None or set(getattr(item.candidate, 'evidence', item.candidate).turn_ids) <= turn_ids) and
                (memory_ids is None or {*getattr(item.candidate, 'evidence', item.candidate).memory_ids, *getattr(item.candidate, 'preference_ids', [])} <= memory_ids)]
        if memory_ids is not None:
            self.local_remember = [item for item in self.local_remember if set(item.candidate.memory_ids) <= memory_ids]
        if self.pending:
            self.pending = None
            self.pending_categories.clear()

    def tick(self, now):
        self.local_remember = [item for item in self.local_remember if now - item.supported_at < GUIDANCE_RETAIN_SECONDS]
        for category in LIVE_CATEGORIES:
            self.items[category] = [item for item in self.items[category] if now - item.supported_at < GUIDANCE_RETAIN_SECONDS]
        if self.pending is None:
            return
        if now - self.pending_at >= 24:
            self.pending = None
            self.pending_categories.clear()
            return
        for category in LIVE_CATEGORIES:
            if category not in self.pending_categories:
                continue
            current = self.items[category]
            candidates = [item for item in getattr(self.pending, category) if self.fingerprint(category, item) not in self.dismissed]
            replacement = []
            for candidate in candidates:
                fingerprint = self.fingerprint(category, candidate)
                if any(self.fingerprint(category, item.candidate) == fingerprint for item in replacement):
                    continue
                existing = next((item for item in current if self.fingerprint(category, item.candidate) == fingerprint), None)
                if existing:
                    # Identical old evidence is not a fresh supporting match.
                    fresh = set(getattr(candidate, 'evidence', candidate).turn_ids) - set(getattr(existing.candidate, 'evidence', existing.candidate).turn_ids)
                    fresh = fresh or (not getattr(candidate, 'evidence', candidate).turn_ids
                        and self.pending.snapshot_id > existing.snapshot_id and self.pending_at > existing.supported_at)
                    if not fresh and not self.pending_manual:
                        confidence = {'low': 0, 'medium': 1, 'high': 2}
                        if confidence[candidate.confidence] < confidence[existing.candidate.confidence]:
                            existing.candidate = candidate
                        continue  # Retain in its old position; repeated evidence is not newest.
                    if fresh or self.pending_manual:
                        existing.supported_at = max(existing.supported_at, self.pending_at)
                        existing.candidate = candidate
                        existing.snapshot_id = self.pending.snapshot_id
                    if self.pending_manual:
                        existing.shown_at = now
                    replacement.append(existing)
                else:
                    replacement.append(DisplayedGuidance(candidate, now, self.pending_at, self.pending.snapshot_id))
            retained = [item for item in current if item not in replacement]
            # New results lead; older supported items fill unused slots, never renew on omission.
            self.items[category] = (replacement + retained)[:LIVE_CATEGORY_LIMIT]
            self.pending_categories.discard(category)
        if not self.pending_categories:
            self.pending = None
