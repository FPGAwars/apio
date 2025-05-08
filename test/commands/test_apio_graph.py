"""Test for the "apio graph" command."""

from test.conftest import ApioRunner
from apio.commands.apio import cli as apio


def test_graph_no_apio_ini(apio_runner: ApioRunner):
    """Test: apio graph with no apio.ini"""

    with apio_runner.in_sandbox() as sb:

        # -- Execute "apio graph"
        result = sb.invoke_apio_cmd(apio, "graph")
        assert result.exit_code == 1, result.output
        assert "Error: Missing project file apio.ini" in result.output
