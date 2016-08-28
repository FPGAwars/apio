from os import environ, getcwd
from apio.commands.uninstall import cli as cmd_uninstall


def test_uninstall(clirunner, validate_cliresult):
    result = clirunner.invoke(cmd_uninstall)
    validate_cliresult(result)


def test_uninstall_list(clirunner, validate_cliresult):
    with clirunner.isolated_filesystem():
        environ['APIO_HOME_DIR'] = getcwd()
        result = clirunner.invoke(cmd_uninstall, ['--list'])
        validate_cliresult(result)


def test_uninstall_wrong_package(clirunner):
    with clirunner.isolated_filesystem():
        environ['APIO_HOME_DIR'] = getcwd()
        result = clirunner.invoke(
            cmd_uninstall, ['missing_package'], input='y')
        assert result.exit_code == 0
        assert 'Do you want to continue?' in result.output
        assert 'Error: No such package' in result.output
