"""This file handles the reading PDB files into appropriate containers."""
from pdbx import load
from pdbx.containers import DataContainer
from pathlib import Path
from typing import List


class PDBReader:
    def __init__(self):
        pass

    def read(self, file_path: Path) -> List[DataContainer]:
        """Read a PDB file into mmcif_pdbx container"""
        pass
        # mmcif_pdbx_data = []
        # with file_path.open() as fin:
        #     mmcif_pdbx_data = load(fin)

        # return mmcif_pdbx_data


# reader = PDBReader()
# data = reader.read(Path('tests/data/1afs.pdb'))
# print(data)
