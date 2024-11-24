"""
  Test for the "apio lint" command
"""

# -- apio lint entry point
from apio.commands.lint import cli as apio_lint


def test_lint_no_packages(
    click_cmd_runner, setup_apio_test_env, write_apio_ini
):
    """Test: apio lint with missing packages."""

    with click_cmd_runner.isolated_filesystem():

        # -- Config the apio test environment
        setup_apio_test_env()

        # -- Create apio.ini file.
        write_apio_ini({"board": "icezum", "top-module": "main"})

        # -- Execute "apio lint"
        result = click_cmd_runner.invoke(apio_lint)
        assert result.exit_code == 1, result.output
        assert (
            "Error: package 'oss-cad-suite' is not installed" in result.output
        )
        assert "apio packages --install --force oss-cad-suite" in result.output
