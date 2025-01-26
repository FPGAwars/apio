"""
  Test for the "apio examples" command
"""

from test.conftest import ApioRunner
from apio.common.apio_console import cunstyle
from apio.commands.apio import cli as apio


def test_examples(apio_runner: ApioRunner):
    """Test "apio examples" with different parameters"""

    with apio_runner.in_sandbox() as sb:

        # -- Execute "apio examples"
        result = sb.invoke_apio_cmd(apio, ["examples"])
        sb.assert_ok(result)
        assert "Subcommands:" in cunstyle(result.output)
        assert "examples list" in cunstyle(result.output)
