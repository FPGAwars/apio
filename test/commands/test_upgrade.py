"""
  Test for the "apio upgrade" command
"""

import pytest

# -- apio upgrade entry point
from apio.commands.upgrade import cli as cmd_upgrade


def test_upgrade(
    click_cmd_runner, setup_apio_test_env, assert_apio_cmd_ok, offline_flag
):
    """Test "apio upgrade" """

    # -- If the option 'offline' is passed, the test is skip
    # -- (apio upgrade uses internet)
    if offline_flag:
        pytest.skip("requires internet connection")

    with click_cmd_runner.isolated_filesystem():

        # -- Config the environment (conftest.configenv())
        setup_apio_test_env()

        # -- Execute "apio upgrade"
        result = click_cmd_runner.invoke(cmd_upgrade)
        assert_apio_cmd_ok(result)
