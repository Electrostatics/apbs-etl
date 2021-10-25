"""
TODO:   No tests for inputgen.py in old repo. Current coverage is
        based on testing the --apbs-input flag in PDB2PQR.
"""

from pathlib import Path
import pytest
from .common import INPUT_DIR, get_ref_output
from pdb2pqr.config import FilePermission
from pdb2pqr.inputgen import Input, get_cli_args, split_input
from pdb2pqr.process_cli import check_file
from pdb2pqr.psize import Psize



@pytest.mark.parametrize(
    "arguments, output_file, method",
    [
        pytest.param(f"{INPUT_DIR}/dx2cube.pqr", "inputgen_1.in", "mg-auto", id="1"),
        pytest.param(f"{INPUT_DIR}/1AFS_ff=AMBER.pqr --asynch", "inputgen_2-para.in", "mg-para", id="2"),
        # pytest.param(f"{DATA_DIR}/1AFS_ff=AMBER.pqr", "intputgen_2.out", id="2"),
    ],
)
def test_inputgen(tmp_path, arguments: str, output_file: str, method):
    """Test the Psize execution.

    :param arguments: String representation of command line arguments
    :type arguments: str
    :param output_file: Reference file to compare results against
    :type output_file: str

    """

    args = get_cli_args(arguments)
    check_file(
        output_file, permission=FilePermission.WRITE, overwrite=False
    )

    size = Psize()
    size.run_psize(args.filename)
    input_ = Input(
        args.filename,
        size,
        method,
        args.asynch,
        args.istrng,
        args.potdx,
    )

    output_path = tmp_path / output_file.replace("-para", "")
    outfile_list = input_.print_input_files(str(output_path))

    for file_path in outfile_list:
        with open(file_path) as output_fin:
            print(file_path)
            assert output_fin.read() == get_ref_output(Path(file_path).name)


@pytest.mark.parametrize(
    "arguments",
    [
        pytest.param(f"{INPUT_DIR}/dx2cube.pqr --split", id="1"),
    ]
)
def test_split_input(arguments):

    args = get_cli_args(arguments)

    with pytest.raises(RuntimeError):
        split_input(args.filename)
