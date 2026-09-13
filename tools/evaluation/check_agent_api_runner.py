"""Offline checks: new cases only, Luna low only, cap before dispatch, no retry."""
import json
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import patch

import agent_api_new_cases as runner
from conversation_copilot.interpretation import InterpretationBudgetExceeded

calls = []
fail = False


def parse(**kw):
    calls.append(kw)
    assert kw['model'] == 'gpt-5.6-luna' and kw['reasoning'] == {'effort': 'low'}
    assert kw['store'] is False
    if fail:
        raise TimeoutError('offline uncertain-billing test')
    output = kw['text_format'].model_validate({
        'interpretation': {'status': 'insufficient_evidence', 'tones': [], 'social_cues': [], 'explanation': 'Offline stub.'},
        'replies': [], 'remember': [], 'follow_up': [],
    })
    return SimpleNamespace(
        model=kw['model'], status='completed', output_parsed=output,
        usage=SimpleNamespace(input_tokens=100, output_tokens=100),
        model_dump=lambda **_: {'offline_stub': True},
    )


for cap, mode in [(0.000001, 'cap'), (.25, 'success'), (.25, 'timeout')]:
    calls.clear()
    fail = mode == 'timeout'
    with TemporaryDirectory() as folder, patch.dict(os.environ, CALL_HELPER_AGENT_EVAL_DIR=folder), \
            patch.object(sys, 'argv', ['check', '--api-cap', str(cap)]), \
            patch.object(runner, 'local_openai_api_key', return_value='offline-stub'), \
            patch('openai.OpenAI', return_value=SimpleNamespace(responses=SimpleNamespace(parse=parse))):
        try:
            runner.main()
        except (InterpretationBudgetExceeded, TimeoutError):
            assert mode != 'success'
        report = json.loads((Path(folder)/'new-luna-api.json').read_text(encoding='utf8'))
        assert len(calls) == {'cap': 0, 'success': 12, 'timeout': 1}[mode]
        assert 0 <= report['cost_estimate'] <= cap
        if mode == 'success':
            assert report['complete'] and all(r['id'].startswith('new/') for r in report['rows'])
        if mode == 'timeout':
            assert report['cost_estimate'] > 0 and not report.get('complete')
print('Offline runner checks passed: no network, no credentials, capped Luna-only new cases, uncertain billing retained.')
