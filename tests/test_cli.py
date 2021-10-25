"""Test processing command line options for pdb2pqr executable.

    - test invalid combinations
    - test file permissions
    - test argument tranformations
"""

# from argparse import ArgumentError
import pytest
from logging import getLogger
from os import remove
from pdb2pqr.config import FilePermission
from pdb2pqr.process_cli import (
    EmptyFileError,
    check_file,
    check_files,
    check_options,
    get_cli_args,
    transform_arguments,
)
from .common import DATA_DIR

_LOGGER = getLogger(__name__)


@pytest.mark.parametrize(
    "arguments, search_phrase",
    [
        # pytest.param("--titration-state-method=propka --with-ph=7 --ff=PARSE --apbs-input=1fas.in  --drop-water 1fas.pdb 1fas.pqr", id="1")
        pytest.param(
            "--titration-state-method=propka --with-ph=-0.1 --ff=PARSE 1fas 1fas.pqr",
            "pH",
            id="Invalid pH below 0",
        ),
        pytest.param(
            "--titration-state-method=propka --with-ph=14.1 --ff=PARSE 1fas 1fas.pqr",
            "pH",
            id="Invalid pH above 14",
        ),
        pytest.param(
            "--ff=amber --neutraln 1fas 1fas.pqr",
            "PARSE",
            id="Invalid forcefield with --neutraln",
        ),
        pytest.param(
            "--ff=swanson --neutralc 1fas 1fas.pqr",
            "PARSE",
            id="Invalid forcefield with --neutralc",
        ),
        pytest.param(
            f"--usernames={DATA_DIR}/custom.names 1fas test.pqr",
            "--usernames without --userff",
            id="Missing userff file",
        ),
        pytest.param(
            f"--userff={DATA_DIR}/custom-ff.dat 1fas test.pqr",
            "--usernames must be specified if using --userff",
            id="--userff but no --usernames",
        ),
    ],
)
def test_invalid_combinations(arguments, search_phrase):
    with pytest.raises(RuntimeError) as err_info:
        check_options(get_cli_args(arguments))

    assert search_phrase in str(err_info.value)


@pytest.mark.parametrize(
    "arguments, expected_error, search_phrase",
    [
        pytest.param(
            f"--userff=missing_ff.dat --usernames={DATA_DIR}/custom.names 1fas test.pqr",
            FileNotFoundError,
            None,
            id="Missing userff file",
        ),
        pytest.param(
            f"--userff={DATA_DIR}/custom-ff.dat --usernames=missing_name.names 1fas test.pqr",
            FileNotFoundError,
            None,
            id="Missing usernames file",
        ),
        pytest.param(
            "--ligand=missing_ligand.mol2 1fas test.pqr",
            FileNotFoundError,
            None,
            id="Missing ligand file",
        ),
    ],
)
def test_file_existence(arguments, expected_error, search_phrase):
    with pytest.raises(expected_error) as err_info:
        args = get_cli_args(arguments)
        check_files(args)

    if search_phrase is not None:
        assert search_phrase in str(err_info.value)


@pytest.mark.parametrize(
    "permission, context, overwrite, expected_error",
    [
        pytest.param(
            FilePermission.READ,
            "Checking for empty file",
            True,
            EmptyFileError,
            id="Empty file",
        ),
        pytest.param(
            FilePermission.WRITE,
            "Checking for existing file",
            False,
            FileExistsError,
            id="File exists",
        ),
    ],
)
def test_file_permissions(permission, context, overwrite, expected_error):
    with pytest.raises(expected_error):
        temp_file = f"{DATA_DIR}/empty.txt"
        fout = open(temp_file, "w")
        fout.close()

        check_file(
            temp_file,
            context=context,
            permission=permission,
            overwrite=overwrite,
        )

    remove(temp_file)


@pytest.mark.parametrize(
    "arguments, expected_debump, expected_opt",
    [
        # pytest.param("--titration-state-method=propka --with-ph=7 --ff=PARSE --apbs-input=1fas.in  --drop-water 1fas.pdb 1fas.pqr", id="1")
        pytest.param(
            "--ff=amber --assign-only 1fas 1fas.pqr",
            False,
            False,
            id="-assign-only",
        ),
        pytest.param(
            "--ff=amber --clean 1fas 1fas.pqr", False, False, id="clean"
        ),
        pytest.param(
            "--ff=amber --assign-only --clean 1fas 1fas.pqr",
            False,
            False,
            id="assign-only clean",
        ),
        pytest.param(
            "--ff=amber 1fas 1fas.pqr",
            True,
            True,
            id="No --assign-only or --clean",
        ),
    ],
)
def test_argument_tranformations(arguments, expected_debump, expected_opt):
    args = transform_arguments(get_cli_args(arguments))
    assert args.debump == expected_debump
    assert args.opt == expected_opt
