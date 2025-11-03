"""Test for the "apio system" command."""

import re
from test.conftest import ApioRunner
from apio.commands.apio import apio_top_cli as apio
from apio.common.apio_console import cunstyle, cwidth


def test_apio_info(apio_runner: ApioRunner):
    """Test "apio info" with different parameters"""

    with apio_runner.in_sandbox() as sb:
        # -- For debugging table column truncation in github testing.
        print(f"Apio console width = {cwidth()}")

        # -- Execute "apio info"
        result = sb.invoke_apio_cmd(apio, ["info"])
        sb.assert_ok(result)
        assert "platforms" in result.output

        # -- Execute "apio info system"
        result = sb.invoke_apio_cmd(apio, ["info", "system"])
        sb.assert_ok(result)
        assert "Platform id" in result.output
        # -- The these env options are set by the apio text fixture. We
        # -- relax the expression to allow additional env vars that are
        # -- injected to the test such as APIO_REMOTE_URL_CONFIG
        assert re.search(
            r"Active env options \[[^]]*APIO_HOME[^]]*\]", result.output
        )

        # -- Execute "apio info platforms"
        result = sb.invoke_apio_cmd(apio, ["info", "platforms"])
        sb.assert_ok(result)
        assert "darwin-arm64" in result.output
        assert "Mac OSX" in result.output
        assert "ARM 64 bit (Apple Silicon)" in result.output

        # -- Execute "apio info colors"
        result = sb.invoke_apio_cmd(apio, ["info", "colors"])
        sb.assert_ok(result)
        assert result.output != cunstyle(result.output)  # Colored
        assert "ANSI Colors" in result.output
        assert "\x1b[31m  1 red                 \x1b[0m" in result.output

        # -- Execute "apio info themes"
        result = sb.invoke_apio_cmd(apio, ["info", "themes"])
        # -- It's normal to have 'error' in the output text.
        sb.assert_ok(result, bad_words=[])
        assert result.output != cunstyle(result.output)  # Colored
        assert "NO-COLORS" in result.output
        assert "apio.cmd_name\x1b[0m" in result.output

        # -- Execute "apio info system". It should not emit colors.
        result = sb.invoke_apio_cmd(apio, ["info", "system"])
        sb.assert_ok(result)
        assert result.output != cunstyle(result.output)  # Colored
