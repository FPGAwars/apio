"""
  Test for the "apio examples" command
"""

from test.conftest import ApioRunner
from click.termui import unstyle
from apio.commands.apio import cli as apio


def test_examples(apio_runner: ApioRunner):
    """Test "apio examples" with different parameters"""

    with apio_runner.in_sandbox() as sb:

        # -- Execute "apio examples"
        result = sb.invoke_apio_cmd(apio, ["examples"])
        sb.assert_ok(result)
        assert "Subcommands:" in unstyle(result.output)
        assert "examples list" in unstyle(result.output)
