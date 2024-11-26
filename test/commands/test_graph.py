"""
  Test for the "apio graph" command
"""

from test.conftest import ApioRunner

# -- apio graph entry point
from apio.commands.graph import cli as apio_graph


def test_graph_no_apio_ini(apio_runner: ApioRunner):
    """Test: apio graph with no apio.ini"""

    with apio_runner.in_disposable_temp_dir():

        # -- Config the apio test environment
        apio_runner.setup_env()

        # -- Execute "apio graph"
        result = apio_runner.invoke(apio_graph)
        assert result.exit_code == 1, result.output
        assert "Error: insufficient arguments: missing board" in result.output


def test_graph_with_apio_ini(apio_runner: ApioRunner):
    """Test: apio graph with apio.ini"""

    with apio_runner.in_disposable_temp_dir():

        # -- Config the apio test environment
        apio_runner.setup_env()

        # -- Create an apio.ini file
        apio_runner.write_apio_ini({"board": "icezum", "top-module": "main"})

        # -- Execute "apio graph"
        result = apio_runner.invoke(apio_graph)
        assert result.exit_code == 1, result.output
        assert "package 'oss-cad-suite' is not installed" in result.output
        assert "apio packages --install --force oss-cad-suite" in result.output

        # -- Execute "apio graph -pdf"
        result = apio_runner.invoke(apio_graph)
        assert result.exit_code == 1, result.output
        assert "package 'oss-cad-suite' is not installed" in result.output
        assert "apio packages --install --force oss-cad-suite" in result.output

        # -- Execute "apio graph -png"
        result = apio_runner.invoke(apio_graph)
        assert result.exit_code == 1, result.output
        assert "package 'oss-cad-suite' is not installed" in result.output
        assert "apio packages --install --force oss-cad-suite" in result.output
