"""
  Test for the "apio graph" command
"""

# -- apio graph entry point
from apio.commands.graph import cli as cmd_graph


def test_graph(clirunner, configenv):
    """Test: apio graph
    when no apio.ini file is given
    No additional parameters are given
    """

    with clirunner.isolated_filesystem():

        # -- Config the environment (conftest.configenv())
        configenv()

        # -- Execute "apio graph"
        result = clirunner.invoke(cmd_graph)

        # -- Check the result
        assert result.exit_code != 0
        # -- TODO (FIXME!)