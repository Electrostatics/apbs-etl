"""
This tests the dx entrypoint executable.
"""

from logging import getLogger
from difflib import Differ
from .common import INPUT_DIR

from pdb2pqr.io import read_pqr, read_dx, write_cube


_LOGGER = getLogger(__name__)


def test_dx2cube(tmp_path):
    """Test conversion of OpenDX files to Cube files."""

    pqr_path = INPUT_DIR / "dx2cube.pqr"
    dx_path = INPUT_DIR / "dx2cube.dx"
    cube_gen = tmp_path / "test.cube"
    cube_test = INPUT_DIR / "dx2cube.cube"

    _LOGGER.info("Reading PQR from %s...", pqr_path)
    with open(pqr_path, "rt") as pqr_file:
        atom_list = read_pqr(pqr_file)

    _LOGGER.info("Reading DX from %s...", dx_path)
    with open(dx_path, "rt") as dx_file:
        dx_dict = read_dx(dx_file)

    _LOGGER.info("Writing Cube to %s...", cube_gen)
    with open(cube_gen, "wt") as cube_file:
        write_cube(cube_file, dx_dict, atom_list)

    _LOGGER.info("Reading this cube from %s...", cube_gen)
    this_lines = [line.strip() for line in open(cube_gen, "rt")]

    _LOGGER.info("Reading test cube from %s...", cube_test)
    test_lines = [line.strip() for line in open(cube_test, "rt")]

    differ = Differ()
    differences = [
        line
        for line in differ.compare(this_lines, test_lines)
        if line[0] != " "
    ]

    if differences:
        for diff in differences:
            _LOGGER.error("Found difference:  %s", diff)
        # raise ValueError()
    assert not differences

    _LOGGER.info("No differences found in output")
