# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- Licence GPLv2
"""Implementation of 'apio upgrade' command"""

import sys
import click
import requests
from packaging import version
from apio.utils import util
from apio.common.apio_console import cout, cerror


def get_pypi_latest_version() -> str:
    """Get the latest stable version of apio from Pypi
    Internet connection is required
    Returns: A string with the version (Ex: "0.9.0")
    Exits on an error.
    """

    # -- Read the latest apio version from pypi
    # -- More information: https://warehouse.pypa.io/api-reference/json.html
    try:
        req = requests.get(
            "https://pypi.python.org/pypi/apio/json", timeout=10
        )
        req.raise_for_status()

    # -- Connection error
    except requests.exceptions.ConnectionError as e:
        cout(str(e), style="yellow")
        cerror("Connection error while accessing Pypi.")
        sys.exit(1)

    # -- HTTP Error
    except requests.exceptions.HTTPError as e:
        cout(str(e), style="yellow")
        cerror("HTTP error while accessing Pypi.")
        sys.exit(1)

    # -- Timeout!
    except requests.exceptions.Timeout as e:
        cout(str(e), style="yellow")
        cerror("HTTP timeout while accessing Pypi.")
        sys.exit(1)

    # -- Another error
    except requests.exceptions.RequestException as e:
        cout(str(e), style="yellow")
        cerror("HTTP exception while accessing Pypi.")
        sys.exit(1)

    # -- Get the version field from the json response
    ver = req.json()["info"]["version"]

    return ver


# ---------------------------
# -- COMMAND
# ---------------------------
APIO_UPGRADE_HELP = """
The command ‘apio upgrade’ checks for the version of the latest Apio release
and provides upgrade directions if necessary.

\b
Examples:
  apio upgrade
"""


@click.command(
    name="upgrade",
    short_help="Check the latest Apio version.",
    help=APIO_UPGRADE_HELP,
)
@click.pass_context
def cli(_: click.Context):
    """Check the latest Apio version."""

    # -- Get the current apio version from the python package installed
    # -- on the system
    current_version = util.get_apio_version()

    # -- Get the latest stable version published at Pypi
    latest_version = get_pypi_latest_version()

    # -- There was an error getting the version from pypi
    if latest_version is None:
        sys.exit(1)

    # -- Print information about apio.
    cout(
        f"Local Apio version: {current_version}",
        f"Lastest Apio stable version (Pypi): {latest_version}",
        style="cyan",
    )

    # -- Case 1: Using an old version.
    if version.parse(current_version) < version.parse(latest_version):
        cout(
            "You're not updated\nPlease execute "
            "`pip install -U apio` to upgrade.",
            style="yellow",
        )
        return

    # -- Case 2: Using a dev version.
    if version.parse(current_version) > version.parse(latest_version):
        cout(
            "You are using a development version. Enjoy it at your own risk.",
            style="magenta",
        )
        return

    # -- Case 3: Using the latest version.
    cout(
        f"You're up-to-date!\nApio {latest_version} is currently the "
        "latest stable version available.",
        style="green",
    )
