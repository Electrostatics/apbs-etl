"""General utility functions."""
from typing import List

from ..config import AtomType
from ..io.pdb_record import BaseRecord


def get_atom_list(record_list: List[BaseRecord]) -> List[BaseRecord]:
    """Return list of records filtered on AtomType

    :param record_list: List of PDB records
    :type record_list: List[BaseRecord]
    :return: List of records filtered on AtomType
    :rtype: List[BaseRecord]
    """
    return [x for x in record_list if x.record_type in AtomType.values()]
