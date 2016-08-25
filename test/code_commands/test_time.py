from os import environ, getcwd
from apio.commands.time import cli as cmd_time


def test_time(clirunner):
    with clirunner.isolated_filesystem():
        environ['APIO_HOME_DIR'] = getcwd()
        result = clirunner.invoke(cmd_upload)
        assert result.exit_code == 1
        assert 'Info: No apio.ini file' in result.output
        assert 'Error: insufficient arguments: missing board' in result.output


def test_time_board(clirunner):
    with clirunner.isolated_filesystem():
        environ['APIO_HOME_DIR'] = getcwd()
        result = clirunner.invoke(cmd_time, ['--board', 'icezum'])
        assert result.exit_code == 1
        assert 'apio install scons' in result.output
