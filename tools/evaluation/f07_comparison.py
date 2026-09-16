"""Frozen F07 144-response comparison; explicit prepare/run, no automatic retries."""
import argparse
from dataclasses import asdict
from datetime import datetime, timedelta, timezone
import hashlib
import importlib
import json
import math
import msvcrt
from pathlib import Path
import shutil
import subprocess
import sys
import time
import types
import zipfile
import zlib

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from tools.evaluation.f07_api import prior_spend


def package(name, source):
    module = types.ModuleType(name)
    module.__path__ = [str(source / 'conversation_copilot')]
    sys.modules[name] = module
    return types.SimpleNamespace(**{part: importlib.import_module(name+'.'+part)
        for part in ['models', 'interpretation', 'guidance', 'memory']})


def save_new(path, value):
    with path.open('x', encoding='utf8') as stream:
        json.dump(value, stream, indent=2)


def invoke(pkg, job, ledger, client):
    i, g, m = pkg.interpretation, pkg.guidance, pkg.memory
    if job['endpoint'] == 'extraction':
        return i.f06_structured_request(m.ExtractionOutput, job['payload'], m.EXTRACTION_INSTRUCTIONS,
            ledger=ledger, client=client, input_limit=9000, output_limit=2400,
            model='gpt-5.6-luna', reasoning='low')[0]
    instructions, expression = i.INTERPRETATION_INSTRUCTIONS, getattr(i, 'EXPRESSION_INSTRUCTIONS', '')
    if job['arm'] in {'none', 'movement', 'expressions'}:
        i.INTERPRETATION_INSTRUCTIONS += expression
        i.EXPRESSION_INSTRUCTIONS = ''  # Identical vocabulary across all three arms.
    try:
        return g.interpret_guidance(i.InterpretationSnapshot.model_validate(job['snapshot']),
            ledger=ledger,client=client,reasoning='low',live=False)
    finally:
        i.INTERPRETATION_INSTRUCTIONS = instructions
        if hasattr(i, 'EXPRESSION_INSTRUCTIONS'): i.EXPRESSION_INSTRUCTIONS = expression


def wire(kwargs):
    return {**{k:v for k,v in kwargs.items() if k != 'text_format'},
            'schema':kwargs['text_format'].model_json_schema()}


def attach_expressions(old_buckets, new_buckets):
    expressions={b.ended_at: b.model_dump(mode='json')['expressions'] for b in new_buckets}
    if set(expressions)!={datetime.fromisoformat(b['ended_at']) for b in old_buckets}:
        raise ValueError('Completed bucket boundaries differ; cannot form matched visual arms')
    return [dict(b,expressions=expressions[datetime.fromisoformat(b['ended_at'])]) for b in old_buckets]


def provenance():
    return dict(hashes={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in
        ['tools/evaluation/f07_comparison.py','tools/evaluation/f07_api.py']},
        git_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        git_status=subprocess.check_output(['git','status','--short'],cwd=ROOT,text=True))


def prepare(freeze, out, stage='before-p1'):
    resuming=out.exists()
    if resuming and (out/'jobs.json').exists(): raise ValueError('Preparation already frozen')
    out.mkdir(exist_ok=True)
    source = out/'candidate-source'/'conversation_copilot'
    if not resuming:
        source.mkdir(parents=True)
        for path in (ROOT/'conversation_copilot').rglob('*.py'):
            target = source/path.relative_to(ROOT/'conversation_copilot')
            target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(path,target)
    else:
        for name,digest in json.loads((out/'protocol.json').read_text())['sources'].items():
            if hashlib.sha256((out/name).read_bytes()).hexdigest()!=digest: raise ValueError('Frozen source changed')
    base=package('f07_base',freeze/'baseline-source')
    candidate=package('f07_candidate',out/'candidate-source')
    corpus=json.loads((freeze/'cases.json').read_text())
    bindings=json.loads((freeze/'source-bindings-and-baseline.json').read_text())['bindings']
    if not resuming: save_new(out/'protocol.json',dict(user_revision='Run comparison before P1, repeat after human testing.',
        status=('Provisional before-P1 comparison, not final held-out acceptance.' if stage=='before-p1'
                else 'After-human comparison; exposed families remain regression evidence.'),
        cases=corpus,bindings=bindings,requests=144,repeats=2,
        future='If used for corrections these families are exposed; later repeat is regression, with fresh equivalents needed for untouched held-out claims.',
        provenance=provenance(),
        sources={str(p.relative_to(out)):hashlib.sha256(p.read_bytes()).hexdigest() for p in source.rglob('*.py')}))
    FaceProcessor=importlib.import_module('f07_candidate.video').FaceProcessor
    import av
    import cv2
    stamp=datetime(2026,9,14,12,tzinfo=timezone.utc)
    visuals={}
    # Licensed media stay local; only bounded derived buckets leave this phase.
    with zipfile.ZipFile(ROOT/'build/datasets/DISFA/Videos_LeftCamera.zip') as archive:
        for binding in bindings:
            expected=f"LeftVideo{binding['subject']}_comp.avi"
            member=next(name for name in archive.namelist() if name.casefold()==expected.casefold())
            path=out/member
            if not path.exists():
                with archive.open(member) as src, path.open('xb') as dst: shutil.copyfileobj(src,dst)
            else:
                crc=0
                with path.open('rb') as stream:
                    for block in iter(lambda:stream.read(1024*1024),b''): crc=zlib.crc32(block,crc)
                if path.stat().st_size!=archive.getinfo(member).file_size or crc!=archive.getinfo(member).CRC:
                    raise ValueError('Existing extraction differs from source archive')
            old=base.interpretation.VisualAggregator()
            new=candidate.interpretation.VisualAggregator()
            processor=FaceProcessor()
            count=available=0
            try:
                with av.open(str(path)) as container:
                    for index,frame in enumerate(container.decode(video=0)):
                        if index>=binding['end_frame']: break
                        pts=float(frame.pts*frame.time_base)
                        if abs(pts-index/20)>.001: raise ValueError('Label/PTS mismatch')
                        if index<binding['start_frame']: continue
                        result=processor.process(cv2.cvtColor(frame.to_ndarray(format='bgr24'),cv2.COLOR_BGR2BGRA),round(pts*1000))
                        at=stamp+timedelta(seconds=pts)
                        old.add(result.signal,at); new.add(result.signal,at)
                        count+=1; available+=int(result.signal is not None)
            finally: processor.close()
            if count != binding['end_frame']-binding['start_frame']: raise ValueError('Truncated clip')
            old_buckets=[b.model_dump(mode='json') for b in old.buckets()]
            improved=attach_expressions(old_buckets,new.buckets())
            visuals[binding['id']]=dict(movement=old_buckets,expressions=improved,
                checkpoint=(stamp+timedelta(seconds=binding['checkpoint_frame']/20)).isoformat(),
                processed=count,available=available,video_sha256=hashlib.file_digest(path.open('rb'),'sha256').hexdigest())
            print('prepared',binding['id'],count,flush=True)
    save_new(out/'visual-buckets.json',visuals)
    jobs=[]
    for case in corpus['held_visual']:
        record=visuals[case['id']]
        for repeat in [1,2]:
            for arm in ['none','movement','expressions','production']:
                pkg=base if arm=='production' else candidate
                when=datetime.fromisoformat(record['checkpoint'])
                turn=pkg.models.ConversationTurn(speaker_name='F07 fictional contact',speaker_role='selected_contact',
                    source='authored-dialogue-paired-with-DISFA',content=case['contact_text'],timestamp=when,display_order=1)
                raw=[] if arm=='none' else record['expressions' if arm=='expressions' else 'movement']
                snapshot=pkg.interpretation.build_snapshot([turn],snapshot_id=1,generation=1,
                    created_at=when,contact_id='fictional-f07',visual_buckets=[pkg.interpretation.VisualBucket.model_validate(b) for b in raw])
                jobs.append(dict(id=case['id'],repeat=repeat,arm=arm,endpoint='guidance',snapshot=snapshot.model_dump(mode='json')))
    for case in corpus['held_semantic']:
        for repeat in [1,2]:
            for arm,pkg in [('production',base),('candidate',candidate)]:
                turn=pkg.models.ConversationTurn(speaker_name='F07 fictional contact',speaker_role='selected_contact',
                    source='f07-fictional',content=case['contact_text'],timestamp=stamp,display_order=1)
                job=dict(id=case['id'],repeat=repeat,arm=arm,endpoint=case['endpoint'])
                if case['endpoint']=='extraction': job['payload']=json.loads(pkg.memory._extraction_payload([turn]))
                else:
                    memories=[pkg.interpretation.RetrievedMemoryContext(memory_id=f'm{i}',revision_id=f'r{i}',excerpt=text,
                        memory_type='event_date',confidence='high',sensitivity_safe=True,rank=i+1,
                        relevance='eligible fictional candidate; assess current relevance') for i,text in enumerate(case['memories'])]
                    job['snapshot']=pkg.interpretation.build_snapshot([turn],snapshot_id=1,generation=1,
                        created_at=stamp,contact_id='fictional-f07',retrieved_memories=memories).model_dump(mode='json')
                jobs.append(job)
    class Captured(Exception): pass
    class Capture:
        def parse(self,**kw):
            job['request']=wire(kw)
            raise Captured()
    for job in jobs:
        pkg=base if job['arm']=='production' else candidate
        ledger=pkg.interpretation.UsageLedger(pkg.interpretation.BudgetLimits(warning_dollars=1,hard_dollars=2))
        try: invoke(pkg,job,ledger,types.SimpleNamespace(responses=Capture()))
        except Captured: pass  # Offline only, never a provider dispatch.
        if 'request' not in job: raise ValueError('Missing frozen request')
    assert len(jobs)==144
    for index in range(0,96,4):
        group=jobs[index:index+3]
        assert len({j['request']['instructions'] for j in group})==1
        assert all('x may append expressions:' in j['request']['instructions'] for j in group)
        inputs=[json.loads(j['request']['input']) for j in group]
        assert all({k:v for k,v in p.items() if k!='x'}=={k:v for k,v in inputs[0].items() if k!='x'} for p in inputs)
        assert [row[:8] for row in inputs[1]['x']]==[row[:8] for row in inputs[2]['x']]
        assert any(len(row)>8 and isinstance(row[8],list) and len(row[8])==3 for row in inputs[2]['x']), 'Expression arm has no expression summary'
        assert inputs[1]['x']!=inputs[2]['x'], 'Visual arms are accidentally identical'
    save_new(out/'jobs.json',jobs)
    print('Frozen 144 exact requests; no API calls.',flush=True)


def run(freeze,out,later_reserved=.13):
    from openai import OpenAI
    lock=(freeze/'api-run.lock').open('a+b'); lock.write(b'0'); lock.flush(); lock.seek(0)
    msvcrt.locking(lock.fileno(),msvcrt.LK_NBLCK,1)
    authorization=json.loads((freeze/'authorization.json').read_text())
    if not math.isfinite(authorization['cap_usd']) or authorization['cap_usd']<=0:
        raise ValueError('Invalid authorized cap')
    assert authorization['model']=='gpt-5.6-luna' and authorization['effort']=='low'
    prior=prior_spend(freeze)
    if not math.isfinite(later_reserved) or later_reserved<0 or later_reserved>authorization['cap_usd']:
        raise ValueError('Invalid later-work reserve')
    # The after-human run can explicitly draw down this reserve; the aggregate cap never resets.
    remaining=authorization['cap_usd']-prior-later_reserved
    if remaining<=0: raise ValueError('No remaining before-P1 allocation')
    target=out/'report.json'
    if target.exists(): raise ValueError('Never overwrite/resume paid responses implicitly')
    jobs=json.loads((out/'jobs.json').read_text())
    for name,digest in json.loads((out/'protocol.json').read_text())['sources'].items():
        if hashlib.sha256((out/name).read_bytes()).hexdigest()!=digest: raise ValueError('Frozen source changed')
    base=package('f07_base',freeze/'baseline-source'); candidate=package('f07_candidate',out/'candidate-source')
    UsageLedger=candidate.interpretation.UsageLedger
    BudgetLimits=candidate.interpretation.BudgetLimits
    local_openai_api_key=candidate.interpretation.local_openai_api_key
    protocol=json.loads((out/'protocol.json').read_text())
    report=dict(prior_dollars=prior,rows=[],authorization=authorization,later_reserved_usd=later_reserved,
        mode=protocol['status'],exposure=protocol['future'],provenance=provenance(),
        jobs_sha256=hashlib.sha256((out/'jobs.json').read_bytes()).hexdigest(),
        limitations='Controlled hybrid: baseline completed movement buckets plus matching candidate expressions. Excludes candidate partial-bucket UI path. Fictional dialogue with DISFA reactions, not real aligned speech. Supplied candidates bypass retrieval. Fixed-checkpoint display reducer, not actual UI latency or human usefulness.')
    def save():
        report.update(committed_dollars=prior+ledger.committed_dollars,usage=[asdict(r) for r in ledger.records])
        tmp=target.with_suffix('.tmp'); tmp.write_text(json.dumps(report,indent=2),encoding='utf8'); tmp.replace(target)
    class Ledger(UsageLedger):
        def reserve(self,*a,**k):
            r=super().reserve(*a,**k); save(); return r
        def complete(self,*a): super().complete(*a); save()
        def release(self,*a): super().release(*a); save()
    ledger=Ledger(BudgetLimits(warning_dollars=remaining*.8,hard_dollars=remaining))
    real=OpenAI(api_key=local_openai_api_key(ROOT/'.env.local'),max_retries=0,timeout=30)
    class Responses:
        def parse(self,**kw):
            if wire(kw)!=job['request']: raise ValueError('Request changed after freeze')
            active['dispatched_at']=datetime.now(timezone.utc).isoformat(); save()
            response=real.responses.parse(**kw)
            active['raw_response']=response.model_dump(mode='json',warnings=False); save()
            return response
    client=types.SimpleNamespace(responses=Responses())
    for index,job in enumerate(jobs):
        active={k:job[k] for k in ['id','repeat','arm','endpoint']}; report['rows'].append(active)
        began=time.perf_counter(); pkg=base if job['arm']=='production' else candidate
        try:
            result=invoke(pkg,job,ledger,client)
            active['validated']=result.model_dump(mode='json')
            if job['endpoint']=='guidance':
                display=pkg.guidance.GuidanceDisplay(); display.offer(result,0)
                active['displayed']={k:[v.candidate.model_dump(mode='json') for v in display.visible(k)] for k in pkg.guidance.CATEGORIES}
        except Exception as exc:
            active['error']=type(exc).__name__; save()
            if type(exc).__name__ in {'InterpretationBudgetExceeded','AuthenticationError','PermissionDeniedError'}: break
            # Preserve this failed request in denominators; next independent job is not a retry.
        finally: active['seconds']=time.perf_counter()-began; save()
        print(index+1,job['id'],job['arm'],round(report['committed_dollars'],6),flush=True)
    report['complete']=len(report['rows'])==144 and all('dispatched_at' in row for row in report['rows'])
    report['completion_counts']=[dict(arm=arm,repeat=repeat,planned=sum(j['arm']==arm and j['repeat']==repeat for j in jobs),
        dispatched=sum(x['arm']==arm and x['repeat']==repeat and 'dispatched_at'in x for x in report['rows']),
        validated=sum(x['arm']==arm and x['repeat']==repeat and 'validated'in x for x in report['rows']))
        for arm in sorted({j['arm'] for j in jobs}) for repeat in [1,2]]
    save()


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('phase',choices=['prepare','run'])
    parser.add_argument('--freeze',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--later-reserve-usd',type=float,default=.13,
        help='Run only: budget left for later work; explicitly reduce for the after-human run, never resets total cap.')
    parser.add_argument('--stage',choices=['before-p1','after-human'],default='before-p1',help='Prepare only: labels the new frozen comparison.')
    args=parser.parse_args()
    if not args.freeze.resolve().is_relative_to(ROOT/'build') or args.output.resolve().parent!=args.freeze.resolve() or not args.output.name.startswith('api-'):
        parser.error('Use original ignored freeze and an api-* child directory')
    if args.phase=='prepare': prepare(args.freeze,args.output,args.stage)
    else: run(args.freeze,args.output,args.later_reserve_usd)
