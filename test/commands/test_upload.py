"""
  Test for the "apio upload" command
"""

# -- apio time entry point
from apio.commands.upload import cli as cmd_upload


def test_upload(click_cmd_runner, setup_apio_test_env):
    """Test: apio upload
    when no apio.ini file is given
    No additional parameters are given
    """

    with click_cmd_runner.isolated_filesystem():

        # -- Config the apio test environment
        setup_apio_test_env()

        # -- Execute "apio upload"
        result = click_cmd_runner.invoke(cmd_upload)

        # -- Check the result
        assert result.exit_code == 1, result.output
        assert "Info: Project has no apio.ini file" in result.output
        assert "Error: insufficient arguments: missing board" in result.output


def test_upload_board(click_cmd_runner, setup_apio_test_env):
    """Test: apio upload --board icezum
    No oss-cad-suite package is installed
    """

    with click_cmd_runner.isolated_filesystem():

        # -- Config the apio test environment
        setup_apio_test_env()

        # -- Execute "apio upload --board icezum"
        result = click_cmd_runner.invoke(cmd_upload, ["--board", "icezum"])

        # -- Check the result
        assert result.exit_code == 1
        assert (
            "Error: package 'oss-cad-suite' is not installed" in result.output
        )


def test_upload_complete(click_cmd_runner, setup_apio_test_env):
    """Test: apio upload with different arguments
    No apio.ini file is given
    """

    with click_cmd_runner.isolated_filesystem():

        # -- Config the apio test environment
        setup_apio_test_env()

        # -- Execute "apio upload --serial-port COM0"
        result = click_cmd_runner.invoke(cmd_upload, ["--serial-port", "COM0"])
        assert result.exit_code == 1, result.output
        assert "Info: Project has no apio.ini file" in result.output
        assert "Error: insufficient arguments: missing board" in result.output

        # -- Execute "apio upload --ftdi-id 0"
        result = click_cmd_runner.invoke(cmd_upload, ["--ftdi-id", "0"])
        assert result.exit_code == 1, result.output
        assert "Info: Project has no apio.ini file" in result.output
        assert "Error: insufficient arguments: missing board" in result.output

        # -- Execute "apio upload --sram"
        result = click_cmd_runner.invoke(cmd_upload, ["--sram"])
        assert result.exit_code == 1, result.output
        assert "Info: Project has no apio.ini file" in result.output
        assert "Error: insufficient arguments: missing board" in result.output

        # -- Execute "apio upload --board icezum --serial-port COM0"
        result = click_cmd_runner.invoke(
            cmd_upload, ["--board", "icezum", "--serial-port", "COM0"]
        )
        assert result.exit_code == 1, result.output
        assert (
            "Error: package 'oss-cad-suite' is not installed" in result.output
        )

        # -- Execute "apio upload --board icezum --ftdi-id 0"
        result = click_cmd_runner.invoke(
            cmd_upload, ["--board", "icezum", "--ftdi-id", "0"]
        )
        assert result.exit_code == 1, result.output
        assert (
            "Error: package 'oss-cad-suite' is not installed" in result.output
        )

        # -- Execute "apio upload --board icezum --sram"
        result = click_cmd_runner.invoke(
            cmd_upload, ["--board", "icezum", "--sram"]
        )
        assert result.exit_code == 1, result.output
        assert (
            "Error: package 'oss-cad-suite' is not installed" in result.output
        )
