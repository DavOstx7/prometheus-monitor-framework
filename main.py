import logging

from src.core import CLIArgs, Config
from src.core.logs import update_loggers_level, setup_logging
from src.app import ExporterBootstrapper, PrometheusMetricsExporter


def main():
    """
    Entry point of the application.

    This function initializes and runs the application, performing the following tasks:
    1. Parses CLI arguments.
    2. Loads the configuration file.
    3. Configures logging based on verbosity and configuration settings.
    4. Bootstraps exporters from the specified exporters directory.
    5. Starts the Prometheus metrics exporter to run indefinitely.
    """
    cli_args = CLIArgs.from_parsing()
    config = Config.from_file(cli_args.config_file)

    if cli_args.verbose:
        update_loggers_level(config.logging, logging.DEBUG)

    setup_logging(config.logging)

    exporter_bootstrapper = ExporterBootstrapper(cli_args.exporters_dir)
    exporters = exporter_bootstrapper.bootstrap_exporters(config.exporters)

    prometheus_metrics_exporter = PrometheusMetricsExporter(config.app)
    prometheus_metrics_exporter.run_forever(exporters, cli_args.dry_run)


if __name__ == "__main__":
    main()
