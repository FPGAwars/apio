"""DOC: TODO"""
# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2019 FPGAwars
# -- Author Jesús Arroyo
# -- Licence GPLv2

import sys
import click
import requests


from apio import util

requests.packages.urllib3.disable_warnings()


def api_request(command, organization="FPGAwars"):
    """DOC:TODO"""

    result = None
    req = None
    try:
        req = requests.get(
            "https://api.github.com/repos/{0}/{1}".format(
                organization, command
            ),
            headers=_get_headers(),
        )

        result = req.json()
        req.raise_for_status()
    except requests.exceptions.ConnectionError as exc:
        error_message = str(exc)
        if "NewConnectionError" in error_message:
            click.secho(
                "Error: could not connect to GitHub API.\n"
                "Check your internet connection and try again",
                fg="red",
            )
        else:
            click.secho(error_message, fg="red")
        sys.exit(1)
    except Exception as exc:
        click.secho("Error: " + str(exc), fg="red")
        sys.exit(1)
    finally:
        if req:
            req.close()
    if result is None:
        click.secho("Error: wrong data from GitHub API", fg="red")
        sys.exit(1)
    return result


def _get_headers():
    enc = (
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJwdWJsaWNfdG9rZW4iOiJ0"
        + "b2tlbiBhNTk2OTUwNjFhYzRkMjBkZjEwNTFlZDljOWZjNGI4M2Q0NzAyYzA3I"
        + "n0.POR6Iae_pSt0m6h-AaRi1X6QaRcnnfl9aZbTSV0BUJw"
    )
    return {"Authorization": util.decode(enc).get("public_token")}
