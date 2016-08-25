import os

from apio.commands.uninstall import cli as cmd_uninstall


def test_uninstall_list(clirunner, validate_cliresult):
    result = clirunner.invoke(cmd_uninstall, ['--list'])
    validate_cliresult(result)


def test_uninstall_examples(clirunner, validate_cliresult):
    with clirunner.isolated_filesystem():
        os.environ["APIO_HOME_DIR"] = os.getcwd()
        result = clirunner.invoke(cmd_uninstall, ['examples'])
        validate_cliresult(result)
        assert 'Do you want to continue?' in result.output
