from datetime import datetime
from enum import StrEnum
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

_NonEmptyText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class SpeakerRole(StrEnum):
    USER = "user"
    SELECTED_CONTACT = "selected_contact"
    UNCLEAR = "unclear"


class ConfidenceLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    UNCLEAR = "unclear"


class ContactSuggestion(BaseModel):
    model_config = ConfigDict(extra="forbid")

    display_name: _NonEmptyText
    source: _NonEmptyText
    confidence: ConfidenceLevel = ConfidenceLevel.UNCLEAR


class SelectedContact(BaseModel):
    model_config = ConfigDict(extra="forbid")

    display_name: _NonEmptyText
    confirmed_by_user: Literal[True]


class ConversationTurn(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    speaker_name: _NonEmptyText
    speaker_role: SpeakerRole = SpeakerRole.UNCLEAR
    source: _NonEmptyText
    content: str = Field(min_length=1)
    timestamp: datetime | None = None
    display_order: int = Field(ge=1)
    is_media: bool = False


def conversation_turn_from_audio(draft, display_order: int):
    return ConversationTurn(
        speaker_name=draft.speaker_name,
        speaker_role=draft.speaker_role,
        source=draft.source,
        content=draft.content,
        timestamp=draft.timestamp,
        display_order=display_order,
        is_media=False,
    )


def vocal_observation_from_audio(draft, display_order: int):
    if draft.vocal is None:
        return None
    from .interpretation import VocalObservation

    vocal = draft.vocal
    return VocalObservation(
        turn_display_order=display_order,
        available=vocal.available,
        duration_seconds=vocal.duration_seconds,
        relative_energy=vocal.relative_energy,
        voiced_ratio=vocal.voiced_ratio,
        words_per_voiced_second=vocal.words_per_voiced_second,
        gap_seconds=vocal.gap_seconds,
        overlaps_user=vocal.overlaps_user,
        unavailable_reason=vocal.unavailable_reason,
    )


class Observation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source: _NonEmptyText
    content: _NonEmptyText
    started_at: datetime
    ended_at: datetime

    @model_validator(mode="after")
    def validate_time_bounds(self) -> "Observation":
        if self.ended_at < self.started_at:
            raise ValueError("ended_at must not precede started_at")
        return self
