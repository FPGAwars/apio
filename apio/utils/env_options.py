# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2018 FPGAwars
# -- Author Jesús Arroyo
# -- License GPLv2
# -- Derived from:
# ---- Platformio project
# ---- (C) 2014-2016 Ivan Kravets <me@ikravets.com>
# ---- License Apache v2
"""Functions for reading the APIO env options. This are system env
variables that are used to modify the default behavior of APIO.
"""

import os
from typing import List

# -- Env variable to override the apio home dir ~/.apio. If specified,
# -- it contains the profile.json file and if APIO_PACKAGES is not
# -- specified, the 'packages' directory with the individual packages.
# -- This env variable is used in testing to have an isolated home for each
# -- test.
APIO_HOME = "APIO_HOME"

# -- Env variable to override the apio packages dir <apio_home>/packages.
# -- it contains the apio packages loaded from github. If specified, the
# -- path must must contains the string 'packages' for safety. This env
# -- variable used in testing to share downloaded packages across tests.
APIO_PACKAGES = "APIO_PACKAGES"

# -- Env variable to override the platform id that is determined automatically
# -- from the system properties. If specified, the value should match one
# -- of the platforms specified in resources/platforms.json.
APIO_PLATFORM = "APIO_PLATFORM"

# -- Env variable to enable printing of debug info, valid values are from
# -- 1 to 10 with 1 for minimal debug info and 10 for maximum.
# --
# -- Do not access it directly. For the apio process use util.is_debug(n) and
# -- for the scons process use scons_util.is_debug(n).
APIO_DEBUG = "APIO_DEBUG"

# -- An env variable that if defined, contains an override url of the remote
# -- config file defined in apio/resources/config.jsonc. During automated
# -- tests, it is overridden to point to the local copy of the remote config
# -- file.
#
# Examples:
#   file:///projects/apio-dev/repo/remote-config/apio-1.1.x.jsonc
#   file:///projects/apio-dev/repo/remote-config/apio-{major}.{minor}.x.jsonc
#   https://github.com/zapta/apio_dev/raw/main/remote-config/apio-{major}.{minor}.x.jsonc
#
APIO_REMOTE_CONFIG_URL = "APIO_REMOTE_CONFIG_URL"


# -- List of all supported env options.
_SUPPORTED_APIO_VARS = [
    APIO_HOME,
    APIO_PACKAGES,
    APIO_PLATFORM,
    APIO_DEBUG,
    APIO_REMOTE_CONFIG_URL,
]


def get(var_name: str, default: str = None):
    """Return the given APIO config env value or default if not found.
    var_name must be in _SUPPORTED_APIO_VARS. The returned
    value is not cached such that mutating the var in this program will
    affect the result of this function.
    """

    # -- Sanity check. To make sure we are aware of all the vars used.
    assert (
        var_name in _SUPPORTED_APIO_VARS
    ), f"Unknown apio env var '{var_name}'"

    # -- Get the value, None if not defined.
    var_value = os.getenv(var_name)

    if var_value is None:
        # -- Var is undefined. Use default
        var_value = default
    else:
        # -- Var is defined. For windows benefit, remove optional quotes.
        if var_value.startswith('"') and var_value.endswith('"'):
            var_value = var_value[1:-1]

    return var_value


def is_defined(var_name) -> bool:
    """Returns true if the env var is currently defined, regardless to its
    value, or False otherwise. var_name must be in _SUPPORTED_APIO_VARS. The
    returned value is not cached such that mutating the var in this program may
    affect the result of this function."""
    # -- Sanity check. To make sure we are aware of all the vars used.
    assert (
        var_name in _SUPPORTED_APIO_VARS
    ), f"Unknown apio env var '{var_name}'"

    # -- Get the value, None if not defined.
    var_value = os.getenv(var_name)
    return var_value is not None


def get_defined() -> List[str]:
    """Return the list of apio env options vars in _SUPPORTED_APIO_VARS
    that are currently defined. The returned value is not cached such that
    mutating the var in this program may affect the result."""
    result = []
    for var in _SUPPORTED_APIO_VARS:
        if is_defined(var):
            result.append(var)
    return result
