from os import environ, getcwd
from apio.commands.clean import cli as cmd_clean


def test_clean(clirunner):
    with clirunner.isolated_filesystem():
        environ['APIO_HOME_DIR'] = getcwd()
        result = clirunner.invoke(cmd_clean)
        assert result.exit_code != 0
        if result.exit_code == 1:
            assert 'apio install scons' in result.output
