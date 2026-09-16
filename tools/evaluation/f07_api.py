"""F07 fictional tuning only. Explicit frozen sources, exclusive outputs, no retries."""
import argparse
from dataclasses import asdict
from datetime import datetime
import hashlib
import json
import math
import msvcrt
from pathlib import Path
import sys
import time
from types import SimpleNamespace


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source', type=Path, required=True)
    p.add_argument('--freeze', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--prior', type=Path)
    args = p.parse_args()
    root = Path(__file__).resolve().parents[2]
    if not args.output.resolve().is_relative_to(root / 'build'):
        p.error('Evidence must stay in ignored build directory')
    if args.output.resolve().parent != args.freeze.resolve() or not args.output.name.startswith('api-'):
        p.error('Use an api-* run directory directly under its freeze for spend discovery')
    if not args.freeze.resolve().is_relative_to(root / 'build'):
        p.error('Freeze must stay in ignored build directory')
    # OS releases this lock on exit/crash. Never allow two independent ledgers
    # to reserve the same remaining allocation concurrently.
    lock = (args.freeze/'api-run.lock').open('a+b')
    lock.write(b'0')
    lock.flush()
    lock.seek(0)
    msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)
    authorization = json.loads((args.freeze / 'authorization.json').read_text())
    if not math.isfinite(authorization['cap_usd']) or authorization['cap_usd'] <= 0:
        p.error('Invalid authorization cap')
    assert authorization['model'] == 'gpt-5.6-luna' and authorization['effort'] == 'low'
    prior = prior_spend(args.freeze)
    if args.prior and json.loads(args.prior.read_text())['committed_dollars'] > prior:
        p.error('Prior report is outside the discovered ledger chain')
    # One first-round allocation within the user's aggregate cap; future runs must
    # carry this report forward, including uncertain billing and reservations.
    allocation = min(.075, authorization['cap_usd']) - prior
    if allocation <= 0:
        p.error('No tuning allocation remains')
    args.output.mkdir(parents=True, exist_ok=False)
    sys.path.insert(0, str(args.source.resolve()))
    from conversation_copilot.interpretation import (BudgetLimits, UsageLedger,
        build_snapshot, RetrievedMemoryContext, f06_structured_request, local_openai_api_key)
    from conversation_copilot.models import ConversationTurn
    from conversation_copilot.guidance import interpret_guidance
    from conversation_copilot.memory import EXTRACTION_INSTRUCTIONS, ExtractionOutput, _extraction_payload
    from openai import OpenAI
    report = dict(authorization=authorization, prior_dollars=prior, rows=[],
        source=str(args.source.resolve()), source_hashes={str(f.relative_to(args.source)):hashlib.sha256(f.read_bytes()).hexdigest()
            for f in (args.source/'conversation_copilot').glob('*.py')},
        pricing_url='https://developers.openai.com/api/docs/models/gpt-5.6-luna',
        pricing_usd_per_million=dict(input=.2,cached_input=.02,output=1.2),
        evaluation='first-round tuning; one response per case/condition, not the final 144',
        retrieval='bypassed: supplied fictional candidates; omissions are supplied-evidence use, not retrieval failures')
    target = args.output / 'report.json'
    def save():
        report.update(committed_dollars=prior+ledger.committed_dollars,
                      usage=[asdict(r) for r in ledger.records])
        tmp=target.with_suffix('.tmp')
        tmp.write_text(json.dumps(report,indent=2),encoding='utf8')
        tmp.replace(target)
    class Ledger(UsageLedger):
        def reserve(self,*a,**kw):
            reservation=super().reserve(*a,**kw)
            save()
            return reservation
        def complete(self,*a):
            super().complete(*a)
            save()
        def release(self,*a):
            super().release(*a)
            save()
    ledger=Ledger(BudgetLimits(warning_dollars=allocation*.8,hard_dollars=allocation))
    real=OpenAI(api_key=local_openai_api_key(root/'.env.local'),max_retries=0,timeout=30)
    active=None
    class Responses:
        def parse(self,**kw):
            assert kw['model']=='gpt-5.6-luna' and kw['reasoning']=={'effort':'low'} and kw['store'] is False
            active['request']={k:v for k,v in kw.items() if k!='text_format'}
            active['schema']=kw['text_format'].model_json_schema()
            active['dispatched_at']=datetime.now().astimezone().isoformat()
            save()  # Exact inputs/schema and reservation durable BEFORE dispatch.
            response=real.responses.parse(**kw)
            active['raw_response']=response.model_dump(mode='json')
            save()
            return response
    client=SimpleNamespace(responses=Responses())
    cases=json.loads((args.freeze/'cases.json').read_text())
    for case in cases['tuning']:
        active=dict(id=case['id'],expectation=case['expectation'])
        report['rows'].append(active)
        began=time.perf_counter()
        try:
            turn=ConversationTurn(speaker_name='F07 fictional contact',speaker_role='selected_contact',
                source='f07-fictional', content=case['contact_text'],display_order=1,
                timestamp=datetime.fromisoformat(cases['common']['timestamp']))
            if case['endpoint']=='guidance':
                memories=[RetrievedMemoryContext(memory_id=f'm{i}',revision_id=f'r{i}',excerpt=text,
                    memory_type='event_date',confidence='high',sensitivity_safe=True,rank=i+1,
                    relevance='eligible fictional candidate; assess current relevance') for i,text in enumerate(case['memories'])]
                snapshot=build_snapshot([turn],snapshot_id=1,generation=1,contact_id='fictional-f07',
                    retrieved_memories=memories,created_at=turn.timestamp)
                active['snapshot']=snapshot.model_dump(mode='json')
                result=interpret_guidance(snapshot,ledger=ledger,client=client,reasoning='low',live=False)
                active['validated_guidance']=result.model_dump(mode='json')
                active['display_status']='Fixed-input eligible output; paced UI display not measured'
            else:
                result,_=f06_structured_request(ExtractionOutput,json.loads(_extraction_payload([turn])),
                    EXTRACTION_INSTRUCTIONS,ledger=ledger,client=client,input_limit=9000,output_limit=2400,
                    model='gpt-5.6-luna',reasoning='low')
                active['validated_extraction']=result.model_dump(mode='json')
                active['display_status']='Schema-valid proposals only; not approved or persisted'
        except Exception as exc:
            active['error']=type(exc).__name__
            save()
            raise  # No retries, no fallback; preserve uncertain billing.
        finally:
            active['seconds']=time.perf_counter()-began
            save()
        print(case['id'],round(active['seconds'],2),round(report['committed_dollars'],6),flush=True)
    report['complete']=True
    save()


def prior_spend(freeze):
    """Each report's committed amount includes its own unresolved reservations."""
    total = 0.0
    for path in freeze.glob('api-*/report.json'):
        report = json.loads(path.read_text())
        amount = report['committed_dollars'] - report.get('prior_dollars', 0)
        if not math.isfinite(amount) or amount < 0:
            raise ValueError('Invalid prior ledger; reconcile before dispatch')
        total += amount
    return total


if __name__ == '__main__':
    main()
