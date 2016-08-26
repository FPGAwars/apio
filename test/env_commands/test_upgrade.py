from apio.commands.upgrade import cli as cmd_upgrade


def test_upgrade(clirunner, validate_cliresult):
    result = clirunner.invoke(cmd_upgrade)
    validate_cliresult(result)
