"""A pseudo test that runs first and fill in the packages cache if needed.
It is not required but provide a better indication to the user if the
package loading pauses the tests for a few seconds.
"""

from test.conftest import ApioRunner
from apio.commands.apio import apio_top_cli as apio


def test_fill_packages_cache(apio_runner: ApioRunner):
    """Fill the packages cache."""

    with apio_runner.in_sandbox() as sb:

        # -- Execute "apio packages"
        result = sb.invoke_apio_cmd(apio, ["packages", "update"])
        sb.assert_result_ok(result)
