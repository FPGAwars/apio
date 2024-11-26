"""
  Test for the "apio examples" command
"""

from test.conftest import ApioRunner

# -- apio examples entry point
from apio.commands.examples import cli as apio_examples


def test_examples(apio_runner: ApioRunner):
    """Test "apio examples" with different parameters"""

    with apio_runner.in_disposable_temp_dir():

        # -- Config the apio test environment
        apio_runner.setup_env()

        # -- Execute "apio examples"
        result = apio_runner.invoke(apio_examples)
        assert result.exit_code == 1, result.output
        assert (
            "Error: Specify one of [--list, --fetch-dir, --fetch-files]"
            in result.output
        )

        # -- Execute "apio examples --list"
        result = apio_runner.invoke(apio_examples, ["--list"])
        assert result.exit_code == 1, result.output
        assert "Error: package 'examples' is not installed" in result.output
        assert "apio packages --install --force examples" in result.output

        # -- Execute "apio examples --fetch-dir dir"
        result = apio_runner.invoke(apio_examples, ["--fetch-dir", "dir"])
        assert result.exit_code == 1, result.output
        assert "Error: package 'examples' is not installed" in result.output
        assert "apio packages --install --force examples" in result.output

        # -- Execute "apio examples --files file"
        result = apio_runner.invoke(apio_examples, ["--fetch-files", "file"])
        assert result.exit_code == 1, result.output
        assert "Error: package 'examples' is not installed" in result.output
        assert "apio packages --install --force examples" in result.output
