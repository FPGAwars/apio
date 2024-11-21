"""
  Test for the "apio test" command
"""

# -- apio test entry point
from apio.commands.sim import cli as cmd_test


def test_test(click_cmd_runner, setup_apio_test_env):
    """Test: apio test
    when no apio.ini file is given
    No additional parameters are given
    """

    with click_cmd_runner.isolated_filesystem():

        # -- Config the environment (conftest.configenv())
        setup_apio_test_env()

        # -- Execute "apio test"
        result = click_cmd_runner.invoke(cmd_test)
        assert result.exit_code != 0, result.output
        # -- TODO
