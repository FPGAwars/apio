"""
  Test for the "apio clean" command
"""

from os import chdir
from os.path import join
from pathlib import Path
from test.conftest import ApioRunner
from apio.commands.apio_clean import cli as apio_clean


def test_clean_without_apio_ini(apio_runner: ApioRunner):
    """Tests the apio clean command without an apio.ini file."""

    with apio_runner.in_sandbox() as sb:

        # -- Create and change to project dir.
        sb.proj_dir.mkdir()
        chdir(sb.proj_dir)

        # -- Run "apio clean" with no apio.ini
        result = sb.invoke_apio_cmd(apio_clean)
        assert result.exit_code != 0, result.output
        assert "Error: missing project file apio.ini" in result.output


# R0801: Similar lines in 2 files
# pylint: disable=R0801
def test_clean_with_apio_ini(apio_runner: ApioRunner):
    """Tests the apio clean command with an apio.ini file."""

    with apio_runner.in_sandbox() as sb:

        # -- Create and change to project dir.
        sb.proj_dir.mkdir()
        chdir(sb.proj_dir)

        # -- Run "apio clean" with a valid apio.ini and no dirty files.
        sb.write_apio_ini({"board": "alhambra-ii", "top-module": "main"})
        result = sb.invoke_apio_cmd(apio_clean)
        assert result.exit_code == 0, result.output

        # -- Run "apio clean" with apio.ini and dirty files.
        sb.write_apio_ini({"board": "alhambra-ii", "top-module": "main"})
        sb.write_file(".sconsign.dblite", "dummy text")
        sb.write_file("_build/hardware.out", "dummy text")
        assert Path(".sconsign.dblite").exists()
        assert Path("_build/hardware.out").exists()
        assert Path("_build").exists()
        result = sb.invoke_apio_cmd(apio_clean)
        assert result.exit_code == 0, result.output
        assert "Removed .sconsign.dblite" in result.output
        assert f"Removed {join('_build', 'hardware.out')}" in result.output
        assert "Removed directory _build" in result.output
        assert not Path(".sconsign.dblite").exists()
        assert not Path("_build/hardware.out").exists()
        assert not Path("_build").exists()
