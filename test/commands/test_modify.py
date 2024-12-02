"""
  Test for the "apio modify" command
"""

from pathlib import Path
from os.path import isfile, exists
from typing import Dict
from test.conftest import ApioRunner
from configobj import ConfigObj


# -- apio modify entry point
from apio.commands.modify import cli as apio_modify


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


def test_modify(apio_runner: ApioRunner):
    """Test "apio modify" with different parameters"""

    with apio_runner.in_sandbox() as sb:

        apio_ini = Path("apio.ini")
        assert not exists(apio_ini)

        # -- Execute "apio modify --top-module my_module"
        result = sb.invoke_apio_cmd(apio_modify, ["--top-module", "my_module"])
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
        result = sb.invoke_apio_cmd(apio_modify, ["--board", "missed_board"])
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
        result = sb.invoke_apio_cmd(apio_modify, ["--board", "alhambra-ii"])
        sb.assert_ok(result)
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
        result = sb.invoke_apio_cmd(apio_modify, ["--top-module", "my_main"])
        sb.assert_ok(result)
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
        result = sb.invoke_apio_cmd(
            apio_modify, ["--board", "icezum", "--top-module", "my_top"]
        )
        sb.assert_ok(result)
        assert "was modified successfully." in result.output
        check_ini_file(
            apio_ini,
            {"board": "icezum", "top-module": "my_top", "extra_var": "dummy"},
        )
