from apio.commands.uninstall import cli as cmd_uninstall


def test_uninstall(clirunner, validate_cliresult):
    result = clirunner.invoke(cmd_uninstall)
    validate_cliresult(result)


def test_uninstall_list(clirunner, validate_cliresult):
    result = clirunner.invoke(cmd_uninstall, ['--list'])
    validate_cliresult(result)
