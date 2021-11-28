"""PDB2PQR

This package takes a PDB file as input and performs optimizations before
yielding a new PDB-style file as output.

For more information, see http://www.poissonboltzmann.org/
"""
import logging
from sys import version_info
from ._version import __version__  # noqa: F401
from .pdb2pqr import main

#: The number of Ångströms added to the molecular dimensions to determine the
#: find grid dimensions
FADD = 20.0

_LOGGER = logging.getLogger(__name__)


assert version_info >= (3, 5)
logging.captureWarnings(True)


if __name__ == "__main__":
    main()
