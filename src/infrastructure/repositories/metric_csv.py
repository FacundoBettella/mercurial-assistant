import csv
from pathlib import Path
from src.domain.interfaces.metric_repository import IMetricRepository
from src.domain.exceptions import PersistenceError


class CsvMetricRepository(IMetricRepository):
    def __init__(self, csv_path: str) -> None:
        self._csv_path = csv_path

    def write_metric(self, metric: dict) -> None:
        try:
            with open(self._csv_path, "a", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=metric.keys())
                if f.tell() == 0:
                    writer.writeheader()
                writer.writerow(metric)
        except OSError as e:
            raise PersistenceError(str(e), path=self._csv_path) from e

    def read_all(self) -> list[dict]:
        path = Path(self._csv_path)
        if not path.exists() or path.stat().st_size == 0:
            return []
        try:
            with open(self._csv_path, newline="", encoding="utf-8") as f:
                return list(csv.DictReader(f))
        except OSError as e:
            raise PersistenceError(str(e), path=self._csv_path) from e
