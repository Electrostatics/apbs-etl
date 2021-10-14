from pdb2pqr.elec import Elec
from pdb2pqr.psize import Psize
# from pytest import mark, param
import pytest


@pytest.mark.parametrize(
    "pqr_name, method, asyncflag, istrng, potdx",
    [
        pytest.param('test1.pqr', 'auto', False, 0.0, False, id='1 auto False 0.0 False'),
        pytest.param('test2.pqr', 'auto', False, 0.0, True, id='1 auto False 0.0 True')
    ],
)
def test_elec(pqr_name, method, asyncflag, istrng, potdx):
    psize = Psize()
    elec = Elec(pqr_name, psize, method, asyncflag, istrng, potdx)
    print(elec)
