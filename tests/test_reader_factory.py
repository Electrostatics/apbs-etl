"""This file tests the input factories."""
from pathlib import Path
from typing import List
import pytest
from pdbx.containers import DataCategory, DataContainer

from pdb2pqr.io.factory import input_factory
from .common import INPUT_DIR


@pytest.mark.parametrize(
    "input_file, expected_error, expected_record_count",
    [
        pytest.param("1FAS.cif", None, 575, id="1FAS.cif"),
        pytest.param("3U7T.cif", None, 721, id="3U7T.cif"),
        pytest.param("1AFS.pdb", NotImplementedError, None, id="1AFS.pdb"),
    ],
)
def test_data_file(input_file, expected_error, expected_record_count):
    """Test data file input."""

    input_path = INPUT_DIR / Path(input_file)
    reader = input_factory(input_path.suffix)
    data_list = []

    if expected_error is not None:
        with pytest.raises(expected_error):
            data_list: List[DataContainer] = reader.read(input_path)
    else:
        data_list: List[DataContainer] = reader.read(input_path)

    for item in data_list:
        atom_site_category: DataCategory = item.get_object("atom_site")
        print(atom_site_category.print_it())
        assert len(atom_site_category.get()[2]) == expected_record_count
