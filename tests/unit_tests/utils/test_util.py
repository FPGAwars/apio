"""
Tests of util.py
"""

import os
from pathlib import Path
import pytest
from tests.conftest import ApioRunner
from apio.common.debug_util import is_debug
from apio.utils.util import (
    get_apio_release_info,
    plurality,
    list_plurality,
    pushd,
    # subprocess_call,
    compute_file_sha256,
    resolve_packages_dir,
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


def test_compute_file_sha256(apio_runner: ApioRunner):
    """Test compute_file_sha256()."""

    with apio_runner.in_sandbox() as sb:

        path = Path("./my-test-file")

        # -- Test with an empty file.
        path = Path("./my-test-file1")
        sb.write_file(path, "")
        sha256 = compute_file_sha256(path)
        assert (
            sha256 == "e3b0c44298fc1c149afbf4c8996fb92427"
            "ae41e4649b934ca495991b7852b855"
        )

        # -- Test with non empty file.
        path = Path("./my-test-file2")
        sb.write_file(path, "hello world")
        sha256 = compute_file_sha256(path)
        assert (
            sha256 == "b94d27b9934d3e08a52e52d7da7dabfac"
            "484efe37a5380ee9088f7ace2efcde9"
        )


def test_resolve_packages_dir_expanded_check(apio_runner: ApioRunner):
    """Tests that the 'packages' safety check of APIO_PACKAGES is applied
    to the value after the env vars expansion."""

    with apio_runner.in_sandbox() as sb:

        # -- The original var value contains 'packages' but the expanded value
        # -- doesn't. Should fail.
        os.environ["packages_dir"] = str(sb.home_dir / "my-tools")
        os.environ["APIO_PACKAGES"] = "${packages_dir}"
        with apio_runner.with_logger() as log:
            with pytest.raises(SystemExit) as e:
                resolve_packages_dir(sb.home_dir)
        assert e.value.code == 1
        assert "should include the strings 'apio' and 'packages'" in log.out

        # -- The original var value doesn't contain 'packages' but the expanded value
        # -- does. Should pass.
        os.environ["my_dir"] = str(sb.home_dir / "my-packages")
        os.environ["APIO_PACKAGES"] = "${my_dir}"
        assert resolve_packages_dir(sb.home_dir) == (
            sb.home_dir / "my-packages"
        )


def test_resolve_packages_dir_apio_and_packages_check(
    apio_runner: ApioRunner,
):
    """Tests that APIO_PACKAGES must contain both 'apio' and 'packages',
    case insensitive."""

    with apio_runner.in_sandbox() as sb:

        # -- Case 1: Contains 'packages' but not 'apio'. Should fail. The check
        # -- happens before the dir is accessed so a fake path is ok.
        os.environ["APIO_PACKAGES"] = str(Path("/no-such-dir/my-packages"))
        with apio_runner.with_logger() as log:
            with pytest.raises(SystemExit) as e:
                resolve_packages_dir(sb.home_dir)
        assert e.value.code == 1
        assert "should include the strings 'apio' and 'packages'" in log.out

        # -- Case 2: Contains 'apio' but not 'packages'. Should fail.
        os.environ["APIO_PACKAGES"] = str(Path("/no-such-dir/my-apio-tools"))
        with apio_runner.with_logger() as log:
            with pytest.raises(SystemExit) as e:
                resolve_packages_dir(sb.home_dir)
        assert e.value.code == 1
        assert "should include the strings 'apio' and 'packages'" in log.out

        # -- Case 3: Contains neither 'apio' nor 'packages'. Should fail.
        os.environ["APIO_PACKAGES"] = str(Path("/no-such-dir/my-tools"))
        with apio_runner.with_logger() as log:
            with pytest.raises(SystemExit) as e:
                resolve_packages_dir(sb.home_dir)
        assert e.value.code == 1
        assert "should include the strings 'apio' and 'packages'" in log.out

        # -- Case 4: Upper case 'PACKAGES' and 'APIO'. Should pass.
        os.environ["APIO_PACKAGES"] = str(sb.home_dir / "APIO-PACKAGES")
        assert resolve_packages_dir(sb.home_dir) == (
            sb.home_dir / "APIO-PACKAGES"
        )


def test_resolve_packages_dir_dot_dot(apio_runner: ApioRunner):
    """Tests that '..' path components in APIO_PACKAGES are rejected."""

    with apio_runner.in_sandbox() as sb:

        # -- Case 1: '..' that removes the 'apio' and 'packages' component.
        # -- Should fail.
        os.environ["APIO_PACKAGES"] = str(
            Path("/no-such-dir/apio-packages/..")
        )
        with apio_runner.with_logger() as log:
            with pytest.raises(SystemExit) as e:
                resolve_packages_dir(sb.home_dir)
        assert e.value.code == 1
        assert "should not contain '..'" in log.out

        # -- Case 2: '..' that keeps the 'apio' and 'packages' component.
        # -- Should fail.
        os.environ["APIO_PACKAGES"] = str(
            Path("/no-such-dir/tmp/../apio-packages")
        )
        with apio_runner.with_logger() as log:
            with pytest.raises(SystemExit) as e:
                resolve_packages_dir(sb.home_dir)
        assert e.value.code == 1
        assert "should not contain '..'" in log.out

        # -- Case 3: '..' inside a dir name is not a '..' component.
        # -- Should pass.
        os.environ["APIO_PACKAGES"] = str(sb.sandbox_dir / "apio..packages")
        assert resolve_packages_dir(sb.home_dir) == (
            sb.sandbox_dir / "apio..packages"
        )
