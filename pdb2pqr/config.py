"""Configuration information for PDB2PQR."""
from enum import Enum
from ._version import __version__

#: PDB2PQR version number.
VERSION = __version__

#: How to format PDB2PQR title in output
TITLE_STR = f"PDB2PQR v{VERSION}: biomolecular structure conversion software."


class BaseEnum(Enum):
    """Base class for enumerables, defining common methods."""

    @classmethod
    def values(cls) -> list:
        return [member.value for member in cls]

    def __str__(self):
        return str(self.value)


class FilePermission(BaseEnum):
    READ = 1
    WRITE = 2


class LogLevels(BaseEnum):
    """Enumerate log levels for argument parser."""

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
    """Enumerate log levels for argument parser."""

    PROPKA = "propka"


class ApbsCalcType(BaseEnum):
    MG_AUTO = "mg-auto"
    MG_PARA = "mg-para"
    MG_MANUAL = "mg-manual"
