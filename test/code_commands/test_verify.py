from os import environ, getcwd
from apio.commands.verify import cli as cmd_verify


def test_apio_verify(clirunner):
    with clirunner.isolated_filesystem():
        environ['APIO_HOME_DIR'] = getcwd()
        result = clirunner.invoke(cmd_verify)
        assert result.exit_code == 1
        assert 'apio install scons' in result.output
