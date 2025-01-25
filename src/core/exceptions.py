class InvalidFileFormatError(ValueError):
    pass


class ConfigFileNotFoundError(FileNotFoundError):
    pass


class ExporterBootstrapError(Exception):
    pass
