"""This file handles the reading PDB files into appropriate containers."""
from pathlib import Path
from typing import List
from pdbx.containers import DataContainer

from .pdb_record import read_pdb

from .reader import Reader


class PDBReader(Reader):
    """Factory class to handle reading PDB input files."""

    def __init__(self):
        pass

    def read(self, file_path: Path) -> List[DataContainer]:
        """Read a PDB file into mmcif_pdbx container"""
        data_containers: List[DataContainer] = []

        # TODO: Convert pdblist to DataContainer
        raise NotImplementedError
        pdblist, errlist = read_pdb(file_path)

        return data_containers


# reader = PDBReader()
# data = reader.read(Path('tests/data/1afs.pdb'))
# print(data)
