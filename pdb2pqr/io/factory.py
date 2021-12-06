"""Functions for providing input/output factories."""
from .reader_cif import CIFReader
from .reader_pdb import PDBReader
from .reader import Reader


def input_factory(reader_type: str = "pdb") -> Reader:
    """Provides the reader based on the input file extension.

    :param reader_type: File extension indicating with reader to use
    :type reader_type: str

    :return:  Reader object for a given input factory
    :rtype:  Reader
    """
    reader_type = reader_type.replace(".", "", 1).lower()

    # KeyError will kill process here
    readers = {
        "pdb": PDBReader,
        "cif": CIFReader,
    }

    return readers[reader_type]()


def output_factory(writer_format="pqr"):
    """Provides the writer based on the output format.

    :param writer_format: Format indicating with writer to use
    :type writer_format: str

    :return:  Writer object for a given output factory
    :rtype:  Writer
    """
    writers = {
        # "pdb": PDBWriter,
        # "cif": CIFWriter,
    }

    return writers[writer_format]()
