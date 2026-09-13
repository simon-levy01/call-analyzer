"""Mechanical indicators and readable paired audit, not an LLM quality score."""
import json
import statistics
from pathlib import Path
from local_models import OUT, load, readable_turns

corpus={c['id']:c for c in load(OUT/'corpus.json')}
if (OUT/'new-cases.json').exists():corpus.update({c['id']:c for c in load(OUT/'new-cases.json')})
if (OUT/'coverage-cases.json').exists():corpus.update({c['id']:c for c in load(OUT/'coverage-cases.json')})
summaries={};audit=[]
for path in sorted(OUT.glob('*.jsonl')):
    if 'visible' in path.name:continue
    rows=[json.loads(line) for line in path.read_text(encoding='utf8').splitlines()]
    if not rows or 'id' not in rows[0]:continue
    stat={'requests':len(rows),'schema_valid':0,'evidence_valid':0,'paired_memory_agreement':0,'memory_pairs':0,'empty_replies':0,'mechanical_topic_failures':0,'new_memory_expected_pass':0,'new_memory_expected_count':0}
    latency=[];warm=[]
    for row in rows:
        c=corpus.get(row['id'],{});raw=row.get('raw');valid=bool(row.get('parsed'))
        if row.get('seconds') is not None:latency.append(row['seconds'])
        if row.get('seconds') is not None and row.get('response',{}).get('load_duration',0)<1e9:warm.append(row['seconds'])
        stat['schema_valid']+=valid
        evidence_ok=not row.get('invalid_evidence') and not row.get('guard_error')
        if valid and c.get('schema')=='CloudAskOutput':
            allowed={e['id'] for e in json.loads(c['request']['input'])['evidence']}
            evidence_ok=evidence_ok and set(raw.get('source_ids',[]))<=allowed
        if valid and evidence_ok:stat['evidence_valid']+=1
        if raw and c.get('schema')=='GuidanceOutput':
            memory=lambda o:{i for m in o.get('remember',[]) for i in m.get('memory_ids',[])}
            if c.get('luna_raw'):
                stat['memory_pairs']+=1;stat['paired_memory_agreement']+=memory(raw)==memory(c['luna_raw'])
            if c.get('expected_memory_ids') is not None:
                stat['new_memory_expected_count']+=1;stat['new_memory_expected_pass']+=memory(raw)==set(c['expected_memory_ids'])
            stat['empty_replies']+=not raw.get('replies')
            payload=json.loads(c['request']['input']);transcript=payload.get('t',[])
            last_contact=next((t for t in reversed(readable_turns(payload)) if ' — CONTACT: ' in t),'')
            if 'Changing the subject:' in last_contact:
                negative={'tense_negative','sad_low_energy'}
                stat['mechanical_topic_failures']+=bool(raw.get('remember')) or any(t['kind'] in negative for t in raw.get('interpretation',{}).get('tones',[]))
            audit.append({'run':path.stem,'id':row['id'],'expected':c.get('expected'),
                'transcript':transcript,'memory_candidates':payload.get('m',[]),'luna':c.get('luna_raw'),
                'local':raw,'validation_error':row.get('validation_error'),'guard_error':row.get('guard_error'),'seconds':row.get('seconds')})
    if latency:stat.update(median_seconds=statistics.median(latency),p95_seconds=sorted(latency)[min(len(latency)-1,int(.95*len(latency)))])
    if warm:stat.update(warm_median_seconds=statistics.median(warm),warm_samples=len(warm))
    stat['by_schema']={}
    for schema in sorted({r.get('schema') for r in rows if r.get('schema')}):
        group=[r for r in rows if r.get('schema')==schema]
        times=[r['seconds'] for r in group if r.get('seconds') is not None]
        baseline=[corpus[r['id']]['luna_seconds'] for r in group if corpus.get(r['id'],{}).get('luna_seconds') is not None]
        stat['by_schema'][schema]={'requests':len(group),'valid':sum(bool(r.get('parsed')) for r in group),
            'median_seconds':statistics.median(times) if times else None,'saved_luna_median_seconds':statistics.median(baseline) if baseline else None}
    summaries[path.stem]=stat
(OUT/'mechanical-metrics.json').write_text(json.dumps(summaries,indent=2),encoding='utf8')
(OUT/'paired-audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(summaries,indent=2))
