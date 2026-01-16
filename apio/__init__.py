"""Open source ecosystem for open FPGA boards"""

# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2019 FPGAwars
# -- Author Jesús Arroyo
# -- License GPLv2

# --------------------------------------------
# - Information for the Distribution package
# --------------------------------------------


# -- DEVELOPER:
# -- Change this release number and date when releasing a new Apio CLI version.
# -- If incrementing Major or Minor, a new remote config file is required.
APIO_VERSION = (1, 2, 1)  # Major, Minor, Patch.

# -- This is set automatically during build or publishing information to
# -- provide additional information about the release. This string is included
# -- the 'apio --version' message.
RELEASE_INFO = ""

# -- Get the version as a string. Ex: "0.10.1"
__version__ = ".".join([str(s) for s in APIO_VERSION])

__title__ = "apio"
__description__ = "Open source ecosystem for open FPGA boards"
__url__ = "https://github.com/FPGAwars/apio"

__author__ = "Jesús Arroyo Torrens"
__email__ = "jesus.arroyo.torrens@gmail.com"

__license__ = "GPLv2"
