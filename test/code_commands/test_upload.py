from os import environ, getcwd
from apio.commands.upload import cli as cmd_upload


def test_upload(clirunner):
    with clirunner.isolated_filesystem():
        environ['APIO_HOME_DIR'] = getcwd()
        result = clirunner.invoke(cmd_upload)
        assert result.exit_code == 1
        assert 'Info: No apio.ini file' in result.output
        assert 'Error: insufficient arguments: missing board' in result.output


def test_upload_device(clirunner):
    with clirunner.isolated_filesystem():
        environ['APIO_HOME_DIR'] = getcwd()
        result = clirunner.invoke(cmd_upload, ['--device', '0'])
        assert result.exit_code == 1
        assert 'Info: No apio.ini file' in result.output
        assert 'Error: insufficient arguments: missing board' in result.output


def test_upload_device(clirunner):
    with clirunner.isolated_filesystem():
        environ['APIO_HOME_DIR'] = getcwd()
        result = clirunner.invoke(cmd_upload, ['--board', 'icezum', '--device', '0'])
        assert result.exit_code == 1
        assert 'apio install system' in result.output


def test_upload_board(clirunner):
    with clirunner.isolated_filesystem():
        environ['APIO_HOME_DIR'] = getcwd()
        result = clirunner.invoke(cmd_upload, ['--board', 'icezum'])
        assert result.exit_code == 1
        assert 'apio install system' in result.output
