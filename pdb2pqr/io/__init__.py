"""Generic functions used for input and output."""

from pathlib import Path
from typing import List

from pdbx.containers import DataContainer

from .factory import input_factory


def read_input(inputfile_path: str) -> List[DataContainer]:
    """Read and parse input files using the appropriate factory class.

    :param inputfile_path: Path to the input file to read
    :type inputfile_path: str

    :return:  List of pdbx DataContainer objects
    :rtype:  List[DataContainer]
    """
    file_path = Path(inputfile_path)
    reader = input_factory(file_path.suffix)
    data_containers: List[DataContainer] = reader.read(file_path)

    return data_containers
