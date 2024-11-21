"""
  Test for the "apio drivers" command
"""

# -- apio drivers entry point
from apio.commands.drivers import cli as cmd_drivers


def test_drivers(click_cmd_runner, assert_apio_cmd_ok, setup_apio_test_env):
    """Test "apio drivers" with different parameters"""

    with click_cmd_runner.isolated_filesystem():

        # -- Config the apio test environment
        setup_apio_test_env()

        # -- Execute "apio drivers"
        result = click_cmd_runner.invoke(cmd_drivers)
        assert_apio_cmd_ok(result)
