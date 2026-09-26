"""Experimental tone presentation and prompts. Product defaults are unchanged."""
from conversation_copilot import interpretation as ip

LABELS = ('Happy / pleased', 'Warm / appreciative', 'Sad / downbeat', 'Neutral / factual',
          'Frustrated / negative', 'Worried / tense', 'Excited / energetic',
          'Curious / interested', 'Uncertain / hesitant', 'Playful / humorous', 'Possible sarcasm')
KIND_LABELS = {
    'positive_warm': 'Warm / appreciative', 'neutral_calm': 'Neutral / factual',
    'sad_low_energy': 'Sad / downbeat', 'tense_negative': 'Frustrated / negative',
    'energetic_high_energy': 'Excited / energetic', 'emotionally_intense': 'Emotionally intense',
}

LABEL_RULE = """Tone hypotheses use 'Label — reason': Happy / pleased; Warm / appreciative; Sad / downbeat; Neutral / factual; Frustrated / negative; Worried / tense; Excited / energetic; Curious / interested; Uncertain / hesitant. Use the closest compatible kind. Evaluate 0-2 distinct supported tones independently of replies. Neutral means factual wording, not inner calm. Rough/downbeat wording can support downbeat, not a diagnosis. Put disclosures/corrections/requests/boundaries in social_cues. Humor/sarcasm use their cue kinds and labels Playful / humorous or Possible sarcasm; require clear contextual support, not praise alone. Cite cue_anchor_turn_id for language; null means no eligible contact speech. No filler, invented feelings or ASR interpretation."""
SPLIT_RULE = """Separate CONTACT tone from conversational meaning. Tones use 'Label — reason': Happy / pleased; Warm / appreciative; Sad / downbeat; Neutral / factual; Frustrated / negative; Worried / tense; Excited / energetic; Curious / interested; Uncertain / hesitant. Use compatible kinds, 0-2 distinct facets, no quota. Neutral means wording, not inner calm. Independently preserve disclosures, corrections, clarifications and boundaries in social_cues even when affect is unknown; avoid repeating tone reasons. Humor/sarcasm use their cue kinds, labeled Playful / humorous or Possible sarcasm, only with contextual contrast or explicit joking. Praise alone proves neither happiness nor sarcasm. Cite cue_anchor_turn_id; ignore filler/ASR noise."""

def prompts(base):
    old=next(p for p in base.split('\n') if p.startswith('Evaluate tones first,'))
    return {'base':base,'labels':base.replace(old,LABEL_RULE),'split':base.replace(old,SPLIT_RULE)}

def present(update, mode):
    """Preserve evidence; relocate factual tone details into conversation cues.

    Retains existing four-slot category ceiling. Saved audit records any overflow.
    Humor/sarcasm remain explicit style cues (not emotional diagnoses).
    """
    if mode=='base':return update
    result=update.model_copy(deep=True)
    cues=list(result.social_cues)
    for tone in result.tones:
        original=tone.hypothesis
        parts=original.split(' — ',1)
        if len(parts)==2 and parts[0] in LABELS:
            label,detail=parts
        else:
            label,detail=KIND_LABELS[tone.kind.value],original
        tone.hypothesis=label
        # Keep each existing observation, but never evict an existing cue for it.
        if len(cues)<ip.LIVE_CATEGORY_LIMIT and detail.casefold() not in {c.hypothesis.casefold() for c in cues}:
            cues.append(ip.SocialCue(kind='other',confidence=tone.confidence,hypothesis=detail,evidence=tone.evidence.model_copy(deep=True)))
    result.social_cues=cues
    return result
