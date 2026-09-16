"""Offline checks: 24 cases twice, Luna low only, cap before dispatch, no retry."""
import json
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import patch

import memory_answer_comparison as runner
from conversation_copilot.interpretation import InterpretationBudgetExceeded

calls = []
fail = False
original_request = runner.f06_structured_request

def request(*args, **kwargs):
    args = list(args)
    if mode == 'instructions': args[2] = 'Altered instructions'
    if mode == 'input': args[1] = {'altered': True}
    if mode == 'model': kwargs['model'] = 'gpt-5.6-terra'
    return original_request(*args, **kwargs)


def parse(**kw):
    calls.append(kw)
    assert kw['model'] == 'gpt-5.6-luna' and kw['reasoning'] == {'effort': 'low'}
    assert kw['store'] is False
    if fail:
        raise TimeoutError('offline uncertain-billing test')
    output = kw['text_format'].model_validate({'status':'no_match','answer':'Offline stub.','source_ids':[]} if kw['text_format'].__name__ == 'CloudAskOutput' else {
        'interpretation': {'status': 'insufficient_evidence', 'tones': [], 'social_cues': [], 'explanation': 'Offline stub.'},
        'replies': [], 'remember': [], 'follow_up': [],
    })
    return SimpleNamespace(
        model=kw['model'], status='completed', output_parsed=output,
        usage=SimpleNamespace(input_tokens=100, output_tokens=100,
            input_tokens_details=SimpleNamespace(cached_tokens=40, cache_write_tokens=30)),
        model_dump=lambda **_: {'offline_stub': True},
    )


for cap, mode in [(0.000001, 'cap'), (.25, 'success'), (.25, 'timeout'), (.25, 'instructions'), (.25, 'input'), (.25, 'model')]:
    calls.clear()
    fail = mode == 'timeout'
    with TemporaryDirectory() as folder, \
            patch.object(sys, 'argv', ['check', '--api-cap', str(cap), '--run-dir', folder]), \
            patch.object(runner, 'local_openai_api_key', return_value='offline-stub'), \
            patch.object(runner, 'f06_structured_request', side_effect=request), \
            patch('openai.OpenAI', return_value=SimpleNamespace(responses=SimpleNamespace(parse=parse))):
        inputs = Path(folder)/'inputs'
        inputs.mkdir()
        for i in range(24):
            case = {'id': str(i), 'schema': 'CloudAskOutput' if i < 12 else 'GuidanceOutput',
                    'request': {'input': '{}', 'instructions': 'Offline budget test.', 'max_output_tokens': 1200}}
            (inputs/f'{i:02}.json').write_text(json.dumps(case))
        (Path(folder)/'assistant-reference.json').write_text('{}')
        try:
            runner.main()
        except (InterpretationBudgetExceeded, TimeoutError, ValueError):
            assert mode != 'success'
        report = json.loads((Path(folder)/'luna-api.json').read_text(encoding='utf8'))
        assert len(calls) == (48 if mode == 'success' else 1 if mode == 'timeout' else 0)
        assert 0 <= report['cost_estimate'] <= cap
        if mode == 'success':
            assert report['complete'] and len(report['rows']) == 48
            expected_cost = 48 * ((30 * .20 + 40 * .02 + 30 * .20 * 1.25 + 100 * 1.20) / 1_000_000)
            assert abs(report['cost_estimate'] - expected_cost) < 1e-12
        try:
            runner.main()
            raise RuntimeError('Overwrite was not blocked')
        except ValueError:
            pass
        if mode == 'timeout':
            assert report['cost_estimate'] > 0 and not report.get('complete')
        (Path(folder)/'luna-api.json').unlink()  # Mock report only; preserve dispatch lock.
        before = len(calls)
        try:
            runner.main()
            raise RuntimeError('Lock-only resume was not blocked')
        except ValueError as exc:
            assert 'Dispatch lock exists' in str(exc)
        assert len(calls) == before
print('Offline comparison checks passed: no network, no credentials, 48 capped Luna-only requests, uncertain billing retained.')

