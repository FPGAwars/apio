"""Test for the "apio create" command."""

from pathlib import Path
from os.path import isfile, exists
from typing import Dict
from test.conftest import ApioRunner
from configobj import ConfigObj
from apio.commands.apio import apio_top_cli as apio


def _check_ini_file(apio_ini: Path, expected_vars: Dict[str, str]) -> None:
    """Assert that apio.ini contains exactly the given vars."""
    # Read the ini file.
    assert isfile(apio_ini)
    conf = ConfigObj(str(apio_ini))
    # Check the expected comment at the top.
    assert "# APIO project configuration file" in conf.initial_comment[0]
    # Check the expected vars.
    assert conf.dict() == {"env:default": expected_vars}


def test_create(apio_runner: ApioRunner):
    """Test "apio create" with different parameters"""

    with apio_runner.in_sandbox() as sb:

        apio_ini = Path("apio.ini")
        assert not exists(apio_ini)

        # -- Execute "apio create"
        result = sb.invoke_apio_cmd(apio, ["create"])
        assert result.exit_code != 0, result.output
        assert "Error: Missing option" in result.output
        assert not exists(apio_ini)

        # -- Execute "apio create --board no-such-board"
        result = sb.invoke_apio_cmd(
            apio, ["create", "--board", "no-such-board"]
        )
        assert result.exit_code == 1, result.output
        assert "Error: Unknown board id 'no-such-board'" in result.output
        assert not exists(apio_ini)

        # -- Execute "apio create --board alhambra-ii"
        result = sb.invoke_apio_cmd(apio, ["create", "--board", "alhambra-ii"])
        sb.assert_result_ok(result)
        assert "was created successfully." in result.output
        _check_ini_file(
            apio_ini, {"board": "alhambra-ii", "top-module": "main"}
        )

        # -- Execute "apio create --board alhambra-ii
        # --                      --top-module my_module" with 'y' input"
        result = sb.invoke_apio_cmd(
            apio,
            [
                "create",
                "--board",
                "alhambra-ii",
                "--top-module",
                "my_module",
            ],
        )
        assert result.exit_code != 0
        assert "Error: The file apio.ini already exists." in result.output
        _check_ini_file(
            apio_ini, {"board": "alhambra-ii", "top-module": "main"}
        )

        # -- Execute "apio create --board alhambra-ii -p aa/bb"
        result = sb.invoke_apio_cmd(
            apio, ["create", "--board", "alhambra-ii", "-p", "aa/bb"]
        )
        sb.assert_result_ok(result)
        assert "was created successfully." in result.output
        _check_ini_file(
            Path("aa/bb") / apio_ini,
            {"board": "alhambra-ii", "top-module": "main"},
        )
