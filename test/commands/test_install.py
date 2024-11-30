"""
  Test for the "apio install" command
"""

from test.conftest import ApioRunner

# -- apio install entry point
from apio.commands.install import cli as apio_install


def test_install(apio_runner: ApioRunner):
    """Test "apio install" with different parameters"""

    with apio_runner.in_sandbox() as sb:

        # -- Execute "apio install"
        result = sb.invoke_apio_cmd(apio_install)
        sb.assert_ok(result)

        # -- Execute "apio install --list"
        result = sb.invoke_apio_cmd(apio_install, ["--list"])
        sb.assert_ok(result)

        # -- Execute "apio install missing_package"
        result = sb.invoke_apio_cmd(apio_install, ["missing_package"])
        assert result.exit_code == 1, result.output
        assert "Error: no such package" in result.output
