"""
  Test for the "apio drivers" command
"""

from test.conftest import ApioRunner

# -- apio drivers entry point
from apio.commands.drivers import cli as apio_drivers


def test_drivers(apio_runner: ApioRunner):
    """Test "apio drivers" """

    with apio_runner.in_sandbox() as sb:

        # -- Execute "apio drivers"
        result = sb.invoke_apio_cmd(apio_drivers)
        assert result.exit_code == 1
        assert (
            "Error: Specify one of [--ftdi-install, --ftdi-uninstall, "
            "--serial-install, --serial-uninstall]" in result.output
        )

        # -- Execute "apio --ftdi-install, --serial-install"
        result = sb.invoke_apio_cmd(
            apio_drivers, ["--ftdi-install", "--serial-install"]
        )
        assert result.exit_code == 1, result.output
        assert (
            "Error: Specify only one of [--ftdi-install, --serial-install]"
            in result.output
        )
