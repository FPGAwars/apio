"""
  Test different "apio" commands
"""

from os import listdir, chdir
from test.conftest import ApioRunner
import pytest


# -- Entry point for apio commands.
from apio.commands.raw import cli as apio_raw
from apio.commands.upgrade import cli as apio_upgrade
from apio.commands.system import cli as apio_system
from apio.commands.packages import cli as apio_packages


# R0801: Similar lines in 2 files
# pylint: disable=R0801
def test_utilities(apio_runner: ApioRunner):
    """Tests apio utility commands."""

    # -- If the option 'offline' is passed, the test is skip
    # -- (This test is slow and requires internet connectivity)
    if apio_runner.offline_flag:
        pytest.skip("requires internet connection")

    with apio_runner.in_sandbox() as sb:

        # -- Create and change to project dir.
        sb.proj_dir.mkdir()
        chdir(sb.proj_dir)

        # -- Install all packages
        result = sb.invoke_apio_cmd(apio_packages, ["--install", "--verbose"])
        sb.assert_ok(result)
        assert "'examples' installed successfully" in result.output
        assert "'oss-cad-suite' installed successfully" in result.output
        assert listdir(sb.packages_dir / "examples")
        assert listdir(sb.packages_dir / "tools-oss-cad-suite")

        # -- Run 'apio upgrade'
        result = sb.invoke_apio_cmd(apio_upgrade)
        sb.assert_ok(result)
        assert "Lastest Apio stable version" in result.output

        # -- Run 'apio system --info'
        result = sb.invoke_apio_cmd(apio_system, ["--info"])
        sb.assert_ok(result)
        assert "Apio version" in result.output

        # -- Run 'apio raw  "nextpnr-ice40 --help"'
        result = sb.invoke_apio_cmd(
            apio_raw, ["--", "nextpnr-ice40", "--help"]
        )
        sb.assert_ok(result)

        # -- Run 'apio raw --env'
        result = sb.invoke_apio_cmd(apio_raw, ["--env"])
        sb.assert_ok(result)
        assert "Envirnment settings:" in result.output
        assert "YOSYS_LIB" in result.output
