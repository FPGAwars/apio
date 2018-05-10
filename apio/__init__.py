# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2018 FPGAwars
# -- Author Jesús Arroyo
# -- Licence GPLv2

VERSION = (0, 3, 3)
__version__ = '.'.join([str(s) for s in VERSION])

__title__ = 'apio'
__description__ = ('Experimental micro-ecosystem for open FPGAs')
__url__ = 'https://github.com/FPGAwars/apio'

__author__ = 'Jesús Arroyo Torrens'
__email__ = 'jesus.arroyo.torrens@gmail.com'

__license__ = 'GPLv2'

# Enable this flag to load data from /etc/apio.json file
# Used in apio-debian distribution
LOAD_CONFIG_DATA = False
