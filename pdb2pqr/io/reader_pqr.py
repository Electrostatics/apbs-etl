from io import FileIO
from typing import List

from ..chemistry import Atom


def read_pqr(pqr_file: FileIO) -> List[Atom]:
    """Read PQR file.

    :param pqr_file:  file object ready for reading as text
    :type pqr_file:  file
    :returns:  list of atoms read from file
    :rtype:  List[Atom]
    """
    atoms: List[Atom] = []
    for line in pqr_file:
        atom = get_atom_from_pqr_line(line)
        if atom is not None:
            atoms.append(atom)
    return atoms


def get_atom_from_pqr_line(line: str) -> Atom:
    """Create an atom from a PQR line.

    :param line:  PQR line
    :type line:  str
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
    atom.serial = int(words.pop(0))
    atom.name = words.pop(0)
    atom.res_name = words.pop(0)
    token = words.pop(0)
    try:
        atom.res_seq = int(token)
    except ValueError:
        atom.chain_id = token
        atom.res_seq = int(words.pop(0))
    token = words.pop(0)
    try:
        atom.x = float(token)
    except ValueError:
        atom.ins_code = token
        atom.x = float(words.pop(0))
    atom.y = float(words.pop(0))
    atom.z = float(words.pop(0))
    atom.charge = float(words.pop(0))
    atom.radius = float(words.pop(0))
    return atom
