"""
  Test for the "apio system" command
"""

from test.conftest import ApioRunner

# -- apio system entry point
from apio.commands.system import cli as apio_system


def test_system(apio_runner: ApioRunner):
    """Test "apio system" with different parameters"""

    with apio_runner.in_sandbox() as sb:

        # -- Execute "apio system"
        result = sb.invoke_apio_cmd(apio_system)
        assert result.exit_code == 1, result.output
        assert (
            "specify one of --lsftdi, --lsusb, --lsserial, --info, "
            "or --platforms" in result.output
        )

        # -- Execute "apio system --lsftdi"
        result = sb.invoke_apio_cmd(apio_system, ["--lsftdi"])
        assert result.exit_code == 1, result.output
        assert "apio packages --install --force oss-cad-suite" in result.output

        # -- Execute "apio system --lsusb"
        result = sb.invoke_apio_cmd(apio_system, ["--lsusb"])
        assert result.exit_code == 1, result.output
        assert "apio packages --install --force oss-cad-suite" in result.output

        # -- Execute "apio system --lsserial"
        sb.invoke_apio_cmd(apio_system, ["--lsserial"])
        assert result.exit_code == 1, result.output
        assert "apio packages --install --force oss-cad-suite" in result.output

        # -- Execute "apio system --info"
        result = sb.invoke_apio_cmd(apio_system, ["--info"])
        assert result.exit_code == 0, result.output
        assert "Platform id" in result.output
        # -- The these env options are set by the apio text fixture.
        assert (
            "Active env options [APIO_HOME_DIR, APIO_PACKAGES_DIR]"
            in result.output
        )
