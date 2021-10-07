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
        # type=str.lower,
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
