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
