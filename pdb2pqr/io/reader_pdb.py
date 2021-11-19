"""This file handles the reading PDB files into appropriate containers."""
from pathlib import Path
from typing import List, Tuple

from .pdb_record import BaseRecord, read_pdb
from .reader import Reader


class PDBReader(Reader):
    """Factory class to handle reading PDB input files."""

    def __init__(self):
        pass

    def read(self, file_path: Path) -> Tuple[List[BaseRecord], List[str]]:
        """Read a PDB file into lists of PDB record and error objects

        :param file_path:  path to CIF file
        :type file_path:  str

        :return:  List of PDB and ERROR objects read from input file
        :rtype:  Tuple[List[BaseRecord], List[str]]
        """
        with open(file_path) as fin:
            return read_pdb(fin)
