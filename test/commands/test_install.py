"""
  Test for the "apio install" command
"""

from test.conftest import ApioRunner

# -- apio install entry point
from apio.commands.install import cli as apio_install


def test_install(apio_runner: ApioRunner):
    """Test "apio install" with different parameters"""

    with apio_runner.in_disposable_temp_dir():

        # -- Config the apio test environment
        apio_runner.setup_env()

        # -- Execute "apio install"
        result = apio_runner.invoke(apio_install)
        apio_runner.assert_ok(result)

        # -- Execute "apio install --list"
        result = apio_runner.invoke(apio_install, ["--list"])
        apio_runner.assert_ok(result)

        # -- Execute "apio install missing_package"
        result = apio_runner.invoke(apio_install, ["missing_package"])
        assert result.exit_code == 1, result.output
        assert "Error: no such package" in result.output
