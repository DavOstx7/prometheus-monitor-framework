import logging
from abc import ABC, abstractmethod
from typing import Generic

from src.core.config import ExporterSettings, ExporterConfigT


class BaseExporter(ABC, Generic[ExporterConfigT]):
    def __init__(self, settings: ExporterSettings, logger: logging.Logger):
        self._settings = settings
        self._logger = logger

    @abstractmethod
    def export_metrics(self):
        """ Export Metrics """
        raise NotImplementedError

    @property
    def config(self) -> ExporterConfigT:
        return self._settings.config

    @property
    def logger(self) -> logging.Logger:
        return self._logger

    def __str__(self):
        return f"{self._settings.type}.{self._settings.name}"

    def __repr__(self):
        return f"<Exporter type={self._settings.type} name={self._settings.name} enabled={self._settings.enabled}>"

