import logging
import logging.config


def get_logger(*name_parts) -> logging.Logger:
    logger_name = ".".join(name_parts)
    return logging.getLogger(logger_name)


def update_loggers_level(config: dict, level: str):
    for _, logger in config["loggers"].items():
        logger["level"] = level


def configure_logging(config: dict):
    logging.config.dictConfig(config)
