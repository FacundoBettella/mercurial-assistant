import json
from pathlib import Path
from typing import Any

from src.domain.interfaces.log_repository import ILogRepository
from src.domain.exceptions import PersistenceError


class JsonLogRepository(ILogRepository):
    """Concrete implementation: writes logs to JSONL files.

    Can be replaced with PostgresLogRepository, ElasticsearchRepository, etc.
    without touching ModerationService.
    """

    def __init__(self, logs_dir: str = "logs") -> None:
        self.logs_dir = Path(logs_dir)
        self.logs_dir.mkdir(exist_ok=True)

    def write_log(self, record: dict[str, Any]) -> None:
        log_path = self.logs_dir / "moderation_events.jsonl"
        try:
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
        except OSError as e:
            raise PersistenceError(str(e), path=str(log_path)) from e
