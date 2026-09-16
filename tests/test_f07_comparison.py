import json
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

from conversation_copilot import guidance, interpretation, memory, models
from tools.evaluation.f07_comparison import attach_expressions, invoke, wire


def test_comparison_vocabulary_and_nonvisual_evidence_are_matched():
    stamp=datetime(2026,9,14,tzinfo=timezone.utc)
    turn=models.ConversationTurn(speaker_name='Fixture',speaker_role='selected_contact',source='fixture',
        content='The meeting is tomorrow.',timestamp=stamp,display_order=1)
    bucket=interpretation.VisualBucket(started_at=stamp-timedelta(seconds=2),ended_at=stamp,
        availability=1,reliability=1,smile_movement=.01)
    expression=interpretation.ExpressionObservation(kind='smile_like',level=.5,quality='observable',onset_at=stamp)
    improved=bucket.model_copy(update={'expressions':[expression]})
    # JSON uses Z while datetime.isoformat uses +00:00; join by the actual instant.
    attached=attach_expressions([bucket.model_dump(mode='json')],[improved])
    assert attached[0]['expressions'][0]['kind']=='smile_like'
    pkg=SimpleNamespace(guidance=guidance,interpretation=interpretation,memory=memory)
    requests=[]
    class Captured(Exception): pass
    class Responses:
        def parse(self,**kw): requests.append(wire(kw)); raise Captured()
    instructions=interpretation.INTERPRETATION_INSTRUCTIONS
    for arm,buckets in [('none',[]),('movement',[bucket]),('expressions',[interpretation.VisualBucket.model_validate(attached[0])])]:
        snapshot=interpretation.build_snapshot([turn],snapshot_id=1,generation=1,visual_buckets=buckets,created_at=stamp)
        job=dict(arm=arm,endpoint='guidance',snapshot=snapshot.model_dump(mode='json'))
        try: invoke(pkg,job,interpretation.UsageLedger(),SimpleNamespace(responses=Responses()))
        except Captured: pass
    assert len(requests)==3
    assert len({r['instructions'] for r in requests})==1
    assert all('x may append expressions:' in r['instructions'] for r in requests)
    assert interpretation.INTERPRETATION_INSTRUCTIONS==instructions
    inputs=[json.loads(r['input']) for r in requests]
    assert all({k:v for k,v in item.items() if k!='x'}=={k:v for k,v in inputs[0].items() if k!='x'} for item in inputs)
    assert inputs[1]['x'][0]==inputs[2]['x'][0][:8]
    assert all(r['max_output_tokens']==1200 and r['reasoning']=={'effort':'low'} and r['store'] is False for r in requests)
