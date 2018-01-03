# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2018 FPGAwars
# -- Author Jesús Arroyo
# -- Licence GPLv2

import click
import requests

from apio import util

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
    if result is None:
        click.secho('Error: wrong data from GitHub API', fg='red')
        exit(1)
    return result


def _get_headers():
    enc = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJwdWJsaWNfdG9rZW4iOiJ0' + \
          'b2tlbiBhNTk2OTUwNjFhYzRkMjBkZjEwNTFlZDljOWZjNGI4M2Q0NzAyYzA3I' + \
          'n0.POR6Iae_pSt0m6h-AaRi1X6QaRcnnfl9aZbTSV0BUJw'
    return {'Authorization': util.decode(enc).get('public_token')}
