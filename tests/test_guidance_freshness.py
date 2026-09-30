"""Display-time regressions; synthetic evidence only, no model calls."""
from datetime import datetime, timedelta, timezone
import pytest
from conversation_copilot import guidance as g, interpretation as ip
from conversation_copilot.models import ConversationTurn, SpeakerRole

def result():
    return g.GuidedInterpretation(snapshot_id=1,generation=1,analyzed_order=2,
        context_at=datetime(2026,9,24,tzinfo=timezone.utc),status='updated',
        social_cues=[ip.SocialCue(kind='interest_engagement',confidence='medium',hypothesis='They are comparing the options.',
            evidence=ip.Evidence(explanation='They ask to see alternatives.',modalities=['language'],turn_ids=[2]))])

def test_changed_explanation_reaches_coordinator_and_stable_card():
    first=result();second=first.model_copy(deep=True)
    second.snapshot_id=2
    second.social_cues[0].hypothesis='They explain a practical concern about the options.'
    second.social_cues[0].evidence.turn_ids=[4]
    assert ip.interpretation_signature(first)!=ip.interpretation_signature(second)
    card=ip.StableInterpretationCard()
    card.offer(first,0)
    assert card.offer(second,13)=='replaced'
    assert card.update.social_cues[0].hypothesis==second.social_cues[0].hypothesis
    from types import SimpleNamespace
    coordinator=ip.InterpretationCoordinator(lambda _:None)
    for index, output in enumerate((first,second,second),1):
        coordinator._results.put((SimpleNamespace(snapshot_id=index,generation=1),output,None))
        expected='duplicate' if index==3 else 'accepted'
        assert coordinator.poll(index)[0].kind.value==expected

def test_render_time_expiry_and_topic_reset_clear_tones_and_cues_without_mutation():
    update=result()
    assert g.reconcile_replies(update,[],update.context_at+timedelta(seconds=23)).social_cues
    expired=g.reconcile_replies(update,[],update.context_at+timedelta(seconds=24))
    assert not expired.social_cues and expired.status=='insufficient_evidence'
    assert isinstance(expired.status, ip.InterpretationStatus)
    ip.interpretation_signature(expired)
    turn=ConversationTurn(speaker_name='User',speaker_role='user',source='test',content='Moving on, what about dinner?',
        timestamp=update.context_at+timedelta(seconds=1),display_order=3)
    assert not g.reconcile_replies(update,[turn],turn.timestamp).social_cues
    assert update.social_cues  # Raw/accepted evidence remains intact.

def test_user_paraphrase_retires_question_but_not_an_unrelated_continuation():
    candidate=g.GuidanceCandidate(text='Could we clarify the delivery date?',confidence='medium',turn_ids=[2])
    turn=ConversationTurn(speaker_name='User',speaker_role='user',source='test',content='What is the delivery date?',
        timestamp=result().context_at,display_order=3)
    assert g.reply_superseded(candidate,turn)
    assert not g.reply_superseded(candidate,turn.model_copy(update={'content':'The budget is limited.'}))


def test_late_topic_result_keeps_displayed_items():
    update=result()
    update.replies=[g.GuidanceCandidate(text='Could we clarify the delivery date?',confidence='medium',turn_ids=[2])]
    display=g.GuidanceDisplay()
    display.offer(update,0)
    assert display.visible('replies')
    reset=ConversationTurn(speaker_name='User',speaker_role='user',source='test',content='Moving on, what about dinner?',
        timestamp=update.context_at,display_order=3)
    display.offer(g.reconcile_replies(update,[reset],reset.timestamp).model_copy(update={'snapshot_id':2}),1)
    assert display.visible('replies') and display.visible('social_cues')
    # Keep the pre-existing CONTACT matching semantics unchanged.
    candidate=g.GuidanceCandidate(text='Could you clarify pricing?',confidence='medium',turn_ids=[2])
    assert not g.reply_superseded(candidate,reset.model_copy(update={'speaker_role':SpeakerRole.SELECTED_CONTACT,'content':'Pricing is complicated.'}))


@pytest.mark.parametrize('text', ["I'd rather not talk about the numbers today.",
    'We can leave that alone.', 'Leave it there.', 'I do not want to discuss the budget.',
    'Stop asking about the budget.', 'I prefer not to talk about the budget.',
    'Moving on, what about dinner?', 'Correction, the date is already set.', 'Could we discuss the budget?'])
def test_filtered_new_result_keeps_every_displayed_section_and_original_expiry(text):
    update=result()
    update.tones=[ip.ToneHypothesis(kind='neutral_calm',confidence='medium',hypothesis='They explain options.',
        evidence=update.social_cues[0].evidence)]
    update.replies=[g.GuidanceCandidate(text='Could we discuss the budget?',confidence='medium',turn_ids=[2])]
    update.remember=[g.GuidanceCandidate(text='Possible job context.',confidence='low',memory_ids=['r'])]
    update.follow_up=[g.GuidanceCandidate(text='What is your budget?',confidence='medium',turn_ids=[2])]
    display=g.GuidanceDisplay();display.offer(update,10)
    local=ip.RetrievedMemoryContext(memory_id='local',revision_id='local-r',excerpt='Another possible memory.',
        memory_type='other',confidence='low',sensitivity_safe=True,rank=1,relevance='semantic')
    display.offer_local_remember([local],1,10)
    before=repr((display.items,display.local_remember))
    refusal=ConversationTurn(speaker_name='Contact',speaker_role='selected_contact',source='test',
        content=text,timestamp=update.context_at+timedelta(seconds=11),display_order=3)
    delivered=g.reconcile_replies(update,[refusal],refusal.timestamp)
    display.offer(delivered.model_copy(update={'snapshot_id':2}),21,source_age=11)
    assert repr((display.items,display.local_remember))==before
    display.tick(189)
    assert all(display.visible(key) for key in g.LIVE_CATEGORIES) and display.local_remember
    display.tick(190)
    assert all(not display.visible(key) for key in g.LIVE_CATEGORIES) and not display.local_remember
    assert update.replies and update.remember and update.follow_up
