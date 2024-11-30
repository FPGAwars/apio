"""
  Test for the "apio graph" command
"""

from test.conftest import ApioRunner

# -- apio graph entry point
from apio.commands.graph import cli as apio_graph


def test_graph_no_apio_ini(apio_runner: ApioRunner):
    """Test: apio graph with no apio.ini"""

    with apio_runner.in_sandbox() as sb:

        # -- Execute "apio graph"
        result = sb.invoke_apio_cmd(apio_graph)
        assert result.exit_code == 1, result.output
        assert "Error: insufficient arguments: missing board" in result.output


def test_graph_with_apio_ini(apio_runner: ApioRunner):
    """Test: apio graph with apio.ini"""

    with apio_runner.in_sandbox() as sb:

        # -- Create an apio.ini file
        sb.write_apio_ini({"board": "icezum", "top-module": "main"})

        # -- Execute "apio graph"
        result = sb.invoke_apio_cmd(apio_graph)
        assert result.exit_code == 1, result.output
        assert "package 'oss-cad-suite' is not installed" in result.output
        assert "apio packages --install --force oss-cad-suite" in result.output

        # -- Execute "apio graph -pdf"
        result = sb.invoke_apio_cmd(apio_graph)
        assert result.exit_code == 1, result.output
        assert "package 'oss-cad-suite' is not installed" in result.output
        assert "apio packages --install --force oss-cad-suite" in result.output

        # -- Execute "apio graph -png"
        result = sb.invoke_apio_cmd(apio_graph)
        assert result.exit_code == 1, result.output
        assert "package 'oss-cad-suite' is not installed" in result.output
        assert "apio packages --install --force oss-cad-suite" in result.output
