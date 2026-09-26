from conversation_copilot.guidance import GUIDANCE_INSTRUCTIONS
from tools.evaluation.tone_coverage import candidate_prompt, TONE_RULE


def test_candidate_changes_only_tone_paragraph_and_preserves_product_default():
    base=GUIDANCE_INSTRUCTIONS
    old=next(line for line in base.splitlines() if line.startswith('Evaluate tones first,'))
    result=candidate_prompt(base)
    assert result.replace(TONE_RULE,old)==base
    assert GUIDANCE_INSTRUCTIONS==base and TONE_RULE not in base
    assert 'second DISTINCT supported kind' in result
    assert 'Never repair garbled words into a joke' in result
    assert 'No quota' in result
