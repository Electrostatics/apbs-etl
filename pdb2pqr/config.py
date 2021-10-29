"""Configuration information for PDB2PQR."""
import logging
from collections import Counter
from enum import Enum
from pathlib import Path
from ._version import VERSION

_LOGGER = logging.getLogger(__name__)

#: How to format PDB2PQR title in output
TITLE_STR = f"PDB2PQR v{VERSION}: biomolecular structure conversion software."


class BaseEnum(Enum):
    """Base class for enumerables, defining common methods."""

    @classmethod
    def values(cls) -> list:
        """Generates list of the Enum values

        :return:  List of enum values
        :rtype:  List[T]
        """
        return [member.value for member in cls]

    def __str__(self):
        return str(self.value)

    # def __eq__(self, o: object) -> bool:
    #     return self.value == o


class FilePermission(BaseEnum):
    """Enumerate file permissions operations."""

    READ = 1
    WRITE = 2


class LogLevels(BaseEnum):
    """Enumerate log levels."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class ForceFields(BaseEnum):
    """Enumerate built-in forcefield types."""

    AMBER = "amber"
    CHARMM = "charmm"
    PARSE = "parse"
    TYL06 = "tyl06"
    PEOEPB = "peoepb"
    SWANSON = "swanson"


class TitrationMethods(BaseEnum):
    """Enumerate titration-state methods."""

    PROPKA = "propka"


class ApbsCalcType(BaseEnum):
    """Enumerate APBS Elec calcuation types."""

    MG_AUTO = "mg-auto"
    MG_PARA = "mg-para"
    MG_MANUAL = "mg-manual"


"""Logging"""


class DuplicateFilter(logging.Filter):
    """Filter duplicate messages."""

    def __init__(self):
        super().__init__()
        self.warn_count = Counter()

    def filter(self, record):
        """Filter current record."""
        if record.levelname == "WARNING":
            #: The start of warning strings to be filtered.
            filter_warnings = [
                "Skipped atom during water optimization",
                "The best donorH was not picked",
                "Multiple occupancies found",
            ]

            # Number of times warning string is printed before supressing
            # further output
            filter_warnings_limit = 10

            for fwarn in filter_warnings:
                if record.getMessage().startswith(fwarn):
                    self.warn_count.update([fwarn])
                    if self.warn_count[fwarn] > filter_warnings_limit:
                        return False
                    elif self.warn_count[fwarn] == filter_warnings_limit:
                        _LOGGER.warning(
                            f'Suppressing further "{fwarn}" messages'
                        )
                        return False
                    else:
                        return True
        return True


def setup_logger(output_filename, level="DEBUG"):
    """Setup the logger.

    Setup logger to output the log file to the same directory as the
    output file.

    :param str output_filename:  path to the output file
    :param str level:  logging level
    """
    # Get the output logging location
    output_path = Path(output_filename)
    log_file = Path(output_path.parent, output_path.stem + ".log")
    log_format = (
        "%(asctime)s %(levelname)s:%(filename)s:"
        "%(lineno)d:%(funcName)s:%(message)s"
    )
    logging.basicConfig(
        filename=log_file,
        format=log_format,
        level=getattr(logging, level),
    )
    console = logging.StreamHandler()
    formatter = logging.Formatter("%(levelname)s:%(message)s")
    console.setFormatter(formatter)
    console.setLevel(level=getattr(logging, level))
    logging.getLogger("").addHandler(console)
    logging.getLogger("").addFilter(DuplicateFilter())

    _LOGGER.info(f"Logs stored: {log_file}")
