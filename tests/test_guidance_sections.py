from conversation_copilot import guidance as g
import pytest


@pytest.mark.parametrize('kind,label', list(g.TONE_LABELS.items()))
def test_every_tone_label_preserves_source_and_expires(kind,label):
    category='social_cues' if kind in {'humor','sarcasm'} else 'tones'
    update=g.GuidedInterpretation.model_validate({'snapshot_id':1,'generation':1,'status':'updated',
        category:[{'kind':kind,'hypothesis':'Supported observation.','confidence':'medium',
                   'evidence':{'explanation':'Explicit evidence.','modalities':['language'],'turn_ids':[2]}}]})
    display=g.GuidanceDisplay();display.offer(update,0)
    source,index,item=display.tone_items()[0]
    assert source==category and g.tone_label(item.candidate)==label
    assert display.context_items()[0][2].candidate is item.candidate
    display.tick(179);assert display.tone_items()
    display.tick(180);assert not display.tone_items()


def test_humor_newest_first_dismisses_cues_not_unrelated_tones():
    evidence={'explanation':'Explicit joke.','modalities':['language'],'turn_ids':[2]}
    update=g.GuidedInterpretation.model_validate({'snapshot_id':1,'generation':1,'status':'updated',
        'tones':[{'kind':'neutral_calm','hypothesis':'Factual delivery.','confidence':'medium','evidence':evidence}]})
    display=g.GuidanceDisplay();display.offer(update,0)
    newer=g.GuidedInterpretation.model_validate({'snapshot_id':2,'generation':1,'status':'updated',
        'social_cues':[{'kind':kind,'hypothesis':text,'confidence':'medium','evidence':evidence}
                       for kind,text in [('other','Clarification.'),('humor','A joke.'),('humor','Another joke.'),('sarcasm','Ironic contrast.')]]})
    display.offer(newer,10)
    assert [g.tone_label(x[2].candidate) for x in display.tone_items()]==[
        'Playful / humorous','Possibly sarcastic','Neutral / factual']
    source,index,_=display.tone_items()[0]
    assert source=='social_cues' and index==1
    display.dismiss_tone(index,source)
    assert [x.candidate.kind.value for x in display.items['social_cues']]==['other','sarcasm']
    assert len(display.items['tones'])==1 and len(newer.social_cues)==4
    display.invalidate(new_topic=True,turn_ids=set(),memory_ids=set())
    assert not display.tone_items()


def test_section_views_preserve_type_sources_and_newest_first():
    evidence={'explanation':'A factual comparison.','modalities':['language'],'turn_ids':[2]}
    update=g.GuidedInterpretation.model_validate({'snapshot_id':1,'generation':1,'status':'updated',
        'tones':[{'kind':'neutral_calm','hypothesis':'They compare the options.','confidence':'medium','evidence':evidence}],
        'social_cues':[{'kind':'other','hypothesis':'They request clarification.','confidence':'medium','evidence':evidence}]})
    display=g.GuidanceDisplay();display.offer(update,0)
    assert g.tone_label(display.tone_items()[0][2].candidate)=='Neutral / factual'
    assert [entry[0] for entry in display.context_items()]==['social_cues','tones']
    assert len(update.social_cues)==1 and update.tones[0].hypothesis=='They compare the options.'
    assert display.context_items()[1][2].candidate.evidence.turn_ids==[2]
    next_update=update.model_copy(deep=True);next_update.snapshot_id=2
    next_update.tones[0].hypothesis='They give a new factual detail.'
    next_update.tones[0].evidence.turn_ids=[3];next_update.social_cues=[]
    display.offer(next_update,20)
    assert display.context_items()[0][0]=='tones'
    assert len(display.tone_items())==1  # Duplicate labels do not fill tone slots.
    assert display.tone_items()[0][2].candidate.evidence.turn_ids==[3]
    display.tick(179);assert len(display.context_items())==3
    display.tick(180);assert len(display.context_items())==1
    # One underlying observation: dismissing its context also removes its tone view.
    source,index,_=display.context_items()[0];display.dismiss(source,index)
    assert not display.context_items() and not display.tone_items()
    assert next_update.tones  # Never mutate model evidence.


def test_dismiss_tone_label_clears_hidden_duplicates_and_context_dedups():
    evidence={'explanation':'Explicit facts.','modalities':['language'],'turn_ids':[2]}
    update=g.GuidedInterpretation.model_validate({'snapshot_id':1,'generation':1,'status':'updated',
        'tones':[{'kind':'neutral_calm','hypothesis':text,'confidence':'medium','evidence':evidence}
                 for text in ('Compare options.','State a fact.')],
        'social_cues':[{'kind':'other','hypothesis':'Compare options.','confidence':'medium','evidence':evidence}]})
    display=g.GuidanceDisplay();display.offer(update,0)
    assert len(display.tone_items())==1 and len(display.context_items())==2
    assert display.context_items()[0][0]=='social_cues'  # Cue wins identical wording.
    display.dismiss_tone(0)
    assert not display.tone_items() and len(display.context_items())==1
    assert len(update.tones)==2
    # A merged row before another label must retain the underlying source index.
    update.tones.append(update.tones[0].model_copy(update={
        'kind': type(update.tones[0].kind)('positive_warm'), 'hypothesis': 'Warm greeting.'}))
    display=g.GuidanceDisplay();display.offer(update,0)
    source,index,item=display.tone_items()[1]
    assert source=='tones' and index==2
    display.dismiss_tone(index)
    assert len(display.items['tones'])==2
    assert all(g.tone_label(entry.candidate)=='Neutral / factual' for entry in display.items['tones'])
