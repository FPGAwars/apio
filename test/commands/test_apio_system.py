"""
  Test for the "apio system" command
"""

from test.conftest import ApioRunner
from apio.commands.apio import cli as apio
from apio.common.apio_console import cunstyle


def test_system(apio_runner: ApioRunner):
    """Test "apio system" with different parameters"""

    with apio_runner.in_sandbox() as sb:

        # -- Execute "apio system"
        result = sb.invoke_apio_cmd(apio, "system")
        sb.assert_ok(result)
        assert "Subcommands" in result.output
        assert "platforms" in result.output

        # -- Execute "apio system info"
        result = sb.invoke_apio_cmd(apio, "system", "info")
        assert result.exit_code == 0, result.output
        assert "Platform id" in result.output
        # -- The these env options are set by the apio text fixture.
        assert "Active env options [APIO_HOME_DIR]" in result.output

        # -- Execute "apio system platforms"
        result = sb.invoke_apio_cmd(apio, "system", "platforms")
        assert result.exit_code == 0, result.output
        assert "darwin_arm64" in result.output
        assert "Mac OSX, ARM 64 bit" in result.output

        # -- Execute "apio system colors"
        result = sb.invoke_apio_cmd(apio, "system", "colors")
        assert result.exit_code == 0, result.output
        assert result.output != cunstyle(result.output)  # Colored
        assert "ANSI Colors [RICH mode]" in result.output
        assert "\x1b[31m  1 red                 \x1b[0m" in result.output

        # -- Execute "apio system info". It should not emit colors.
        result = sb.invoke_apio_cmd(apio, "system", "info")
        sb.assert_ok(result)
        assert result.output != cunstyle(result.output)  # Colored
