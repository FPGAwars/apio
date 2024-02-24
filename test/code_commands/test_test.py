"""
  Test for the "apio test" command
"""

# -- apio test entry point
from apio.commands.sim import cli as cmd_test


def test_test(clirunner, configenv):
    """Test: apio test
    when no apio.ini file is given
    No additional parameters are given
    """

    with clirunner.isolated_filesystem():

        # -- Config the environment (conftest.configenv())
        configenv()

        # -- Execute "apio test"
        result = clirunner.invoke(cmd_test)
        assert result.exit_code != 0
        # -- TODO
