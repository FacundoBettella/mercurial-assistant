from dataclasses import dataclass
from .moderation_action import ModerationAction

@dataclass(frozen=True)
class ModerationResponse:
    flagged: bool
    detected_risks: list[str]
    moderation_action: ModerationAction
    reason: str
