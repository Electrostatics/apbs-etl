from enum import Enum
from ._version import __version__

#: PDB2PQR version number.
VERSION = __version__


class BaseEnum(Enum):
    @classmethod
    def values(cls) -> list:
        return [member.value for member in cls]

    def __str__(self):
        return str(self.value)


class LogLevels(BaseEnum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class ForceFields(BaseEnum):
    AMBER = "amber"
    CHARMM = "charmm"
    PARSE = "parse"
    TYL06 = "tyl06"
    PEOEPB = "peoepb"
    SWANSON = "swanson"


class TitrationMethods(BaseEnum):
    PROPKA = "propka"
