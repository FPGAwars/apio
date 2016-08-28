# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016 FPGAwars
# -- Author Jesús Arroyo
# -- Licence GPLv2

import click
import requests
requests.packages.urllib3.disable_warnings()

ERROR_MESSAGE = """Error: Could not connect to GitHub API.
Check your internet connection and try again"""


def api_request(command, organization='FPGAwars'):
    result = None
    r = None
    try:
        r = requests.get(
            'https://api.github.com/repos/{0}/{1}'.format(
                organization, command),
            headers=_get_headers())
        result = r.json()
        r.raise_for_status()
    except requests.exceptions.ConnectionError:
        click.secho(ERROR_MESSAGE, fg='red')
        exit(1)
    except Exception as e:
        click.secho('Error: ' + str(e), fg='red')
        exit(1)
    finally:
        if r:
            r.close()
    return result


def _get_headers():
    return {'Authorization': 'token 35637034c3d4cb3d4b84ac09eee5c4b0aac2c661'}
