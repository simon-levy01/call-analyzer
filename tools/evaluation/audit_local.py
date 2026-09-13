"""Revalidate saved output offline; structural checks are not a semantic quality score."""
import json
from unittest.mock import patch
from local_models import OUT, load, GuidanceOutput
from conversation_copilot.guidance import interpret_guidance
from conversation_copilot.interpretation import InterpretationSnapshot

cases={c['id']:c for name in ('corpus','coverage-cases','new-cases') for c in load(OUT/(name+'.json'))}
audit=[]
for path in sorted(OUT.glob('*.jsonl')):
    for line in path.read_text(encoding='utf8').splitlines():
        row=json.loads(line);case=cases.get(row.get('id'));raw=row.get('raw')
        if not case or not raw:continue
        if case['schema']=='CloudAskOutput':
            data=json.loads(case['request']['input']);allowed={e['id'] for e in data['evidence']}
            audit.append({'run':path.stem,'id':row['id'],'schema':'CloudAskOutput','invalid_source_ids':sorted(set(raw.get('source_ids',[]))-allowed)})
            continue
        if case['schema']!='GuidanceOutput':continue
        data=json.loads(case['request']['input']);allowed={m[0] for m in data.get('m',[])};turns=set(data['turn_ids'])
        styles={m[0] for m in data.get('m',[]) if m[2] in ('communication_style','relationship_preference')}
        item={'run':path.stem,'id':row['id'],'violations':[]}
        for category in ('remember','replies','follow_up'):
            for c in raw.get(category,[]):
                reason=[]
                if not set(c.get('memory_ids',[]))<=allowed:reason.append('unavailable memory ID')
                if not set(c.get('turn_ids',[]))<=turns:reason.append('unavailable turn ID')
                if not set(c.get('preference_ids',[]))<=styles:reason.append('unavailable preference ID')
                if not 1<=len(c.get('turn_ids',[]))+len(c.get('memory_ids',[]))<=3:reason.append('source count outside 1–3')
                if category=='remember' and not c.get('memory_ids'):reason.append('reminder has no approved memory ID')
                if reason:item['violations'].append({'category':category,'text':c['text'],'reason':reason})
        if case.get('snapshot'):
            try:
                with patch('conversation_copilot.guidance.f06_structured_request',return_value=(GuidanceOutput.model_validate(raw),None)):
                    item['current_guarded']=interpret_guidance(InterpretationSnapshot.model_validate(case['snapshot']),ledger=None,live=False).model_dump(mode='json')
            except Exception as e:item['guard_error']=str(e)
        if row['id'].startswith('current/frozen/'):
            targets={'vague_job_user_script':'McDonald','prize':'first prize','exam_stress':'chemistry'}
            scenario=row['id'].split('/')[2];needle=targets.get(scenario)
            expected={m[0] for m in data.get('m',[]) if needle and needle.lower() in m[1].lower()}
            selected={mid for c in raw.get('remember',[]) for mid in c.get('memory_ids',[])}
            item['memory_check']={'positive':bool(needle),'expected':sorted(expected),'selected':sorted(selected),'exact':selected==expected,'target_found':bool(expected & selected),'extra':bool(selected-expected)}
            referenced={mid for category in ('remember','replies','follow_up') for candidate in raw.get(category,[]) for mid in candidate.get('memory_ids',[])}
            item['memory_check']['extraneous_event_ids_anywhere']=sorted(referenced-expected-styles)
        audit.append(item)
(OUT/'offline-validation.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf8')
print('Offline validation complete:',len(audit),'saved responses; no inference.')
