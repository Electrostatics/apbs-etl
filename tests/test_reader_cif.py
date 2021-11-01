"""This file tests the PDB reader."""
from typing import List
from pdbx.containers import DataContainer
from pytest import mark
from pathlib import Path
from pdb2pqr.io.factory import input_factory
from .common import INPUT_DIR


@mark.parametrize("input_file", ["1FAS.cif", "3U7T.cif", "1AFS.pdb"], ids=str)
def test_data_file(input_file):
    """Test data file input."""

    input_path = INPUT_DIR / Path(input_file)
    reader = input_factory(input_path.suffix)

    data_list: List[DataContainer] = reader.read(input_path)
    for item in data_list:
        print(item.get_object("atom_site").print_it())
