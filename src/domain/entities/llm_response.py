from dataclasses import dataclass

@dataclass(frozen=True)
class LLMResponse:
    content: str
    model_used: str
    tokens_used: int = 0

    @staticmethod
    def empty() -> "LLMResponse":
        """Factory for empty response when content is blocked."""
        return LLMResponse(
            content="",
            model_used="none",
            tokens_used=0
        )
