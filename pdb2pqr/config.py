from enum import Enum
from ._version import __version__

#: PDB2PQR version number.
VERSION = __version__


class BaseEnum(Enum):
    @classmethod
    def values(self) -> list:
        return [member.value for member in self]


class ForceFields(BaseEnum):
    AMBER = "amber"
    CHARMM = "charmm"
    PARSE = "parse"
    TYL06 = "tyl06"
    PEOEPB = "peoepb"
    SWANSON = "swanson"
