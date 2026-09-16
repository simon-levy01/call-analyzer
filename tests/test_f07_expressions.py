from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
import pytest

from conversation_copilot.interpretation import VisualAggregator
from conversation_copilot.video import FaceBox


def signal(index, smile=0.5, brow=0.4, corners=0.1, jaw=0.0):
    return SimpleNamespace(timestamp_ms=index * 100, face_box=FaceBox(.1, .1, .4, .4),
        blendshapes=[(name, value) for prefix, value in
            [('mouthSmile', smile), ('browDown', brow), ('mouthFrown', corners)]
            for name in (prefix+'Left', prefix+'Right')] + [('jawOpen', jaw)])


def test_persistent_separate_levels_capture_time_and_loss_reset():
    start = datetime(2026, 9, 14, tzinfo=timezone.utc)
    agg = VisualAggregator()
    for i in range(41):
        capture = start + timedelta(seconds=i / 10)
        agg.add(signal(i), capture + timedelta(seconds=.1), captured_at=capture)
    observations = agg.expressions()
    assert [v.kind for v in observations] == ['smile_like', 'brow_lowering', 'mouth_corner_lowering']
    assert all(v.observed_seconds == pytest.approx(4) and v.onset_at == start for v in observations)
    assert all(v.confidence == 'low' for v in observations)
    assert agg.buckets()[0].smile_movement == 0  # A held level survives zero motion.
    agg.add(signal(41, smile=0, brow=0, corners=0), start + timedelta(seconds=4.2))
    assert all(v.offset_at is not None for v in agg.expressions())
    agg.add(None, start + timedelta(seconds=4.3))
    assert not agg.expressions()
    agg.add(signal(44), start + timedelta(seconds=4.4))
    assert all(v.observed_seconds == 0 for v in agg.expressions())
    # Repeated samples do not extend a hold, and eventually become unavailable.
    agg.add(signal(44), start + timedelta(seconds=5))
    assert not agg.expressions()
    agg.reset()
    assert not agg.buckets() and not agg.expressions()


def test_mouth_activity_missing_categories_and_long_suspension():
    start = datetime(2026, 9, 14, tzinfo=timezone.utc)
    agg = VisualAggregator()
    agg.add(signal(0, jaw=.8), start)
    smile, brow, corners = agg.expressions()
    assert smile.level is corners.level is None
    assert brow.level == .4 and brow.quality == 'observable'
    agg.add(signal(1, smile=.8, jaw=.8), start + timedelta(seconds=.1))
    assert agg.expressions()[0].level == .8
    missing = signal(2)
    missing.blendshapes = []
    agg.add(missing, start + timedelta(seconds=.2))
    assert all(v.quality == 'unavailable' and v.onset_at is None for v in agg.expressions())
    agg.add(signal(3), start + timedelta(hours=12))
    assert all(v.observed_seconds == 0 for v in agg.expressions())
    assert len(agg.buckets()) <= 45


def test_current_summary_future_cutoff_and_missing_modality():
    import json
    from conversation_copilot.interpretation import build_snapshot, prepare_interpretation_request, visual_row_has_evidence
    from conversation_copilot.models import ConversationTurn
    start = datetime(2026, 9, 14, tzinfo=timezone.utc)
    agg = VisualAggregator()
    agg.add(signal(0), start)
    agg.add(signal(1), start + timedelta(seconds=.1))
    current = agg.buckets(start + timedelta(seconds=.2))
    assert len(current) == 1 and not agg.buckets()
    turn = ConversationTurn(speaker_name='Fixture', speaker_role='selected_contact',
        source='fixture', content='The train leaves at four.', timestamp=start, display_order=1)
    before = build_snapshot([turn], snapshot_id=1, generation=1,
        visual_buckets=current, created_at=start)
    assert not before.visual_buckets
    snapshot = build_snapshot([turn], snapshot_id=2, generation=1,
        visual_buckets=current, created_at=start + timedelta(seconds=.2))
    payload = json.loads(prepare_interpretation_request(snapshot, preserve_transcript=True).input_text)
    assert payload['x'][0][8][0][0] == 'smile_like'
    assert payload['x'][0][8][0][6] == 'unknown'
    assert visual_row_has_evidence(payload['x'][0])
    assert not visual_row_has_evidence([0, 1, 1, None, None, None, None, None,
        [['smile_like', None, 0, None, None, 'unavailable', 'unknown']]])
    assert not visual_row_has_evidence([0, 1, 1, None, None, None, None, None,
        [['smile_like', .01, 0, None, None, 'below_threshold', 'unknown']]])


def test_switch_during_processing_cannot_publish_old_face(monkeypatch):
    import threading
    import time
    import numpy as np
    from conversation_copilot import video
    from conversation_copilot.capture import LatestFrameSlot, FramePacket, CallWindow
    entered, release = threading.Event(), threading.Event()
    class Processor:
        def process(self, pixels, timestamp):
            entered.set()
            assert release.wait(2)
            return SimpleNamespace(tracking_state='Tracking', face_count=1,
                signal=SimpleNamespace(timestamp_ms=timestamp,landmarks=(),blendshapes=()),thumbnail_rgb=None)
        def switch_face(self): pass
        def continue_tracking(self): pass
        def close(self): pass
    class Capture:
        frames=LatestFrameSlot()
        worker_alive=True
        stop_reason=''
        def start(self): pass
        def stop(self, timeout=3):
            self.worker_alive=False
            self.frames.clear()
    monkeypatch.setattr(video,'FaceProcessor',Processor)
    capture=Capture()
    session=video.LiveVideoSession(CallWindow(1,'Fixture','fixture.exe','Fixture'),capture)
    session.start()
    try:
        capture.frames.replace(FramePacket(np.zeros((1,1,4),dtype=np.uint8),time.perf_counter(),1))
        assert entered.wait(2)
        session.switch_face()
        release.set()
        assert session.snapshot().current_signal is None
    finally:
        release.set()
        session.stop()
    assert session._processed_count == 0 and session._signal is None


def test_uncertain_samples_pause_duration_and_offsets_survive():
    start = datetime(2026,9,14,tzinfo=timezone.utc)
    agg = VisualAggregator()
    for i in range(5):
        # Frame age varies while actual capture spacing remains exactly 100ms.
        capture = start + timedelta(seconds=i/10)
        agg.add(signal(i),capture+timedelta(seconds=.4),captured_at=capture)
    onset = agg.expressions()[0].onset_at
    agg.add(signal(5,jaw=.8),start+timedelta(seconds=.9),captured_at=start+timedelta(seconds=.5))
    uncertain=agg.expressions()[0]
    assert uncertain.onset_at==onset and uncertain.observed_seconds==pytest.approx(.4)
    asym=signal(6)
    asym.blendshapes[0]=('mouthSmileLeft',.1)
    agg.add(asym,start+timedelta(seconds=1),captured_at=start+timedelta(seconds=.6))
    assert agg.expressions()[0].quality=='asymmetric'
    agg.add(signal(7),start+timedelta(seconds=1.1),captured_at=start+timedelta(seconds=.7))
    assert agg.expressions()[0].onset_at==onset
    assert agg.expressions()[0].observed_seconds==pytest.approx(.4)
    for i in range(8,13):
        agg.add(signal(i,smile=.01),start+timedelta(seconds=i/10+.4),captured_at=start+timedelta(seconds=i/10))
    ended=agg.expressions()[0]
    assert ended.quality=='below_threshold' and ended.offset_at==start+timedelta(seconds=.8)
    assert ended.onset_at==onset and ended.observed_seconds==pytest.approx(.4)
    # Repeated timestamp with a slightly older reconstructed UTC time must not
    # throw out of the UI callback, even before the stable-origin UI mapping.
    agg.add(signal(12,smile=.01),start+timedelta(seconds=1.7),captured_at=start+timedelta(seconds=1.199))
    assert not agg.expressions()


def test_boundary_filter_retains_independent_positive_tone_and_cadence():
    from conversation_copilot.interpretation import (InterpretationUpdate, InterpretationCoordinator,
        build_snapshot, _calibrate_high_confidence, _cautious_policy)
    from conversation_copilot.models import ConversationTurn
    start=datetime(2026,9,14,tzinfo=timezone.utc)
    turn=ConversationTurn(speaker_name='Fixture',speaker_role='selected_contact',source='fixture',
        content='We can talk later, but I am thrilled I got the job!',timestamp=start,display_order=1)
    snapshot=build_snapshot([turn],snapshot_id=1,generation=1)
    candidate=InterpretationUpdate(status='updated',tones=[dict(kind='positive_warm',confidence='medium',
        hypothesis='Possible positive tone',evidence=dict(explanation='Thrilled about the job',modalities=['language']))],
        social_cues=[dict(kind='disengagement_withdrawal',confidence='medium',hypothesis='Possible withdrawal',
            evidence=dict(explanation='Talk later',modalities=['language']))])
    result=_calibrate_high_confidence(candidate,snapshot)
    assert result.tones and not result.social_cues
    policy=_cautious_policy(snapshot)
    assert policy is None or policy.status.value=='updated'
    coordinator=InterpretationCoordinator(lambda _: result)
    coordinator._last_started_at=10
    coordinator.reset(2,preserve_cadence=True)
    assert coordinator.snapshot().last_started_at==10


def test_bucket_alignment_and_prior_spend(tmp_path):
    import json
    from conversation_copilot.interpretation import build_snapshot, prepare_interpretation_request, VocalObservation
    from conversation_copilot.models import ConversationTurn
    from tools.evaluation.f07_api import prior_spend
    start=datetime(2026,9,14,tzinfo=timezone.utc)
    agg=VisualAggregator()
    agg.add(signal(0),start)
    agg.add(signal(1),start+timedelta(seconds=.1))
    turn=ConversationTurn(speaker_name='Fixture',speaker_role='selected_contact',source='fixture',
        content='The train leaves at four.',timestamp=start,display_order=1)
    vocal=VocalObservation(turn_display_order=1,available=True,duration_seconds=1,
        relative_energy=1,voiced_ratio=.8,words_per_voiced_second=2,gap_seconds=0,overlaps_user=False)
    snapshot=build_snapshot([turn],snapshot_id=1,generation=1,vocal_observations=[vocal],
        visual_buckets=agg.buckets(start+timedelta(seconds=.2)),created_at=start+timedelta(seconds=.2))
    payload=json.loads(prepare_interpretation_request(snapshot,preserve_transcript=True).input_text)
    assert payload['x'][0][8][0][6]=='contact_speaking'
    from conversation_copilot.interpretation import RetrievedMemoryContext
    memories=[RetrievedMemoryContext(memory_id=f'm{i}',revision_id=f'r{i}',
        excerpt=('Detailed relevant contact memory ' * 8)[:180], memory_type='other',
        confidence='medium',sensitivity_safe=True,rank=i+1,relevance='fixture') for i in range(4)]
    bounded=build_snapshot([turn],snapshot_id=2,generation=1,vocal_observations=[vocal],
        visual_buckets=snapshot.visual_buckets,created_at=snapshot.created_at,
        contact_id='fixture',retrieved_memories=memories)
    prepared=prepare_interpretation_request(bounded)
    bounded_payload=json.loads(prepared.input_text)
    assert prepared.estimated_input_tokens <= 2200
    assert bounded_payload['t'] == payload['t']
    assert prepared.memory_count == len(bounded_payload.get('m',[]))
    for name, prior, committed in [('api-a',0,.01),('api-b',.01,.025)]:
        folder=tmp_path/name; folder.mkdir()
        (folder/'report.json').write_text(json.dumps(dict(prior_dollars=prior,committed_dollars=committed)))
    assert prior_spend(tmp_path)==pytest.approx(.025)
    (tmp_path/'api-b/report.json').write_text(json.dumps(dict(prior_dollars=.01,committed_dollars=-1)))
    with pytest.raises(ValueError): prior_spend(tmp_path)
