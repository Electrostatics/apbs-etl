"""Configuration information for PDB2PQR."""
from enum import Enum
from ._version import VERSION

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
