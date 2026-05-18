from abc import ABC, abstractmethod
from typing import Any

class ILLMProvider(ABC):
    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        model: str | None = None,
    ) -> dict:
        """
        Args:
            prompt: Input text content.
            model: Optional model override.
            system_prompt: Optional system instruction for the assistant.
        Returns:
            dict with keys:
                - content: str (the generated text)
                - usage: dict (with prompt_tokens, completion_tokens, total_tokens)
        """
        pass
