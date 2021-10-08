"""This file deals with parsing command line arguments and validating them."""

import sys
from pathlib import Path
from logging import getLogger
from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser, Namespace
import propka.lib
from .config import VERSION, ForceFields, LogLevels, TitrationMethods

_LOGGER = getLogger(f"PDB2PQR {VERSION}")


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

    # TODO: Should we bail if multiple options present, instead of override?
    required_options = parser.add_argument_group(
        title="Mandatory options",
        description="One of the following options must be used",
    )
    required_options.add_argument(
        "--ff",
        choices=ForceFields.values(),
        default=ForceFields.PARSE,
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
        default=ForceFields.PARSE,
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

    # Define titration state arguments
    titration_options = parser.add_argument_group(
        title="pKa options", description="Options for titration calculations"
    )
    titration_options.add_argument(
        "--titration-state-method",
        dest="pka_method",
        choices=TitrationMethods.values(),
        default=TitrationMethods.PROPKA,
        type=str.lower,
        help=(
            "Method used to calculate titration states. If a titration state "
            "method is selected, titratable residue charge states will be set "
            "by the pH value supplied by --with_ph"
        ),
    )
    titration_options.add_argument(
        "--with-ph",
        dest="ph",
        type=float,
        action="store",
        default=7.0,
        help=(
            "pH values to use when applying the results of the selected pH "
            "calculation method."
        ),
    )

    # Import PROPKA arguments into parser
    parser = propka.lib.build_parser(parser)

    # Fix log flag placement
    parser.add_argument(
        "--log-level",
        help="Logging level",
        default=LogLevels.INFO,
        choices=LogLevels.values(),
    )

    # Override version flag set by PROPKA
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {VERSION}"
    )

    args = None
    try:
        # TODO: Can we get parse_args to return something other than Namespace?
        args = parser.parse_args()
    except Exception as err:
        _LOGGER.error("ERROR in cli parsing: %s", err)
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
    return args


def check_files(args: Namespace):
    """Check for other necessary files.

    :param args:  command-line arguments
    :type args:  argparse.Namespace
    :raises FileNotFoundError:  necessary files not found
    :raises RuntimeError:  input argument or file parsing problems
    """
    if args.usernames is not None:
        usernames = Path(args.usernames)
        if not usernames.is_file():
            error = f"User-provided names file does not exist: {usernames}"
            raise FileNotFoundError(error)

    if args.userff is not None:
        userff = Path(args.userff)
        if not userff.is_file():
            error = f"User-provided forcefield file does not exist: {userff}"
            raise FileNotFoundError(error)
        if args.usernames is None:
            err = "--usernames must be specified if using --userff"
            raise RuntimeError(err)
    elif args.ff is not None:
        # TODO bring back the following: io.test_dat_file(args.ff)
        pass

    if args.ligand is not None:
        ligand = Path(args.ligand)
        if not ligand.is_file():
            error = f"Unable to find ligand file: {ligand}"
            raise FileNotFoundError(error)


def check_options(args: Namespace):
    """Sanity check options.

    :param args:  command-line arguments
    :type args:  argparse.Namespace
    :raises RuntimeError:  silly option combinations were encountered.
    """
    if (args.ph < 0) or (args.ph > 14):
        err = (
            f"Specified pH ({args.ph}) is outside the range "
            "[1, 14] of this program"
        )
        raise RuntimeError(err)
    # TODO: Wouldn't "args.ff != PARSE" cover the "args.ff is None" case, too?
    if args.neutraln and (args.ff is None or args.ff != ForceFields.PARSE):
        err = "--neutraln option only works with PARSE forcefield!"
        raise RuntimeError(err)
    if args.neutralc and (args.ff is None or args.ff != ForceFields.PARSE):
        err = "--neutralc option only works with PARSE forcefield!"
        raise RuntimeError(err)


def validate(args: Namespace):
    """TODO: Add docs"""
    _LOGGER.info("Checking and transforming input arguments.")
    args = transform_arguments(args)
    check_files(args)
    check_options(args)


def process_cli() -> Namespace:
    """TODO: Add docs"""
    args: Namespace = get_cli_args()
    validate(args)
    return args
