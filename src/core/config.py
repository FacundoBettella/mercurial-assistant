import os
from enum import Enum
from dotenv import load_dotenv

load_dotenv()

class LLMProviderType(str, Enum):
    OPENAI = "openai"
    GEMINI = "gemini"

class Settings:
    def __init__(self) -> None:
        self.llm_provider: LLMProviderType = LLMProviderType(
            os.getenv("LLM_PROVIDER", "openai").lower()
        )
        self.openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
        self.openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4")

        self.gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
        self.gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-1.5-pro")

        # Existing configs
        self.logs_dir: str = os.getenv("LOGS_DIR", "logs")
        self.log_hash_salt: str = os.getenv("LOG_HASH_SALT", "default-salt-change-me")

settings = Settings()
