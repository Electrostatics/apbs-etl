"""This file deals with parsing command line arguments and validating them."""

from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser, Namespace
from .config import VERSION, ForceFields
import sys


def get_cli_args() -> Namespace:
    """TODO: Add docs"""

    # Define primary PDB2PQR arguments
    parser = ArgumentParser(
        prog="pdb2pqr",
        description="TODO: Get global description here",
        formatter_class=ArgumentDefaultsHelpFormatter,
        conflict_handler="resolve",
    )
    parser.add_argument(
        "input_path",
        help="Input PDB path or ID (to be retrieved from RCSB database",
    )
    parser.add_argument(
        "--log-level",
        help="Logging level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
    )

    required_options = parser.add_argument_group(
        title="Mandatory options",
        description="One of the following options must be used",
    )
    required_options.add_argument(
        "--ff",
        choices=ForceFields.values(),
        default=ForceFields.PARSE.value,
        type=str.lower,
        help="The forcefield to use.",
    )
    required_options.add_argument(
        "--userff",
        help=(
            "The user-created forcefield file to use. Requires "
            "--usernames and overrides --ff"
        ),
    )
    required_options.add_argument(
        "--clean",
        action="store_true",
        default=False,
        help=(
            "Do no optimization, atom addition, or parameter assignment, "
            "just return the original PDB file in aligned format. Overrides "
            "--ff and --userff"
        ),
    )

    # General optional arguments
    general_options = parser.add_argument_group(title="General options")
    general_options.add_argument(
        "--nodebump",
        dest="debump",
        action="store_false",
        default=True,
        help="Do not perform the debumping operation",
    )
    general_options.add_argument(
        "--noopt",
        dest="opt",
        action="store_false",
        default=True,
        help="Do not perform hydrogen optimization",
    )
    general_options.add_argument(
        "--keep-chain",
        action="store_true",
        default=False,
        help="Keep the chain ID in the output PQR file",
    )
    general_options.add_argument(
        "--assign-only",
        action="store_true",
        default=False,
        help=(
            "Only assign charges and radii - do not add atoms, "
            "debump, or optimize."
        ),
    )
    general_options.add_argument(
        "--ffout",
        choices=ForceFields.values(),
        default=ForceFields.PARSE.value,
        type=str.lower,
        help=(
            "Instead of using the standard canonical naming scheme for "
            "residue and atom names, use the names from the given forcefield"
        ),
    )
    general_options.add_argument(
        "--usernames",
        help=(
            "The user-created names file to use. Required if using --userff"
        ),
    )
    general_options.add_argument(
        "--apbs-input",
        help=(
            "Create a template APBS input file based on the generated PQR "
            "file at the specified location."
        ),
    )
    general_options.add_argument(
        "--pdb-output",
        default=None,
        help=(
            "Create a PDB file based on input. This will be missing charges "
            "and radii"
        ),
    )
    general_options.add_argument(
        "--ligand",
        help=(
            "Calculate the parameters for the specified MOL2-format ligand at "
            "the path specified by this option."
        ),
    )
    general_options.add_argument(
        "--whitespace",
        action="store_true",
        default=False,
        help=(
            "Insert whitespaces between atom name and residue name, between x "
            "and y, and between y and z."
        ),
    )
    general_options.add_argument(
        "--neutraln",
        action="store_true",
        default=False,
        help=(
            "Make the N-terminus of a protein neutral (default is "
            "charged). Requires PARSE force field."
        ),
    )
    general_options.add_argument(
        "--neutralc",
        action="store_true",
        default=False,
        help=(
            "Make the C-terminus of a protein neutral (default is "
            "charged). Requires PARSE force field."
        ),
    )
    general_options.add_argument(
        "--drop-water",
        action="store_true",
        default=False,
        help="Drop waters before processing biomolecule.",
    )
    general_options.add_argument(
        "--include-header",
        action="store_true",
        default=False,
        help=(
            "Include pdb header in pqr file. WARNING: The resulting PQR file "
            "will not work with APBS versions prior to 1.5"
        ),
    )

    # Define PROPKA arguments

    # Override version flag set by PROPKA
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {VERSION}"
    )

    args = None
    try:
        # TODO: Can we get parse_args to return something other than Namespace?
        args = parser.parse_args()
    except Exception as err:
        # TODO: Added LOGGER code
        print("ERROR in cli parsing")
        sys.exit(1)
    return args


def transform_arguments(args: Namespace):
    """Transform arguments with logic not provided by argparse.

    .. todo::  I wish this could be done with argparse.

    :param args:  command-line arguments
    :type args:  argparse.Namespace
    :return:  modified arguments
    :rtype:  argparse.Namespace
    """
    if args.assign_only or args.clean:
        # TODO: This should check to debump or opt then Warn user and override
        args.debump = False
        args.opt = False
    # if args.userff is not None:
    #     args.userff = args.userff.lower()
    # elif args.ff is not None:
    #     args.ff = args.ff.lower()
    if args.ffout is not None:
        args.ffout = args.ffout.lower()
    return args


def check_files(args: Namespace):
    """TODO: Add docs"""
    pass


def check_options(args: Namespace):
    """TODO: Add docs"""
    pass


def validate(args: Namespace):
    """TODO: Add docs"""
    args = transform_arguments(args)
    check_files(args)
    check_options(args)


def process_cli() -> Namespace:
    """TODO: Add docs"""
    args: Namespace = get_cli_args()
    validate(args)
    print(args.ff)
    return args
