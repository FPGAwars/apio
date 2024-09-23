"""
  Test for the "apio drivers" command
"""

# -- apio drivers entry point
from apio.commands.drivers import cli as cmd_drivers


def test_drivers(clirunner, validate_cliresult, configenv):
    """Test "apio drivers" with different parameters"""

    with clirunner.isolated_filesystem():

        # -- Config the environment (conftest.configenv())
        configenv()

        # -- Execute "apio drivers"
        result = clirunner.invoke(cmd_drivers)
        validate_cliresult(result)
