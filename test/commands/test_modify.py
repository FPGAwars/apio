"""
  Test for the "apio modify" command
"""

from pathlib import Path
from os.path import isfile, exists
from typing import Dict
from configobj import ConfigObj

# -- apio modify entry point
from apio.commands.modify import cli as cmd_modify


# R0801: Similar lines in 2 files
# pylint: disable=R0801
def check_ini_file(apio_ini: Path, expected_vars: Dict[str, str]) -> None:
    """Assert that apio.ini contains exactly the given vars."""
    # Read the ini file.
    assert isfile(apio_ini)
    conf = ConfigObj(str(apio_ini))
    # Check the expected comment at the top.
    assert "# My initial comment." in conf.initial_comment[0]
    # Check the expected vars.
    assert conf.dict() == {"env": expected_vars}


def test_modify(click_cmd_runner, setup_apio_test_env, assert_apio_cmd_ok):
    """Test "apio modify" with different parameters"""

    with click_cmd_runner.isolated_filesystem():

        # -- Config the environment (conftest.configenv())
        setup_apio_test_env()

        apio_ini = Path("apio.ini")
        assert not exists(apio_ini)

        # -- Execute "apio modify --top-module my_module"
        result = click_cmd_runner.invoke(
            cmd_modify, ["--top-module", "my_module"]
        )
        assert result.exit_code != 0, result.output
        assert "Error: 'apio.ini' not found" in result.output
        assert not exists(apio_ini)

        # -- Create initial apio.ini file.
        conf = ConfigObj(str(apio_ini))
        conf.initial_comment = ["# My initial comment.", ""]
        conf["env"] = {
            "board": "icezum",
            "top-module": "my_module",
            "extra_var": "dummy",
        }
        conf.write()
        check_ini_file(
            apio_ini,
            {
                "board": "icezum",
                "top-module": "my_module",
                "extra_var": "dummy",
            },
        )

        # -- Execute "apio modify --board missed_board"
        result = click_cmd_runner.invoke(
            cmd_modify, ["--board", "missed_board"]
        )
        assert result.exit_code == 1, result.output
        assert "Error: no such board" in result.output
        check_ini_file(
            apio_ini,
            {
                "board": "icezum",
                "top-module": "my_module",
                "extra_var": "dummy",
            },
        )

        # -- Execute "apio modify --board alhambra-ii"
        result = click_cmd_runner.invoke(
            cmd_modify, ["--board", "alhambra-ii"]
        )
        assert_apio_cmd_ok(result)
        assert "was modified successfully." in result.output
        check_ini_file(
            apio_ini,
            {
                "board": "alhambra-ii",
                "top-module": "my_module",
                "extra_var": "dummy",
            },
        )

        # -- Execute "apio modify --top-module my_main"
        result = click_cmd_runner.invoke(
            cmd_modify, ["--top-module", "my_main"]
        )
        assert_apio_cmd_ok(result)
        assert "was modified successfully." in result.output
        check_ini_file(
            apio_ini,
            {
                "board": "alhambra-ii",
                "top-module": "my_main",
                "extra_var": "dummy",
            },
        )

        # -- Execute "apio modify --board icezum --top-module my_top"
        result = click_cmd_runner.invoke(
            cmd_modify, ["--board", "icezum", "--top-module", "my_top"]
        )
        assert_apio_cmd_ok(result)
        assert "was modified successfully." in result.output
        check_ini_file(
            apio_ini,
            {"board": "icezum", "top-module": "my_top", "extra_var": "dummy"},
        )
