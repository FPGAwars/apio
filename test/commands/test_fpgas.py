"""
  Test for the "apio boards" command
"""

from test.conftest import ApioRunner

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


def test_fpgas_ok(apio_runner: ApioRunner):
    """Test "apio fpgas" command with standard fpgas.json."""

    with apio_runner.in_disposable_temp_dir():

        # -- Config the apio test environment
        apio_runner.setup_env()

        # -- Execute "apio fpgas"
        result = apio_runner.invoke(apio_fpgas)
        apio_runner.assert_ok(result)
        # -- Note: pytest sees the piped version of the command's output.
        # -- Run 'apio fpgas' | cat' to reproduce it.
        assert "Loading custom 'fpgas.json'" not in result.output
        assert "iCE40-HX4K-TQ144" in result.output
        assert "my_custom_fpga" not in result.output


def test_custom_fpga(apio_runner: ApioRunner):
    """Test "apio fpgas" command with a custom fpgas.json."""

    with apio_runner.in_disposable_temp_dir():

        # -- Config the apio test environment
        apio_runner.setup_env()

        # -- Write a custom boards.json file in the project's directory.
        with open("fpgas.json", "w", encoding="utf-8") as f:
            f.write(CUSTOM_FPGAS)

        # -- Execute "apio boards"
        result = apio_runner.invoke(apio_fpgas)
        apio_runner.assert_ok(result)
        # -- Note: pytest sees the piped version of the command's output.
        # -- Run 'apio build' | cat' to reproduce it.
        assert "Loading custom 'fpgas.json'" in result.output
        assert "iCE40-HX4K-TQ144" not in result.output
        assert "my_custom_fpga" in result.output
        assert "Total of 1 fpga" in result.output
