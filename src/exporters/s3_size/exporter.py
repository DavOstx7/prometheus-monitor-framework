import time

from src.exporters import BaseExporter
from .config import Config

_FAKE_EXPORT_METRICS_DURATION = 3


class Exporter(BaseExporter[Config]):
    def export_metrics(self):
        self.logger.info(f"Starting to export metrics from url: '{self.config.s3_url}'")
        time.sleep(_FAKE_EXPORT_METRICS_DURATION)
        self.logger.info(f"Finished exporting metrics from url: '{self.config.s3_url}'")
