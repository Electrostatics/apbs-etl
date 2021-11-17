"""This file handles the reading CIF files into appropriate containers."""
from pathlib import Path
from typing import List, Tuple

from pdbx import load
from pdbx.containers import DataContainer

from .reader import Reader


class CIFReader(Reader):
    """Factory class to handle reading CIF input files."""

    def __init__(self):
        pass

    def read(self, file_path: Path) -> Tuple[List[str], List[str]]:
        """Read a CIF file into mmcif_pdbx container

        :param file_path:  path to CIF file
        :type file_path:  str

        :return:  List of PDB and ERROR objects read from input file
        :rtype:  Tuple[List[str], List[str]]
        """
        mmcif_pdbx_data: List[DataContainer] = []
        with file_path.open() as fin:
            mmcif_pdbx_data = load(fin)

        # TODO: We need to convert mmcif_pdbx_data.get_object['atom_site']
        #       to pdblist and errlist

        pdblist: List[str] = []
        errlist: List[str] = []

        return pdblist, errlist
