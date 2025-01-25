import yaml
import json
from pathlib import PurePath
from pydantic import BaseModel, ConfigDict
from enum import Enum
from typing import Optional, List, Union, TypeVar

from src.core.exceptions import InvalidFileFormatError, ConfigFileNotFoundError


class ExecutionMode(str, Enum):
    """
    Enum representing different execution modes for the application.

    Attributes:
        SYNC: Synchronous execution mode.
        ASYNC: Asynchronous execution mode.
        MULTITHREADED: Multithreaded execution mode.
    """
    SYNC = "sync"
    ASYNC = "async"
    MULTITHREADED = "multithreaded"


class AppConfig(BaseModel):
    """
    Represents the application configuration.

    Attributes:
        prometheus_port (int): Port number for Prometheus metrics.
        execution_mode (ExecutionMode): Mode of execution (sync, async, or multithreaded).
        export_interval_seconds (int): Interval (in seconds) for data export.
    """
    model_config = ConfigDict(use_enum_values=True)

    prometheus_port: int
    execution_mode: ExecutionMode
    export_interval_seconds: int


ExporterConfigT = TypeVar("ExporterConfigT")


class ExporterSettings(BaseModel):
    """
    Represents the configuration for a data exporter.

    Attributes:
        type (str): The type of exporter.
        name (Optional[str]): The optional name of the exporter.
        enabled (bool): A flag indicating whether the exporter is enabled.
        config (Optional[Union[dict, ExporterConfigT]]): Optional configuration specific to the exporter type.
    """
    model_config = ConfigDict(frozen=True)

    type: str
    name: Optional[str] = None
    enabled: bool = True
    config: Optional[Union[dict, ExporterConfigT]] = None


_FILE_SUFFIX_TO_LOADER = {
    ".yml": yaml.safe_load,
    ".yaml": yaml.safe_load,
    ".json": json.load
}


def _load_config_from_file(file_path: str) -> dict:
    """
    Loads configuration data from a file, based on its extension.

    Args:
        file_path (str): The path to the configuration file.

    Raises:
        InvalidFileFormatError: If the file format is unsupported.
        ConfigFileNotFoundError: If the file does not exist.

    Returns:
        dict: The parsed configuration data.
    """
    suffix = PurePath(file_path).suffix
    loader = _FILE_SUFFIX_TO_LOADER.get(suffix)
    if not loader:
        raise InvalidFileFormatError(f"Unsupported format of config file: '{file_path}'")

    try:
        with open(file_path, "r") as file:
            return loader(file)
    except FileNotFoundError:
        raise ConfigFileNotFoundError(f"Path to config file does not exist: '{file_path}'")


class Config(BaseModel):
    """
    Represents the full application configuration, including app settings, exporters, and logging settings.

    Attributes:
        app (AppConfig): The application-specific configuration.
        exporters (List[ExporterSettings]): A list of exporters and their settings.
        logging (dict): The logging configuration.
    """
    app: AppConfig
    exporters: List[ExporterSettings]
    logging: dict

    @classmethod
    def from_file(cls, file_path: str):
        """
        Creates a Config instance by loading and parsing a configuration file.

        Args:
            file_path (str): The path to the configuration file.

        Returns:
            Config: A Config instance populated with the data from the file.
        """
        config = _load_config_from_file(file_path)
        return cls(**config)
