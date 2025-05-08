"""Test for the "apio preferences" command."""

import re
from test.conftest import ApioRunner
from apio.common.apio_console import cunstyle
from apio.commands.apio import cli as apio


def test_colors_on_off(apio_runner: ApioRunner):
    """Test "apio preferences" with different parameters"""

    with apio_runner.in_sandbox() as sb:

        # -- Execute "apio preferences"
        result = sb.invoke_apio_cmd(apio, "preferences")
        sb.assert_ok(result)
        assert "'apio preferences' allows" in cunstyle(result.output)
        assert "-t, --theme [light|dark|no-colors]" in result.output
        assert result.output != cunstyle(result.output)  # Colored.

        # -- Execute "apio preferences --theme dark"
        result = sb.invoke_apio_cmd(apio, "preferences", "--theme", "dark")
        sb.assert_ok(result)
        assert "Theme set to [dark]" in result.output
        assert result.output != cunstyle(result.output)  # Colored.

        # -- Execute "apio preferences --list". It should reports the dark
        # -- theme.
        result = sb.invoke_apio_cmd(apio, "preferences", "--list")
        sb.assert_ok(result)
        assert result.output != cunstyle(result.output)  # Colored.
        assert "dark" in result.output

        # -- Execute "apio system info". It should emit colors.
        result = sb.invoke_apio_cmd(apio, "info", "system")
        sb.assert_ok(result)
        assert result.output != cunstyle(result.output)  # Colored.

        # -- Execute "apio preferences --theme no-colors"
        result = sb.invoke_apio_cmd(
            apio, "preferences", "--theme", "no-colors"
        )
        sb.assert_ok(result)
        assert "Theme set to [no-colors]" in result.output

        # -- Execute "apio preferences --list". It should reports the
        # -- no-colors theme.
        result = sb.invoke_apio_cmd(apio, "preferences", "--list")
        sb.assert_ok(result)
        assert re.search(r"Theme.*no-colors", result.output), result.output
        assert result.output == cunstyle(result.output)  # Non colored..

        # -- Execute "apio preferences --colors".
        result = sb.invoke_apio_cmd(apio, "preferences", "--colors")
        assert result.exit_code == 0
        assert result.output != cunstyle(result.output)  # Colored..
        # -- Ideally we would like to have this assertion enabled but
        # -- when running on github workflows we sometimes get different
        # -- colors.
        # assert "\x1b[38;5;237mbar.back        " in result.output
