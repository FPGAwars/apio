"""
  Test for the "apio config" command
"""

# -- apio config entry point
from apio.commands.config import cli as cmd_config


def test_config(clirunner, validate_cliresult, configenv):
    """Test "apio config" with different parameters"""

    with clirunner.isolated_filesystem():

        # -- Config the environment (conftest.configenv())
        configenv()

        # -- Execute "apio config"
        result = clirunner.invoke(cmd_config)
        validate_cliresult(result)

        # -- Execute "apio config --list"
        result = clirunner.invoke(cmd_config, ['--list'])
        validate_cliresult(result)

        # -- Execute "apio config --exe native"
        result = clirunner.invoke(cmd_config, ['--exe', 'native'])
        validate_cliresult(result)
