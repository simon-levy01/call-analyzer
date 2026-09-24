"""Display-time regressions; synthetic evidence only, no model calls."""
from datetime import datetime, timedelta, timezone
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


def test_reset_clears_pending_visible_and_local_items():
    update=result()
    update.replies=[g.GuidanceCandidate(text='Could we clarify the delivery date?',confidence='medium',turn_ids=[2])]
    display=g.GuidanceDisplay()
    display.offer(update,0)
    assert display.visible('replies')
    reset=ConversationTurn(speaker_name='User',speaker_role='user',source='test',content='Moving on, what about dinner?',
        timestamp=update.context_at,display_order=3)
    display.on_speech(reset)
    assert not display.visible('replies') and not display.pending and not display.local_remember
    # Keep the pre-existing CONTACT matching semantics unchanged.
    candidate=g.GuidanceCandidate(text='Could you clarify pricing?',confidence='medium',turn_ids=[2])
    assert not g.reply_superseded(candidate,reset.model_copy(update={'speaker_role':SpeakerRole.SELECTED_CONTACT,'content':'Pricing is complicated.'}))
