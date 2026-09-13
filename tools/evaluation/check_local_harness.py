"""Offline harness checks: no inference, no credentials, no network."""
import json
from unittest.mock import patch
import local_models as lm

case={'schema':'GuidanceOutput','request':{'input':json.dumps({'t':[['c',0,'I feel stressed.']], 'turn_ids':[1]}),
    'instructions':'Use only supplied evidence.','max_output_tokens':1200}}
assert lm.readable_turns({'turn_ids':[1,2,3,4],'t':[['u',-3,'Question'],[None,-2,'More question'],['c',-1,'Answer'],[None,0,'More answer']]}) == ['Turn 1 — USER: Question','Turn 2 — USER: More question','Turn 3 — CONTACT: Answer','Turn 4 — CONTACT: More answer']
valid={'interpretation':{'status':'insufficient_evidence','tones':[],'social_cues':[]},'replies':[], 'remember':[], 'follow_up':[]}
def fake(path,data=None,timeout=240):
    if path=='show':return {'model_info':{'test.context_length':8192}}
    if path=='ps':return {'models':[]}
    assert path=='chat' and data['stream'] is False and data['options']['num_ctx']==8192
    return {'message':{'content':json.dumps(valid)},'done_reason':'stop'}
with patch.object(lm,'rpc',side_effect=fake):
    assert lm.infer('local:4b',case)['parsed']['remember']==[]
    bad=json.loads(json.dumps(valid));bad['remember']=[{'text':'Invented memory','confidence':'high','turn_ids':[1],'memory_ids':['not-supplied']}]
    with patch.object(lm,'rpc',side_effect=lambda p,d=None: {'message':{'content':json.dumps(bad)},'done_reason':'stop'} if p=='chat' else fake(p,d)):
        assert lm.infer('local:4b',case)['invalid_evidence']
with patch.object(lm,'rpc',return_value={'model_info':{'test.context_length':4096}}):
    try: lm.infer('short:4b',case)
    except ValueError as e: assert 'truncation' in str(e)
    else: raise AssertionError('Must refuse too-small context')
with patch.object(lm,'rpc',return_value={'remote_host':'example.com'}):
    try: lm.infer('remote',case)
    except ValueError as e: assert 'local weights' in str(e)
    else: raise AssertionError('Must refuse remote models')
print('Local harness: schema, unavailable evidence, context and remote-model guards passed.')
