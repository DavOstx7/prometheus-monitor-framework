class InvalidFileFormatError(ValueError):
    """
    Exception raised when an invalid file format is encountered.

    Inherits from `ValueError` and is used to indicate that a file has an unsupported or invalid format.
    """
    pass


class ConfigFileNotFoundError(FileNotFoundError):
    """
    Exception raised when a configuration file cannot be found.

    Inherits from `FileNotFoundError` and is used to indicate that the specified configuration file
    does not exist or cannot be accessed.
    """
    pass


class ExporterBootstrapError(Exception):
    """
    Exception raised when there is an error during the exporter bootstrap process.

    This class is used to represent errors that occur when initializing or setting up an exporter.
    """
    pass
