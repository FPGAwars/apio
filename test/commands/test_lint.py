"""
  Test for the "apio lint" command
"""

from test.conftest import ApioRunner

# -- apio lint entry point
from apio.commands.lint import cli as apio_lint


def test_lint_no_packages(apio_runner: ApioRunner):
    """Test: apio lint with missing packages."""

    with apio_runner.in_disposable_temp_dir():

        # -- Config the apio test environment
        apio_runner.setup_env()

        # -- Create apio.ini file.
        apio_runner.write_apio_ini({"board": "icezum", "top-module": "main"})

        # -- Execute "apio lint"
        result = apio_runner.invoke(apio_lint)
        assert result.exit_code == 1, result.output
        assert (
            "Error: package 'oss-cad-suite' is not installed" in result.output
        )
        assert "apio packages --install --force oss-cad-suite" in result.output
