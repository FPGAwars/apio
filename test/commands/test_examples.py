"""
  Test for the "apio examples" command
"""

# -- apio examples entry point
from apio.commands.examples import cli as apio_examples


def test_examples(click_cmd_runner, setup_apio_test_env):
    """Test "apio examples" with different parameters"""

    with click_cmd_runner.isolated_filesystem():

        # -- Config the apio test environment
        setup_apio_test_env()

        # -- Execute "apio examples"
        result = click_cmd_runner.invoke(apio_examples)
        assert result.exit_code == 1, result.output
        assert (
            "Error: Specify one of [--list, --fetch-dir, --fetch-files]"
            in result.output
        )

        # -- Execute "apio examples --list"
        result = click_cmd_runner.invoke(apio_examples, ["--list"])
        assert result.exit_code == 1, result.output
        assert "Error: package 'examples' is not installed" in result.output
        assert "apio packages --install --force examples" in result.output

        # -- Execute "apio examples --fetch-dir dir"
        result = click_cmd_runner.invoke(apio_examples, ["--fetch-dir", "dir"])
        assert result.exit_code == 1, result.output
        assert "Error: package 'examples' is not installed" in result.output
        assert "apio packages --install --force examples" in result.output

        # -- Execute "apio examples --files file"
        result = click_cmd_runner.invoke(
            apio_examples, ["--fetch-files", "file"]
        )
        assert result.exit_code == 1, result.output
        assert "Error: package 'examples' is not installed" in result.output
        assert "apio packages --install --force examples" in result.output
