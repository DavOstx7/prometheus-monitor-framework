import functools
import logging
import importlib
import re
from typing import List, Type
from types import ModuleType
from src.exporters import BaseExporter
from src.core.config import ExporterSettings, ExporterConfigT
from src.core.logs import get_logger
from src.core.exceptions import ExporterBootstrapError

log = logging.getLogger(__name__)

EXPORTERS_PARENT_LOGGER_NAME = "exporters"

EXPORTER_MODULE_NAME = "exporter"
EXPORTER_CLASS_NAME = "Exporter"

EXPORTER_CONFIG_MODULE_NAME = "config"
EXPORTER_CONFIG_CLASS_NAME = "Config"


def _convert_path_to_module_path(path: str) -> str:
    module_path = re.sub(r"[\\/]+", ".", path)
    module_path = module_path.lstrip(".").rstrip(".")
    while ".." in module_path:
        module_path = module_path.replace("..", ".")
    return module_path


def get_exporter_logger(exporter_type: str, exporter_name: str) -> logging.Logger:
    log.debug(f"Getting logger of exporter: '{exporter_type}.{exporter_name}'")
    return get_logger(EXPORTERS_PARENT_LOGGER_NAME, exporter_type, exporter_name)


class ExporterBootstrapper:
    def __init__(self, exporters_dir_path: str):
        self._exporters_dir_path = exporters_dir_path
        self._exporters_dir_module_path = _convert_path_to_module_path(exporters_dir_path)

    def bootstrap_exporters(self, exporters_settings: List[ExporterSettings]) -> List[BaseExporter]:
        exporters = []

        log.info(f"Bootstrapping {len(exporters_settings)} exporters...")
        for exporter_setting in exporters_settings:
            exporter = self.bootstrap_exporter(exporter_setting)
            exporters.append(exporter)
        log.info(f"Bootstrapped all exporters successfully")

        return exporters

    def bootstrap_exporter(self, exporter_settings: ExporterSettings) -> BaseExporter:
        logger = get_exporter_logger(exporter_settings.type, exporter_settings.name)

        if exporter_settings.config:
            exporter_config_class = self.load_exporter_config_class(exporter_settings.type)
            log.debug(f"Initializing config class of exporter: '{exporter_settings.type}.{exporter_settings.name}'")
            exporter_config = exporter_config_class(**exporter_settings.config)
            exporter_settings = exporter_settings.model_copy(update={"config": exporter_config}, deep=False)

        exporter_class = self.load_exporter_class(exporter_settings.type)
        log.debug(f"Initializing class of exporter: '{exporter_settings.type}.{exporter_settings.name}'")
        exporter = exporter_class(exporter_settings, logger)
        log.info(f"Bootstrapped exporter: '{exporter}'")
        return exporter

    def load_exporter_class(self, exporter_type: str) -> Type[BaseExporter]:
        log.debug(f"Loading class of exporter: '{exporter_type}'")
        exporter_module = self.load_exporter_module(exporter_type)
        try:
            return getattr(exporter_module, EXPORTER_CLASS_NAME)
        except AttributeError as error:
            raise ExporterBootstrapError(
                f"Exporter module does not have attribute of exporter class: '{EXPORTER_CLASS_NAME}'"
            ) from error

    def load_exporter_config_class(self, exporter_type: str) -> Type[ExporterConfigT]:
        log.debug(f"Loading config class of exporter: '{exporter_type}'")
        exporter_config_module = self.load_exporter_config_module(exporter_type)
        try:
            return getattr(exporter_config_module, EXPORTER_CONFIG_CLASS_NAME)
        except AttributeError as error:
            raise ExporterBootstrapError(
                f"Exporter config module does not have attribute of config class: '{EXPORTER_CONFIG_CLASS_NAME}'"
            ) from error

    @functools.lru_cache
    def load_exporter_module(self, exporter_type: str) -> ModuleType:
        exporter_module_path = self.get_exporter_module_path(exporter_type)
        try:
            return importlib.import_module(exporter_module_path)
        except ImportError as error:
            raise ExporterBootstrapError(
                f"Failed to load exporter module: '{exporter_module_path}'"
            ) from error

    @functools.lru_cache
    def load_exporter_config_module(self, exporter_type: str) -> ModuleType:
        exporter_config_module_path = self.get_exporter_config_module_path(exporter_type)
        try:
            return importlib.import_module(exporter_config_module_path)
        except ImportError as error:
            raise ExporterBootstrapError(
                f"Failed to load exporter config module: '{exporter_config_module_path}'"
            ) from error

    def get_exporter_module_path(self, exporter_type: str) -> str:
        return f"{self._exporters_dir_module_path}.{exporter_type}.{EXPORTER_MODULE_NAME}"

    def get_exporter_config_module_path(self, exporter_type: str) -> str:
        return f"{self._exporters_dir_module_path}.{exporter_type}.{EXPORTER_CONFIG_MODULE_NAME}"
