"""
  Test for the "apio boards" command
"""

# -- apio boards entry point
from apio.commands.boards import cli as cmd_boards


def test_boards(click_cmd_runner, setup_apio_test_env, assert_apio_cmd_ok):
    """Test "apio boards" command."""

    with click_cmd_runner.isolated_filesystem():

        # -- Config the environment (conftest.configenv())
        setup_apio_test_env()

        # -- Execute "apio boards"
        result = click_cmd_runner.invoke(cmd_boards)
        assert_apio_cmd_ok(result)
        assert "alhambra-ii" in result.output
