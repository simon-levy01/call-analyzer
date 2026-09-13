"""Offline Ollama comparisons. Never imports a paid runner or reads API credentials."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from openai.lib._pydantic import to_strict_json_schema
from conversation_copilot.guidance import GuidanceOutput
from conversation_copilot.memory import ExtractionOutput, SummaryOutput
from conversation_copilot.ask_memory import CloudAskOutput

OUT = Path(os.environ.get('CALL_HELPER_LOCAL_EVAL_DIR',ROOT/'build/local-model-comparison-20260913'))
BASE = 'http://127.0.0.1:11436'
SCHEMAS = {s.__name__: s for s in (GuidanceOutput, ExtractionOutput, SummaryOutput, CloudAskOutput)}

def rpc(path, data=None, timeout=240):
    assert path in {'tags', 'show', 'chat', 'ps', 'version'}, 'Only local inference/metadata operations allowed'
    request = urllib.request.Request(BASE+'/api/'+path,
        data=json.dumps(data).encode() if data is not None else None,
        headers={'Content-Type': 'application/json'})
    # Explicit loopback URL; no redirects to external providers.
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, *args, **kwargs):
            raise RuntimeError('Local evaluation must not follow HTTP redirects')
    with urllib.request.build_opener(urllib.request.ProxyHandler({}),NoRedirect).open(request, timeout=timeout) as response:
        return json.load(response)

def load(path):
    return json.loads(Path(path).read_text(encoding='utf8'))

def readable_turns(data):
    speaker=None
    lines=[]
    for n,t in zip(data['turn_ids'],data['t']):
        if t[0] is not None: speaker=t[0]
        if speaker not in ('u','c'):raise ValueError('Compact transcript has no initial speaker')
        lines.append(f"Turn {n} — {'USER' if speaker=='u' else 'CONTACT'}: {t[2]}")
    return lines

def prepare():
    OUT.mkdir(parents=True,exist_ok=True)
    source = ROOT/'build/luna-comparison-20260913'
    historical = {c['id']: c for c in load(source/'corpus.json')}
    repairs = load(source/'repair/results.json')['rows']
    rows = []
    for row in load(source/'results.json')['rows']:
        if row.get('response_model','').startswith('gpt-5.6-terra') or '/gpt-5.6-terra/' in row['id']:
            continue
        request = row.get('request')
        if not request:
            continue
        old = historical.get(row['id'].removeprefix('current/'), {})
        baseline = row
        if row.get('error'):
            matches = [r for r in repairs if row['id'] in r.get('id','')]
            if matches: baseline = matches[0]
        rows.append({'id': row['id'], 'schema': row['schema'], 'request': request,
            'snapshot': row.get('snapshot',old.get('snapshot')),
            'expected': row.get('expected',old.get('expected')),
            'luna_raw': baseline.get('raw'), 'luna_validated': baseline.get('output'),
            'luna_seconds': baseline.get('seconds'), 'luna_usage': baseline.get('api_usage'),
            'baseline_source':'build/luna-comparison-20260913/'+('results.json' if baseline is row else 'repair/results.json')})
    (OUT/'corpus.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8')
    return rows

def infer(model, case, *, think=False, cpu=False, readable=False, compact=False, brief=False, output_multiplier=1):
    schema = SCHEMAS[case['schema']]
    q = case['request']
    body = q['input'] if isinstance(q['input'],str) else json.dumps(q['input'],ensure_ascii=False)
    spec = to_strict_json_schema(schema)
    system = q['instructions']
    # Schema is a format constraint and is also visible to the model, like the API's response format.
    user = body+'\n\nReturn JSON matching this schema:\n'+json.dumps(spec,separators=(',',':'))
    if compact and case['schema']=='GuidanceOutput':
        data=json.loads(body)
        system=(Path(__file__).parent/'local_guidance_prompt.txt').read_text(encoding='utf8')
        readable_data={
            'transcript_oldest_to_newest':readable_turns(data),
            'approved_memories':[dict(zip(('id','content','type','confidence','retrieval_reason'),m)) for m in data.get('m',[])],
            'latest_turn_id':data.get('latest_turn_id',data['turn_ids'][-1]),
            'reply_to_turn_id':data.get('reply_to_turn_id'),
            'user_spoke_last':data.get('user_spoke_last',data.get('reply_to_turn_id') is None),
            'vocal_observations':data.get('v',[]),'visual_observations':data.get('x',[]),
            'observation_format':'v=[turn_index,available,duration,relative_energy,voiced_ratio,words_per_voiced_second,gap,overlaps_user,reason]; x=[seconds_from_newest,availability,reliability,face,smile,brow,eye,mouth]',
        }
        user=json.dumps(readable_data,ensure_ascii=False)+'\nReturn JSON matching this schema:\n'+json.dumps(spec,separators=(',',':'))
    if readable and case['schema']=='GuidanceOutput':
        data=json.loads(body)
        lines=readable_turns(data)
        user+='\n\nREADABLE TRANSCRIPT (same evidence, oldest to newest):\n'+'\n'.join(lines)
        user+='\nThe FINAL line above is the current point. If the user already responded, suggest their next move or waiting, never answer them as the contact. A new topic ends old emotional interpretations and reminders. A stated boundary means do not ask about that topic again. Generic stress alone must not select any memory. Keep useful indirect memory links tentative. Return only the required JSON.'
    if brief and case['schema']=='GuidanceOutput':
        system+='\nBe concise: each hypothesis at most 12 words; each evidence explanation at most 16 words. Set the optional overall explanation to null. Give one reply and at most one follow-up. Keep the factual details of relevant memory reminders. Never fill empty categories.'
    maximum=round(q['max_output_tokens']*output_multiplier)
    ctx = 16384 if (len(system)+len(user))/3+maximum>7600 else 8192
    info = rpc('show',{'model':model})
    if ':cloud' in model or info.get('remote_model') or info.get('remote_host'):
        raise ValueError('Only downloaded local weights are allowed in this evaluation')
    model_context = min((v for k,v in info.get('model_info',{}).items() if k.endswith('.context_length')),default=ctx)
    if model_context < ctx:
        raise ValueError(f'Model context {model_context} below required test context {ctx}; refusing silent truncation')
    options={'num_ctx':ctx,'num_predict':maximum,'temperature':0,'seed':42}
    if cpu: options['num_gpu']=0
    request={'model':model,'messages':[{'role':'system','content':system},{'role':'user','content':user}],
        'format':spec,'stream':False,'keep_alive':'15m','options':options}
    if 'thinking' in info.get('capabilities',[]): request['think']=think
    start=time.perf_counter()
    response=rpc('chat',request)
    result={'seconds':time.perf_counter()-start,'request':request,'response':response,
        'local_model':model,'api_cost':0}
    result['placement']=rpc('ps')
    content=response['message']['content']
    try:
        if response.get('done_reason')=='length': raise ValueError('Output reached token limit')
        result['raw']=json.loads(content)
        result['parsed']=schema.model_validate(result['raw']).model_dump(mode='json')
    except Exception as exc: result['validation_error']=str(exc)
    payload=json.loads(body)
    if result.get('parsed') and case['schema']=='GuidanceOutput':
        allowed={m[0] for m in payload.get('m',[])}
        styles={m[0] for m in payload.get('m',[]) if m[2] in {'communication_style','relationship_preference'}}
        turns=set(payload.get('turn_ids',[]))
        result['invalid_evidence']=[{'category':k,'text':item['text']} for k in ('replies','remember','follow_up')
            for item in result['parsed'][k] if not set(item['memory_ids'])<=allowed or not set(item['turn_ids'])<=turns or not set(item['preference_ids'])<=styles]
        if case.get('snapshot'):
            from unittest.mock import patch
            from conversation_copilot.guidance import interpret_guidance
            from conversation_copilot.interpretation import InterpretationSnapshot
            try:
                with patch('conversation_copilot.guidance.f06_structured_request',return_value=(schema.model_validate(result['raw']),None)):
                    result['current_guarded']=interpret_guidance(InterpretationSnapshot.model_validate(case['snapshot']),ledger=None,live=False).model_dump(mode='json')
            except Exception as exc: result['guard_error']=str(exc)
    return result

def run(args):
    corpus=load(OUT/'corpus.json') if (OUT/'corpus.json').exists() else prepare()
    if args.phase=='screen':
        corpus=[c for c in corpus if c['id'].startswith('current/frozen/')]
    elif args.phase=='new': corpus=load(OUT/'new-cases.json')
    elif args.phase=='coverage': corpus=load(OUT/'coverage-cases.json')
    if args.limit: corpus=corpus[:args.limit]
    target=OUT/(args.model.replace(':','_').replace('/','_')+'-'+args.phase+('-think' if args.think else '')+('-cpu' if args.cpu else '')+('-readable' if args.readable else '')+('-compact' if args.compact else '')+('-brief' if args.brief else '')+(f'-out{args.output_multiplier:g}' if args.output_multiplier!=1 else '')+'.jsonl')
    done={r['id'] for r in [json.loads(line) for line in target.read_text(encoding='utf8').splitlines()]} if target.exists() else set()
    for i,case in enumerate(corpus):
        if case['id'] in done: continue
        row={'id':case['id'],'schema':case['schema'],'local_model':args.model,'phase':args.phase}
        try: row.update(infer(args.model,case,think=args.think,cpu=args.cpu,readable=args.readable,compact=args.compact,brief=args.brief,output_multiplier=args.output_multiplier))
        except Exception as exc: row['error']=type(exc).__name__+': '+str(exc)
        with target.open('a',encoding='utf8') as stream: stream.write(json.dumps(row,ensure_ascii=False)+'\n')
        print(args.model,args.phase,i+1,len(corpus),case['id'],round(row.get('seconds',0),2),row.get('error',row.get('validation_error','OK'))[:150],flush=True)
    (target.with_suffix('.done')).write_text('complete',encoding='utf8')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--model');p.add_argument('--phase',choices=['screen','full','new','coverage'],default='screen')
    p.add_argument('--limit',type=int);p.add_argument('--think',action='store_true');p.add_argument('--cpu',action='store_true');p.add_argument('--readable',action='store_true');p.add_argument('--compact',action='store_true');p.add_argument('--prepare',action='store_true')
    p.add_argument('--output-multiplier',type=float,default=1)
    p.add_argument('--brief',action='store_true')
    args=p.parse_args()
    if args.prepare: print('Prepared',len(prepare()),'historical paired cases')
    elif args.model: run(args)
    else: p.error('--model or --prepare is required')
