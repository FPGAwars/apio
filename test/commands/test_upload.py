"""
  Test for the "apio upload" command
"""

from test.conftest import ApioRunner

# -- apio time entry point
from apio.commands.upload import cli as apio_upload


def test_upload(apio_runner: ApioRunner):
    """Test: apio upload
    when no apio.ini file is given
    No additional parameters are given
    """

    with apio_runner.in_sandbox() as sb:

        # -- Execute "apio upload"
        result = sb.invoke_apio_cmd(apio_upload)

        # -- Check the result
        assert result.exit_code == 1, result.output
        assert "Info: Project has no apio.ini file" in result.output
        assert "Error: insufficient arguments: missing board" in result.output


def test_upload_board(apio_runner: ApioRunner):
    """Test: apio upload --board icezum
    No oss-cad-suite package is installed
    """

    with apio_runner.in_sandbox() as sb:

        # -- Execute "apio upload --board icezum"
        result = sb.invoke_apio_cmd(apio_upload, ["--board", "icezum"])

        # -- Check the result
        assert result.exit_code == 1
        assert (
            "Error: package 'oss-cad-suite' is not installed" in result.output
        )


def test_upload_complete(apio_runner: ApioRunner):
    """Test: apio upload with different arguments
    No apio.ini file is given
    """

    with apio_runner.in_sandbox() as sb:

        # -- Execute "apio upload --serial-port COM0"
        result = sb.invoke_apio_cmd(apio_upload, ["--serial-port", "COM0"])
        assert result.exit_code == 1, result.output
        assert "Info: Project has no apio.ini file" in result.output
        assert "Error: insufficient arguments: missing board" in result.output

        # -- Execute "apio upload --ftdi-id 0"
        result = sb.invoke_apio_cmd(apio_upload, ["--ftdi-id", "0"])
        assert result.exit_code == 1, result.output
        assert "Info: Project has no apio.ini file" in result.output
        assert "Error: insufficient arguments: missing board" in result.output

        # -- Execute "apio upload --sram"
        result = sb.invoke_apio_cmd(apio_upload, ["--sram"])
        assert result.exit_code == 1, result.output
        assert "Info: Project has no apio.ini file" in result.output
        assert "Error: insufficient arguments: missing board" in result.output

        # -- Execute "apio upload --board icezum --serial-port COM0"
        result = sb.invoke_apio_cmd(
            apio_upload, ["--board", "icezum", "--serial-port", "COM0"]
        )
        assert result.exit_code == 1, result.output
        assert (
            "Error: package 'oss-cad-suite' is not installed" in result.output
        )

        # -- Execute "apio upload --board icezum --ftdi-id 0"
        result = sb.invoke_apio_cmd(
            apio_upload, ["--board", "icezum", "--ftdi-id", "0"]
        )
        assert result.exit_code == 1, result.output
        assert (
            "Error: package 'oss-cad-suite' is not installed" in result.output
        )

        # -- Execute "apio upload --board icezum --sram"
        result = sb.invoke_apio_cmd(
            apio_upload, ["--board", "icezum", "--sram"]
        )
        assert result.exit_code == 1, result.output
        assert (
            "Error: package 'oss-cad-suite' is not installed" in result.output
        )
