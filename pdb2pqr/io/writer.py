"""Abstract class for implementing writers"""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List

from .pdb_record import BaseRecord


class Writer(ABC):
    """Abstract base class for writer."""

    @abstractmethod
    def __init_(self):
        """Initialize Writer object"""

    @abstractmethod
    def write(self, file_path: Path, records: List[BaseRecord]):
        """Write an output using data from list of BaseRecord objects

        :param file_path:  path to output file
        :type file_path:  str
        :param records:  List of BaseRecords objects to write to file
        :type records:  List[BaseRecord]
        """
