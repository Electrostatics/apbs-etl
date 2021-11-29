"""PDB2PQR

This package takes a PDB file as input and performs optimizations before
yielding a new PDB-style file as output.

For more information, see http://www.poissonboltzmann.org/
"""
import logging
from sys import version_info
from ._version import __version__  # noqa: F401
from .pdb2pqr import main


_LOGGER = logging.getLogger(__name__)


# TODO: update minimum required version to 3.7
assert version_info >= (3, 5)
logging.captureWarnings(True)


if __name__ == "__main__":
    main()
