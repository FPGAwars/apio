"""
Testing the ledon example on the alhambra-ii board. This test does not
use a sandbox and doesn't install the apio packages, and therefore, apio
is expected to be preinstalled.

To test:

1. Connect an Alhambra-ii board

2. Run the following command from the repo root:

   pytest -vv test/board_tests/alhambra-ii/test_leds.py
"""

import os
from pathlib import Path

# -- Class for executing click commands
# https://click.palletsprojects.com/en/8.1.x/api/#click.testing.CliRunner
from click.testing import CliRunner

# -- Entry point for apio's top level command.
from apio.commands.apio import apio_top_cli as apio


# -------------------------------------------
# -- Change to the folder where the ledon example is located
# -----------------------------


# -- Change to test project's folder.

ledon_dir = Path(
    "test/example_projects/ice40/alhambra-ii/icestudio-leds-buttons"
)
os.chdir(ledon_dir)


def test_ledon_clean():
    """Test the apio clean command"""

    # ----------------------------
    # -- Execute "apio clean"
    # ----------------------------
    result = CliRunner().invoke(apio, ["clean"])

    # -- It should return an exit code of 0: success
    assert result.exit_code == 0, result.output
    assert (
        "Cleanup completed" in result.output
        or "Already clean" in result.output
    )


def test_ledon_build():
    """Test the apio build command"""

    # ----------------------------
    # -- Execute "apio build"
    # ----------------------------
    result = CliRunner().invoke(apio, ["build"])

    # -- It should return an exit code of 0: success
    assert result.exit_code == 0, result.output
    assert "[SUCCESS]" in result.output
    assert "yosys" in result.output
    assert "nextpnr" in result.output
    assert "icepack" in result.output


def test_ledon_lint():
    """Test the apio lint command"""

    # ----------------------------
    # -- Execute "apio lint"
    # ----------------------------
    result = CliRunner().invoke(apio, ["lint"])

    # -- It should return an exit code of 0: success
    assert result.exit_code == 0, result.output
    assert "[SUCCESS]" in result.output
    assert "verilator" in result.output


def test_ledon_upload():
    """Test the apio upload. This requires a connected alhambra-ii board."""

    # ----------------------------
    # -- Execute "apio upload"
    # ----------------------------
    result = CliRunner().invoke(apio, ["upload"])

    # -- It should return an exit code of 0: success
    assert result.exit_code == 0, result.output
    assert "[SUCCESS]" in result.output
    assert "openFPGALoader" in result.output
