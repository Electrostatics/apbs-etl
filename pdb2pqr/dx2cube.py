"""Convert DX file format to Cube file format."""

from argparse import (
    ArgumentDefaultsHelpFormatter,
    ArgumentError,
    ArgumentParser,
    Namespace,
)
import logging
import sys

from pdb2pqr.process_cli import check_file
from .config import TITLE_STR, VERSION, FilePermission, LogLevels
from .io.dx import read_dx, write_cube
from .io.reader_pqr import read_pqr

_LOGGER = logging.getLogger(f"dx2cube {VERSION}")


def get_cli_args(args_str: str = None) -> Namespace:
    """Define and parse command line arguments via argparse.

    :param args_str: String representation of command line arguments
    :type args_str: str

    :return:  Parsed arguments object
    :rtype:  argparse.Namespace
    """
    desc = f"{TITLE_STR}\ndx2cube: converting OpenDX-format files to "
    desc += "Gaussian Cube format since (at least) 2015"
    parser = ArgumentParser(
        description=desc,
        formatter_class=ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("dx_input", type=str, help="Name of the DX input file")
    parser.add_argument(
        "pqr_input", type=str, help="Name of the PQR input file"
    )
    parser.add_argument("output", type=str, help="Name of the output file")
    parser.add_argument(
        "--log-level",
        help="Set logging level",
        default=str(LogLevels.INFO),
        choices=LogLevels.values(),
        type=str,
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


def main():
    """Convert DX file format to Cube file format.

    The OpenDX file format is defined at
    <https://www.idvbook.com/wp-content/uploads/2010/12/opendx.pdf` and the
    Cube file format is defined at
    <https://docs.chemaxon.com/display/Gaussian_Cube_format.html>.

    .. todo:: This function should be moved into the APBS code base.
    """
    args: Namespace = get_cli_args()
    check_file(args.pqr_input)
    check_file(args.dx_input)
    check_file(args.output, permission=FilePermission.WRITE, overwrite=False)

    log_level = getattr(logging, args.log_level.name)
    logging.basicConfig(level=log_level)
    _LOGGER.debug("Got arguments: %s", args)
    _LOGGER.info("Reading PQR from %s...", args.pqr_input)

    # TODO: use try/except to catch/log permission-based exceptions
    with open(args.pqr_input, "rt", encoding="utf-8") as pqr_file:
        atom_list = read_pqr(pqr_file)

    _LOGGER.info("Reading DX from %s...", args.dx_input)
    with open(args.dx_input, "rt", encoding="utf-8") as dx_file:
        dx_dict = read_dx(dx_file)

    _LOGGER.info("Writing Cube to %s...", args.output)
    with open(args.output, "wt", encoding="utf-8") as cube_file:
        write_cube(cube_file, dx_dict, atom_list)


if __name__ == "__main__":
    main()
