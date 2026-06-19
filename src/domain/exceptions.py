class AppError(Exception):
    """Root for all application errors."""


# ── Domain ────────────────────────────────────────────────────────────────────

class DomainError(AppError):
    """Pure business-rule violations."""


class ContentBlockedError(DomainError):
    """Moderation blocked the request before it reached the LLM."""

    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


# ── Application ───────────────────────────────────────────────────────────────

class ApplicationError(AppError):
    """Use-case / orchestration failures."""


class LLMResponseParseError(ApplicationError):
    """LLM returned content that could not be parsed into the expected schema."""

    def __init__(self, raw: str, cause: Exception) -> None:
        super().__init__(f"Failed to parse LLM response: {cause}")
        self.raw = raw
        self.cause = cause


# ── Infrastructure ────────────────────────────────────────────────────────────

class InfrastructureError(AppError):
    """Failures in external systems or I/O."""


class LLMProviderError(InfrastructureError):
    """Base for all LLM provider failures."""

    def __init__(self, message: str, provider: str = "unknown") -> None:
        super().__init__(f"[{provider}] {message}")
        self.provider = provider


class LLMTimeoutError(LLMProviderError):
    """Provider did not respond within the allowed time."""


class LLMRateLimitError(LLMProviderError):
    """Provider rejected the request due to rate limiting (HTTP 429)."""


class PersistenceError(InfrastructureError):
    """Failed to write to a local storage backend (CSV, JSONL, etc.)."""

    def __init__(self, message: str, path: str = "") -> None:
        super().__init__(f"{message} (path={path!r})" if path else message)
        self.path = path
