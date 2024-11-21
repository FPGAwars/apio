"""
  Test for the "apio boards" command
"""

# -- apio fpgas entry point
from apio.commands.fpgas import cli as cmd_fpgas


def test_boards(click_cmd_runner, setup_apio_test_env, assert_apio_cmd_ok):
    """Test "apio fpgas" command."""

    with click_cmd_runner.isolated_filesystem():

        # -- Config the environment (conftest.configenv())
        setup_apio_test_env()

        # -- Execute "apio fpgas"
        result = click_cmd_runner.invoke(cmd_fpgas)
        assert_apio_cmd_ok(result)
        assert "iCE40-HX4K-TQ144" in result.output
