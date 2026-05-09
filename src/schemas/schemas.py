"""Data Transfer Objects and abstractions for moderation."""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ModerationAction(str, Enum):
    """Possible actions after content evaluation."""
    ALLOW = "allow"
    FLAG = "flag"
    BLOCK = "block"
    ESCALATE = "escalate"


class ModerationRequest(BaseModel):
    """Incoming moderation request payload."""
    user_id: str = Field(min_length=1)
    text: str = Field(min_length=1)


class ModerationResponse(BaseModel):
    """Moderation decision response."""
    flagged: bool
    detected_risks: list[str]
    moderation_action: ModerationAction
    reason: str


class LogRepository(ABC):
    """Abstract base class for logging moderation events."""

    @abstractmethod
    def write_log(self, record: dict[str, Any]) -> None:
        """Persist a moderation log record."""
        pass
