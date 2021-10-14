"""Create an APBS input file using :mod:`psize` data.

.. codeauthor::  Todd Dolinsky
.. codeauthor::  Nathan Baker
"""
import logging
import argparse
from pathlib import Path
from . import psize
from .config import LogLevels, TITLE_STR
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
        self.asyncflag = asyncflag
        # Initialize variables to default elec values
        elec1 = Elec(self.pqrname, size, method, asyncflag, istrng, potdx)
        if not potdx:
            elec2 = Elec(self.pqrname, size, method, asyncflag, istrng, potdx)
            setattr(elec2, "sdie", 2.0)
            setattr(elec2, "write", [])
        else:
            elec2 = ""
        self.elecs = [elec1, elec2]
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

    def print_input_files(self, output_path):
        """Generate the input file(s) associated with this object.

        :param output_path:  location for generated files
        :type output_path:  str
        """
        path = Path(output_path)
        base_name = path.stem
        if self.asyncflag:
            outname = base_name + "-para.in"
            # Temporarily disable async flag
            for elec in self.elecs:
                elec.asyncflag = False
            with open(outname, "wt") as out_file:
                out_file.write(str(self))
            # Now make the async files
            elec = self.elecs[0]
            nproc = elec.pdime[0] * elec.pdime[1] * elec.pdime[2]
            for i in range(int(nproc)):
                outname = base_name + f"-PE{i}.in"
                for elec in self.elecs:
                    elec.asyncflag = True
                    elec.async_ = i
                with open(outname, "wt") as out_file:
                    out_file.write(str(self))
        else:
            with open(path, "wt") as out_file:
                out_file.write(str(self))


def split_input(filename):
    """Split the parallel input file into multiple async file names.

    :param filename:  the path to the original parallel input file
    :type filename:  str
    """
    nproc = 0
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
    base_pqr_name = Path(filename).stem
    for iproc in int(range(nproc)):
        outname = base_pqr_name + f"-PE{iproc}.in"
        outtext = text.replace("mg-para\n", f"mg-para\n    async {iproc}\n")
        with open(outname, "w") as outfile:
            outfile.write(outtext)


def build_parser():
    """Build argument parser."""
    desc = f"{TITLE_STR}\ninputgen: generating APBS input files since "
    desc += "(at least) 2004"
    parse = argparse.ArgumentParser(
        description=desc,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parse.add_argument(
        "--log-level",
        help="Set logging level",
        default=LogLevels.INFO,
        choices=LogLevels.values(),
    )
    parse.add_argument(
        "--asynch",
        action="store_true",
        help="perform an asynchronous parallel calculation.",
    )
    parse.add_argument(
        "--split",
        action="store_true",
        help=(
            "split an existing parallel input file to multiple "
            "async input files."
        ),
    )
    parse.add_argument(
        "--potdx",
        action="store_true",
        help=("create an input to compute an electrostatic potential map."),
    )
    parse.add_argument(
        "--method",
        help=("force output file to write a specific APBS ELEC method."),
        choices=["para", "auto", "manual", "async"],  # TODO: make into enum
    )
    parse.add_argument(
        "--cfac",
        type=float,
        default=psize.CFAC,
        help=(
            "factor by which to expand molecular dimensions to "
            "get coarse grid dimensions."
        ),
    )
    parse.add_argument(
        "--fadd",
        type=float,
        default=psize.FADD,
        help=(
            "amount to add to molecular dimensions to get fine "
            "grid dimensions."
        ),
    )
    parse.add_argument(
        "--space",
        type=float,
        default=psize.SPACE,
        help="desired fine mesh resolution",
    )
    parse.add_argument(
        "--gmemfac",
        type=int,
        default=psize.GMEMFAC,
        help=(
            "number of bytes per grid point required for sequential "
            "MG calculation"
        ),
    )
    parse.add_argument(
        "--gmemceil",
        type=int,
        default=psize.GMEMCEIL,
        help=(
            "max MB allowed for sequential MG calculation; adjust "
            "this to force the script to perform faster calculations "
            "(which require more parallelism)"
        ),
    )
    parse.add_argument(
        "--ofrac",
        type=float,
        default=psize.OFRAC,
        help="overlap factor between mesh partitions (parallel)",
    )
    parse.add_argument(
        "--redfac",
        type=float,
        default=psize.REDFAC,
        help=(
            "the maximum factor by which a domain dimension can "
            "be reduced during focusing"
        ),
    )
    parse.add_argument(
        "--istrng", help="Ionic strength (M); Na+ and Cl- ions will be used"
    )
    parse.add_argument("filename")
    return parse


def main():
    """Main driver"""
    parser = build_parser()
    args = parser.parse_args()
    size = psize.Psize()
    filename = args.filename
    if args.split:
        split_input(filename)
    else:
        size.run_psize(filename)
        input_ = Input(
            filename, size, args.method, args.asynch, args.istrng, args.potdx
        )
        path = Path(filename)
        output_path = path.parent + path.stem + Path(".in")
        input_.print_input_files(output_path)


if __name__ == "__main__":
    main()
