"""
  Test for the "apio preferences" command
"""

from test.conftest import ApioRunner
from click import unstyle
from apio.commands.apio import cli as apio


def test_colors_on_off(apio_runner: ApioRunner):
    """Test "apio preferences" with different parameters"""

    with apio_runner.in_sandbox() as sb:

        # -- Execute "apio preferences set --colors on"
        result = sb.invoke_apio_cmd(
            apio, ["preferences", "set", "--colors", "on"], color=True
        )
        sb.assert_ok(result)
        assert "\n\x1b[32m\x1b[1mColors set to [on]\x1b[0m\n" in result.output

        # -- Execute "apio preferences list". It should reports colors on,
        # -- in colors.
        result = sb.invoke_apio_cmd(apio, ["preferences", "list"], color=True)
        sb.assert_ok(result)
        assert "\nColors:   \x1b[36m\x1b[1mon\x1b[0m\n" in result.output

        # -- Execute "apio system info". It should emit colors.
        result = sb.invoke_apio_cmd(apio, ["system", "info"], color=True)
        sb.assert_ok(result)
        assert result.output != unstyle(result.output)

        # -- Execute "apio preferences set --colors off"
        result = sb.invoke_apio_cmd(
            apio, ["preferences", "set", "--colors", "off"], color=True
        )
        sb.assert_ok(result)
        assert "\nColors set to [off]\n" in result.output
        print(result.output)

        # -- Execute "apio preferences list". It should reports colors off,
        # -- without colors.
        result = sb.invoke_apio_cmd(apio, ["preferences", "list"], color=True)
        sb.assert_ok(result)
        assert "\nColors:   off\n" in result.output

        # -- Execute "apio system info". It should not emit colors.
        result = sb.invoke_apio_cmd(apio, ["system", "info"], color=True)
        sb.assert_ok(result)
        assert result.output == unstyle(result.output)
