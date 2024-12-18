"""
  Test for the "apio upload" command
"""

from os import chdir
from test.conftest import ApioRunner
from apio.commands.upload import cli as apio_upload


# R0801: Similar lines in 2 files
# pylint: disable=R0801
def test_upload_without_apio_ini(apio_runner: ApioRunner):
    """Test: apio upload
    when no apio.ini file is given
    No additional parameters are given
    """

    with apio_runner.in_sandbox() as sb:

        # -- Create and change to project dir.
        sb.proj_dir.mkdir()
        chdir(sb.proj_dir)

        # -- Execute "apio upload"
        result = sb.invoke_apio_cmd(apio_upload)

        # -- Check the result
        assert result.exit_code == 1, result.output
        assert "Error: missing project file apio.ini" in result.output


def test_upload_complete(apio_runner: ApioRunner):
    """Test: apio upload with different arguments
    No apio.ini file is given
    """

    with apio_runner.in_sandbox() as sb:

        # -- Create and change to project dir.
        sb.proj_dir.mkdir()
        chdir(sb.proj_dir)

        # -- Execute "apio upload --serial-port COM0"
        sb.write_apio_ini({"board": "alhambra-ii", "top-module": "main"})
        result = sb.invoke_apio_cmd(apio_upload, ["--serial-port", "COM0"])
        assert result.exit_code == 1, result.output
        assert "package 'oss-cad-suite' is not installed" in result.output

        # -- Execute "apio upload --ftdi-id 0"
        result = sb.invoke_apio_cmd(apio_upload, ["--ftdi-id", "0"])
        assert result.exit_code == 1, result.output
        assert "package 'oss-cad-suite' is not installed" in result.output

        # -- Execute "apio upload --sram"
        result = sb.invoke_apio_cmd(apio_upload, ["--sram"])
        assert result.exit_code == 1, result.output
        assert "package 'oss-cad-suite' is not installed" in result.output
