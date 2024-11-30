"""
  Test for the "apio clean" command
"""

from pathlib import Path
from test.conftest import ApioRunner


# -- apio clean entry point
from apio.commands.clean import cli as apio_clean


def test_clean_no_apio_ini_no_params(apio_runner: ApioRunner):
    """Test: apio clean when no apio.ini file is given
    No additional parameters are given
    """

    with apio_runner.in_sandbox() as sb:

        # -- Execute "apio clean"
        result = sb.invoke_apio_cmd(apio_clean)

        # -- It is an error. Exit code should not be 0
        assert result.exit_code != 0, result.output
        assert "Info: Project has no apio.ini file" in result.output
        assert "Error: insufficient arguments: missing board" in result.output

        # -- Execute "apio clean --board alhambra-ii"
        result = sb.invoke_apio_cmd(apio_clean, ["--board", "alhambra-ii"])
        assert result.exit_code == 0, result.output


def test_clean_no_apio_ini_params(apio_runner: ApioRunner):
    """Test: apio clean when no apio.ini file is given. Board definition
    comes from --board parameter.
    """

    with apio_runner.in_sandbox() as sb:

        # -- Create a legacy artifact file.
        Path("main_tb.vcd").touch()

        # -- Create a current artifact file.
        Path("_build").mkdir()
        Path("_build/main_tb.vcd").touch()

        # Confirm that the files exists
        assert Path("main_tb.vcd").is_file()
        assert Path("_build/main_tb.vcd").is_file()

        # -- Execute "apio clean --board alhambra-ii"
        result = sb.invoke_apio_cmd(apio_clean, ["--board", "alhambra-ii"])
        assert result.exit_code == 0, result.output

        # Confirm that the files do not exist.
        assert not Path("main_tb.vcd").exists()
        assert not Path("_build/main_tb.vcd").exists()


def test_clean_create(apio_runner: ApioRunner):
    """Test: apio clean when there is an apio.ini file"""

    with apio_runner.in_sandbox() as sb:

        # -- Create apio.ini
        sb.write_apio_ini({"board": "icezum", "top-module": "main"})

        # -- Create a legacy artifact file.
        Path("main_tb.vcd").touch()

        # -- Create a current artifact file.
        Path("_build").mkdir()
        Path("_build/main_tb.vcd").touch()

        # Confirm that the files exists
        assert Path("main_tb.vcd").is_file()
        assert Path("_build/main_tb.vcd").is_file()

        # --- Execute "apio clean"
        result = sb.invoke_apio_cmd(apio_clean)
        assert result.exit_code == 0, result.output

        # Confirm that the files do not exist.
        assert not Path("main_tb.vcd").exists()
        assert not Path("_build/main_tb.vcd").exists()
