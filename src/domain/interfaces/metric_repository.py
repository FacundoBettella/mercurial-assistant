from abc import ABC, abstractmethod

class IMetricRepository(ABC):
    @abstractmethod
    def write_metric(self, metric: dict) -> None:
        """Persist a single metric record (dict) to storage."""
        pass
