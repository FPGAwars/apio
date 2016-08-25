from apio.commands.drivers import cli as cmd_drivers


def test_drivers(clirunner, validate_cliresult):
    result = clirunner.invoke(cmd_drivers)
    validate_cliresult(result)
