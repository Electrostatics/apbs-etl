"""This file handles writing PQR files to specified file.
.. todo:: write tests for PQR writer
"""
from pathlib import Path
from typing import List

from .pdb_record import BaseRecord
from .writer import Writer


class PQRWriter(Writer):
    """Factory class to handle reading PDB input files."""

    def __init__(self):
        pass

    def write(self, file_path: Path, records: List[BaseRecord]):
        """Read a PDB file into lists of PDB record and error objects

        :param file_path:  path to PQR file
        :type file_path:  str
        :param records:  List of PDB records
        :type records:  List[BaseRecord]
        """

        raise NotImplementedError

        with open(file_path, "w", encoding="utf-8") as fin:
            for record in records:
                # if record in AtomType.values():
                fin.write(f"{record}\n")

        # TODO: Need to figure out how to handle this later due to Atom class
