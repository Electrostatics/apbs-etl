"""This file handles the reading PDB files into appropriate containers."""
from pathlib import Path
from typing import List
from pdbx.containers import DataContainer


class PDBReader:
    """Factory class to handle reading PDB input files."""
    def __init__(self):
        pass

    def read(self, file_path: Path) -> List[DataContainer]:
        """Read a PDB file into mmcif_pdbx container"""


# reader = PDBReader()
# data = reader.read(Path('tests/data/1afs.pdb'))
# print(data)
