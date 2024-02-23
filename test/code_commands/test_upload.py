"""
  Test for the "apio upload" command
"""

# -- apio time entry point
from apio.commands.upload import cli as cmd_upload


def test_upload(clirunner, configenv):
    """Test: apio upload
    when no apio.ini file is given
    No additional parameters are given
    """

    with clirunner.isolated_filesystem():

        # -- Config the environment (conftest.configenv())
        configenv()

        # -- Execute "apio upload"
        result = clirunner.invoke(cmd_upload)

        # -- Check the result
        assert result.exit_code == 1
        assert 'Info: No apio.ini file' in result.output
        assert 'Error: insufficient arguments: missing board' in result.output


def test_upload_board(clirunner, configenv):
    """Test: apio upload --board icezum
    No oss-cad-suite package is installed
    """

    with clirunner.isolated_filesystem():

        # -- Config the environment (conftest.configenv())
        configenv()

        # -- Execute "apio upload --board icezum"
        result = clirunner.invoke(cmd_upload, ['--board', 'icezum'])

        # -- Check the result
        assert result.exit_code == 1
        assert "Error: package 'oss-cad-suite' is not installed" in result.output


def test_upload_complete(clirunner, configenv):
    """Test: apio upload with different arguments
    No apio.ini file is given
    """

    with clirunner.isolated_filesystem():

        # -- Config the environment (conftest.configenv())
        configenv()

        # -- Execute "apio upload --serial-port COM0"
        result = clirunner.invoke(cmd_upload, ['--serial-port', 'COM0'])
        assert result.exit_code == 1
        assert 'Info: No apio.ini file' in result.output
        assert 'Error: insufficient arguments: missing board' in result.output

        # -- Execute "apio upload --ftdi-id 0"
        result = clirunner.invoke(cmd_upload, ['--ftdi-id', '0'])
        assert result.exit_code == 1
        assert 'Info: No apio.ini file' in result.output
        assert 'Error: insufficient arguments: missing board' in result.output


        # -- Execute "apio upload --sram"
        result = clirunner.invoke(cmd_upload, ['--sram'])
        assert result.exit_code == 1
        assert 'Info: No apio.ini file' in result.output
        assert 'Error: insufficient arguments: missing board' in result.output

        # -- Execute "apio upload --board icezum --serial-port COM0"
        result = clirunner.invoke(cmd_upload, [
            '--board', 'icezum', '--serial-port', 'COM0'])
        assert result.exit_code == 1
        assert "Error: package 'oss-cad-suite' is not installed" in result.output

        # -- Execute "apio upload --board icezum --ftdi-id 0"
        result = clirunner.invoke(cmd_upload, [
            '--board', 'icezum', '--ftdi-id', '0'])
        assert result.exit_code == 1
        assert "Error: package 'oss-cad-suite' is not installed" in result.output

        # -- Execute "apio upload --board icezum --sram"
        result = clirunner.invoke(cmd_upload, [
            '--board', 'icezum', '--sram'])
        assert result.exit_code == 1
        assert "Error: package 'oss-cad-suite' is not installed" in result.output
