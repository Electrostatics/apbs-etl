"""This file handles the reading CIF files into appropriate containers."""
from pathlib import Path
from typing import List

from pdbx import load
from pdbx.containers import DataContainer

from .reader import Reader


class CIFReader(Reader):
    """Factory class to handle reading CIF input files."""

    def __init__(self):
        pass

    def read(self, file_path: Path) -> List[DataContainer]:
        """Read a CIF file into mmcif_pdbx container

        :param file_path:  path to CIF file
        :type file_path:  str

        :return:  List of DataContainer objects read from CIF file
        :rtype:  List[DataContainer]
        """
        mmcif_pdbx_data = []
        with file_path.open() as fin:
            mmcif_pdbx_data = load(fin)

        return mmcif_pdbx_data
