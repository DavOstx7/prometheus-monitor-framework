import logging
import logging.config
from typing import Union


def get_logger(*name_parts: str) -> logging.Logger:
    """
    Retrieves a logging logger with the specified name.

    The logger name is constructed by joining the provided name parts with periods ('.').

    Args:
        *name_parts (str): Parts of the logger name, which will be concatenated.

    Returns:
        logging.Logger: A logger instance with the specified name.
    """
    name_parts = [name_part for name_part in name_parts if name_part]
    logger_name = ".".join(name_parts)
    return logging.getLogger(logger_name)


def update_loggers_level(logging_config: dict, level: Union[int, str]):
    """
    Updates the logging level for all loggers in the provided configuration.

    This function modifies the 'level' field in the loggers section of the configuration
    to the specified logging level.

    Args:
        logging_config (dict): The logging configuration dictionary containing logger settings.
        level (Union[int, str]): The logging level to set for all loggers (e.g., 'DEBUG', 'INFO').
    """
    for _, logger in logging_config.get("loggers", {}).items():
        logger["level"] = level


def setup_logging(logging_config: dict):
    """
    Set up the logging system using the provided configuration dictionary.

    This function applies the logging configuration using `logging.config.dictConfig`.

    Args:
        logging_config (dict): The logging configuration dictionary to use for setting up logging.
    """
    logging.config.dictConfig(logging_config)
