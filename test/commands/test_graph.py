"""
  Test for the "apio graph" command
"""

# -- apio graph entry point
from apio.commands.graph import cli as cmd_graph


def test_graph_no_apio_ini(click_cmd_runner, setup_apio_test_env):
    """Test: apio graph with no apio.ini"""

    with click_cmd_runner.isolated_filesystem():

        # -- Config the apio test environment
        setup_apio_test_env()

        # -- Execute "apio graph"
        result = click_cmd_runner.invoke(cmd_graph)
        assert result.exit_code == 1, result.output
        assert "Error: insufficient arguments: missing board" in result.output


def test_graph_with_apio_ini(
    click_cmd_runner, setup_apio_test_env, write_apio_ini
):
    """Test: apio graph with apio.ini"""

    with click_cmd_runner.isolated_filesystem():

        # -- Config the apio test environment
        setup_apio_test_env()

        # -- Create an apio.ini file
        write_apio_ini({"board": "icezum", "top-module": "main"})

        # -- Execute "apio graph"
        result = click_cmd_runner.invoke(cmd_graph)
        assert result.exit_code == 1, result.output
        assert "package 'oss-cad-suite' is not installed" in result.output
        assert "apio packages --install --force oss-cad-suite" in result.output

        # -- Execute "apio graph -pdf"
        result = click_cmd_runner.invoke(cmd_graph)
        assert result.exit_code == 1, result.output
        assert "package 'oss-cad-suite' is not installed" in result.output
        assert "apio packages --install --force oss-cad-suite" in result.output

        # -- Execute "apio graph -png"
        result = click_cmd_runner.invoke(cmd_graph)
        assert result.exit_code == 1, result.output
        assert "package 'oss-cad-suite' is not installed" in result.output
        assert "apio packages --install --force oss-cad-suite" in result.output
