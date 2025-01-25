from src.core import CLIArgs, Config
from src.core.logs import update_loggers_level, configure_logging
from src.app import ExporterBootstrapper, PrometheusMetricsExporter


def main():
    cli_args = CLIArgs.from_parsing()
    config = Config.from_file(cli_args.config_file)

    if cli_args.verbose:
        update_loggers_level(config.logging, "DEBUG")

    configure_logging(config.logging)

    exporter_bootstrapper = ExporterBootstrapper(cli_args.exporters_dir)
    exporters = exporter_bootstrapper.bootstrap_exporters(config.exporters)

    prometheus_metrics_exporter = PrometheusMetricsExporter(config.app)
    prometheus_metrics_exporter.run_forever(exporters, cli_args.dry_run)


if __name__ == "__main__":
    main()
