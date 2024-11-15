"""
  Test for the "apio examples" command
"""

# -- apio examples entry point
from apio.commands.examples import cli as cmd_examples


def test_examples(clirunner, configenv):
    """Test "apio examples" with different parameters"""

    with clirunner.isolated_filesystem():

        # -- Config the environment (conftest.configenv())
        configenv()

        # -- Execute "apio examples"
        result = clirunner.invoke(cmd_examples)
        assert result.exit_code == 1, result.output
        assert (
            "One of [--list, --fetch-dir, --fetch-files] "
            "must be specified" in result.output
        )

        # -- Execute "apio examples --list"
        result = clirunner.invoke(cmd_examples, ["--list"])
        assert result.exit_code == 1, result.output
        assert "apio packages --install --force examples" in result.output

        # -- Execute "apio examples --dir dir"
        result = clirunner.invoke(cmd_examples, ["--fetch-dir", "dir"])
        assert result.exit_code == 1, result.output
        assert "apio packages --install --force examples" in result.output

        # -- Execute "apio examples --files file"
        result = clirunner.invoke(cmd_examples, ["--fetch-files", "file"])
        assert result.exit_code == 1, result.output
        assert "apio packages --install --force examples" in result.output
