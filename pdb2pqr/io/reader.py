"""Abstract class for implementing input readers"""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Tuple

from .pdb_record import BaseRecord


class Reader(ABC):
    """Abstract base class for reader."""

    @abstractmethod
    def read(self, file_path: Path) -> Tuple[List[BaseRecord], List[str]]:
        """Read an input file into lists of PDB record and error objects

        :param file_path:  path to input file
        :type file_path:  str

        :return:  Lists of PDB and ERROR objects read from input file
        :rtype:  Tuple[List[BaseRecord], List[str]]
        """
