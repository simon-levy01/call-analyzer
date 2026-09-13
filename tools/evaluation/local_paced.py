"""Real wall-clock local inference through the production adaptive coordinator."""
import argparse
import json
import threading
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

from local_models import ROOT, OUT, infer, load
from conversation_copilot import guidance
from conversation_copilot.interpretation import InterpretationCoordinator, InterpretationSnapshot, RetrievedMemoryContext, build_snapshot
from conversation_copilot.memory import MemoryStore, default_database_path, memory_retrieval_inputs, memory_semantic_input
from conversation_copilot.models import ConversationTurn, SpeakerRole
from conversation_copilot.semantic import default_cache_dir

def run(model, name, *, recorded=None, script=None, memories=None, compact=False, readable=False, brief=False):
    if compact: name+='-compact'
    if readable: name+='-readable'
    if brief: name+='-brief'
    target=OUT/(model.replace(':','_')+'-paced-'+name+'.json')
    assert not target.exists(), 'Never overwrite a completed or partial replay'
    report={'model':model,'case':name,'feed':[],'requests':[],'events':[],'api_cost':0}
    lock=threading.RLock()
    def save():
        with lock: target.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
    latest=[0];boundary=[0];start=[0.0];active=threading.local()
    def local_request(schema,payload,instructions,**kw):
        row=active.row
        case={'schema':schema.__name__,'request':{'input':json.dumps(payload,ensure_ascii=False),
            'instructions':instructions,'max_output_tokens':kw['output_limit']}}
        row['local']=infer(model,case,compact=compact,readable=readable,brief=brief)
        save()
        if row['local'].get('validation_error'): raise ValueError(row['local']['validation_error'])
        return schema.model_validate(row['local']['raw']),None
    original=guidance.f06_structured_request;guidance.f06_structured_request=local_request
    def analyze(snap):
        n=max(t.display_order for t in snap.turns)
        row={'through_turn':n,'request_at':time.perf_counter()-start[0],'snapshot':snap.model_dump(mode='json')}
        report['requests'].append(row);active.row=row;save()
        try:
            result=guidance.interpret_guidance(snap,ledger=None,live=False,is_current=lambda s:n>=boundary[0])
            row['validated']=result.model_dump(mode='json')
            result=guidance.suppress_outdated_replies(result,n,latest[0]);row['delivered']=result.model_dump(mode='json')
            return result
        except Exception as exc: row['error']=str(exc);raise
        finally:
            row['response_at']=time.perf_counter()-start[0];row['latest_turn_on_return']=latest[0];save()
            print(name,n,round(row['response_at']-row['request_at'],2),row.get('error','OK')[:120],flush=True)
    offers=[];turn_feed=[];stop_seconds=None
    if recorded:
        events=[json.loads(l) for l in Path(recorded).read_text(encoding='utf8').splitlines()]
        base=datetime.fromisoformat(next(e['at'] for e in events if e['event']=='create_record.result'))
        sec=lambda e:(datetime.fromisoformat(e['at'])-base).total_seconds()
        turn_feed=[(sec(e),e['result']) for e in events if e['event']=='_conversation_turn_from_audio.result']
        stop_seconds=sec(next(e for e in events if e['event']=='stop_record.start'))
        for e in events:
            if e['event']!='offer.start':continue
            old=InterpretationSnapshot.model_validate(e['args'][0]);n=max(t.display_order for t in old.turns)
            full=[ConversationTurn.model_validate(t) for _,t in turn_feed if t['display_order']<=n]
            offers.append((sec(e),build_snapshot(full,snapshot_id=old.snapshot_id,generation=old.generation,
                contact_id=old.contact_id,retrieved_memories=old.memories,vocal_observations=old.vocal_observations,visual_buckets=old.visual_buckets)))
        report['method']='Original finalized-turn timing, production coordinator, preserved historical memory candidates and structured observations; not fresh retrieval'
    else:
        report['method']='One finalized turn every 4 seconds, fresh local BGE retrieval and production coordinator'
    class Store(MemoryStore):
        @property
        def semantic_cache_dir(self):return default_cache_dir(default_database_path())
    try:
        with Store(':memory:') as store:
            if not recorded:
                contact=store.create_contact('Maya')
                for m in memories:store.create_memory(contact.id,m,memory_type='event_date')
                store.backfill_semantic_embeddings()
            generation=offers[0][1].generation if offers else 1
            start[0]=time.perf_counter()
            coordinator=InterpretationCoordinator(analyze,generation=generation,first_request_at=time.monotonic()+12,adaptive_cadence=True)
            index=0;ti=0;visible=[];stopped=False;count=len(offers) if recorded else len(script)
            while index<count or coordinator.snapshot().in_flight or coordinator.snapshot().pending_snapshot_id is not None:
                elapsed=time.perf_counter()-start[0]
                while ti<len(turn_feed) and turn_feed[ti][0]<=elapsed:
                    latest[0]=turn_feed[ti][1]['display_order'];ti+=1
                due=offers[index][0] if recorded and index<count else index*4
                if index<count and elapsed>=due:
                    if recorded: snap=offers[index][1];retrieval=None
                    else:
                        role,text=script[index];n=index+1;latest[0]=n
                        visible.append(ConversationTurn(speaker_name='Alex' if role=='user' else 'Maya',speaker_role=SpeakerRole(role),
                            source='local_model_evaluation',content=text,timestamp=datetime(2026,9,13,12,tzinfo=timezone.utc)+timedelta(seconds=due),display_order=n))
                        if text.startswith(('Changing the subject:','Correction:')):boundary[0]=n
                        q,d=memory_retrieval_inputs(visible)
                        found=store.retrieve(contact.id,q,for_cloud=False,date_query=d,semantic_query=memory_semantic_input(visible),contact_cue_query=memory_semantic_input(visible,speaker_role=SpeakerRole.SELECTED_CONTACT))
                        contexts=[RetrievedMemoryContext(memory_id=m.memory_id,revision_id=m.revision_id,excerpt=m.content,memory_type=m.memory_type,
                            confidence=m.confidence,sensitivity_safe=m.cloud_eligible,rank=m.rank,relevance=m.reason) for m in found.matches[:4] if m.cloud_eligible and not found.ambiguous]
                        snap=build_snapshot(visible,snapshot_id=n,generation=generation,contact_id=contact.id,retrieved_memories=contexts)
                        retrieval={'ambiguous':found.ambiguous,'matches':[{'text':m.content,'reason':m.reason} for m in found.matches]}
                    coordinator.offer(snap,time.monotonic())
                    report['feed'].append({'scheduled':due,'actual':elapsed,'through_turn':max(t.display_order for t in snap.turns),'retrieval':retrieval});index+=1;save()
                for ev in coordinator.poll(time.monotonic()):report['events'].append({'at':elapsed,'kind':ev.kind.value,'snapshot_id':ev.snapshot_id,'error':ev.error_type})
                if stop_seconds is not None and elapsed>=stop_seconds and not stopped:
                    boundary[0]=10**9;coordinator.reset(generation+1);stopped=True
                time.sleep(.02)
            # Reset can detach an in-flight result. Retain its audit before leaving the process.
            deadline=time.monotonic()+250
            while any('response_at' not in r for r in report['requests']) and time.monotonic()<deadline:time.sleep(.05)
            report['complete']=True;report['max_feed_error']=max(abs(f['actual']-f['scheduled']) for f in report['feed']);save()
    finally:guidance.f06_structured_request=original

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--model',required=True);p.add_argument('--recorded',choices=['recent','earlier']);p.add_argument('--synthetic',action='store_true');p.add_argument('--compact',action='store_true');p.add_argument('--readable',action='store_true');p.add_argument('--brief',action='store_true');a=p.parse_args()
    if a.recorded:
        folder='live-test-20260913-121412' if a.recorded=='recent' else 'live-test-20260912-201026'
        run(a.model,a.recorded,recorded=ROOT/'build'/folder/'events.jsonl',compact=a.compact,readable=a.readable,brief=a.brief)
    if a.synthetic:
        f=load(ROOT/'conversation_copilot/assets/f06/implicit-variety.json')
        for c in f['cases']:
            texts=c['turns']+['Okay, let us talk about something else.','Changing the subject: I am enjoying a new mystery novel.']
            run(a.model,c['id'],script=[('user' if i%2==0 else 'selected_contact',t) for i,t in enumerate(texts)],memories=f['memories'],compact=a.compact,readable=a.readable,brief=a.brief)
        texts=['How have you been?','I feel stressed.','What has been on your mind?','I do not know how I will pay rent.','That sounds difficult.','I was there for so long. It was a big part of my life.','I am listening.','I am not sure what the future holds.','Let us talk about something else.','Changing the subject: I am enjoying a mystery novel.']
        run(a.model,'vague_job_4s',script=[('user' if i%2==0 else 'selected_contact',t) for i,t in enumerate(texts)],memories=f['memories'],compact=a.compact,readable=a.readable,brief=a.brief)
        no_rent=[m.replace(', and is worried about paying rent','') for m in f['memories']]
        assert no_rent!=f['memories'], 'The harder fixture must remove the rent clue from saved memory'
        run(a.model,'vague_job_no_rent_memory_4s',script=[('user' if i%2==0 else 'selected_contact',t) for i,t in enumerate(texts)],memories=no_rent,compact=a.compact,readable=a.readable,brief=a.brief)
