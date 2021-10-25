"""
This tests the dx entrypoint executable.
"""

import pytest
from logging import getLogger
from difflib import Differ
from .common import INPUT_DIR

# from pdb2pqr.io import read_pqr, read_dx, write_cube, read_qcd

_LOGGER = getLogger(__name__)


@pytest.mark.xfail(raises=NotImplementedError)
def test_dx2cube(tmp_path):
    """Test conversion of OpenDX files to Cube files."""

    pqr_path = INPUT_DIR / "dx2cube.pqr"
    dx_path = INPUT_DIR / "dx2cube.dx"
    cube_gen = tmp_path / "test.cube"
    cube_test = INPUT_DIR / "dx2cube.cube"
    _LOGGER.info(f"Reading PQR from {pqr_path}...")

    raise NotImplementedError

    with open(pqr_path, "rt") as pqr_file:
        # TODO: import function from PDB2PQR repo
        # atom_list = read_pqr(pqr_file)
        pass
    _LOGGER.info(f"Reading DX from {dx_path}...")
    with open(dx_path, "rt") as dx_file:
        # TODO: import function from PDB2PQR repo
        # dx_dict = read_dx(dx_file)
        pass
    _LOGGER.info(f"Writing Cube to {cube_gen}...")
    with open(cube_gen, "wt") as cube_file:
        # TODO: import function from PDB2PQR repo
        # write_cube(cube_file, dx_dict, atom_list)
        pass
    _LOGGER.info(f"Reading this cube from {cube_gen}...")
    this_lines = [line.strip() for line in open(cube_gen, "rt")]
    _LOGGER.info(f"Reading test cube from {cube_test}...")
    test_lines = [line.strip() for line in open(cube_test, "rt")]
    differ = Differ()
    differences = [
        line
        for line in differ.compare(this_lines, test_lines)
        if line[0] != " "
    ]

    if differences:
        for diff in differences:
            _LOGGER.error(f"Found difference:  {diff}")
        raise ValueError()
    _LOGGER.info("No differences found in output")
