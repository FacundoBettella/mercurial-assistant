class DomainError(Exception):
    """Base for all domain-level errors."""


class ContentBlockedError(DomainError):
    """Raised when moderation blocks a request from reaching the LLM."""

    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason
