"""
  Test for the "apio graph" command
"""

from os import chdir
from test.conftest import ApioRunner
from apio.commands.apio_graph import cli as apio_graph


# R0801: Similar lines in 2 files
# pylint: disable=R0801
def test_graph_no_apio_ini(apio_runner: ApioRunner):
    """Test: apio graph with no apio.ini"""

    with apio_runner.in_sandbox() as sb:

        # -- Create and change to project dir.
        sb.proj_dir.mkdir()
        chdir(sb.proj_dir)

        # -- Execute "apio graph"
        result = sb.invoke_apio_cmd(apio_graph)
        assert result.exit_code == 1, result.output
        assert "Error: missing project file apio.ini" in result.output


def test_graph_with_apio_ini(apio_runner: ApioRunner):
    """Test: apio graph with apio.ini"""

    with apio_runner.in_sandbox() as sb:

        # -- Create and change to project dir.
        sb.proj_dir.mkdir()
        chdir(sb.proj_dir)

        # -- Create an apio.ini file
        sb.write_default_apio_ini()

        # -- Execute "apio graph"
        result = sb.invoke_apio_cmd(apio_graph)
        assert result.exit_code == 1, result.output
        assert "package 'oss-cad-suite' is not installed" in result.output

        # -- Execute "apio graph -pdf"
        result = sb.invoke_apio_cmd(apio_graph)
        assert result.exit_code == 1, result.output
        assert "package 'oss-cad-suite' is not installed" in result.output

        # -- Execute "apio graph -png"
        result = sb.invoke_apio_cmd(apio_graph)
        assert result.exit_code == 1, result.output
        assert "package 'oss-cad-suite' is not installed" in result.output
