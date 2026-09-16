"""Run 24 frozen supplied-evidence cases twice on Luna low under one explicit cap."""
import argparse
import json
import math
import os
import time
from dataclasses import asdict
from pathlib import Path
from types import SimpleNamespace

from local_models import ROOT, SCHEMAS, load
from conversation_copilot.interpretation import (
    BudgetLimits, UsageLedger, f06_structured_request, local_openai_api_key,
)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--api-cap', required=True, type=float)
    parser.add_argument('--run-dir', required=True, type=Path)
    args = parser.parse_args()
    if not math.isfinite(args.api_cap) or args.api_cap <= 0:
        parser.error('A positive finite user-approved cap is required')
    out = args.run_dir
    target = out/'luna-api.json'
    if not out.is_dir() or target.exists():
        raise ValueError('Use a fresh run directory; never overwrite paid results')
    cases = [load(out/'inputs'/f'{i:02}.json') for i in range(24)]
    if len({c['id'] for c in cases}) != 24:
        raise ValueError('Expected 24 distinct frozen cases')
    if not (out/'assistant-reference.json').is_file():
        raise ValueError('Freeze assistant reference before dispatch')
    # Exclusive marker prevents a second process or resumed run resetting spend.
    try:
        (out/'dispatch.lock').open('x').close()
    except FileExistsError as exc:
        raise ValueError('Dispatch lock exists; resuming would reset spend and is forbidden') from exc
    report = {'model': 'gpt-5.6-luna', 'reasoning': 'low', 'cap': args.api_cap, 'rows': []}

    def save():
        report.update(cost_estimate=ledger.committed_dollars, usage=[asdict(r) for r in ledger.records])
        temporary = target.with_suffix('.tmp')
        temporary.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf8')
        temporary.replace(target)

    class Ledger(UsageLedger):
        def reserve(self, *a, **kw):
            result = super().reserve(*a, **kw)
            save()
            return result

        def complete(self, *a):
            super().complete(*a)
            save()

        def release(self, *a):
            super().release(*a)
            save()

    ledger = Ledger(BudgetLimits(warning_dollars=args.api_cap * .8, hard_dollars=args.api_cap))
    from openai import OpenAI
    real = OpenAI(api_key=local_openai_api_key(), max_retries=0, timeout=30)
    active = None

    class Responses:
        def parse(self, **kw):
            if kw['model'] != 'gpt-5.6-luna' or kw['reasoning'] != {'effort': 'low'} or kw['store'] is not False:
                raise ValueError('Only Luna low with store=false is authorized')
            active['request'] = {k: v for k, v in kw.items() if k != 'text_format'}
            from openai.lib._pydantic import to_strict_json_schema
            active['strict_schema'] = to_strict_json_schema(kw['text_format'])
            if any(kw[k] != c['request'][k] for k in ('input', 'instructions', 'max_output_tokens')):
                raise ValueError('Request differs from frozen case')
            save()
            response = real.responses.parse(**kw)
            active['raw_response'] = response.model_dump(mode='json')
            save()
            return response

    client = SimpleNamespace(responses=Responses())
    for index, c in enumerate(cases * 2):
        active = {'id': c['id'], 'repeat': index // 24 + 1}
        report['rows'].append(active)
        started = time.monotonic()
        save()
        try:
            q = c['request']
            result, _ = f06_structured_request(
                SCHEMAS[c['schema']], json.loads(q['input']), q['instructions'],
                ledger=ledger, input_limit=15000, output_limit=q['max_output_tokens'],
                model='gpt-5.6-luna', reasoning='low', client=client,
            )
            active['raw'] = result.model_dump(mode='json')
        except Exception as exc:
            active['error'] = type(exc).__name__ + ': ' + str(exc)
            save()
            raise  # No automatic retries or fallback; retain uncertain billing.
        finally:
            active['seconds'] = time.monotonic() - started
            save()
        print(c['id'], round(active['seconds'], 2), round(ledger.committed_dollars, 6), flush=True)
    report['complete'] = True
    save()


if __name__ == '__main__':
    main()
