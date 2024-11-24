"""
  Test for the "apio boards" command
"""

# -- apio fpgas entry point
from apio.commands.fpgas import cli as apio_fpgas

CUSTOM_FPGAS = """
{
  "my_custom_fpga": {
    "arch": "ice40",
    "type": "lp",
    "size": "1k",
    "pack": "swg16tr"
  }
}
"""


def test_fpgas_ok(click_cmd_runner, setup_apio_test_env, assert_apio_cmd_ok):
    """Test "apio fpgas" command with standard fpgas.json."""

    with click_cmd_runner.isolated_filesystem():

        # -- Config the apio test environment
        setup_apio_test_env()

        # -- Execute "apio fpgas"
        result = click_cmd_runner.invoke(apio_fpgas)
        assert_apio_cmd_ok(result)
        # -- Note: pytest sees the piped version of the command's output.
        # -- Run 'apio fpgas' | cat' to reproduce it.
        assert "Loading custom 'fpgas.json'" not in result.output
        assert "iCE40-HX4K-TQ144" in result.output
        assert "my_custom_fpga" not in result.output


def test_custom_fpga(
    click_cmd_runner, setup_apio_test_env, assert_apio_cmd_ok
):
    """Test "apio fpgas" command with a custom fpgas.json."""

    with click_cmd_runner.isolated_filesystem():

        # -- Config the apio test environment
        setup_apio_test_env()

        # -- Write a custom boards.json file in the project's directory.
        with open("fpgas.json", "w", encoding="utf-8") as f:
            f.write(CUSTOM_FPGAS)

        # -- Execute "apio boards"
        result = click_cmd_runner.invoke(apio_fpgas)
        assert_apio_cmd_ok(result)
        # -- Note: pytest sees the piped version of the command's output.
        # -- Run 'apio build' | cat' to reproduce it.
        assert "Loading custom 'fpgas.json'" in result.output
        assert "iCE40-HX4K-TQ144" not in result.output
        assert "my_custom_fpga" in result.output
        assert "Total of 1 fpga" in result.output
