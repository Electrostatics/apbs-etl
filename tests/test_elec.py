from pdb2pqr.elec import Elec
from pdb2pqr.psize import Psize
from pathlib import Path
import pytest
from re import sub


@pytest.mark.parametrize(
    "pqr_name, method, asyncflag, istrng, potdx, output",
    [
        # To generate test output:
        #   1) get output from code then add as 'output' variable
        #   2) remove newlines from code output
        #   3) replace multiple spaces with single space
        pytest.param(
            "test1.pqr",
            "mg-auto",
            False,
            0.0,
            False,
            "elec mg-auto dime 0 0 0 cglen 0.0000 0.0000 0.0000 fglen 0.0000 0.0000 0.0000 cgcent mol 1 fgcent mol 1 mol 1 lpbe bcfl sdh pdie 2.0000 sdie 78.5400 srfm smol chgm spl2 sdens 10.00 srad 1.40 swin 0.30 temp 298.15 calcenergy total calcforce no write pot dx pot end",
            id="1 auto False 0.0 False",
        ),
        pytest.param(
            "test2.pqr",
            "mg-auto",
            False,
            0.0,
            True,
            "elec mg-auto dime 0 0 0 cglen 0.0000 0.0000 0.0000 fglen 0.0000 0.0000 0.0000 cgcent mol 1 fgcent mol 1 mol 1 lpbe bcfl sdh pdie 2.0000 sdie 78.5400 srfm smol chgm spl2 sdens 10.00 srad 1.40 swin 0.30 temp 298.15 calcenergy total calcforce no write pot dx test2 end",
            id="1 auto False 0.0 True",
        ),
    ],
)
def test_elec(pqr_name, method, asyncflag, istrng, potdx, output):
    psize = Psize()
    pqr_path = Path(pqr_name)
    pqr_stem: str = pqr_path.stem

    elec = Elec(pqr_stem, psize, method, asyncflag, istrng, potdx)
    print(elec)

    # Replace all newlines and multiple whitespaces with a single space
    assert sub("\s+", " ", str(elec).replace("\n", " ").strip()) == output
