"""
  Test for the "apio raw" command
"""

from test.conftest import ApioRunner
from apio.commands.apio import cli as apio


def test_raw(apio_runner: ApioRunner):
    """Test "apio raw" with different parameters"""

    with apio_runner.in_sandbox() as sb:

        # -- Execute "apio raw"
        result = sb.invoke_apio_cmd(apio, ["raw"])
        assert result.exit_code != 0, result.output
        assert "Error: Missing an option or a command" in result.output
        assert "Try 'apio raw -h' for help" in result.output

        # -- Execute "apio raw --env"
        result = sb.invoke_apio_cmd(apio, ["raw", "--env"])
        assert result.exit_code == 0, result.output
        assert "Envirnment settings:" in result.output
        assert "PATH" in result.output
        assert "YOSYS_LIB" in result.output

        # -- Execute "apio raw yosys --version"
        result = sb.invoke_apio_cmd(apio, ["raw", "yosys", "--version"])
        assert result.exit_code != 0, result.output
        assert "package 'oss-cad-suite' is not installed" in result.output
