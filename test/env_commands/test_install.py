from os import environ, getcwd
from apio.commands.install import cli as cmd_install


def test_install(clirunner, validate_cliresult):
    result = clirunner.invoke(cmd_install)
    validate_cliresult(result)


def test_install_list(clirunner, validate_cliresult):
    with clirunner.isolated_filesystem():
        environ['APIO_HOME_DIR'] = getcwd()
        result = clirunner.invoke(cmd_install, ['--list'])
        validate_cliresult(result)


def test_install_wrong_package(clirunner):
    with clirunner.isolated_filesystem():
        environ['APIO_HOME_DIR'] = getcwd()
        result = clirunner.invoke(cmd_install, ['missing_package'])
        assert result.exit_code == 0
        assert 'Error: No such package' in result.output
