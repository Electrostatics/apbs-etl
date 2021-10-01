"""PDB2PQR

This package takes a PDB or CIF input file and performs optimizations before
yielding a new output file in PQR or CIF format.

For more information, see http://www.poissonboltzmann.org/
"""

from logging import captureWarnings, getLogger
from sys import version_info
from .pdb2pqr import main

# DEVELOPER NOTE: This only ever gets called when a user types the following:
#   python -m pdb2pqr
#                 Therefore there is no automated test for this case

if __name__ == "__main__":
    assert version_info >= (3, 7)

    _LOGGER = getLogger(__name__)
    captureWarnings(True)

    main()
