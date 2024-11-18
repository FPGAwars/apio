# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2018 FPGAwars
# -- Author Jesús Arroyo
# -- Licence GPLv2
# -- Derived from:
# ---- Platformio project
# ---- (C) 2014-2016 Ivan Kravets <me@ikravets.com>
# ---- Licence Apache v2
"""Functions for reading the APIO env options. This are system env
variables that are used to modify the default behavior of APIO.
"""

import os
from typing import List

# -- Env variable to override the apio home dir ~/.apio
APIO_HOME_DIR = "APIO_HOME_DIR"

# -- Env variable to override the apio packages dir ~/.apio/packages.
APIO_PKG_DIR = "APIO_PKG_DIR"


_SUPPORTED_APIO_VARS = [
    APIO_HOME_DIR,
    APIO_PKG_DIR,
]


def get(var_name: str, default: str = None):
    """Return the given APIO config env value or default if not found.
    var_name must start with 'APIO_' and match _API_ENV_NAME_REGEX.
    """

    # -- Sanity check. To make sure we are aware of all the vars used.
    assert (
        var_name in _SUPPORTED_APIO_VARS
    ), f"Unknown apio env var '{var_name}'"

    # -- Get the value, None if not defined.
    var_value = os.getenv(var_name)

    if var_value is None:
        # -- Var is undefied. Use default
        var_value = default
    else:
        # -- Var is defined. For windows benefit, remove optional quotes.
        if var_value.startswith('"') and var_value.endswith('"'):
            var_value = var_value[1:-1]

    return var_value


def get_defined() -> List[str]:
    """Return the list of apio env options vars that are defined."""
    result = []
    for var in _SUPPORTED_APIO_VARS:
        if get(var):
            result.append(var)
    return result
