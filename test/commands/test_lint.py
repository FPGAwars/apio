"""
  Test for the "apio lint" command
"""
# -- apio lint entry point
from apio.commands.lint import cli as cmd_lint


def test_lint(clirunner, configenv):
    """Test: apio lint
    when no apio.ini file is given
    No additional parameters are given
    """

    with clirunner.isolated_filesystem():

        # -- Config the environment (conftest.configenv())
        configenv()

        # -- Execute "apio lint"
        result = clirunner.invoke(cmd_lint, ['--board', 'alhambra-ii'])
        assert result.exit_code != 0
