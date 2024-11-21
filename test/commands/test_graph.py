"""
  Test for the "apio graph" command
"""

# -- apio graph entry point
from apio.commands.graph import cli as cmd_graph


def test_graph(click_cmd_runner, setup_apio_test_env):
    """Test: apio graph
    when no apio.ini file is given
    No additional parameters are given
    """

    with click_cmd_runner.isolated_filesystem():

        # -- Config the environment (conftest.configenv())
        setup_apio_test_env()

        # -- Execute "apio graph"
        result = click_cmd_runner.invoke(cmd_graph)

        # -- Check the result
        assert result.exit_code != 0, result.output
        # -- TODO (FIXME!)
