import time
from src.exporters import BaseExporter
from .config import Config

_FAKE_EXPORT_METRICS_DURATION = 3


class Exporter(BaseExporter[Config]):
    """
    An example exporter implementation that simulates exporting metrics.

    This exporter fetches metrics from a configured S3 URL and logs the process.
    It demonstrates how to implement the `export_metrics` method for a specific use case.
    """

    def export_metrics(self):
        """
        Simulates the process of exporting metrics from a specific S3 URL.

        The method logs the start and end of the export process, with a delay
        to simulate the duration of the export task.
        """
        self.logger.info(f"Starting to export metrics from url: '{self.config.s3_url}'")
        time.sleep(_FAKE_EXPORT_METRICS_DURATION)
        self.logger.info(f"Finished exporting metrics from url: '{self.config.s3_url}'")
