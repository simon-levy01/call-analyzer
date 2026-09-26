from conversation_copilot import interpretation as ip
from tools.evaluation.tone_labels import present


def test_labels_preserve_observations_sources_and_original():
    evidence=ip.Evidence(explanation='Explicit thanks',modalities=['language'],turn_ids=[3])
    tone=ip.ToneHypothesis(kind='positive_warm',confidence='medium',hypothesis='Warm / appreciative — Expresses thanks.',evidence=evidence)
    original=ip.InterpretationUpdate(status='updated',tones=[tone])
    labeled=present(original,'labels')
    assert labeled.tones[0].hypothesis=='Warm / appreciative'
    assert labeled.social_cues[0].hypothesis=='Expresses thanks.'
    assert labeled.social_cues[0].evidence==evidence
    assert original.tones[0].hypothesis.endswith('Expresses thanks.')
    assert not original.social_cues
    assert present(original,'base') is original
