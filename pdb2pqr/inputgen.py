"""Create an APBS input file using :mod:`psize` data.

.. codeauthor::  Todd Dolinsky
.. codeauthor::  Nathan Baker
"""
import logging
import sys
from argparse import (
    ArgumentDefaultsHelpFormatter,
    ArgumentError,
    ArgumentParser,
    Namespace,
)
from pathlib import Path
from typing import List

from pdb2pqr.process_cli import check_file
from .psize import Psize, CFAC, FADD, SPACE, GMEMFAC, GMEMCEIL, OFRAC, REDFAC
from .config import ApbsCalcType, FilePermission, LogLevels, TITLE_STR
from .elec import Elec

_LOGGER = logging.getLogger(__name__)


class Input:
    """Each object of this class is one APBS input file."""

    def __init__(
        self, pqrpath, size, method, asyncflag, istrng=0, potdx=False
    ):
        """Initialize the input file class.

        Each input file contains a PQR name, a list of elec objects, and a
        list of strings containing print statements.
        For starters, assume two ELEC statements are needed, one for the
        inhomgenous and the other for the homogenous dielectric calculations.

        .. note::
            This assumes you have already run psize, either by
            :func:`size.run_psize(...)` or :func:`size.parse_string(...)`
            followed by :func:`size.set_all()`.

        :param pqrpath:  path to PQR file
        :type pqrpath:  str
        :param size:  parameter sizing object
        :type size:  Psize
        :param method:  solution method (e.g., mg-para, mg-auto, etc.)
        :type method:  str
        :param asyncflag:  perform an asynchronous parallel focusing
            calculation
        :type asyncflag:  bool
        :param istrng:  ionic strength/concentration (M)
        :type istring:  float
        :param potdx:  whether to write out potential information in DX format
        :type potdx:  bool
        """
        self.pqrpath = Path(pqrpath)
        self.pqrname = self.pqrpath.name
        pqr_stem: str = self.pqrpath.stem
        self.asyncflag = asyncflag
        # Initialize variables to default elec values
        elec1 = Elec(pqr_stem, method, size, asyncflag, istrng, potdx)
        if not potdx:
            elec2 = Elec(pqr_stem, method, size, asyncflag, istrng, potdx)
            setattr(elec2, "sdie", 2.0)
            setattr(elec2, "write", [])
        else:
            elec2 = ""
        self.elecs: List[Elec] = [elec1, elec2]
        if not potdx:
            self.prints = ["print elecEnergy 2 - 1 end"]
        else:
            self.prints = ["print elecEnergy 1 end"]

    def __str__(self):
        text = "read\n"
        text += f"    mol pqr {self.pqrname}\n"
        text += "end\n"
        for elec in self.elecs:
            text += str(elec)
        for prints in self.prints:
            text += prints
        text += "\nquit\n"
        return text

    def print_input_files(self, output_path) -> List[str]:
        """Generate the input file(s) associated with this object.

        :param output_path:  location for generated files
        :type output_path:  str
        """
        file_list = []
        path = Path(output_path)
        if self.asyncflag:
            base_name = path.stem
            outname = path.parent / f"{base_name}"
            # Temporarily disable async flag
            for elec in self.elecs:
                elec.asyncflag = False
            para_name = path.parent / f"{outname}-para.in"
            with open(para_name, "wt") as out_file:
                out_file.write(str(self))
            file_list.append(para_name)

            # Now make the async files
            file_list.extend(split_input(para_name, outname))

        else:
            with open(path, "wt") as out_file:
                out_file.write(str(self))
            file_list.append(path)

        return file_list


def split_input(filename: Path, stem: str = None):
    """Split the parallel input file into multiple async file names.

    :param filename:  the path to the original parallel input file
    :type filename:  str
    """
    nproc = 0
    file_list = []
    with open(filename, "rt") as file_:
        text = ""
        while True:
            line = file_.readline()
            if not line:
                break
            text += line
            line = line.strip()
            if line.startswith("pdime"):  # Get # Procs
                words = line.split()
                nproc = int(words[1]) * int(words[2]) * int(words[3])
    if nproc == 0:
        errstr = f"{filename} is not a valid APBS parallel input file!\n"
        errstr = errstr + (
            "The inputgen script was unable to asynchronize this file!"
        )
        raise RuntimeError(errstr)

    for iproc in range(nproc):
        if stem is None:
            stem = filename.stem
        outname = filename.parent / f"{stem}-PE{iproc}.in"
        outtext = text.replace("mg-para\n", f"mg-para\n    async {iproc}\n")
        with open(outname, "w") as outfile:
            outfile.write(outtext)
        file_list.append(outname)

    return file_list


def get_cli_args(args_str: str = None) -> Namespace:
    """Define and parse command line arguments via argparse.

    :param args_str: String representation of command line arguments
    :type args_str: str

    :return:  Parsed arguments object
    :rtype:  argparse.Namespace
    """
    desc = f"{TITLE_STR}\ninputgen: generating APBS input files since "
    desc += "(at least) 2004"
    parser = ArgumentParser(
        description=desc,
        formatter_class=ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--log-level",
        help="Set logging level",
        default=str(LogLevels.INFO),
        choices=LogLevels.values(),
    )
    parser.add_argument(
        "--asynch",
        action="store_true",
        help="perform an asynchronous parallel calculation.",
    )
    parser.add_argument(
        "--split",
        action="store_true",
        help=(
            "split an existing parallel input file to multiple "
            "async input files."
        ),
    )
    parser.add_argument(
        "--potdx",
        action="store_true",
        help=("create an input to compute an electrostatic potential map."),
    )
    parser.add_argument(
        "--method",
        help=("force output file to write a specific APBS ELEC method."),
        choices=ApbsCalcType.values(),
        default=str(ApbsCalcType.MG_AUTO),
        type=str.lower,
    )
    parser.add_argument(
        "--cfac",
        type=float,
        default=CFAC,
        help=(
            "factor by which to expand molecular dimensions to "
            "get coarse grid dimensions."
        ),
    )
    parser.add_argument(
        "--fadd",
        type=float,
        default=FADD,
        help=(
            "amount to add to molecular dimensions to get fine "
            "grid dimensions."
        ),
    )
    parser.add_argument(
        "--space",
        type=float,
        default=SPACE,
        help="desired fine mesh resolution",
    )
    parser.add_argument(
        "--gmemfac",
        type=int,
        default=GMEMFAC,
        help=(
            "number of bytes per grid point required for sequential "
            "MG calculation"
        ),
    )
    parser.add_argument(
        "--gmemceil",
        type=int,
        default=GMEMCEIL,
        help=(
            "max MB allowed for sequential MG calculation; adjust "
            "this to force the script to perform faster calculations "
            "(which require more parallelism)"
        ),
    )
    parser.add_argument(
        "--ofrac",
        type=float,
        default=OFRAC,
        help="overlap factor between mesh partitions (parallel)",
    )
    parser.add_argument(
        "--redfac",
        type=float,
        default=REDFAC,
        help=(
            "the maximum factor by which a domain dimension can "
            "be reduced during focusing"
        ),
    )
    parser.add_argument(
        "--istrng",
        type=float,
        default=0.0,
        help="Ionic strength (M); Na+ and Cl- ions will be used",
    )
    parser.add_argument("filename")

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
    """Main driver"""
    args = get_cli_args()

    check_file(args.filename)

    filename = Path(args.filename)
    if args.split:
        split_input(filename)
    else:
        output_path = filename.parent / Path(f"{filename.stem}.in")

        check_file(
            output_path, permission=FilePermission.WRITE, overwrite=False
        )
        psize = Psize()
        psize.run_psize(args.filename)
        input_ = Input(
            args.filename,
            psize,
            args.method,
            args.asynch,
            args.istrng,
            args.potdx,
        )
        input_.print_input_files(output_path)


if __name__ == "__main__":
    main()
