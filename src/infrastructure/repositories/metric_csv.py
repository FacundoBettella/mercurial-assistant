import csv
from src.domain.interfaces.metric_repository import IMetricRepository


class CsvMetricRepository(IMetricRepository):
    def __init__(self, csv_path: str) -> None:
        self._csv_path = csv_path

    def write_metric(self, metric: dict) -> None:
        with open(self._csv_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=metric.keys())
            if f.tell() == 0:
                writer.writeheader()
            writer.writerow(metric)
