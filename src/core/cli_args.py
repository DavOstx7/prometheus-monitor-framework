import argparse

from pydantic import BaseModel


def _parse_cli_args() -> dict:
    parser = argparse.ArgumentParser(description="Run the monitoring framework.")

    parser.add_argument(
        "--config-file",
        type=str,
        default="config/config.yml",
        help="Path to the config file (yaml or json)."
    )
    parser.add_argument(
        "--exporters-dir",
        type=str,
        default="src/exporters/",
        help="Path to the exporters directory (relative to the current directory)."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run in dry-run mode (no actions performed)."
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Increase output verbosity (override logging to debug)."
    )

    return dict(vars(parser.parse_args()))


class CLIArgs(BaseModel):
    config_file: str
    exporters_dir: str
    dry_run: bool
    verbose: bool

    @classmethod
    def from_parsing(cls):
        cli_args = _parse_cli_args()
        return cls(**cli_args)
