from apio.commands.config import cli as cmd_config


def test_config(clirunner, validate_cliresult):
    result = clirunner.invoke(cmd_config)
    validate_cliresult(result)


def test_config_list(clirunner, validate_cliresult):
    result = clirunner.invoke(cmd_config, ['--list'])
    validate_cliresult(result)


def test_config_exe(clirunner, validate_cliresult):
    result = clirunner.invoke(cmd_config, ['--exe', 'native'])
    validate_cliresult(result)
