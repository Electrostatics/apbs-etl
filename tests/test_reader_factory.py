"""This file tests the input factories."""
from pathlib import Path
from typing import List
import pytest

from pdb2pqr.io.factory import input_factory
from pdb2pqr.io.pdb_record import BaseRecord
from .common import INPUT_DIR


@pytest.mark.parametrize(
    "input_file, expected_error, expected_record_count",
    [
        pytest.param("1FAS.cif", NotImplementedError, None, id="1FAS.cif"),
        pytest.param("3U7T.cif", NotImplementedError, None, id="3U7T.cif"),
        pytest.param("1AFS.pdb", None, 5951, id="1AFS.pdb"),
    ],
)
def test_data_file_read(input_file, expected_error, expected_record_count):
    """Test data file input."""

    input_path = INPUT_DIR / Path(input_file)
    reader = input_factory(input_path.suffix)
    pdblist: List[BaseRecord] = []
    errlist: List[str] = []

    if expected_error is not None:
        with pytest.raises(expected_error):
            pdblist, errlist = reader.read(input_path)
    else:
        pdblist, errlist = reader.read(input_path)
        assert len(pdblist) == expected_record_count
