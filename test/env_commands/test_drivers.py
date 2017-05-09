from apio.commands.drivers import cli as cmd_drivers


def test_drivers(clirunner, validate_cliresult, configenv):
    with clirunner.isolated_filesystem():
        configenv()
        result = clirunner.invoke(cmd_drivers)
        validate_cliresult(result)
