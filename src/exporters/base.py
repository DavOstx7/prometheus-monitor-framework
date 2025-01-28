import logging
from abc import ABC, abstractmethod
from typing import Generic, Optional

from src.core.config import ExporterSettings, ExporterConfigT


class BaseExporter(ABC, Generic[ExporterConfigT]):
    """
    Abstract base class for exporters.

    This class serves as a base for all exporters, defining common functionality and properties.
    It includes abstract methods that must be implemented by subclasses to export metrics.
    """

    def __init__(self, settings: ExporterSettings, logger: logging.Logger):
        """
        Initializes the BaseExporter with the given settings and logger.

        Args:
            settings (ExporterSettings): Configuration settings for the exporter.
            logger (logging.Logger): Logger instance to be used by the exporter.
        """
        self._settings = settings
        self._logger = logger

    @abstractmethod
    def export_metrics(self):
        """
        Abstract method to export metrics.

        This method must be implemented by subclasses to define the logic for exporting metrics.
        """
        raise NotImplementedError

    @property
    def config(self) -> Optional[ExporterConfigT]:
        """
        Returns the configuration associated with the exporter.

        Returns:
            Optional[ExporterConfigT]: The configuration settings for the exporter.
        """
        return self._settings.config

    @property
    def logger(self) -> logging.Logger:
        """
        Returns the logger to be used by the exporter.

        Returns:
            logging.Logger: The logger instance used for logging by the exporter.
        """
        return self._logger

    def __str__(self):
        """
        Returns a string representation of the exporter.

        Returns:
            str: A string representation of the exporter in the format 'type.name'.
        """
        return self._settings.qualified_name

    def __repr__(self):
        """
        Returns a detailed string representation of the exporter.

        Returns:
            str: A string representation of the exporter including its type, name, and enabled status.
        """
        return f"<Exporter type={self._settings.type} name={self._settings.name} enabled={self._settings.enabled}>"
