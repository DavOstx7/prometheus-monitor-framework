import yaml
import json
from pathlib import PurePath
from pydantic import BaseModel, ConfigDict
from enum import Enum
from typing import Optional, List, Union, TypeVar

from src.core.exceptions import InvalidFileFormatError, ConfigFileNotFoundError


class ExecutionMode(str, Enum):
    SYNC = "sync"
    ASYNC = "async"
    MULTITHREADED = "multithreaded"


class AppConfig(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    prometheus_port: int
    execution_mode: ExecutionMode
    export_interval_seconds: int


ExporterConfigT = TypeVar("ExporterConfigT")


class ExporterSettings(BaseModel):
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
    app: AppConfig
    exporters: List[ExporterSettings]
    logging: dict

    @classmethod
    def from_file(cls, file_path: str):
        config = _load_config_from_file(file_path)
        return cls(**config)
