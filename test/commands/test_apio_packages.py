"""
  Test for the "apio packages" command
"""

from test.conftest import ApioRunner
from apio.commands.apio import cli as apio


def test_packages(apio_runner: ApioRunner):
    """Test "apio packages" with different parameters"""

    with apio_runner.in_sandbox() as sb:

        # -- Execute "apio packages"
        result = sb.invoke_apio_cmd(apio, ["packages"])
        sb.assert_ok(result)
        assert "Subcommands:" in result.output
        assert "apio packages install" in result.output

        # -- Execute "apio packages list"
        result = sb.invoke_apio_cmd(apio, ["packages", "list"])
        sb.assert_ok(result)

        # -- Execute "apio packages install no-such-package"
        result = sb.invoke_apio_cmd(
            apio, ["packages", "install", "no-such-package"]
        )
        assert result.exit_code == 1, result.output
        assert "Error: no such package 'no-such-package'" in result.output

        # -- Execute "apio packages uninstall no-such-package"
        result = sb.invoke_apio_cmd(
            apio, ["packages", "uninstall", "no-such-package"]
        )
        assert result.exit_code == 1, result.output
        assert "Error: no such package 'no-such-package'" in result.output

        # -- Execute "apio packages fix"
        result = sb.invoke_apio_cmd(apio, ["packages", "fix"])
        assert result.exit_code == 0, result.output
