"""This is used to create the ELEC section of an APBS input file."""


from pdb2pqr.psize import Psize


class Elec:
    """Holds the data and creates ASCII representation of APBS input file"""
    def __init__(
        self, pqrpath: str, size: Psize, method: str, asyncflag: bool, istrng: float=0.0, potdx: bool=False
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
        # If this is an async or parallel calc, we want to use
        # the per-grid dime rather than the global dime.
        self.dime = size.ngrid

        # Derived from:
        #   (200 * (dime[0] * dime[1] * dime[2])) / 1024 / 1024
        memory_estimation = 0.00019073486

        gmem = memory_estimation * self.dime[0] * self.dime[1] * self.dime[2]
        if method == "":  # method not named - use ceiling
            method = "mg-auto"
            if gmem > size.gmemceil:
                method = "mg-para"
        if method == "mg-para":
            self.dime = size.getSmallest()
        self.method = method
        self.istrng = istrng
        self.glen = size.coarse_length
        self.cglen = size.coarse_length
        self.fglen = size.fine_length
        self.pdime = size.proc_grid
        self.label = ""
        self.nlev = 4
        self.ofrac = 0.1
        self.async_ = 0
        self.asyncflag = asyncflag
        self.cgcent = "mol 1"
        self.fgcent = "mol 1"
        self.gcent = "mol 1"
        self.mol = 1
        self.lpbe = 1
        self.npbe = 0
        self.bcfl = "sdh"
        # TODO - where did these very arbitrary numbers come from?
        self.ion = [[-1, 1.815], [1, 1.875]]  # Multiple ions possible
        self.pdie = 2.0
        self.sdie = 78.54
        self.srfm = "smol"
        self.chgm = "spl2"
        self.sdens = 10.0
        self.srad = 1.4
        self.swin = 0.3
        self.temp = 298.15
        self.gamma = 0.105
        self.calcenergy = "total"
        self.calcforce = "no"
        if potdx:
            self.write = [["pot", "dx", pqrpath]]
        else:
            # Multiple write statements possible
            self.write = [["pot", "dx", "pot"]]

    def __str__(self):
        text = f"elec {self.label}\n"
        text += f"    {self.method}\n"
        text += f"    dime {int(self.dime[0])} {int(self.dime[1])} "
        text += f"{int(self.dime[2])}\n"
        if self.method == "mg-auto":
            text += f"    cglen {self.cglen[0]:.4f} {self.cglen[1]:.4f} "
            text += f"{self.cglen[2]:.4f}\n"
            text += f"    fglen {self.fglen[0]:.4f} {self.fglen[1]:.4f} "
            text += f"{self.fglen[2]:.4f}\n"
            text += f"    cgcent {self.cgcent}\n"
            text += f"    fgcent {self.fgcent}\n"
        elif self.method == "mg-manual":
            text += f"    glen {self.glen[0]:.3f} {self.glen[1]:.3f} "
            text += f"{self.glen[2]:.3f}\n"
            text += f"    gcent {self.gcent}\n"
        elif self.method == "mg-para":
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
