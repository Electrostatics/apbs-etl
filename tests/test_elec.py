from pdb2pqr.elec import Elec
from pdb2pqr.psize import Psize
import pytest


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
            r"""elec 
    mg-auto
    dime 0 0 0
    cglen 0.0000 0.0000 0.0000
    fglen 0.0000 0.0000 0.0000
    cgcent mol 1
    fgcent mol 1
    mol 1
    lpbe
    bcfl sdh
    pdie 2.0000
    sdie 78.5400
    srfm smol
    chgm spl2
    sdens 10.00
    srad 1.40
    swin 0.30
    temp 298.15
    calcenergy total
    calcforce no
    write pot dx pot
end
""",
            id="1 mg-auto False 0.0 False",
        ),
        pytest.param(
            "test2.pqr",
            "mg-auto",
            False,
            0.0,
            True,
            r"""elec 
    mg-auto
    dime 0 0 0
    cglen 0.0000 0.0000 0.0000
    fglen 0.0000 0.0000 0.0000
    cgcent mol 1
    fgcent mol 1
    mol 1
    lpbe
    bcfl sdh
    pdie 2.0000
    sdie 78.5400
    srfm smol
    chgm spl2
    sdens 10.00
    srad 1.40
    swin 0.30
    temp 298.15
    calcenergy total
    calcforce no
    write pot dx test2
end
""",
            id="2 mg-auto False 0.0 True",
        ),
        pytest.param(
            "test3.pqr",
            "mg-para",
            True,
            0.0,
            True,
            r"""elec 
    mg-para
    dime 0 0 0
    pdime 0 0 0
    ofrac 0.1
    cglen 0.0000 0.0000 0.0000
    fglen 0.0000 0.0000 0.0000
    cgcent mol 1
    fgcent mol 1
    async 0
    mol 1
    lpbe
    bcfl sdh
    pdie 2.0000
    sdie 78.5400
    srfm smol
    chgm spl2
    sdens 10.00
    srad 1.40
    swin 0.30
    temp 298.15
    calcenergy total
    calcforce no
    write pot dx test3
end
""",
            id="3 mg-para False 0.0 True",
        ),
        pytest.param(
            "test4.pqr",
            "mg-manual",
            False,
            0.0,
            True,
            r"""elec 
    mg-manual
    dime 0 0 0
    glen 0.000 0.000 0.000
    gcent mol 1
    mol 1
    lpbe
    bcfl sdh
    pdie 2.0000
    sdie 78.5400
    srfm smol
    chgm spl2
    sdens 10.00
    srad 1.40
    swin 0.30
    temp 298.15
    calcenergy total
    calcforce no
    write pot dx test4
end
""",
            id="4 mg-manual False 0.0 True",
        ),
    ],
)
def test_elec(pqr_name, method, asyncflag, istrng, potdx, output):
    """Tests valid construction of Elec objects"""
    elec = Elec(pqr_name, method, Psize(), asyncflag, istrng, potdx)

    assert str(elec) == output


def test_invalid_calctype():
    """Tests for input of invalid calculation types."""
    with pytest.raises(ValueError, match=r"Method.*"):
        Elec("test1.pqr", method="SHOULD_FAIL")
