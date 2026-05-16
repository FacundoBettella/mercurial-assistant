from abc import ABC, abstractmethod

class ILLMProvider(ABC):
    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        model: str | None = None,
    ) -> str:
        """
        Args:
            prompt: Input text content.
            model: Optional model override.
            system_prompt: Optional system instruction for the assistant.
        """
        pass
