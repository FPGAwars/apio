# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- License GPLv2
"""Implementation of 'apio upgrade' command"""

import sys
import click
import requests
from packaging import version
from apio.utils import util, cmd_util
from apio.common.apio_console import cout, cerror
from apio.common.apio_styles import INFO, WARNING, EMPH1, EMPH3, SUCCESS


def get_pypi_latest_version() -> str:
    """Get the latest stable version of apio from Pypi
    Internet connection is required
    Returns: A string with the version (Ex: "0.9.0")
    Exits on an error.
    """

    # -- Create http request headers.
    # -- Added May 2025 when we started to get the following error:
    # -- "406 Client Error: go-http-client redirect ..."
    headers = {"User-Agent": "python-requests/2.31.0"}

    # -- Read the latest apio version from pypi
    # -- More information: https://warehouse.pypa.io/api-reference/json.html
    try:
        req = requests.get(
            "https://pypi.python.org/pypi/apio/json",
            headers=headers,
            timeout=10,
        )
        req.raise_for_status()

    # -- Connection error
    except requests.exceptions.ConnectionError as e:
        cout(str(e), style=WARNING)
        cerror("Connection error while accessing Pypi.")
        sys.exit(1)

    # -- HTTP Error
    except requests.exceptions.HTTPError as e:
        cout(str(e), style=WARNING)
        cerror("HTTP error while accessing Pypi.")
        sys.exit(1)

    # -- Timeout!
    except requests.exceptions.Timeout as e:
        cout(str(e), style=WARNING)
        cerror("HTTP timeout while accessing Pypi.")
        sys.exit(1)

    # -- Another error
    except requests.exceptions.RequestException as e:
        cout(str(e), style=WARNING)
        cerror("HTTP exception while accessing Pypi.")
        sys.exit(1)

    # -- Get the version field from the json response
    ver = req.json()["info"]["version"]

    return ver


# ---------- apio upgrade

# -- Text in the rich-text format of the python rich library.
APIO_UPGRADE_HELP = """
The command 'apio upgrade' checks for the version of the latest Apio release \
and provides upgrade directions if necessary.

Examples:[code]
  apio upgrade[/code]
"""


@click.command(
    name="upgrade",
    cls=cmd_util.ApioCommand,
    short_help="Check the latest Apio version.",
    help=APIO_UPGRADE_HELP,
)
@click.pass_context
def cli(_: click.Context):
    """Check the latest Apio version."""

    # -- Get the current apio version from the python package installed
    # -- on the system
    current_version = util.get_apio_version_str()

    # -- Get the latest stable version published at Pypi
    latest_version = get_pypi_latest_version()

    # -- There was an error getting the version from pypi
    if latest_version is None:
        sys.exit(1)

    # -- Print information about apio.
    cout(
        f"Local Apio version: {current_version}",
        f"Latest Apio stable version (Pypi): {latest_version}",
        style=EMPH1,
    )

    # -- Case 1: Using an old version.
    if version.parse(current_version) < version.parse(latest_version):
        cout(
            "You're not up to date.",
            "Please execute 'pip install -U apio' to upgrade.",
            style=INFO,
        )
        return

    # -- Case 2: Using a dev version.
    if version.parse(current_version) > version.parse(latest_version):
        cout(
            "You are using a development version. Enjoy it at your own risk.",
            style=EMPH3,
        )
        return

    # -- Case 3: Using the latest version.
    cout(
        f"You're up-to-date!\nApio {latest_version} is currently the "
        "latest stable version available.",
        style=SUCCESS,
    )
