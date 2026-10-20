# This file is part of the Apio project
# (C) 2016-present FPGAwars
# Project authors:
#   * Jesús Arroyo (Jesus89) (2016-2019)
#   * Juan Gonzalez (obijuan) (2019-2024)
#   * The Apio Team (2024-present)
# License: GPLv2

"""Test for the "apio test" command."""

from tests.conftest import ApioRunner
from apio.commands.apio import apio_top_cli as apio


def test_test(apio_runner: ApioRunner):
    """Test: apio test
    when no apio.ini file is given
    No additional parameters are given
    """

    with apio_runner.in_sandbox() as sb:

        # -- Execute "apio test"
        result = sb.invoke_apio_cmd(apio, ["test"])
        assert result.exit_code != 0, result.output
        assert "Error: Missing project file apio.ini" in result.output


def test_with_env_arg_error(apio_runner: ApioRunner):
    """Tests the command with an invalid --env value. This error message
    confirms that the --env arg was propagated to the apio.ini loading
    logic."""

    with apio_runner.in_sandbox() as sb:

        # -- Run "apio test --env no-such-env"
        sb.write_apio_ini({"[env:default]": {"top-module": "main"}})
        result = sb.invoke_apio_cmd(apio, ["test", "--env", "no-such-env"])
        assert result.exit_code == 1, result.output
        assert (
            "Error: Env 'no-such-env' not found in apio.ini" in result.output
        )
