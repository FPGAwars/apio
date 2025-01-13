"""
Tests of jsonc.py
"""

import os
import pytest
from apio.utils import jsonc 

# -- The jsonc input. Notice the '//' inside the string. It should 
# -- not be classified as comment start.
BEFORE = """
    // Comment 1.
    "image": { 
        // Comment 2.
        "src": "Images//Sun.png", // Comment 3
        "name": "aaa\n",
        "hOffset": 250
    }
"""

# -- The expected json output. Some of the lines below have trailing
# -- spaces after the comments removal.
AFTER = """
    
    "image": { 
        
        "src": "Images//Sun.png", 
        "name": "aaa\n",
        "hOffset": 250
    }
"""


def test_to_json():
    """Test the comments removal."""
    assert jsonc.to_json(BEFORE) == AFTER


