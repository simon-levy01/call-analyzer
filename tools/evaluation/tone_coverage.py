"""Isolated tone-coverage candidate; not imported by the product."""

TONE_RULE = """Evaluate tones before replies. Check a second DISTINCT supported kind: factual wording may coexist with explicit warmth, sadness, criticism or emphasis. No quota: one/none is correct without separate evidence; no paraphrases or invented feelings. Neutral means factual, not inner calm. Humor/sarcasm use cue kinds and existing evidence rules. Require coherent deliberate playfulness/irony; odd names, homophones, fragments, corrections or reported jokes are insufficient. Never repair garbled words into a joke. If ASR error is plausible, abstain without independent coherent support. Preserve up to two observable cues: other for acknowledgment, disclosure, clarification, correction or explanation. Cite cue_anchor_turn_id for language; null means no eligible contact speech."""


def candidate_prompt(base):
    old = next(line for line in base.splitlines() if line.startswith('Evaluate tones first,'))
    return base.replace(old, TONE_RULE, 1)
