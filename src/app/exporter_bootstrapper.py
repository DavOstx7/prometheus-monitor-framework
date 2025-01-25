import functools
import logging
import importlib
import re
from typing import Optional, List, Type
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
    """
    Converts a filesystem path to a Python module path.

    Args:
        path (str): The filesystem path to convert.

    Returns:
        str: The corresponding Python module path.
    """
    module_path = re.sub(r"[\\/]+", ".", path).lstrip(".").rstrip(".")
    while ".." in module_path:
        module_path = module_path.replace("..", ".")
    return module_path


def get_exporter_logger(exporter_type: str, exporter_name: Optional[str]) -> logging.Logger:
    """
    Retrieves the logger for the specified exporter.

    Args:
        exporter_type (str): The type of the exporter.
        exporter_name (Optional[str]): The name of the exporter.

    Returns:
        logging.Logger: The logger for the exporter.
    """
    return get_logger(EXPORTERS_PARENT_LOGGER_NAME, exporter_type, exporter_name)


class ExporterBootstrapper:
    """
    A class responsible for bootstrapping exporters by loading their configurations and classes.

    This class loads and initializes the exporters based on the provided settings.
    """

    def __init__(self, exporters_dir_path: str):
        """
        Initializes the ExporterBootstrapper with the path to the exporters' directory.

        Args:
            exporters_dir_path (str): The path to the directory containing exporter modules.
        """
        self._exporters_dir_path = exporters_dir_path
        self._exporters_dir_module_path = _convert_path_to_module_path(exporters_dir_path)

    def bootstrap_exporters(self, exporters_settings: List[ExporterSettings]) -> List[BaseExporter]:
        """
        Bootstraps a list of exporters based on their settings.

        This method iterates over the provided exporter settings, initializes
        the exporters that are enabled, and skips those that are disabled.
        Successfully bootstrapped exporters are returned in a list.

        Args:
            exporters_settings (List[ExporterSettings]): A list of settings for each exporter.

        Returns:
            List[BaseExporter]: A list of successfully bootstrapped exporter instances.
        """
        exporters = []

        log.info(f"Processing {len(exporters_settings)} exporters settings...")
        for exporter_setting in exporters_settings:
            if exporter_setting.enabled:
                log.debug(f"Exporter '{exporter_setting.qualified_name}' is enabled. Bootstrapping...")
                exporter = self.bootstrap_exporter(exporter_setting)
                exporters.append(exporter)
            else:
                log.debug(f"Exporter '{exporter_setting.qualified_name}' is disabled. Skipping bootstrap...")

        if not exporters:
            log.warning(f"No exporters were bootstrapped (no exporters configured or all are disabled)")
        else:
            log.info(f"Successfully bootstrapped {len(exporters)} enabled exporters")

        return exporters

    def bootstrap_exporter(self, exporter_settings: ExporterSettings) -> BaseExporter:
        """
        Bootstraps a single exporter based on the provided settings.

        Args:
            exporter_settings (ExporterSettings): The configuration settings for the exporter.

        Returns:
            BaseExporter: The initialized exporter instance.
        """
        log.debug(f"Retrieving logger for exporter: '{exporter_settings.qualified_name}'")
        logger = get_exporter_logger(exporter_settings.type, exporter_settings.name)

        if exporter_settings.config:
            log.debug(f"Loading config class for exporter type: '{exporter_settings.type}'")
            exporter_config_class = self.load_exporter_config_class(exporter_settings.type)

            log.debug(f"Initializing config model for exporter: '{exporter_settings.qualified_name}'")
            exporter_config = exporter_config_class(**exporter_settings.config)
            exporter_settings = exporter_settings.model_copy(update={"config": exporter_config}, deep=False)

        log.debug(f"Loading class for exporter type: '{exporter_settings.type}'")
        exporter_class = self.load_exporter_class(exporter_settings.type)

        log.debug(f"Initializing exporter instance: '{exporter_settings.qualified_name}'")
        exporter = exporter_class(exporter_settings, logger)
        log.debug(f"Successfully bootstrapped exporter: '{exporter}'")

        return exporter

    def load_exporter_class(self, exporter_type: str) -> Type[BaseExporter]:
        """
        Loads the class of an exporter based on the exporter type.

        Args:
            exporter_type (str): The type of the exporter to load.

        Returns:
            Type[BaseExporter]: The class of the exporter.

        Raises:
            ExporterBootstrapError: If the exporter module does not contain the expected exporter class.
        """
        exporter_module = self.load_exporter_module(exporter_type)
        try:
            return getattr(exporter_module, EXPORTER_CLASS_NAME)
        except AttributeError as error:
            raise ExporterBootstrapError(
                f"Exporter module does not have attribute of exporter class: '{EXPORTER_CLASS_NAME}'"
            ) from error

    def load_exporter_config_class(self, exporter_type: str) -> Type[ExporterConfigT]:
        """
        Loads the configuration class of an exporter based on the exporter type.

        Args:
            exporter_type (str): The type of the exporter to load the configuration class for.

        Returns:
            Type[ExporterConfigT]: The configuration class for the exporter.

        Raises:
            ExporterBootstrapError: If the exporter config module does not contain the expected config class.
        """
        exporter_config_module = self.load_exporter_config_module(exporter_type)
        try:
            return getattr(exporter_config_module, EXPORTER_CONFIG_CLASS_NAME)
        except AttributeError as error:
            raise ExporterBootstrapError(
                f"Exporter config module does not have attribute of config class: '{EXPORTER_CONFIG_CLASS_NAME}'"
            ) from error

    @functools.lru_cache
    def load_exporter_module(self, exporter_type: str) -> ModuleType:
        """
        Loads the exporter module using caching.

        Args:
            exporter_type (str): The type of the exporter to load.

        Returns:
            ModuleType: The loaded exporter module.

        Raises:
            ExporterBootstrapError: If the exporter module cannot be loaded.
        """
        exporter_module_path = self.get_exporter_module_path(exporter_type)
        try:
            return importlib.import_module(exporter_module_path)
        except ImportError as error:
            raise ExporterBootstrapError(
                f"Failed to load exporter module: '{exporter_module_path}'"
            ) from error

    @functools.lru_cache
    def load_exporter_config_module(self, exporter_type: str) -> ModuleType:
        """
        Loads the exporter configuration module using caching.

        Args:
            exporter_type (str): The type of the exporter to load the config module for.

        Returns:
            ModuleType: The loaded exporter configuration module.

        Raises:
            ExporterBootstrapError: If the exporter config module cannot be loaded.
        """
        exporter_config_module_path = self.get_exporter_config_module_path(exporter_type)
        try:
            return importlib.import_module(exporter_config_module_path)
        except ImportError as error:
            raise ExporterBootstrapError(
                f"Failed to load exporter config module: '{exporter_config_module_path}'"
            ) from error

    def get_exporter_module_path(self, exporter_type: str) -> str:
        """
        Constructs the module path for the exporter module based on its type.

        Args:
            exporter_type (str): The type of the exporter.

        Returns:
            str: The module path for the exporter.
        """
        return f"{self._exporters_dir_module_path}.{exporter_type}.{EXPORTER_MODULE_NAME}"

    def get_exporter_config_module_path(self, exporter_type: str) -> str:
        """
        Constructs the module path for the exporter config module based on its type.

        Args:
            exporter_type (str): The type of the exporter.

        Returns:
            str: The module path for the exporter config module.
        """
        return f"{self._exporters_dir_module_path}.{exporter_type}.{EXPORTER_CONFIG_MODULE_NAME}"
