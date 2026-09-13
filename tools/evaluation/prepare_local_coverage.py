"""Rebuild earlier F04/F06 scenario coverage using today's production guidance prompt."""
import json
from unittest.mock import patch
from local_models import ROOT,OUT,load
from conversation_copilot.guidance import interpret_guidance
from conversation_copilot.interpretation import RetrievedMemoryContext
from conversation_copilot.f04_evaluation import SCENARIOS, MODES, EvaluationScenario
from datetime import datetime, timedelta, timezone
from conversation_copilot.models import ConversationTurn, SpeakerRole
from conversation_copilot.interpretation import build_snapshot
from conversation_copilot.memory import MemoryStore, default_database_path, memory_retrieval_inputs, memory_semantic_input
from conversation_copilot.semantic import default_cache_dir

class Captured(Exception):pass
rows=[]
def capture(snap,identifier,expected):
    row={'id':identifier,'schema':'GuidanceOutput','snapshot':snap.model_dump(mode='json'),'expected':expected,
        'baseline_note':'Earlier fixture, current prompt; no exact Luna API baseline claimed'}
    def collect(schema,payload,instructions,**kw):
        row['request']={'input':json.dumps(payload,ensure_ascii=False),'instructions':instructions,'max_output_tokens':kw['output_limit']}
        raise Captured()
    with patch('conversation_copilot.guidance.f06_structured_request',side_effect=collect):
        try:interpret_guidance(snap,ledger=None,live=False)
        except Captured:pass
    assert 'request' in row
    rows.append(row)
for scenario in SCENARIOS:
    for mode in MODES:
        capture(scenario.snapshot(mode),f'coverage/f04/{scenario.identifier}/{mode}',
            {'status':scenario.expected_status(mode),'acceptable_tones':scenario.acceptable_tones,'acceptable_cues':scenario.acceptable_cues,
             'rule':'Only present modalities are evidence; hypotheses only, never diagnoses or certain inner states.'})
for case in load(ROOT/'conversation_copilot/assets/f06/quality.json')['guidance']:
    snap=EvaluationScenario(case['id'],'f06',case['user'],case['remote']).snapshot('transcript')
    mem=[RetrievedMemoryContext(memory_id='m-style',revision_id='r-style',excerpt=case['style'],memory_type='communication_style',confidence='high',sensitivity_safe=True,rank=1,relevance='explicit style')] if 'style' in case else []
    capture(snap.model_copy(update={'contact_id':'fictional-yaheli','memories':mem}),'coverage/f06/'+case['id'],case)
fixture=load(ROOT/'conversation_copilot/assets/f04/basic-video-chat.json')
started=datetime(2026,8,25,12,tzinfo=timezone.utc)
turns=[ConversationTurn(speaker_name=t['speaker'],speaker_role=SpeakerRole.USER if t['speaker']=='alex' else SpeakerRole.SELECTED_CONTACT,
    source='saved_video_transcript',content=t['text'],timestamp=started+timedelta(seconds=t['end_seconds']),display_order=n)
    for n,t in enumerate(fixture['turns'],1)]
class Store(MemoryStore):
    @property
    def semantic_cache_dir(self):return default_cache_dir(default_database_path())
with Store(':memory:') as store:
    contact=store.create_contact('Maya')
    for m in fixture['seed_memories']:
        mid=store.create_memory(contact.id,m['content'],memory_type=m['type'],sensitivity='sensitive' if m['sensitive'] else 'normal',normalized_date_start=datetime.fromisoformat(m['date']).replace(tzinfo=timezone.utc))
        if m['sensitive']:store.set_cloud_permission(mid,True)
    store.backfill_semantic_embeddings()
    for checkpoint in fixture['progressive_checkpoints']:
        prefix=turns[:checkpoint['through_turn']];q,d=memory_retrieval_inputs(prefix)
        found=store.retrieve(contact.id,q,for_cloud=False,date_query=d,semantic_query=memory_semantic_input(prefix),contact_cue_query=memory_semantic_input(prefix,speaker_role=SpeakerRole.SELECTED_CONTACT))
        contexts=[RetrievedMemoryContext(memory_id=m.memory_id,revision_id=m.revision_id,excerpt=m.content,memory_type=m.memory_type,confidence=m.confidence,sensitivity_safe=m.cloud_eligible,rank=m.rank,relevance=m.reason) for m in found.matches[:4] if m.cloud_eligible and not found.ambiguous]
        capture(build_snapshot(prefix,snapshot_id=len(prefix),generation=1,contact_id=contact.id,retrieved_memories=contexts),'coverage/video/'+str(len(prefix)),
            {'historical_checkpoint':checkpoint,'rule':'Actual saved video words with fresh BGE retrieval; no visual/vocal observations here, so authored sarcasm/face cues are not mandatory. Media decoding and face tracking are separate offline checks.'})
(OUT/'coverage-cases.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8')
print('Prepared',len(rows),'current-prompt historical scenarios; no inference.')
