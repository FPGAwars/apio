"""
Tests of jsonc.py
"""

from apio.utils import jsonc

# -- The converstion input and expected output strings. Notice the '//' within
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
