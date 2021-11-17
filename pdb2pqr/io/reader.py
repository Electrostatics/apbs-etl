"""Abstract class for implementing input readers"""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Tuple


class Reader(ABC):
    """Abstract base class for reader."""

    @abstractmethod
    def read(self, file_path: Path) -> Tuple[List[str], List[str]]:
        """Read an input file into mmcif_pdbx container

        :param file_path:  path to input file
        :type file_path:  str

        :return:  List of PDB and ERROR objects read from input file
        :rtype:  Tuple[List[str], List[str]]
        """
