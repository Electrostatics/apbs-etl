"""Configuration information for PDB2PQR."""
from enum import Enum
from ._version import __version__

#: PDB2PQR version number.
VERSION = __version__


class BaseEnum(Enum):
    """Base class for enumerables, defining common methods."""
    @classmethod
    def values(cls) -> list:
        return [member.value for member in cls]

    def __str__(self):
        return str(self.value)


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
