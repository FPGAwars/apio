"""
  Test for the "apio examples" command
"""

from test.conftest import ApioRunner
from apio.commands.apio import cli as apio


def test_examples(apio_runner: ApioRunner):
    """Test "apio examples" with different parameters"""

    with apio_runner.in_sandbox() as sb:

        # -- Execute "apio examples"
        result = sb.invoke_apio_cmd(apio, ["examples"])
        sb.assert_ok(result)
        assert "Subcommands:" in result.output
        assert "examples list" in result.output

        # -- Execute "apio examples list"
        result = sb.invoke_apio_cmd(apio, ["examples", "list"])
        assert result.exit_code == 1, result.output
        assert "package 'examples' is not installed" in result.output

        # -- Execute "apio examples fetch alhambra-ii/ledon"
        result = sb.invoke_apio_cmd(
            apio, ["examples", "fetch", "alhambra-ii/ledon"]
        )
        assert result.exit_code == 1, result.output
        assert "package 'examples' is not installed" in result.output

        # -- Execute "apio examples fetch-board alhambra-ii"
        result = sb.invoke_apio_cmd(
            apio, ["examples", "fetch-board", "alhambra-ii"]
        )
        assert result.exit_code == 1, result.output
        assert "package 'examples' is not installed" in result.output
