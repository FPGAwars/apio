"""Open source ecosystem for open FPGA boards"""
# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2019 FPGAwars
# -- Author Jesús Arroyo
# -- Licence GPLv2

# --------------------------------------------
# - Information for the Distribution package
# --------------------------------------------

VERSION = (0, 7, 5)
__version__ = ".".join([str(s) for s in VERSION])

__title__ = "apio"
__description__ = "Open source ecosystem for open FPGA boards"
__url__ = "https://github.com/FPGAwars/apio"

__author__ = "Jesús Arroyo Torrens"
__email__ = "jesus.arroyo.torrens@gmail.com"

__license__ = "GPLv2"

# Enable this flag to load data from /etc/apio.json file
# Used in apio-debian distribution
LOAD_CONFIG_DATA = False
