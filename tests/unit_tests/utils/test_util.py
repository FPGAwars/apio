"""
Tests of util.py
"""

import os
import sys
from pathlib import Path
import pytest
from pytest import raises
from tests.conftest import ApioRunner
from apio.utils.util import (
    get_apio_release_info,
    plurality,
    list_plurality,
    is_debug,
    pushd,
    subprocess_call,
)

# TODO: Add more tests.


def test_release_info():
    """Tests that the release info placeholder is empty. This value
    is set on the fly by build and publishing github workflows."""
    version_info = get_apio_release_info()
    assert isinstance(version_info, str)
    assert version_info == ""


def test_pluraliry():
    """Tests the plurality() function."""
    # -- Test for ints 1, 2, 3
    assert plurality(1, "file") == "1 file"
    assert plurality(2, "file") == "2 files"
    assert plurality(3, "file") == "3 files"

    # -- Test for lengths 1, 2, 3.
    assert plurality(["aa"], "file") == "1 file"
    assert plurality(["aa", "bb"], "file") == "2 files"
    assert plurality(["aa", "bb", "cc"], "file") == "3 files"


def test_list_pluraliry():
    """Tests the list_plurality() function."""

    # -- Test for lengths 1, 2, and 3.
    assert list_plurality(["aa"], "or") == "aa"
    assert list_plurality(["aa", "bb"], "and") == "aa and bb"
    assert list_plurality(["aa", "bb", "cc"], "or") == "aa, bb, or cc"

    # -- An empty list should trhow an assert exception.
    with pytest.raises(AssertionError):
        list_plurality([], "or")


def test_is_debug():
    """Tests the is_debug() function."""

    # -- Assuming APIO_DEBUG is not defined.
    assert not is_debug(1)
    assert not is_debug(2)
    assert not is_debug(3)

    # -- Enter debug mode level 1.
    os.environ["APIO_DEBUG"] = "1"
    assert is_debug(1)
    assert not is_debug(2)
    assert not is_debug(3)

    # -- Enter debug mode level 2.
    os.environ["APIO_DEBUG"] = "2"
    assert is_debug(1)
    assert is_debug(2)
    assert not is_debug(3)

    # -- Enter debug mode level 3.
    os.environ["APIO_DEBUG"] = "3"
    assert is_debug(1)
    assert is_debug(2)
    assert is_debug(3)

    # -- Exit debug mode
    os.environ.pop("APIO_DEBUG")
    assert not is_debug(1)
    assert not is_debug(2)
    assert not is_debug(3)


def test_pushd(apio_runner: ApioRunner):
    """Test the pushd context manager."""

    with apio_runner.in_sandbox() as sb:
        # -- Define dir 1.
        dir1 = sb.proj_dir
        assert dir1.is_dir()

        # -- Define dir 2
        dir2 = dir1 / "dir2"
        assert dir2.resolve() != dir1.resolve()
        dir2.mkdir()

        # -- Change to dir1
        os.chdir(dir1)
        assert Path.cwd().resolve() == dir1.resolve()

        # -- Pushd to dir 2
        with pushd(dir2):
            assert Path.cwd().resolve() == dir2.resolve()

        # -- Back from pushd to dir1
        assert Path.cwd().resolve() == dir1.resolve()


def test_subprocess_call(apio_runner: ApioRunner):
    """Test subprocess_call()."""

    with apio_runner.in_sandbox():

        # -- Test a successful subprocess
        file1 = Path("file1")
        assert not file1.exists()
        subprocess_call(
            [
                sys.executable,
                "-c",
                f'import pathlib; pathlib.Path("{str(file1)}").'
                'write_text("content1")',
            ]
        )
        assert file1.is_file()
        assert file1.read_text(encoding="utf-8") == "content1"

        # -- Test a failing subprocess
        with raises(SystemExit) as e:
            subprocess_call(
                [
                    sys.executable,
                    "-c",
                    "import sys; sys.exit(7)",
                ]
            )
            # -- Apio exits with 1, regardless of the subprocess error status.
            assert e.value.code == 1
