from pdb2pqr.io.reader_cif import CIFReader
from pdb2pqr.io.reader_pdb import PDBReader


def InputFactory(reader="pdb"):
    readers = {
        "pdb": PDBReader,
        "cif": CIFReader,
    }

    return readers[reader]()


def OutputFactory(reader="pqr"):
    readers = {
        # "pdb": PDBReader,
        # "cif": CIFReader,
    }

    return readers[reader]()
