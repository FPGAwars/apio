"""
  Test for the "apio packages" command
"""

from test.conftest import ApioRunner

# -- apio packages entry point
from apio.commands.packages import cli as apio_packages


def test_packages(apio_runner: ApioRunner):
    """Test "apio packages" with different parameters"""

    with apio_runner.in_sandbox() as sb:

        # -- Execute "apio packages"
        result = sb.invoke_apio_cmd(apio_packages)
        assert result.exit_code == 1, result.output
        assert (
            "specify one of --list, --install, --uninstall, or --fix"
            in result.output
        )

        # -- Execute "apio packages --list"
        result = sb.invoke_apio_cmd(apio_packages, ["--list"])
        assert result.exit_code == 0, result.output
        assert "No errors" in result.output

        # -- Execute "apio packages --install missing_package"
        result = sb.invoke_apio_cmd(
            apio_packages, ["--install", "missing_package"]
        )
        assert result.exit_code == 1, result.output
        assert "Error: unknown package 'missing_package'" in result.output

        # -- Execute "apio packages --uninstall --sayyes missing_package"
        result = sb.invoke_apio_cmd(
            apio_packages, ["--uninstall", "--sayyes", "missing_package"]
        )
        assert result.exit_code == 1, result.output
        assert "Error: no such package 'missing_package'" in result.output
