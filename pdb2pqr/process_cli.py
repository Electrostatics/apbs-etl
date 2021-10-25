"""This file deals with parsing command line arguments and validating them."""

import sys
from os import R_OK, access, W_OK
from pathlib import Path
from logging import getLogger
from argparse import (
    ArgumentDefaultsHelpFormatter,
    ArgumentError,
    ArgumentParser,
    Namespace,
)
import propka.lib
from .config import (
    TITLE_STR,
    VERSION,
    FilePermission,
    ForceFields,
    LogLevels,
    TitrationMethods,
    setup_logger
)

_LOGGER = getLogger(f"PDB2PQR {VERSION}")


class EmptyFileError(Exception):
    """Exception raised if file is empty (0 bytes).

    :param message: Error message for exception
    :type message: str
    """

    # Based on:
    #   https://pycodequ.al/docs/pylint-messages/w0235-useless-super-delegation.html
    ...


def get_cli_args(args_str: str = None) -> Namespace:
    """Define and parse command line arguments via argparse.

    :param args_str: String representation of command line arguments
    :type args_str: str

    :return:  Parsed arguments object
    :rtype:  argparse.Namespace
    """

    # Define primary PDB2PQR arguments
    parser = ArgumentParser(
        prog="pdb2pqr",
        description=TITLE_STR,
        formatter_class=ArgumentDefaultsHelpFormatter,
        conflict_handler="resolve",
    )
    parser.add_argument(
        "input_path",
        help="Input PDB path or ID (to be retrieved from RCSB database",
    )
    parser.add_argument("output_pqr", help="Output PQR path")

    required_options = parser.add_argument_group(
        title="Mandatory options",
        description="One of the following options must be used",
    )
    required_options.add_argument(
        "--ff",
        choices=ForceFields.values(),
        default=str(ForceFields.PARSE),
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
        default=str(LogLevels.INFO),
        choices=LogLevels.values(),
    )

    # Override version flag set by PROPKA
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {VERSION}"
    )

    args = None
    try:
        if args_str:
            return parser.parse_args(args_str.split())
        args = parser.parse_args()
    except ArgumentError as err:
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
        _LOGGER.warning(
            "Found option(s) '--clean' or '--assign-only'. "
            "Disabling 'debump' and 'opt' options."
        )
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
        check_file(args.usernames, context="Checking User-provided names")

    if args.userff is not None:
        check_file(args.userff, context="Checking User-provided forcefield")

    elif args.ff is not None:
        # TODO bring back the following: io.test_dat_file(args.ff)
        pass

    if args.ligand is not None:
        check_file(args.ligand, context="Checking ligand")


def check_file(
    file_name: str,
    context: str = "Error",
    permission: FilePermission = FilePermission.READ,
    overwrite: bool = True,
):
    """Preliminary checks before running algorithm.

    :param file_name:  The path to a file
    :type file_name:  str
    :param permission:  The permissions to check against
    :type permission:  FilePermission
    :param overwrite:  Is it ok to overwrite file
    :type overwrite:  bool
    """
    file_path = Path(file_name)

    _LOGGER.debug("%s", context)

    # READ
    if permission == FilePermission.READ:
        # file must exist
        if not file_path.is_file():
            raise FileNotFoundError(f"{context}: File '{file_name}' cannot be found.")

        # file must be readable
        if not access(file_path, R_OK):
            raise PermissionError(f"{context}: Cannot read file, {file_path.absolute()}")

        # file must be nonzero
        size: int = file_path.stat().st_size
        if size == 0:
            raise EmptyFileError(f"{context}: File, '{file_name}', has {size} bytes.")

    # WRITE
    elif permission == FilePermission.WRITE:
        # Check if we have write access to directory:
        if not access(file_path.parent, W_OK):
            raise PermissionError(
                f"{context}: Cannot write to directory, {file_path.parent.absolute()}"
            )

        # File must not exist unless overwrite
        if not overwrite and file_path.is_file():
            raise FileExistsError(f"{context}: File, '{file_name}', already exists.")

        # Must have write access if attempting to overwrite
        if overwrite and file_path.is_file() and not access(file_path, W_OK):
            raise PermissionError(
                f"{context}: Cannot write to file, {file_path.absolute()}"
            )


def check_options(args: Namespace):
    """Sanity check options.

    :param args:  command-line arguments
    :type args:  argparse.Namespace
    :raises RuntimeError:  silly option combinations were encountered.
    """
    if (args.ph < 0) or (args.ph > 14):
        # TODO: Error message inconsistent with boundary check
        err = (
            f"Specified pH ({args.ph}) is outside the range "
            "[1, 14] of this program"
        )
        raise RuntimeError(err)
    if args.neutraln and args.ff != str(ForceFields.PARSE):
        err = "--neutraln option only works with PARSE forcefield!"
        raise RuntimeError(err)
    if args.neutralc and args.ff != str(ForceFields.PARSE):
        err = "--neutralc option only works with PARSE forcefield!"
        raise RuntimeError(err)
    if args.userff is not None and args.usernames is None:
        err = "--usernames must be specified if using --userff"
        raise RuntimeError(err)
    if args.usernames is not None and args.userff is None:
        err = "Specified --usernames without --userff file."
        raise RuntimeError(err)


def validate(args: Namespace):
    """Validate options from command line.

    :param args:  command-line arguments
    :type args:  argparse.Namespace
    """
    _LOGGER.info("Checking and transforming input arguments.")
    args = transform_arguments(args)
    check_files(args)
    check_options(args)


def process_cli() -> Namespace:
    """Processes command line arguments.

    :return:  Parsed arguments object
    :rtype:  argparse.Namespace
    """
    args: Namespace = get_cli_args()
    setup_logger(args.output_pqr, level=args.log_level)
    validate(args)
    return args
