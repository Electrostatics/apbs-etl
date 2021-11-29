"""Configuration information for PDB2PQR."""
import logging
from collections import Counter
from enum import Enum
from pathlib import Path
from ._version import VERSION

_LOGGER = logging.getLogger(__name__)

#: How to format PDB2PQR title in output
TITLE_STR = f"PDB2PQR v{VERSION}: biomolecular structure conversion software."
#: The number of Ångströms added to the molecular dimensions to determine the
#: find grid dimensions
FINE_GRID_ADD = 20.0
#: The fine grid dimensions are multiplied by this constant to calculate the
#: coarse grid dimensions
COARSE_GRID_FACTOR = 1.7
#: Desired fine grid spacing (in Ångströms)
GRID_SPACING = 0.50
#: Approximate memory usage (in bytes) can be estimated by multiplying the
#: number of grid points by this constant
BYTES_PER_GRID = 200
#: Maxmimum memory (in MB) to be used for a calculation
MEMORY_CEILING_MB = 400
#: The fractional overlap between grid partitions in a parallel focusing
#: calculation
PARTITION_OVERLAP = 0.1
#: The maximum factor by which a domain can be "shrunk" during a focusing
#: calculation
FOCUS_FACTOR = 0.25
#: The minimum length of a molecule (in Ångströms) in any direction
MIN_MOL_LENGTH = 0.1
#: The minimum number of points in a grid
MIN_GRID_POINTS = 33
#: Byte prefix conversion factor
PREFIX_CONVERT = 1024.0
#: The maximum accuracy of old PDB coordinates (no atom left behind when
#: partitioning).
MAX_PDB_ACCURACY = 0.001
#: Number of bytes for stored representation of floating point values
BYTES_STORED = 8.0 * 12.0
#:  Minimum number of multigrid levels
MIN_LEVELS = 4
#:  Charge of a chloride ion
CL_CHARGE = -1
#:  Solvated chloride radius (in ångströms)
CL_RADIUS = 1.815
#:  Charge of a sodium ion
NA_CHARGE = -1
#:  Solvated sodium radius (in ångströms)
NA_RADIUS = 1.875
#:  Dielectric of a solute due to only molecular polarizability
SOLUTE_DIELECTRIC = 2.0
#:  One potential value for the dielectric constant of water under standard
#:  conditions
SOLVENT_DIELECTRIC = 78.54
#:  Number of grid points per squared Ångström for dielectric surfaces
SURFACE_DENSITY = 10.0
#:  Solvent (water) molecule radius in Ångströms
SOLVENT_RADIUS = 1.4
#:  Window (in Ångströms) for spline-based dielectric surface definitions
SPLINE_WINDOW = 0.3
#:  Room temperature (in Kelvin)
ROOM_TEMPERATURE = 298.15
#:  Surface tension (in kJ mol^{-1} Å^{-2})
SURFACE_TENSION = 0.105


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


class AtomType(BaseEnum):
    """Enumerate atom types."""

    ATOM = "ATOM"
    HETATM = "HETATM"


class Backbone(BaseEnum):
    """Standard backbone atom names."""

    N = "N"
    CA = "CA"
    C = "C"
    O = "O"  # noqa: E741
    O2 = "O2"
    HA = "HA"
    HN = "HN"
    H = "H"
    TN = "tN"


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
                            'Suppressing further "%s" messages', fwarn
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

    _LOGGER.info("Logs stored: %s", log_file)
