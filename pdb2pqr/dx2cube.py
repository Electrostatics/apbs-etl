from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser, Namespace
import logging
from .config import TITLE_STR, VERSION, LogLevels

_LOGGER = logging.getLogger(f"PDB2PQR {VERSION}")


def get_cli_args() -> Namespace:
    """Define and parse command line arguments via argparse.

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
        default=LogLevels.INFO,
        choices=LogLevels.values(),
    )
    return parser.parse_args()


def main():
    """Convert DX file format to Cube file format.

    The OpenDX file format is defined at
    <https://www.idvbook.com/wp-content/uploads/2010/12/opendx.pdf` and the
    Cube file format is defined at
    <https://docs.chemaxon.com/display/Gaussian_Cube_format.html>.

    .. todo:: This function should be moved into the APBS code base.
    """
    args: Namespace = get_cli_args()
    log_level = getattr(logging, args.log_level)

    logging.basicConfig(level=log_level)
    _LOGGER.debug(f"Got arguments: {args}", args)
    _LOGGER.info(f"Reading PQR from {args.pqr_input}...")

    with open(args.pqr_input, "rt") as pqr_file:
        # atom_list = io.read_pqr(pqr_file)
        pass

    _LOGGER.info(f"Reading DX from {args.dx_input}...")
    with open(args.dx_input, "rt") as dx_file:
        # dx_dict = io.read_dx(dx_file)
        pass

    _LOGGER.info(f"Writing Cube to {args.output}...")
    with open(args.output, "wt") as cube_file:
        # io.write_cube(cube_file, dx_dict, atom_list)
        pass


if __name__ == "__main__":
    main()
