"""DOC: TODO"""
# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2019 FPGAwars
# -- Author Jesús Arroyo
# -- Licence GPLv2

import sys
import click
import requests

requests.packages.urllib3.disable_warnings()


def api_request(command, organization="FPGAwars"):
    """Perform a request of data to Github, through its API"""

    result = None
    req = None

    # -- Create the URL for accesing the github API
    cmd_url = f"https://api.github.com/repos/{organization}/{command}"

    # -- Do the request!
    try:
        req = requests.get(cmd_url)
        result = req.json()
        req.raise_for_status()

    # -- There is a connection problem
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

    # -- There is another error
    except Exception as exc:
        click.secho("Error: " + str(exc), fg="red")
        sys.exit(1)

    # -- In any case, close the request
    finally:
        if req:
            req.close()

    # -- Return the response object from github
    if result is None:
        click.secho("Error: wrong data from GitHub API", fg="red")
        sys.exit(1)

    return result
