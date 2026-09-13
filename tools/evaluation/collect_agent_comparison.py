"""Collect saved agent answers for the existing offline audit; never runs inference."""
import hashlib
import json
import os
import shutil
from pathlib import Path
from local_models import ROOT, SCHEMAS, load

source = ROOT/'build/local-model-comparison-20260913'
out = Path(os.environ.get('CALL_HELPER_AGENT_EVAL_DIR', ROOT/'build/agent-api-expanded-20260913'))
for name in ('corpus.json', 'coverage-cases.json', 'new-cases.json'):
    shutil.copyfile(source/name, out/name)
cases = {c['id']: c for name in ('corpus', 'new-cases', 'coverage-cases') for c in load(source/(name+'.json'))}
manifest = load(out/'manifest.json')
progress = {}
recorded = []
for case in cases.values():
    if 'luna_raw' not in case:
        continue
    row = {'id': case['id'], 'schema': case['schema'], 'method': 'recorded-api',
           'raw': case['luna_raw'], 'baseline_source': case.get('baseline_source'),
           'seconds': case.get('luna_seconds'), 'usage': case.get('luna_usage')}
    try:
        row['parsed'] = SCHEMAS[case['schema']].model_validate(row['raw']).model_dump(mode='json')
    except Exception as exc:
        row['validation_error'] = str(exc)
    recorded.append(row)
(out/'luna-recorded-api-collected.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in recorded), encoding='utf8')
progress['recorded_api'] = {'completed': len(recorded), 'schema_valid': sum('parsed' in r for r in recorded)}
for model, method, prefix in (('luna', 'isolated', 'luna-isolated'), ('luna', 'batched-pilot', 'luna'), ('terra', 'isolated', 'terra-isolated')):
    rows = []
    selected = [e for e in manifest if method != 'batched-pilot' or not e['source_id'].startswith('new/')]
    for entry in selected:
        path = out/f"{prefix}-{entry['case_id']}.json"
        if not path.exists():
            continue
        case = cases[entry['source_id']]
        text = path.read_text(encoding='utf8')
        row = {'id':case['id'], 'case_id':entry['case_id'], 'schema':case['schema'], 'method':method,
               'configured_model':f'gpt-5.6-{model}', 'reasoning':'low', 'fork_turns':'none',
               'file_sha256':hashlib.sha256(text.encode()).hexdigest()}
        try:
            row['raw'] = json.loads(text)
            row['parsed'] = SCHEMAS[case['schema']].model_validate(row['raw']).model_dump(mode='json')
        except Exception as exc:
            row['validation_error'] = str(exc)
        rows.append(row)
    if rows:
        (out/f'{model}-{method}-collected.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows), encoding='utf8')
    progress[f'{model}-{method}'] = {'completed':len(rows), 'schema_valid':sum('parsed' in r for r in rows),
                       'missing_case_ids':[e['case_id'] for e in selected if not (out/f"{prefix}-{e['case_id']}.json").exists()]}
api_path = out/'new-luna-api.json'
if api_path.exists():
    api = load(api_path)
    (out/'new-luna-api-collected.jsonl').write_text(''.join(json.dumps({
        'id':r['id'], 'raw':r.get('raw'), 'parsed':r.get('raw'), 'seconds':r.get('seconds'),
        'request':r.get('request'), 'response':r.get('raw_response'), 'method':'api', 'error':r.get('error'),
    },ensure_ascii=False)+'\n' for r in api['rows']), encoding='utf8')
    progress['new_api'] = {'completed':sum('raw' in r for r in api['rows']), 'cost':api['cost_estimate']}
(out/'collection-progress.json').write_text(json.dumps(progress,indent=2), encoding='utf8')
print({k:{x:y for x,y in v.items() if x!='missing_case_ids'} for k,v in progress.items()})
