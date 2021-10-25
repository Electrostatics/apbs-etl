"""
TODO:   No tests for inputgen.py in old repo. Current coverage is
        based on testing the --apbs-input flag in PDB2PQR.
"""

import pytest
from .common import DATA_DIR, get_ref_output
from pdb2pqr.config import FilePermission
from pdb2pqr.inputgen import Input, get_cli_args
from pdb2pqr.process_cli import check_file
from pdb2pqr.psize import Psize


@pytest.mark.parametrize(
    "arguments, output_file",
    [
        pytest.param(f"{DATA_DIR}/dx2cube.pqr", "intputgen_1.out", id="1"),
        # pytest.param(f"{DATA_DIR}/1AFS_ff=AMBER.pqr", "intputgen_2.out", id="2"),
    ],
)
def test_inputgen(arguments: str, output_file: str):
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
        args.method,
        args.asynch,
        args.istrng,
        args.potdx,
    )
    # input_.print_input_files(output_file)

    assert str(input_) == get_ref_output(output_file)
