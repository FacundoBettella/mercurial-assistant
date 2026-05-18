from abc import ABC, abstractmethod
from typing import Any

class ILogRepository(ABC):
    @abstractmethod
    def write_log(self, record: dict[str, Any]) -> None:
        """Persist a single prompt metric record to storage."""
        pass
