"""This is used to create the ELEC section of an APBS input file."""
from pathlib import Path
from pdb2pqr.config import ApbsCalcType
from pdb2pqr.psize import Psize
from .config import (
    MIN_LEVELS,
    PARTITION_OVERLAP,
    CL_CHARGE,
    CL_RADIUS,
    NA_CHARGE,
    NA_RADIUS,
    SOLUTE_DIELECTRIC,
    SOLVENT_DIELECTRIC,
    SURFACE_DENSITY,
    SOLVENT_RADIUS,
    SPLINE_WINDOW,
    ROOM_TEMPERATURE,
    SURFACE_TENSION,
)


class Elec:
    """Holds the data and creates ASCII representation of APBS input file"""

    def __init__(
        self,
        pqrpath: str,
        method: str = str(ApbsCalcType.MG_AUTO),
        size: Psize = Psize(),
        asyncflag: bool = False,
        istrng: float = 0.0,
        potdx: bool = False,
    ):
        """Initialize object.

        .. todo::  Remove hard-coded parameters.

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

        if method not in ApbsCalcType.values():
            raise ValueError(
                f"Method, '{method}', must be one of {ApbsCalcType.values()}."
            )

        # If this is an async or parallel calc, we want to use
        # the per-grid dime rather than the global dime.
        self.dime = size.ngrid
        if method == str(ApbsCalcType.MG_PARA):
            self.dime = size.get_smallest()
        self.method = method
        self.istrng = istrng
        self.glen = size.coarse_length
        self.cglen = size.coarse_length
        self.fglen = size.fine_length
        self.pdime = size.proc_grid
        # TODO: self.label can never be set. Should it be deleted?
        self.label = ""
        self.nlev = MIN_LEVELS
        self.ofrac = PARTITION_OVERLAP
        self.async_ = 0
        self.asyncflag = asyncflag
        self.cgcent = "mol 1"
        self.fgcent = "mol 1"
        self.gcent = "mol 1"
        self.mol = 1
        self.lpbe = True
        self.npbe = False
        self.bcfl = "sdh"
        self.ion = [
            [CL_CHARGE, CL_RADIUS],
            [NA_CHARGE, NA_RADIUS],
        ]  # Multiple ions possible
        self.pdie = SOLUTE_DIELECTRIC
        self.sdie = SOLVENT_DIELECTRIC
        self.srfm = "smol"
        self.chgm = "spl2"
        self.sdens = SURFACE_DENSITY
        self.srad = SOLVENT_RADIUS
        self.swin = SPLINE_WINDOW
        self.temp = ROOM_TEMPERATURE
        self.gamma = SURFACE_TENSION
        self.calcenergy = "total"
        self.calcforce = "no"
        if potdx:
            self.write = [["pot", "dx", Path(pqrpath).stem]]
        else:
            # TODO: is this valid output? Ends up writing "write pot dx pot"
            # Multiple write statements possible
            self.write = [["pot", "dx", "pot"]]

    def __str__(self):
        # TODO: Should Elec be allowed to print dimensions and lengths of 0?
        #       Right now, code succeeds, but with 0-dimensions implies no data
        text = f"elec {self.label}\n"
        text += f"    {self.method}\n"
        text += f"    dime {int(self.dime[0])} {int(self.dime[1])} "
        text += f"{int(self.dime[2])}\n"
        if self.method == str(ApbsCalcType.MG_AUTO):
            text += f"    cglen {self.cglen[0]:.4f} {self.cglen[1]:.4f} "
            text += f"{self.cglen[2]:.4f}\n"
            text += f"    fglen {self.fglen[0]:.4f} {self.fglen[1]:.4f} "
            text += f"{self.fglen[2]:.4f}\n"
            text += f"    cgcent {self.cgcent}\n"
            text += f"    fgcent {self.fgcent}\n"
        elif self.method == str(ApbsCalcType.MG_MANUAL):
            text += f"    glen {self.glen[0]:.3f} {self.glen[1]:.3f} "
            text += f"{self.glen[2]:.3f}\n"
            text += f"    gcent {self.gcent}\n"
        elif self.method == str(ApbsCalcType.MG_PARA):
            text += f"    pdime {int(self.pdime[0])} {int(self.pdime[1])} "
            text += f"{int(self.pdime[2])}\n"
            text += f"    ofrac {self.ofrac:.1f}\n"
            text += f"    cglen {self.cglen[0]:.4f} {self.cglen[1]:.4f} "
            text += f"{self.cglen[2]:.4f}\n"
            text += f"    fglen {self.fglen[0]:.4f} {self.fglen[1]:.4f} "
            text += f"{self.fglen[2]:.4f}\n"
            text += f"    cgcent {self.cgcent}\n"
            text += f"    fgcent {self.fgcent}\n"
            if self.asyncflag:
                text += f"    async {self.async_}\n"
        text += f"    mol {int(self.mol)}\n"
        text += "    lpbe\n" if self.lpbe else "    npbe\n"
        text += f"    bcfl {self.bcfl}\n"
        if self.istrng > 0:
            for ion in self.ion:
                text += f"    ion charge {ion[0]:.2f} conc {self.istrng:.3f} "
                text += f"radius {ion[1]:.4f}\n"
        text += f"    pdie {self.pdie:.4f}\n"
        text += f"    sdie {self.sdie:.4f}\n"
        text += f"    srfm {self.srfm}\n"
        text += f"    chgm {self.chgm}\n"
        text += f"    sdens {self.sdens:.2f}\n"
        text += f"    srad {self.srad:.2f}\n"
        text += f"    swin {self.swin:.2f}\n"
        text += f"    temp {self.temp:.2f}\n"
        text += f"    calcenergy {self.calcenergy}\n"
        text += f"    calcforce {self.calcforce}\n"
        for write in self.write:
            text += f"    write {write[0]} {write[1]} {write[2]}\n"
        text += "end\n"
        return text
