"""
  Test for the "apio lint" command
"""

# -- apio lint entry point
from apio.commands.lint import cli as cmd_lint


def test_lint(click_cmd_runner, setup_apio_test_env):
    """Test: apio lint
    when no apio.ini file is given
    No additional parameters are given
    """

    with click_cmd_runner.isolated_filesystem():

        # -- Config the apio test environment
        setup_apio_test_env()

        # -- Execute "apio lint"
        result = click_cmd_runner.invoke(cmd_lint, ["--board", "alhambra-ii"])
        assert result.exit_code != 0, result.output
