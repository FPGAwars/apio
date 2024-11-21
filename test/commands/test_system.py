"""
  Test for the "apio system" command
"""

# -- apio system entry point
from apio.commands.system import cli as cmd_system


def test_system(click_cmd_runner, setup_apio_test_env):
    """Test "apio system" with different parameters"""

    with click_cmd_runner.isolated_filesystem():

        # -- Config the environment (conftest.configenv())
        setup_apio_test_env()

        # -- Execute "apio system"
        result = click_cmd_runner.invoke(cmd_system)
        assert result.exit_code == 1, result.output
        assert (
            "One of [--lsftdi, --lsusb, --lsserial, --info, --platforms] "
            "must be specified" in result.output
        )

        # -- Execute "apio system --lsftdi"
        result = click_cmd_runner.invoke(cmd_system, ["--lsftdi"])
        assert result.exit_code == 1, result.output
        assert "apio packages --install --force oss-cad-suite" in result.output

        # -- Execute "apio system --lsusb"
        result = click_cmd_runner.invoke(cmd_system, ["--lsusb"])
        assert result.exit_code == 1, result.output
        assert "apio packages --install --force oss-cad-suite" in result.output

        # -- Execute "apio system --lsserial"
        click_cmd_runner.invoke(cmd_system, ["--lsserial"])
        assert result.exit_code == 1, result.output
        assert "apio packages --install --force oss-cad-suite" in result.output

        # -- Execute "apio system --info"
        result = click_cmd_runner.invoke(cmd_system, ["--info"])
        assert result.exit_code == 0, result.output
        assert "Platform id" in result.output
        # -- The these env options are set by the apio text fixture.
        assert (
            "Active env options [APIO_HOME_DIR, APIO_PACKAGES_DIR]"
            in result.output
        )
