from abc import ABC, abstractmethod

class IMetricRepository(ABC):
    @abstractmethod
    def write_metric(self, metric: dict) -> None:
        """Persist a single metric record (dict) to storage."""
        pass

    @abstractmethod
    def read_all(self) -> list[dict]:
        """Return all persisted metric records."""
        pass
