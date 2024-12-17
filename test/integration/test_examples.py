"""
  Test different "apio" commands
"""

from os import stat
from os import chdir
from os.path import getsize
from os import path
from os import system
from pathlib import Path
from test.conftest import ApioRunner
import pytest

# -- Entry point for apio commands.
from apio.commands.packages import cli as apio_packages
from apio.commands.examples import cli as apio_examples


# R0801: Similar lines in 2 files
# pylint: disable=R0801
def test_examples(apio_runner: ApioRunner):
    """Tests the listing and fetching apio examples."""

    # -- If the option 'offline' is passed, the test is skip
    # -- (This test is slow and requires internet connectivity)
    if apio_runner.offline_flag:
        pytest.skip("requires internet connection")

    with apio_runner.in_sandbox() as sb:

        # -- Create and change to project dir.
        sb.proj_dir.mkdir()
        chdir(sb.proj_dir)

        base_path = Path(sb.packages_dir)
        file_path = (
            base_path / "examples" / "Alhambra-II" / "ledon" / "ledon.v"
        )
        file_path = path.normpath(str(file_path))

        # -- Install the examples package.
        result = sb.invoke_apio_cmd(apio_packages, ["--install", "examples"])
        sb.assert_ok(result)
        assert "Package 'examples' installed successfully" in result.output
        try:
            size = stat(file_path).st_size
            assert size > 0
        except FileNotFoundError:
            assert False, f"El archivo {file_path} no existe"

        # -- 'apio examples --list'
        result = sb.invoke_apio_cmd(
            apio_examples,
            ["--list"],
        )
        sb.assert_ok(result)
        assert "Alhambra-II/ledon" in result.output
        assert "Hello world for the Alhambra-II board" in result.output

        # -- 'apio examples --fetch-files Alhambra-II/ledon'
        result = sb.invoke_apio_cmd(
            apio_examples,
            ["--fetch-files", "Alhambra-II/ledon"],
        )
        sb.assert_ok(result)
        assert "Copying Alhambra-II/ledon example files" in result.output
        assert "have been successfully created!" in result.output
        assert getsize("ledon.v")

        # -- 'apio examples --fetch-dir Alhambra-II/ledon'
        result = sb.invoke_apio_cmd(
            apio_examples,
            ["--fetch-dir", "Alhambra-II/ledon"],
        )
        sb.assert_ok(result)
        assert "Creating Alhambra-II/ledon directory" in result.output
        assert "has been successfully created" in result.output
        assert getsize("Alhambra-II/ledon/ledon.v")

        # -- 'apio examples --fetch-files" Alhambra-II/ledon -p dir1'
        result = sb.invoke_apio_cmd(
            apio_examples,
            ["--fetch-files", "Alhambra-II/ledon", "-p", "dir1"],
        )
        sb.assert_ok(result)
        assert "Copying Alhambra-II/ledon example files" in result.output
        assert "have been successfully created!" in result.output
        assert getsize("dir1/ledon.v")

        # -- 'apio examples --fetch-dir Alhambra-II/ledon -p dir2
        result = sb.invoke_apio_cmd(
            apio_examples,
            ["--fetch-dir", "Alhambra-II/ledon", "-p", "dir2"],
        )
        sb.assert_ok(result)
        assert "Creating Alhambra-II/ledon directory" in result.output
        assert "has been successfully created" in result.output
        assert getsize("dir2/Alhambra-II/ledon/ledon.v")
