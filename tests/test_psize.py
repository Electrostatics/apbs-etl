"""
This tests the Psize entrypoint executable.
.. todo:: Add finer grain tests
"""

import pytest
from pdb2pqr.psize import Psize, get_cli_args
from .common import DATA_DIR, get_ref_output


@pytest.mark.parametrize(
    "arguments, output_file",
    [
        pytest.param(f"{DATA_DIR}/dx2cube.pqr", "psize_1.out", id="1"),
    ],
)
def test_psize(arguments: str, output_file: str):
    """Test the Psize execution.

    :param arguments: String representation of command line arguments
    :type arguments: str
    :param output_file: Reference file to compare results against
    :type output_file: str

    """
    args = get_cli_args(arguments)
    psize = Psize(
        cfac=args.cfac,
        fadd=args.fadd,
        space=args.space,
        gmemfac=args.gmemfac,
        gmemceil=args.gmemceil,
        ofrac=args.ofrac,
        redfac=args.redfac,
    )
    psize.run_psize(args.mol_path)

    assert str(psize) == get_ref_output(output_file)
