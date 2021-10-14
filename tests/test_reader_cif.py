from pytest import mark
from pathlib import Path
from pdb2pqr.io.reader_cif import CIFReader

DATA_DIR = Path(__file__).parent.absolute() / "data"


@mark.parametrize("input_cif", ["1FAS.cif", "3U7T.cif"], ids=str)
def test_data_file(input_cif):
    """Test data file input."""

    reader = CIFReader()

    input_path = DATA_DIR / Path(input_cif)
    data_list = reader.read(input_path)
    for item in data_list:
        print(item.get_object("atom_site").print_it())
