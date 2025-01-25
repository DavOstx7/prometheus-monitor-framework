import argparse

from pydantic import BaseModel


def _parse_cli_args() -> dict:
    """
    Parses the command-line arguments for the monitoring framework.

    This function uses argparse to define the expected arguments and their associated help descriptions.
    It returns a dictionary containing the parsed arguments.

    Returns:
        dict: A dictionary containing the parsed command-line arguments, with keys as argument names
              and values as the corresponding parsed values.
    """
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
    """
    Represents the parsed command-line arguments as a Pydantic model.

    Attributes:
        config_file (str): Path to the config file (yaml or json).
        exporters_dir (str): Path to the exporters directory (relative to the current directory).
        dry_run (bool): Flag indicating whether to run in dry-run mode.
        verbose (bool): Flag to increase output verbosity, overriding logging to debug.
    """
    config_file: str
    exporters_dir: str
    dry_run: bool
    verbose: bool

    @classmethod
    def from_parsing(cls):
        """
        Creates an instance of CLIArgs by parsing the command-line arguments.

        This class method calls _parse_cli_args() to retrieve the parsed arguments and populates
        an instance of CLIArgs with those values.

        Returns:
            CLIArgs: An instance of the CLIArgs class with the parsed values.
        """
        cli_args = _parse_cli_args()
        return cls(**cli_args)
