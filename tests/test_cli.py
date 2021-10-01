"""Test parsing command line options"""

from logging import getLogger
from pathlib import Path
from pytest import mark
from pdb2pqr.pdb2pqr import get_cli_args

_LOGGER = getLogger(__name__)

# @mark.parametrize("input_pdb", ["1EJG"], ids=str)
# def test_valid_input_data_file
# if -e file && -r file && ! -z file
# success
# fail

# @mark.parametrize("input_pdb", ["1EJG"], ids=str)
# def test_valid_input_download_file
# download(file)
# if status code == 200
# if -e file && -r file
# success
# fail
