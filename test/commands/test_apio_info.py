"""Test for the "apio system" command."""

import re
from test.conftest import ApioRunner
from apio.commands.apio import cli as apio
from apio.common.apio_console import cunstyle, cwidth


def test_apio_info(apio_runner: ApioRunner):
    """Test "apio info" with different parameters"""

    with apio_runner.in_sandbox() as sb:
        # -- For debugging table column truncation in github testing.
        print(f"Apio console width = {cwidth()}")

        # -- Execute "apio info"
        result = sb.invoke_apio_cmd(apio, ["info"])
        sb.assert_ok(result)
        assert "Documentation:" in result.output
        assert "Documentation:" in result.output
        assert "platforms" in result.output

        # -- Execute "apio info system"
        result = sb.invoke_apio_cmd(apio, ["info", "system"])
        assert result.exit_code == 0, result.output
        assert "Platform id" in result.output
        # -- The these env options are set by the apio text fixture. We
        # -- relax the expression to allow additional env vars that are
        # -- injected to the test such as APIO_REMOTE_URL_CONFIG
        assert re.search(
            r"Active env options \[[^]]*APIO_HOME[^]]*\]", result.output
        )

        # -- Execute "apio info platforms"
        result = sb.invoke_apio_cmd(apio, ["info", "platforms"])
        assert result.exit_code == 0, result.output
        assert "darwin-arm64" in result.output
        assert "Mac OSX, ARM 64 bit (Apple Silicon)" in result.output

        # -- Execute "apio info colors"
        result = sb.invoke_apio_cmd(apio, ["info", "colors"])
        assert result.exit_code == 0, result.output
        assert result.output != cunstyle(result.output)  # Colored
        assert "ANSI Colors [RICH mode]" in result.output
        assert "\x1b[31m  1 red                 \x1b[0m" in result.output

        # -- Execute "apio info system". It should not emit colors.
        result = sb.invoke_apio_cmd(apio, ["info", "system"])
        sb.assert_ok(result)
        assert result.output != cunstyle(result.output)  # Colored

        # -- Execute "apio info cli"
        result = sb.invoke_apio_cmd(apio, ["info", "cli"])
        sb.assert_ok(result)
        assert "This page describes the conventions" in cunstyle(result.output)
        assert result.output != cunstyle(result.output)  # Colored.

        # # -- Execute "apio info resources"
        result = sb.invoke_apio_cmd(apio, ["info", "resources"])
        assert result.exit_code == 0
        assert "Apio documentation" in result.output
        assert result.output != cunstyle(result.output)  # Colored.
