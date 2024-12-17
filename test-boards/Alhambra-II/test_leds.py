"""
Testing the ledon example on the alhambra-ii board
"""

import os
from pathlib import Path

# -- Class for executing click commands
# https://click.palletsprojects.com/en/8.1.x/api/#click.testing.CliRunner
from click.testing import CliRunner

# -- apio build entry point
from apio.commands.build import cli as apio_build

# -- apio clean entry point
from apio.commands.clean import cli as apio_clean

# -- apio verify entry point
from apio.commands.verify import cli as apio_verify

# -- apio time entry point
from apio.commands.upload import cli as apio_upload


# -------------------------------------------
# -- Change to the folder where the ledon example is located
# -----------------------------

# -- Get the current working directory
cwd = Path.cwd()

# -- Create the new path
ledon_dir = cwd / "test-examples" / "alhambra-ii" / "01-LEDs-buttons"

# -- Change to the new folder!
os.chdir(ledon_dir)


def test_ledon_clean():
    """Test the apio clean command"""

    # ----------------------------
    # -- Execute "apio clean"
    # ----------------------------
    result = CliRunner().invoke(apio_clean)

    # -- It should return an exit code of 0: success
    assert result.exit_code == 0, result.output
    assert "[SUCCESS]" in result.output


def test_ledon_build():
    """Test the apio build command"""

    # ----------------------------
    # -- Execute "apio build"
    # ----------------------------
    result = CliRunner().invoke(apio_build)

    # -- It should return an exit code of 0: success
    assert result.exit_code == 0, result.output
    assert "[SUCCESS]" in result.output
    assert "yosys" in result.output
    assert "nextpnr" in result.output
    assert "icepack" in result.output


def test_ledon_verify():
    """Test the apio verify command"""

    # ----------------------------
    # -- Execute "apio verify"
    # ----------------------------
    result = CliRunner().invoke(apio_verify)

    # -- It should return an exit code of 0: success
    assert result.exit_code == 0, result.output
    assert "[SUCCESS]" in result.output
    assert "iverilog" in result.output


def test_ledon_upload():
    """Test the apio upload. This requires a connected alhambra-ii board."""

    # ----------------------------
    # -- Execute "apio upload"
    # ----------------------------
    result = CliRunner().invoke(apio_upload)

    # -- It should return an exit code of 0: success
    assert result.exit_code == 0, result.output
    assert "[SUCCESS]" in result.output
    assert "iceprog" in result.output
