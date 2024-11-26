"""
  Test for the "apio system" command
"""

from test.conftest import ApioRunner

# -- apio system entry point
from apio.commands.system import cli as apio_system


def test_system(apio_runner: ApioRunner):
    """Test "apio system" with different parameters"""

    with apio_runner.in_disposable_temp_dir():

        # -- Config the apio test environment
        apio_runner.setup_env()

        # -- Execute "apio system"
        result = apio_runner.invoke(apio_system)
        assert result.exit_code == 1, result.output
        assert (
            "Specify one of "
            "[--lsftdi, --lsusb, --lsserial, --info, --platforms]"
            in result.output
        )

        # -- Execute "apio system --lsftdi"
        result = apio_runner.invoke(apio_system, ["--lsftdi"])
        assert result.exit_code == 1, result.output
        assert "apio packages --install --force oss-cad-suite" in result.output

        # -- Execute "apio system --lsusb"
        result = apio_runner.invoke(apio_system, ["--lsusb"])
        assert result.exit_code == 1, result.output
        assert "apio packages --install --force oss-cad-suite" in result.output

        # -- Execute "apio system --lsserial"
        apio_runner.invoke(apio_system, ["--lsserial"])
        assert result.exit_code == 1, result.output
        assert "apio packages --install --force oss-cad-suite" in result.output

        # -- Execute "apio system --info"
        result = apio_runner.invoke(apio_system, ["--info"])
        assert result.exit_code == 0, result.output
        assert "Platform id" in result.output
        # -- The these env options are set by the apio text fixture.
        assert (
            "Active env options [APIO_HOME_DIR, APIO_PACKAGES_DIR]"
            in result.output
        )
