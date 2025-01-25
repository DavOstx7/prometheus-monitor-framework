import logging
import time
import asyncio
import threading
from prometheus_client import start_http_server
from typing import Callable, List, Dict

from src.core.config import AppConfig, ExecutionMode
from src.exporters.base import BaseExporter

RunFuncT = Callable[[List[BaseExporter], bool], None]

log = logging.getLogger(__name__)


def export_metrics_sync(exporters: List[BaseExporter], dry_run: bool):
    """
    Exports metrics synchronously by calling the `export_metrics` method of each exporter.

    Args:
        exporters (List[BaseExporter]): List of exporters to process.
        dry_run (bool): If True, skip actual metric export and log debug messages instead.
    """
    for exporter in exporters:
        if dry_run:
            log.debug(f"Skipping 'export_metrics' method of exporter: '{exporter}' (dry-run enabled)")
        else:
            log.debug(f"Calling 'export_metrics' method of exporter: '{exporter}'")
            try:
                exporter.export_metrics()
            except Exception as error:
                log.error(f"Exporter '{exporter}' raised an error: {repr(error)}")


def export_metrics_async(exporters: List[BaseExporter], dry_run: bool):
    """
    Exports metrics asynchronously by calling the `export_metrics` method of each exporter.

    Args:
        exporters (List[BaseExporter]): List of exporters to process.
        dry_run (bool): If True, skip actual metric export and log debug messages instead.
    """
    coroutines = []

    for exporter in exporters:
        if dry_run:
            log.debug(f"Skipping 'export_metrics' method of exporter: '{exporter}' (dry-run enabled)")
        else:
            log.debug(f"Calling 'export_metrics' method of exporter: '{exporter}'")
            try:
                if asyncio.iscoroutinefunction(exporter.export_metrics):
                    coroutine = exporter.export_metrics()
                else:
                    coroutine = asyncio.to_thread(exporter.export_metrics)
                coroutines.append(coroutine)
            except Exception as error:
                log.error(f"Exporter '{exporter}' raised an error: {repr(error)}")

    asyncio.get_event_loop().run_until_complete(asyncio.gather(*coroutines))


class PrometheusMetricsExporter:
    """
    Handles periodic metric export to Prometheus with support for various execution modes.

    Attributes:
        _config (AppConfig): Configuration for the Prometheus metrics exporter.
        _execution_mode_to_run_func (Dict[ExecutionMode, RunFuncT]): Mapping of execution modes to their respective run functions.
    """

    def __init__(self, config: AppConfig):
        """
        Initializes the PrometheusMetricsExporter with the given configuration.

        Args:
            config (AppConfig): Configuration object containing settings like execution mode and export interval.
        """
        self._config = config
        self._execution_mode_to_run_func: Dict[ExecutionMode, RunFuncT] = {
            ExecutionMode.SYNC: self._run_sync,
            ExecutionMode.ASYNC: self._run_async,
            ExecutionMode.MULTITHREADED: self._run_multithreaded
        }

    def run_forever(self, exporters: List[BaseExporter], dry_run: bool):
        """
        Starts the exporter in a continuous loop, exporting metrics based on the configured execution mode.

        Args:
            exporters (List[BaseExporter]): List of exporters to process.
            dry_run (bool): If True, skip actual metric export and log debug messages instead.
        """
        if dry_run:
            log.debug("Skipping Prometheus server (dry-run enabled)")
        else:
            log.info(f"Starting Prometheus HTTP server on port: {self._config.prometheus_port}")
            start_http_server(self._config.prometheus_port)

        log.info(f"Using execution mode: '{self._config.execution_mode}'")
        run_func = self._execution_mode_to_run_func[self._config.execution_mode]

        log.info("Starting to run forever")
        run_func(exporters, dry_run)

    def _run_sync(self, exporters: List[BaseExporter], dry_run: bool):
        """
        Runs the metric export synchronously in a continuous loop.

        Args:
            exporters (List[BaseExporter]): List of exporters to process.
            dry_run (bool): If True, skip actual metric export and log debug messages instead.
        """
        while True:
            export_metrics_sync(exporters, dry_run)
            self._wait_between_exports()

    def _run_async(self, exporters: List[BaseExporter], dry_run: bool):
        """
        Runs the metric export asynchronously in a continuous loop.

        Args:
            exporters (List[BaseExporter]): List of exporters to process.
            dry_run (bool): If True, skip actual metric export and log debug messages instead.
        """
        while True:
            export_metrics_async(exporters, dry_run)
            self._wait_between_exports()

    def _run_multithreaded(self, exporters: List[BaseExporter], dry_run: bool):
        """
        Runs the metric export in a multithreaded mode, creating a thread for each exporter.

        Args:
            exporters (List[BaseExporter]): List of exporters to process.
            dry_run (bool): If True, skip actual metric export and log debug messages instead.
        """
        threads = []

        for exporter in exporters:
            thread = threading.Thread(target=self._run_sync, args=([exporter], dry_run))
            threads.append(thread)

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

    def _wait_between_exports(self):
        """
        Introduces a delay between metric exports.
        """
        log.info(f"Sleeping for {self._config.export_interval_seconds} seconds...")
        time.sleep(self._config.export_interval_seconds)
