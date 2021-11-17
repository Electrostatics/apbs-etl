"""Generic functions used for input and output."""

from pathlib import Path
from typing import List, Tuple

from .factory import input_factory


def read_input(inputfile_path: str) -> Tuple[List[str], List[str]]:
    """Read and parse input files using the appropriate factory class.

    :param inputfile_path: Path to the input file to read
    :type inputfile_path: str

    :return:  List of PDB and ERROR objects
    :rtype:  Tuple[List[str], List[str]]
    """
    file_path = Path(inputfile_path)
    reader = input_factory(file_path.suffix)
    return reader.read(file_path)
