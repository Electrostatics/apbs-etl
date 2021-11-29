#!/usr/bin/python
"""Get dimensions and other information from a PQR file.

.. todo:: This code could be combined with :mod:`inputgen`.

.. todo:: This code should be moved to the APBS code base.

.. codeauthor:: Dave Sept
.. codeauthor:: Nathan Baker
.. codeauthor:: Todd Dolinksy
.. codeauthor:: Yong Huang
"""
import sys
import logging
from math import log
from argparse import (
    ArgumentDefaultsHelpFormatter,
    ArgumentError,
    ArgumentParser,
    Namespace,
)

from typing import List
from numpy import ndarray

from .chemistry.structures import Atom
from .io import read_pqr
from .process_cli import check_file
from .config import (
    AtomType,
    BYTES_PER_GRID,
    BYTES_STORED,
    COARSE_GRID_FACTOR,
    FINE_GRID_ADD,
    FOCUS_FACTOR,
    GRID_SPACING,
    LogLevels,
    MAX_PDB_ACCURACY,
    MEMORY_CEILING_MB,
    MIN_GRID_POINTS,
    MIN_MOL_LENGTH,
    PARTITION_OVERLAP,
    PREFIX_CONVERT,
    TITLE_STR,
)


_LOGGER = logging.getLogger(__name__)


class Psize:
    """Class for parsing input files and suggesting settings."""

    def __init__(
        self,
        cfac=COARSE_GRID_FACTOR,
        fadd=FINE_GRID_ADD,
        space=GRID_SPACING,
        gmemfac=BYTES_PER_GRID,
        gmemceil=MEMORY_CEILING_MB,
        ofrac=PARTITION_OVERLAP,
        redfac=FOCUS_FACTOR,
    ):
        """Initialize.

        :param cfac:  factor by which to expand molecular dimensions to get
            coarse grid dimensions
        :type cfac:  float
        :param fadd:  amount (in Angstroms) to add to molecular dimensions to
            get the fine grid dimensions
        :type fadd:  float
        :param space:  desired fine mesh resolution (in Angstroms)
        :type space:  float
        :param gmemfac:  number of bytes per grid point required for
            a sequential multigrid calculation
        :type gmemfac:  float
        :param gmemceil:  maximum memory (in MB) allowed for sequential
            multigrid calculation. Adjust this value to force the script to
            perform faster calculations (which require more parallelism).
        :type gmemceil:  float
        :param ofrac:  overlap factor between mesh partitions in parallel
            focusing calculation
        :type ofrac:  float
        :param redfac:  the maximum factor by which a domain dimension can be
            reduced during focusing
        :type redfac:  float
        """
        self.minlen = [None, None, None]
        self.maxlen = [None, None, None]
        self.cfac = cfac
        self.fadd = fadd
        self.space = space
        self.gmemfac = gmemfac
        self.gmemceil = gmemceil
        self.ofrac = ofrac
        self.redfac = redfac
        self.charge = 0.0
        self.gotatom = 0
        self.gothet = 0
        self.mol_length = [0.0, 0.0, 0.0]
        self.center = [0.0, 0.0, 0.0]
        self.coarse_length = [0.0, 0.0, 0.0]
        self.fine_length = [0.0, 0.0, 0.0]
        self.ngrid = [0, 0, 0]
        self.proc_grid = [0.0, 0.0, 0.0]
        self.nsmall = [0, 0, 0]
        self.nfocus = 0

    def _parse_input(self, filename):
        """Parse input structure file in PDB or PQR format.

        :param filename:  string with path to PDB- or PQR-format file.
        :type filename:  str
        """
        with open(filename, "rt", encoding="utf-8") as file_:
            self._parse_lines(file_.readlines())

    def _parse_input_for_dimensions(self, filename: str):
        """Parse PQR file for minimum/maximum grid dimensions

        :param filename: path the PQR file to read
        :type filename: str
        """
        with open(filename, "r", encoding="utf-8") as fin:
            atoms: List[Atom] = read_pqr(fin)
            center = ndarray(shape=(3, len(atoms)))
            rad = ndarray(shape=(len(atoms)))

            for idx, atom in enumerate(atoms):
                if atom.type == str(AtomType.ATOM):
                    self.gotatom += 1
                else:
                    self.gothet += 1

                x_axis, y_axis, z_axis = 0, 1, 2
                center[x_axis][idx] = atom.x
                center[y_axis][idx] = atom.y
                center[z_axis][idx] = atom.z

                rad[idx] = atom.radius
                self.charge += atom.charge

            self.minlen = ndarray.min(center - rad, 1)
            self.maxlen = ndarray.max(center + rad, 1)

    def _parse_lines(self, lines):
        """Parse the PQR/PDB lines.

        .. todo::
           This is messed up. Why are we parsing the PQR manually here when
           we already have other routines to do that?  This function should
           be replaced by a call to existing routines.

        :param lines:  PDB/PQR lines to parse
        :type lines:  [str]
        """
        for line in lines:
            if line.find("ATOM") == 0:
                subline = line[30:].replace("-", " -")
                words = subline.split()
                if len(words) < 5:
                    continue
                self.gotatom += 1
                self.charge = self.charge + float(words[3])
                rad = float(words[4])
                center = [float(word) for word in words[0:3]]
                for i in range(3):
                    if (
                        self.minlen[i] is None
                        or center[i] - rad < self.minlen[i]
                    ):
                        self.minlen[i] = center[i] - rad
                    if (
                        self.maxlen[i] is None
                        or center[i] + rad > self.maxlen[i]
                    ):
                        self.maxlen[i] = center[i] + rad
            elif line.find("HETATM") == 0:
                self.gothet = self.gothet + 1
                # Special handling for no ATOM entries in the pqr file, only
                # HETATM entries
                if self.gotatom == 0:
                    subline = line[30:].replace("-", " -")
                    words = subline.split()
                    if len(words) < 5:
                        continue
                    self.charge = self.charge + float(words[3])
                    rad = float(words[4])
                    center = [float(word) for word in words[0:3]]
                    for i in range(3):
                        if (
                            self.minlen[i] is None
                            or center[i] - rad < self.minlen[i]
                        ):
                            self.minlen[i] = center[i] - rad
                        if (
                            self.maxlen[i] is None
                            or center[i] + rad > self.maxlen[i]
                        ):
                            self.maxlen[i] = center[i] + rad

    def _set_length(self, maxlen, minlen):
        """Compute molecular dimensions, adjusting for zero-length values.

        .. todo:: Replace hard-coded values in this function.

        :param maxlen:  maximum dimensions from molecule
        :type maxlen:  [float, float, float]
        :param minlen:  minimum dimensions from molecule
        :type minlen:  [float, float, float]
        :return:  molecular dimensions
        :rtype:  [float, float, float]
        """
        for i in range(3):
            self.mol_length[i] = maxlen[i] - minlen[i]
            if self.mol_length[i] < MIN_MOL_LENGTH:
                self.mol_length[i] = MIN_MOL_LENGTH
        return self.mol_length

    def _set_coarse_grid_dims(self, mol_length):
        """Compute coarse mesh lengths.

        :param mol_length:  input molecule lengths
        :type mol_length:  [float, float, float]
        :return:  coarse grid dimensions
        :rtype:  [float, float, float]
        """
        for i in range(3):
            self.coarse_length[i] = self.cfac * mol_length[i]
        return self.coarse_length

    def _set_fine_grid_dims(self, mol_length, coarse_length):
        """Compute fine mesh lengths.

        :param mol_length:  input molecule lengths
        :type mol_length:  [float, float, float]
        :param coarse_length:  coarse grid lengths
        :type coarse_length:  [float, float, float]
        :return:  fine grid lengths
        :rtype:  [float, float, float]
        """
        for i in range(3):
            self.fine_length[i] = mol_length[i] + self.fadd
            if self.fine_length[i] > coarse_length[i]:
                self.fine_length[i] = coarse_length[i]
        return self.fine_length

    def _set_center(self, maxlen, minlen):
        """Compute molecular center.

        :param maxlen:  maximum molecule lengths
        :type maxlen:  [float, float, float]
        :param minlen:  minimum molecule lengths
        :type minlen:  [float, float, float]
        :return:  center of molecule
        :rtype:  [float, float, float]
        """
        for i in range(3):
            self.center[i] = (maxlen[i] + minlen[i]) / 2
        return self.center

    def _set_fine_grid_points(self, fine_length):
        """Compute mesh grid points, assuming 4 levels in multigrid hierarchy.

        .. todo:: remove hard-coded values from this function.

        :param fine_length:  lengths of the fine grid
        :type fine_length:  [float, float, float]
        :return:  number of grid points in each direction
        :rtype:  [int, int, int]
        """
        temp_num = [0, 0, 0]
        for i in range(3):
            temp_num[i] = int(fine_length[i] / self.space + 0.5)
            self.ngrid[i] = (MIN_GRID_POINTS - 1) * (
                int((temp_num[i] - 1) / (MIN_GRID_POINTS - 1.0) + 0.5)
            ) + 1
            if self.ngrid[i] < MIN_GRID_POINTS:
                self.ngrid[i] = MIN_GRID_POINTS
        return self.ngrid

    def _set_smallest(self, ngrid):
        """Set smallest dimensions.

        Compute parallel division of domain in case the memory requirements
        for the calculation are above the memory ceiling. Find the smallest
        dimension and see if the number of grid points in that dimension will
        fit below the memory ceiling Reduce nsmall until an nsmall^3 domain
        will fit into memory.

        .. todo:: Remove hard-coded values from this function.

        :param ngrid:  number of grid points
        :type ngrid:  [int, int, int]
        :return:  smallest number of grid points in each direction to fit in
            memory
        :rtype:  [int, int, int]
        """
        nsmall = [ngrid[i] for i in range(3)]
        while 1:
            nsmem = (
                BYTES_PER_GRID
                * nsmall[0]
                * nsmall[1]
                * nsmall[2]
                / PREFIX_CONVERT
                / PREFIX_CONVERT
            )
            if nsmem < self.gmemceil:
                break
            i = nsmall.index(max(nsmall))
            nsmall[i] = (MIN_GRID_POINTS - 1) * (
                (nsmall[i] - 1) / (MIN_GRID_POINTS - 1) - 1
            ) + 1
            if nsmall[i] <= 0:
                _LOGGER.error("You picked a memory ceiling that is too small")
                raise ValueError(nsmall[i])
        self.nsmall = nsmall
        return nsmall

    def _set_proc_grid(self, ngrid, nsmall):
        """Calculate the number of processors required in a parallel focusing
        calculation to span each dimension of the grid given the grid size
        suitable for memory constraints.

        :param ngrid:  number of needed grid points
        :type ngrid:  [int, int, int]
        :param nsmall:  number of grid points that will fit in memory
        :type nsmall:  [int, int, int]
        :return:  number of processors needed in each direction
        :rtype:  [int, int, int]
        """
        zofac = 1 + 2 * self.ofrac
        for i in range(3):
            self.proc_grid[i] = ngrid[i] / float(nsmall[i])
            if self.proc_grid[i] > 1:
                self.proc_grid[i] = int(zofac * ngrid[i] / nsmall[i] + 1.0)
        return self.proc_grid

    def _set_focus(self, fine_length, nproc, coarse_length):
        """Calculate the number of levels of focusing required for each
        processor subdomain.

        :param fine_length:  fine grid length
        :type fine_length:  [float, float, float]
        :param nproc:  number of processors in each dimension
        :type nproc:  [int, int, int]
        :param coarse_length:  coarse grid length
        :type coarse_length:  [float, float, float]
        """
        nfoc = [0, 0, 0]
        for i in range(3):
            nfoc[i] = int(
                log((fine_length[i] / nproc[i]) / coarse_length[i])
                / log(self.redfac)
                + 1.0
            )
        nfocus = nfoc[0]
        if nfoc[1] > nfocus:
            nfocus = nfoc[1]
        if nfoc[2] > nfocus:
            nfocus = nfoc[2]
        if nfocus > 0:
            nfocus = nfocus + 1
        self.nfocus = nfocus

    def _set_all(self):
        """Set up all of the things calculated individually above."""
        maxlen = self.maxlen
        minlen = self.minlen
        self._set_length(maxlen, minlen)
        mol_length = self.mol_length
        self._set_coarse_grid_dims(mol_length)
        coarse_length = self.coarse_length
        self._set_fine_grid_dims(mol_length, coarse_length)
        fine_length = self.fine_length
        self._set_center(maxlen, minlen)
        self._set_fine_grid_points(fine_length)
        ngrid = self.ngrid
        self._set_smallest(ngrid)
        nsmall = self.nsmall
        self._set_proc_grid(ngrid, nsmall)
        nproc = self.proc_grid
        self._set_focus(fine_length, nproc, coarse_length)

    def get_smallest(self):
        """Get Smallest"""
        return self.nsmall

    def run_psize(self, filename):
        """Parse input PQR file and set parameters.

        :param filename:  path of PQR file
        :type filename:  str
        """
        # self._parse_input(filename)
        self._parse_input_for_dimensions(filename)
        self._set_all()

    def __str__(self):
        """Return a string with the formatted results.

        :return:  string with formatted results
        :rtype:  str
        """
        str_ = "\n"
        if self.gotatom > 0:
            maxlen = self.maxlen
            minlen = self.minlen
            charge = self.charge
            mol_length = self.mol_length
            coarse_length = self.coarse_length
            fine_length = self.fine_length
            center = self.center
            ngrid = self.ngrid
            nsmall = self.nsmall
            nproc = self.proc_grid
            nfocus = self.nfocus
            # Compute memory requirements
            nsmem = (
                BYTES_PER_GRID
                * nsmall[0]
                * nsmall[1]
                * nsmall[2]
                / PREFIX_CONVERT
                / PREFIX_CONVERT
            )
            gmem = (
                BYTES_PER_GRID
                * ngrid[0]
                * ngrid[1]
                * ngrid[2]
                / PREFIX_CONVERT
                / PREFIX_CONVERT
            )
            # Print the calculated entries
            str_ += "######## MOLECULE INFO ########\n"
            str_ += f"Number of ATOM entries = {self.gotatom}\n"
            str_ += f"Number of HETATM entries (ignored) = {self.gothet}\n"
            str_ += f"Total charge = {charge:.3f} e\n"
            str_ += f"Dimensions = {mol_length[0]:.3f} Å x "
            str_ += f"{mol_length[1]:.3f} Å x {mol_length[2]:.3f} Å\n"
            str_ += f"Center = {center[0]:.3f} Å x {center[1]:.3f} Å x "
            str_ += f"{center[2]:.3f} Å\n"
            str_ += f"Lower corner = {minlen[0]:.3f} Å x {minlen[1]:.3f} Å x "
            str_ += f"{minlen[2]:.3f} Å\n"
            str_ += f"Upper corner = {maxlen[0]:.3f} Å x {maxlen[1]:.3f} Å x "
            str_ += f"{maxlen[2]:.3f} Å\n"
            str_ += "\n"
            str_ += "######## GENERAL CALCULATION INFO ########\n"
            str_ += f"Course grid dims = {coarse_length[0]:.3f} Å x "
            str_ += f"{coarse_length[1]:.3f} Å x "
            str_ += f"{coarse_length[2]:.3f} Å\n"
            str_ += f"Fine grid dims = {fine_length[0]:.3f} Å x "
            str_ += f"{fine_length[1]:.3f} Å x "
            str_ += f"{fine_length[2]:.3f} Å\n"
            str_ += f"Num. fine grid pts. = {ngrid[0]:d} Å x "
            str_ += f"{ngrid[1]:d} Å x "
            str_ += f"{ngrid[2]:d} Å\n"
            str_ += "\n"
            if gmem > self.gmemceil:
                str_ += f"Parallel solve required ({gmem:.3f} MB > "
                str_ += f"{self.gmemceil:.3f} MB)\n"
                str_ += "Total processors required = "
                str_ += f"{nproc[0] * nproc[1] * nproc[2]}\n"
                str_ += f"Proc. grid = {nproc[0]:d} x {nproc[1]:d} x "
                str_ += f"{nproc[2]:d}\n"
                str_ += f"Grid pts. on each proc. = {nsmall[0]:d} x "
                str_ += f"{nsmall[1]:d} x {nsmall[2]:d}\n"
                xglob = nproc[0] * round(
                    nsmall[0] / (1 + 2 * self.ofrac - MAX_PDB_ACCURACY)
                )
                yglob = nproc[1] * round(
                    nsmall[1] / (1 + 2 * self.ofrac - MAX_PDB_ACCURACY)
                )
                zglob = nproc[2] * round(
                    nsmall[2] / (1 + 2 * self.ofrac - MAX_PDB_ACCURACY)
                )
                if nproc[0] == 1:
                    xglob = nsmall[0]
                if nproc[1] == 1:
                    yglob = nsmall[1]
                if nproc[2] == 1:
                    zglob = nsmall[2]
                str_ += "Fine mesh spacing = "
                str_ += f"{fine_length[0] / (xglob - 1):g} x "
                str_ += f"{fine_length[1] / (yglob - 1):g} x "
                str_ += f"{fine_length[2] / (zglob - 1):g} A\n"
                str_ += "Estimated mem. required for parallel solve = "
                str_ += f"{nsmem:.3f} MB/proc.\n"
                ntot = nsmall[0] * nsmall[1] * nsmall[2]
            else:
                str_ += "Fine mesh spacing = "
                str_ += f"{fine_length[0] / (ngrid[0] - 1):g} x "
                str_ += f"{fine_length[1] / (ngrid[1] - 1):g} x "
                str_ += f"{fine_length[2] / (ngrid[2] - 1):g} A\n"
                str_ += "Estimated mem. required for sequential solve = "
                str_ += f"{gmem:.3f} MB\n"
                ntot = ngrid[0] * ngrid[1] * ngrid[2]
            str_ += f"Number of focusing operations = {nfocus}\n"
            str_ += "\n"
            str_ += "######## ESTIMATED REQUIREMENTS ########\n"
            str_ += "Memory per processor = "
            str_ += f"{BYTES_PER_GRID * ntot / PREFIX_CONVERT / PREFIX_CONVERT:.3f} MB\n"
            str_ += "Grid storage requirements (ASCII) = "
            grid_storage_req = (
                BYTES_STORED
                * nproc[0]
                * nproc[1]
                * nproc[2]
                * ntot
                / PREFIX_CONVERT
                / PREFIX_CONVERT
            )
            str_ += f"{grid_storage_req:.3f} MB\n"
            str_ += "\n"
        else:
            str_ = "No ATOM entries in file!\n\n"
        return str_


def get_cli_args(args_str: str = None) -> Namespace:
    """Build argument parser.

    :param args_str: String representation of command line arguments
    :type args_str: str

    :return:  argument parser
    :rtype:  Namespace
    """
    desc = f"{TITLE_STR}\npsize: figuring out the size of electrostatics "
    desc += "calculations since (at least) 2002."

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
        "--cfac",
        default=COARSE_GRID_FACTOR,
        type=float,
        help=(
            "Factor by which to expand molecular dimensions to "
            "get coarse grid dimensions"
        ),
    )
    parser.add_argument(
        "--fadd",
        default=FINE_GRID_ADD,
        type=float,
        help="Amount to add to mol dims to get fine grid dims",
    )
    parser.add_argument(
        "--space",
        default=GRID_SPACING,
        type=float,
        help="Desired fine mesh resolution",
    )
    parser.add_argument(
        "--gmemfac",
        default=BYTES_PER_GRID,
        type=int,
        help=(
            "Number of bytes per grid point required for "
            "sequential MG calculation"
        ),
    )
    parser.add_argument(
        "--gmemceil",
        default=MEMORY_CEILING_MB,
        type=int,
        help=(
            "Max MB allowed for sequential MG calculation. "
            "Adjust this to force the script to perform faster "
            "calculations (which require more parallelism)."
        ),
    )
    parser.add_argument(
        "--ofrac",
        default=PARTITION_OVERLAP,
        type=float,
        help="Overlap factor between mesh partitions",
    )
    parser.add_argument(
        "--redfac",
        default=FOCUS_FACTOR,
        type=float,
        help=(
            "The maximum factor by which a domain dimension "
            "can be reduced during focusing"
        ),
    )
    parser.add_argument("mol_path", help="Path to PQR file.")

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
    """Main driver for module."""
    args: Namespace = get_cli_args()

    psize = Psize(
        cfac=args.cfac,
        fadd=args.fadd,
        space=args.space,
        gmemfac=args.gmemfac,
        gmemceil=args.gmemceil,
        ofrac=args.ofrac,
        redfac=args.redfac,
    )

    check_file(args.mol_path)
    psize.run_psize(args.mol_path)

    print(psize)


if __name__ == "__main__":
    main()
