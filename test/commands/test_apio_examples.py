"""
  Test for the "apio examples" command
"""

from test.conftest import ApioRunner

# -- apio examples entry point
from apio.commands.apio_examples import cli as apio_examples


def test_examples(apio_runner: ApioRunner):
    """Test "apio examples" with different parameters"""

    with apio_runner.in_sandbox() as sb:

        # -- Execute "apio examples"
        result = sb.invoke_apio_cmd(apio_examples)
        sb.assert_ok(result)
        assert "Subcommands:" in result.output
        assert "examples list" in result.output

        # -- Execute "apio examples list"
        result = sb.invoke_apio_cmd(apio_examples, ["list"])
        assert result.exit_code == 1, result.output
        assert "package 'examples' is not installed" in result.output

        # -- Execute "apio examples fetch alhambra-ii/ledon"
        result = sb.invoke_apio_cmd(
            apio_examples, ["fetch", "alhambra-ii/ledon"]
        )
        assert result.exit_code == 1, result.output
        assert "package 'examples' is not installed" in result.output

        # -- Execute "apio examples fetch-board alhambra-ii"
        result = sb.invoke_apio_cmd(
            apio_examples, ["fetch-board", "alhambra-ii"]
        )
        assert result.exit_code == 1, result.output
        assert "package 'examples' is not installed" in result.output
