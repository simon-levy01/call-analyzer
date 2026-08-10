from datetime import datetime

import pytest
from pydantic import ValidationError

from conversation_copilot.models import (
    ConfidenceLevel,
    ContactSuggestion,
    ConversationTurn,
    Observation,
    SelectedContact,
)


def test_models_reject_unapproved_vocabulary():
    with pytest.raises(ValidationError):
        ConversationTurn(
            speaker_name="Alex",
            speaker_role="contact",
            source="paste",
            content="Hello",
            display_order=1,
        )

    with pytest.raises(ValidationError):
        ContactSuggestion(display_name="Alex", source="window_title", confidence="certain")


def test_contact_suggestion_cannot_silently_become_selected():
    suggestion = ContactSuggestion(
        display_name="Alex", source="window_title", confidence=ConfidenceLevel.LOW
    )

    with pytest.raises(ValidationError):
        SelectedContact.model_validate(suggestion.model_dump())
    with pytest.raises(ValidationError):
        SelectedContact(display_name="Alex", confirmed_by_user=False)


def test_observation_rejects_reversed_time_bounds():
    with pytest.raises(ValidationError):
        Observation(
            source="fixture",
            content="visible movement",
            started_at=datetime(2026, 8, 10, 12, 1),
            ended_at=datetime(2026, 8, 10, 12, 0),
        )
