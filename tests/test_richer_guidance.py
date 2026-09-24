"""User-approved richer guidance behavior, no API calls."""
from datetime import datetime, timezone, timedelta
from conversation_copilot import guidance as g, interpretation as ip
from conversation_copilot.models import ConversationTurn

def output(n, text):
    return g.GuidedInterpretation(snapshot_id=n,generation=1,analyzed_order=n,
        context_at=datetime(2026,9,24,tzinfo=timezone.utc),status='updated',
        social_cues=[ip.SocialCue(kind='interest_engagement',confidence='medium',hypothesis=text,
            evidence=ip.Evidence(explanation=text,modalities=['language'],turn_ids=[n]))],
        replies=[g.GuidanceCandidate(text=text,confidence='medium',turn_ids=[n])])

def test_luna_routing_prices_and_first_analysis():
    assert ip.LUNA_MODEL=='gpt-5.6-luna'
    assert ip.LIVE_ASK_MODELS==(ip.LUNA_MODEL,'gpt-6-sol')
    assert ip.REVIEW_MODEL=='gpt-6-sol'
    assert ip.MODEL_PRICES['gpt-6-luna'].output_per_million==.50
    assert ip.MODEL_PRICES[ip.LUNA_MODEL].output_per_million==1.20
    assert ip.FIRST_ANALYSIS_DELAY_SECONDS==6

def test_newest_first_fill_four_and_expire_without_renewing_old_evidence():
    display=g.GuidanceDisplay()
    for n in range(1,6):display.offer(output(n,f'Choice {n}?'),n)
    for category in ('social_cues','replies'):
        assert len(display.visible(category))==4
        assert [x.snapshot_id for x in display.visible(category)]==[5,4,3,2]
    display.offer(output(6,'Choice 5?').model_copy(update={'replies':[],'social_cues':[]}),30)
    assert len(display.visible('social_cues'))==4
    display.tick(51)
    assert [x.snapshot_id for x in display.visible('social_cues')]==[5,4]
    display.tick(53)
    assert not display.visible('social_cues') and not display.visible('replies')

def test_retained_cue_dismissal_reset_and_source_invalidation():
    display=g.GuidanceDisplay();display.offer(output(1,'Compare sizes?'),0);display.offer(output(2,'Compare colors?'),8)
    display.dismiss('social_cues',1)
    assert len(display.visible('social_cues'))==1
    display.invalidate(turn_ids={1},memory_ids=set())
    assert not display.visible('social_cues')
    display.offer(output(3,'Compare lengths?'),10)
    turn=ConversationTurn(speaker_name='Contact',speaker_role='selected_contact',source='test',display_order=4,
        timestamp=datetime.now(timezone.utc),content='I do not want to talk about that anymore.')
    display.on_speech(turn)
    assert all(not display.visible(k) for k in g.LIVE_CATEGORIES)

def test_old_source_reply_is_still_rejected_at_delivery():
    update=output(1,'Compare?')
    assert not g.reconcile_replies(update,[],update.context_at+timedelta(seconds=24)).replies


def test_reset_clears_visual_only_cues_and_renewal_never_moves_backwards():
    display=g.GuidanceDisplay(); update=output(1,'A visible gesture.')
    update.social_cues[0].evidence.turn_ids=[]
    update.social_cues[0].evidence.modalities=[ip.EvidenceModality.VISUAL]
    display.offer(update,10)
    display.offer(update,12,manual=True,source_age=5)
    assert display.visible('social_cues')[0].supported_at==10
    display.invalidate(turn_ids=set(),memory_ids=set())
    assert not display.visible('social_cues')


def test_neutral_wording_does_not_license_inferred_calm():
    now=datetime.now(timezone.utc)
    turn=ConversationTurn(speaker_name='Contact',speaker_role='selected_contact',source='test',
        display_order=1,timestamp=now,content='The blue one is thirty dollars.')
    snapshot=ip.build_snapshot([turn],snapshot_id=1,generation=1,created_at=now)
    for text,expected in [('Neutral, factual wording.',True),('Calm and practical.',False),('Composed, factual.',False)]:
        update=ip.InterpretationUpdate(status='updated',tones=[ip.ToneHypothesis(kind='neutral_calm',
            confidence='medium',hypothesis=text,evidence=ip.Evidence(explanation='Price statement.',modalities=['language'],turn_ids=[1]))])
        assert bool(ip._ground_interpretation(update,snapshot,[1]).tones)==expected


def test_optional_checks_do_not_allow_invented_commitments(monkeypatch):
    from conversation_copilot.f04_evaluation import EvaluationScenario
    snapshot=EvaluationScenario('optional','live','Here are the shirts.','Could you compare the sizes?').snapshot('transcript')
    for text,allowed in [("I'll check the sizes.",True),("I'll look at the label.",True),
        ("I'll check in tomorrow.",False),("I'll look forward to it.",False),("I'll look after it.",False),
        ("I'll check that and call you tomorrow.",False),("I'll check it out and get back to you.",False),
        ("I'll check that by Friday.",False),("I'll look at it on Monday.",False),("I'll check this weekend.",False),
        ("I'll check it soon.",False),("I'll look at it next Tuesday.",False),("I'll check it, then order it.",False)]:
        raw=g.GuidanceOutput.model_validate({'interpretation':{'status':'insufficient_evidence','explanation':'No affect evidence.'},
            'replies':[{'text':text,'confidence':'medium','turn_ids':[2]}]})
        monkeypatch.setattr(g,'f06_structured_request',lambda *a,**k:(raw.model_copy(deep=True),None))
        assert bool(g.interpret_guidance(snapshot,ledger=ip.UsageLedger.product()).replies)==allowed


def test_repeated_old_evidence_stays_old_but_confidence_can_fall():
    display=g.GuidanceDisplay();first=output(1,'First suggestion?')
    display.offer(first,0);display.offer(output(2,'New suggestion?'),5)
    repeat=first.model_copy(deep=True,update={'snapshot_id':3})
    repeat.replies[0].confidence='low'
    display.offer(repeat,10)
    items=display.visible('replies')
    assert [i.snapshot_id for i in items]==[2,1]
    assert items[1].candidate.confidence=='low' and items[1].supported_at==0
    display.dismiss('replies',0)
    display.invalidate(turn_ids=set(),memory_ids=set(),new_topic=True)
    assert not display.dismissed and display.last_snapshot==3


def test_uncertain_memory_lowers_cue_confidence_without_mutating_input():
    from conversation_copilot.f04_evaluation import EvaluationScenario
    snapshot=EvaluationScenario('uncertain-cue','live','What is happening?','Money is tight.').snapshot('transcript')
    snapshot=snapshot.model_copy(update={'memories':[ip.RetrievedMemoryContext(memory_id='m',revision_id='r',excerpt='Prior job loss.',
        memory_type='event_date',confidence='low',sensitivity_safe=True,rank=1,relevance='uncertain retrieval candidate; identity not established')]})
    update=output(2,'They may be looking for support.')
    update.social_cues[0].evidence.memory_ids=['r']
    update.social_cues[0].evidence.modalities.append(ip.EvidenceModality.MEMORY)
    result=ip._ground_interpretation(update,snapshot,[1,2])
    assert result.social_cues[0].confidence=='low'
    assert update.social_cues[0].confidence=='medium'


def test_same_memory_reworded_does_not_take_two_slots():
    display=g.GuidanceDisplay()
    for n,text in enumerate(('Possibly related: an earlier job loss.','Possibly related: the previously saved job loss.'),1):
        update=output(n,'Discuss options?')
        update.remember=[g.GuidanceCandidate(text=text,confidence='low',memory_ids=['r'],turn_ids=[n])]
        display.offer(update,n)
    assert len(display.visible('remember'))==1
    assert display.visible('remember')[0].snapshot_id==2


def test_reendorsed_visual_only_cue_is_fresh_not_an_omission():
    display=g.GuidanceDisplay()
    for n,now in enumerate((0,12,24),1):
        update=output(n,'A visible gesture.')
        update.social_cues[0].evidence.turn_ids=[]
        update.social_cues[0].evidence.modalities=[ip.EvidenceModality.VISUAL]
        display.offer(update,now)
    display.tick(50)
    assert display.visible('social_cues')[0].snapshot_id==3
    assert display.visible('social_cues')[0].supported_at==24
