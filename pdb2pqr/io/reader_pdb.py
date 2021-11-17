"""This file handles the reading PDB files into appropriate containers."""
from pathlib import Path
from typing import List, Tuple

from .pdb_record import read_pdb

from .reader import Reader


class PDBReader(Reader):
    """Factory class to handle reading PDB input files."""

    def __init__(self):
        pass

    def read(self, file_path: Path) -> Tuple[List[str], List[str]]:
        """Read a PDB file into mmcif_pdbx container

        :param file_path:  path to CIF file
        :type file_path:  str

        :return:  List of PDB and ERROR objects read from input file
        :rtype:  Tuple[List[str], List[str]]
        """

        # TODO: Convert pdblist to DataContainer
        return read_pdb(file_path)
