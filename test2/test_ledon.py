"""
Testing the ledon example on the Alhambra-II board
"""

import os
from pathlib import Path

# -- Class for executing click commands
# https://click.palletsprojects.com/en/8.1.x/api/#click.testing.CliRunner
from click.testing import CliRunner

# -- apio build entry point
from apio.commands.build import cli as cmd_build

# -- apio clean entry point
from apio.commands.clean import cli as cmd_clean

# -- apio verify entry point
from apio.commands.verify import cli as cmd_verify

# -- apio time entry point
from apio.commands.upload import cli as cmd_upload


# -------------------------------------------
# -- Change to the folder where the ledon example is located
# -----------------------------

#-- Get the current working directory
cwd = Path.cwd()

#-- Create the new path
ledon_dir = cwd / 'test-examples' / 'Alhambra-II' / 'ledon'

#-- Change to the new folder!
os.chdir(ledon_dir)



def test_ledon_clean():
    """Test the apio clean command"""

    # ----------------------------
    # -- Execute "apio clean"
    # ----------------------------
    result = CliRunner().invoke(cmd_clean)

    #-- Debug! Mostrar la salida
    #print(result.output)

    #-- It should return an exit code of 0: success
    assert result.exit_code == 0
    assert "[SUCCESS]" in result.output


def test_ledon_build():
    """Test the apio build command"""

    # ----------------------------
    # -- Execute "apio build"
    # ----------------------------
    result = CliRunner().invoke(cmd_build)

    #-- Debug! Mostrar la salida
    #print(result.output)

    #-- It should return an exit code of 0: success
    assert result.exit_code == 0
    assert "[SUCCESS]" in result.output
    assert "yosys" in result.output
    assert "nextpnr" in result.output
    assert "icepack" in result.output


def test_ledon_verify():
    """Test the apio verify command"""

    # ----------------------------
    # -- Execute "apio verify"
    # ----------------------------
    result = CliRunner().invoke(cmd_verify)

    #-- Debug! Mostrar la salida
    #print(result.output)

    #-- It should return an exit code of 0: success
    assert result.exit_code == 0
    assert "[SUCCESS]" in result.output
    assert "iverilog" in result.output

def test_ledon_upload():
    """Test the apio verify upload"""

    # ----------------------------
    # -- Execute "apio upload"
    # ----------------------------
    result = CliRunner().invoke(cmd_upload)

    #-- Debug! Mostrar la salida
    print(result.output)

    #-- It should return an exit code of 0: success
    assert result.exit_code == 0
    assert "[SUCCESS]" in result.output
    assert "iceprog" in result.output
