from pdbx import load
from pdbx.containers import DataContainer
from pathlib import Path
from typing import List


class CIFReader:
    def __init__(self):
        pass

    def read(self, file_path: Path) -> List[DataContainer]:
        """Read into mmcif_pdbx container"""
        mmcif_pdbx_data = []
        with file_path.open() as fin:
            mmcif_pdbx_data = load(fin)

        return mmcif_pdbx_data
