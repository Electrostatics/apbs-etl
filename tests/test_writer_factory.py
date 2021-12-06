"""This file tests the input factories."""
from difflib import Differ
from logging import getLogger
from pathlib import Path
from typing import List
import pytest

from pdb2pqr.io.factory import input_factory, output_factory
from pdb2pqr.io.pdb_record import BaseRecord
from .common import INPUT_DIR, REF_DIR

_LOGGER = getLogger(__name__)


@pytest.mark.parametrize(
    "input_file, output_file, expected_error",
    [
        pytest.param(
            "1FAS.cif", "1FAS.pqr", NotImplementedError, id="1FAS.cif -> pqr"
        ),
        pytest.param(
            "3U7T.cif", "3U7T.pqr", NotImplementedError, id="3U7T.cif -> pqr"
        ),
        pytest.param("1AFS.pdb", "1AFS.pdb", None, id="1AFS.pdb -> pdb"),
        pytest.param(
            "1AFS.pdb", "1AFS.pqr", NotImplementedError, id="1AFS.pdb -> pqr"
        ),
    ],
)
def test_data_file_write(
    tmp_path, input_file: str, output_file: str, expected_error
):
    """Test data file input."""

    input_path = INPUT_DIR / Path(input_file)
    reference_path = REF_DIR / Path(output_file)
    output_path: Path = tmp_path / Path(output_file)
    reader = input_factory(input_path.suffix)
    writer = output_factory(output_path.suffix)
    pdblist: List[BaseRecord] = []
    errlist: List[str] = []

    if expected_error is not None:
        with pytest.raises(expected_error):
            pdblist, errlist = reader.read(input_path)
            writer.write(output_path, pdblist)
    else:
        pdblist, errlist = reader.read(input_path)
        writer.write(output_path, pdblist)

        _LOGGER.info(f"Reading output file: {output_path}...")
        output_lines = [line.strip() for line in open(str(output_path), "rt")]

        _LOGGER.info(f"Reading reference file: {reference_path}...")
        reference_lines = [
            line.strip() for line in open(str(reference_path), "rt")
        ]

        differ = Differ()
        differences = [
            line
            for line in differ.compare(output_lines, reference_lines)
            if line[0] != " "
        ]

        if differences:
            for diff in differences:
                _LOGGER.error(f"Found difference:  {diff}")
            # raise ValueError()
        assert not differences

        _LOGGER.info("No differences found in output")
