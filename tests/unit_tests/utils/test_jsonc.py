# This file is part of the Apio project
# (C) 2016-present FPGAwars
# Project authors:
#   * Jesús Arroyo (Jesus89) (2016-2019)
#   * Juan Gonzalez (obijuan) (2019-2024)
#   * The Apio Team (2024-present)
# License: GPLv2

"""
Tests of jsonc.py
"""

from apio.utils import jsonc

# -- The conversion input and expected output strings. Notice the '//' within
# -- the string, it should not be classified as a comment. The '_' characters
# -- are place holders for trailing white space.
BEFORE = """
    // Comment 1.
    "image": {__
        // Comment 2.
        "src": "Images//Sun.png", // Comment 3
        "name": "aaa\n",
        "hOffset": 250
    }
"""

AFTER = """
____
    "image": {__
________
        "src": "Images//Sun.png",_
        "name": "aaa\n",
        "hOffset": 250
    }
"""


def test_to_json():
    """Test the comments removal."""
    assert jsonc.to_json(BEFORE.replace("_", " ")) == AFTER.replace("_", " ")
