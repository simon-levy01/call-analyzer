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
    InterpretationUpdate, _InterpretationWireUpdate, _canonical_interpretation,
    _calibrate_high_confidence, _restrict_evidence_to_present_modalities,
    f06_structured_request, prepare_interpretation_request,
    estimate_english_tokens, REQUEST_PROTOCOL_OVERHEAD_TOKENS, EvidenceModality,
    _cautious_policy, _ground_interpretation, LUNA_MODEL, visual_row_has_evidence,
)

CATEGORIES = ("replies", "remember", "follow_up")
GUIDANCE_INPUT_LIMIT = 4_700  # Explicit roles and source citations; user-authorized +200 input tokens.

GUIDANCE_INSTRUCTIONS = """
Return optional replies, remember and follow_up candidates; empty lists are valid. Replies are optional words the USER could say to the CONTACT, never automatic messages.
First identify who spoke last, who asked each question, and whose experience is described. Read adjacent clarifications/corrections before responding.
Respond to contact disclosures; never retell them as the user's experience. First-person facts, feelings, knowledge, agreement or commitments require explicit USER evidence. Offering to listen/show/clarify now is an optional action, not a personal-state claim.
Never answer for the contact or respond to the user's own words; avoid questions already asked/answered. Corrections are not acceptance: 'Got it—four PM', not 'Four PM works for me'. No invented facts/placeholders. Never infer call duration from this rolling context window.
reply_to_turn_id is the latest contact turn. Replies/follow_up cite latest_turn_id and account for the user's words.
user_spoke_last does not require waiting. Wait only for unfinished CONTACT speech or an outstanding answer; never invent either speaker's continuation. Otherwise offer relevant clarification, support or a next step.
Each candidate must add something useful beyond BOTH speakers' recent words: omit repeated advice/dependencies and paraphrases of the user's last statement. Prefer silence to filler.
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
Garbled fragments inconsistent with the topic are uncertain transcription, not a greeting/topic reset. Prefer one or two concise reply alternatives and at most one distinct follow_up.
"""


def guidance_context_reset(text):
    from .memory import _TOPIC_BOUNDARY
    return bool(_TOPIC_BOUNDARY.search(text) or re.search(
        r"^\s*(?:correction|make that)\b|\b(?:don't|do not) want to (?:talk|discuss)|"
        r"\bstop (?:asking|talking)|\bleave (?:it|that) (?:there|alone)", text, re.I))


def reconcile_replies(update, turns, now=None):
    """Recent, optional ideas may outlive a turn, never a reset or their 24s source age."""
    now = now or datetime.now(timezone.utc)
    changed = [turn for turn in turns if turn.display_order > update.analyzed_order]
    expired = update.context_at is not None and (now - update.context_at).total_seconds() >= 24
    if any(guidance_context_reset(turn.content) for turn in changed):
        return update.model_copy(update={key: [] for key in CATEGORIES})
    if expired:
        return update.model_copy(update={"replies": [], "follow_up": []})
    return update.model_copy(update={key: [item for item in getattr(update, key)
        if not any(reply_superseded(item, turn) for turn in changed)]
        for key in ("replies", "follow_up")})


def normalized_words(text):
    return " " + re.sub(r"\W+", " ", text.casefold()).strip() + " "


def reply_superseded(item, turn):
    if turn.display_order <= max(item.turn_ids, default=0):
        return False
    if turn.speaker_role.value == "user":
        return normalized_words(item.text) in normalized_words(turn.content)
    # ponytail: conservative lexical supersession; paraphrases still need model evaluation.
    # Keep unrelated continuations, but retire a suggestion once the contact addresses its subject.
    stop = set("i you we they it that this the a an to of for is are was be have has do does can could would should will might think not so far about what which how your my me on in and or but just sure yes yeah no okay thanks like something anything say more now thing".split())
    def subjects(text):
        return {word.rstrip("s") for word in re.findall(r"[a-z]+", text.casefold()) if word not in stop and len(word) > 2}
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
    replies: list[GuidanceCandidate] = Field(default_factory=list, max_length=3)
    remember: list[GuidanceCandidate] = Field(default_factory=list, max_length=3)
    follow_up: list[GuidanceCandidate] = Field(default_factory=list, max_length=3)


class GuidedInterpretation(InterpretationUpdate):
    replies: list[GuidanceCandidate] = Field(default_factory=list, max_length=3)
    remember: list[GuidanceCandidate] = Field(default_factory=list, max_length=3)
    follow_up: list[GuidanceCandidate] = Field(default_factory=list, max_length=3)
    snapshot_id: int
    generation: int
    manual: bool = False
    analyzed_order: int = 0
    context_at: datetime | None = None


def interpret_guidance(snapshot, *, ledger, client=None, model=LUNA_MODEL, reasoning="none", is_current=lambda _item: True, live=True):
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
        input_limit=GUIDANCE_INPUT_LIMIT, output_limit=1200, live=live, client=client, model=model, reasoning=reasoning,
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
                for claim in personal_claims)
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
        room = min(1, 3 - len(policy.tones) - len(policy.social_cues))
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


class GuidanceDisplay:
    def __init__(self):
        self.reset()

    def reset(self):
        self.items = {key: [] for key in CATEGORIES}
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
        words = re.findall(r"\w+", item.text.casefold())
        meaning = tuple("clarify" if word in {"explain", "clarify", "elaborate"} else word
                        for word in words if word not in {"could", "would", "can", "you", "please", "that"})
        return category, tuple(sorted(item.memory_ids)), meaning

    def dismiss(self, category, index):
        item = self.all_items(category)[index]
        if item in self.local_remember:
            self.local_remember.remove(item)
        else:
            self.items[category].remove(item)
        if len(self.dismissed) < 256:
            self.dismissed.add(self.fingerprint(category, item.candidate))

    def visible(self, category):
        return self.all_items(category)[:3 if category in self.expanded else 2]

    def all_items(self, category):
        return (self.local_remember + self.items[category])[:3] if category == "remember" else self.items[category]

    def offer_local_remember(self, memories, snapshot_id, now):
        renewed = []
        for memory in memories[:3]:
            candidate = GuidanceCandidate(text=memory.excerpt, confidence=memory.confidence.value, memory_ids=[memory.revision_id])
            if self.fingerprint("remember", candidate) in self.dismissed:
                continue
            old = next((item for item in self.local_remember if item.candidate.memory_ids == candidate.memory_ids), None)
            if old and old.snapshot_id < snapshot_id:
                old.supported_at, old.snapshot_id = now, snapshot_id
            renewed.append(old or DisplayedGuidance(candidate, now, now, snapshot_id))
        retained = [item for item in self.local_remember if now - item.supported_at < 24 and item not in renewed]
        self.local_remember = (renewed + retained)[:3]

    def offer(self, update, now, *, manual=False, source_age=0):
        manual = manual or getattr(update, "manual", False)
        if update.snapshot_id < self.last_snapshot or (update.snapshot_id == self.last_snapshot and not manual):
            return
        if manual:
            self.dismissed.clear()
        self.last_snapshot = update.snapshot_id
        self.pending = update
        self.pending_categories = set(CATEGORIES)
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
        if new_topic:
            self.reset()
            return
        for category in CATEGORIES:
            self.items[category] = [item for item in self.items[category] if
                (turn_ids is None or set(item.candidate.turn_ids) <= turn_ids) and
                (memory_ids is None or {*item.candidate.memory_ids, *item.candidate.preference_ids} <= memory_ids)]
        if memory_ids is not None:
            self.local_remember = [item for item in self.local_remember if set(item.candidate.memory_ids) <= memory_ids]
        if self.pending:
            self.pending = None
            self.pending_categories.clear()

    def tick(self, now):
        self.local_remember = [item for item in self.local_remember if now - item.supported_at < 24]
        for category in CATEGORIES:
            self.items[category] = [item for item in self.items[category] if now - item.supported_at < 24]
        if self.pending is None:
            return
        if now - self.pending_at >= 24:
            self.pending = None
            self.pending_categories.clear()
            return
        for category in CATEGORIES:
            if category not in self.pending_categories:
                continue
            current = self.items[category]
            candidates = [item for item in getattr(self.pending, category) if self.fingerprint(category, item) not in self.dismissed]
            replacement = []
            for candidate in candidates:
                existing = next((item for item in current if item.candidate.text.casefold() == candidate.text.casefold()), None)
                if existing:
                    # Identical old evidence is not a fresh supporting match.
                    fresh = set(candidate.turn_ids) - set(existing.candidate.turn_ids)
                    if fresh or self.pending_manual:
                        existing.supported_at = self.pending_at
                        existing.candidate = candidate
                    if self.pending_manual:
                        existing.shown_at = now
                    replacement.append(existing)
                else:
                    replacement.append(DisplayedGuidance(candidate, now, self.pending_at, self.pending.snapshot_id))
            if not self.pending_manual and any(now - item.shown_at < 12 for item in current):
                continue
            else:
                self.items[category] = replacement
                self.pending_categories.discard(category)
        if not self.pending_categories:
            self.pending = None
