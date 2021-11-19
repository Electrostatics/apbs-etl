"""This file handles the reading QCD files into appropriate containers."""

from io import FileIO
from typing import List

from ..chemistry import Atom


def read_qcd(qcd_file: FileIO) -> List[Atom]:
    """Read QCD (UHDB QCARD format) file.

    :param file qcd_file:  file object ready for reading as text
    :returns:  list of atoms read from file
    :rtype:  List[Atom]
    """
    atoms: List[Atom] = []
    atom_serial = 1
    for line in qcd_file:
        atom = get_atom_from_qcd_line(line, atom_serial)
        if atom is not None:
            atoms.append(atom)
            atom_serial += 1
    return atoms


def get_atom_from_qcd_line(line: str, atom_serial: int) -> Atom:
    """Create an atom from a QCD (UHBD QCARD format) line.

    :param str line:  QCD line
    :param int atom_serial:  atom serial number
    :returns:  new atom or None (for REMARK and similar lines)
    :rtype:  Atom
    :raises ValueError:  for problems parsing
    """
    atom = Atom()
    words = [w.strip() for w in line.split()]
    token = words.pop(0)
    if token in [
        "REMARK",
        "TER",
        "END",
        "HEADER",
        "TITLE",
        "COMPND",
        "SOURCE",
        "KEYWDS",
        "EXPDTA",
        "AUTHOR",
        "REVDAT",
        "JRNL",
    ]:
        return None
    if token in ["ATOM", "HETATM"]:
        atom.type = token
    elif token[:4] == "ATOM":
        atom.type = "ATOM"
        words = [token[4:]] + words
    elif token[:6] == "HETATM":
        atom.type = "HETATM"
        words = [token[6:]] + words
    else:
        err = f"Unable to parse line: {line}"
        raise ValueError(err)
    atom.serial = int(atom_serial)
    atom.res_seq = int(words.pop(0))
    atom.res_name = words.pop(0)
    atom.name = words.pop(0)
    atom.x = float(words.pop(0))
    atom.y = float(words.pop(0))
    atom.z = float(words.pop(0))
    atom.charge = float(words.pop(0))
    atom.radius = float(words.pop(0))
    return atom
