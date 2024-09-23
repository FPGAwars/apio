"""
  Test for the "apio modify" command
"""

from pathlib import Path
from os.path import isfile, exists
from configobj import ConfigObj
from typing import Dict

# -- apio modify entry point
from apio.commands.modify import cli as cmd_modify


def check_ini_file(apio_ini: Path, expected_vars: Dict[str, str]) -> None:
    # Read the ini file.
    assert isfile(apio_ini)
    conf = ConfigObj(str(apio_ini))
    # Check the expected comment at the top.
    assert "# My initial comment." in conf.initial_comment[0]
    # Check the expected vars.
    assert conf.dict() == {"env": expected_vars}


def test_modify(clirunner, configenv, validate_cliresult):
    """Test "apio modify" with different parameters"""

    with clirunner.isolated_filesystem():

        # -- Config the environment (conftest.configenv())
        configenv()

        apio_ini = Path("apio.ini")
        assert not exists(apio_ini)

        # -- Execute "apio modify --top-module my_module"
        result = clirunner.invoke(cmd_modify, ["--top-module", "my_module"])
        print(f"{result.output = }")
        assert result.exit_code != 0
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
        result = clirunner.invoke(cmd_modify, ["--board", "missed_board"])
        assert result.exit_code == 1
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
        result = clirunner.invoke(cmd_modify, ["--board", "alhambra-ii"])
        validate_cliresult(result)
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
        result = clirunner.invoke(cmd_modify, ["--top-module", "my_main"])
        validate_cliresult(result)
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
        result = clirunner.invoke(
            cmd_modify, ["--board", "icezum", "--top-module", "my_top"]
        )
        validate_cliresult(result)
        assert "was modified successfully." in result.output
        check_ini_file(
            apio_ini,
            {"board": "icezum", "top-module": "my_top", "extra_var": "dummy"},
        )
