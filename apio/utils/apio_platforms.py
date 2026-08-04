# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2018 FPGAwars
# -- Author Jesús Arroyo
# -- License GPLv2
# -- Derived from:
# ---- Platformio project
# ---- (C) 2014-2016 Ivan Kravets <me@ikravets.com>
# ---- License Apache v2
"""Definition of underlying platforms supported by Apio."""

import sys
import re
import platform
from dataclasses import dataclass
from typing import Dict
from apio.utils import env_options
from apio.common.apio_console import cout, cerror
from apio.common.apio_styles import INFO

# -- The list of supported platforms and their attribute. The fields match
# -- the dataclass ApioPlatform below.
_SUPPORTED_PLATFORMS = {
    "darwin-arm64": {
        "type": "Mac OSX",
        "variant": "ARM 64 bit (Apple Silicon)",
        "is_darwin": True,
        "supports_xilinx": True,
    },
    "darwin-x86-64": {
        "type": "Mac OSX",
        "variant": "x86 64 bit (Intel)",
        "is_darwin": True,
        "supports_xilinx": False,
    },
    "linux-x86-64": {
        "type": "Linux",
        "variant": "X86 64 bit",
        "is_linux": True,
        "supports_xilinx": True,
    },
    "linux-aarch64": {
        "type": "Linux",
        "variant": "ARM 64 bit",
        "is_linux": True,
        "supports_xilinx": False,
    },
    "windows-amd64": {
        "type": "Windows",
        "variant": "x86 64 bit",
        "is_windows": True,
        "supports_xilinx": False,
    },
}


@dataclass(frozen=True)
class ApioPlatform:
    """A class with Apio supported platforms and their attributes."""

    # -- Platform id.
    id: str

    # -- Human readable general platform type.
    type: str

    # -- Human readable variant of the platform type.
    variant: str

    # -- True if xlinx is supported on this platform.
    supports_xilinx: bool

    # -- Set to True exactly one of these
    is_darwin: bool = False
    is_linux: bool = False
    is_windows: bool = False

    def __post_init__(self):
        """Post init validation"""

        # -- Constraint chars in platform id.
        assert re.fullmatch(r"[a-z0-9-]+", self.id), self.id

        # -- Exactly one of the platform types should be true.
        assert (
            sum([self.is_linux, self.is_windows, self.is_darwin]) == 1
        ), self.id

        # -- Sanity check the matching between names and types.
        assert ("darwin" in self.id) == self.is_darwin, self.id
        assert ("linux" in self.id) == self.is_linux, self.id
        assert ("windows" in self.id) == self.is_windows, self.id


# -- The supported platforms as a dict with platform id as keys and
# -- ApioPlatform as values. It is constructed from the values in
# -- _SUPPORTED_PLATFORMS.
_APIO_PLATFORMS: Dict[str, ApioPlatform] = {
    id: ApioPlatform(id=id, **fields)
    for id, fields in _SUPPORTED_PLATFORMS.items()
}


def _determine_system_platform_id() -> str:
    """Return a String with the current platform:
    ex. linux-x86-64
    ex. windows-amd64"""

    # -- Get the platform: linux, windows, darwin
    type_ = platform.system().lower()
    platform_str = f"{type_}"

    # -- Get the architecture
    arch = platform.machine().lower()

    # -- Special case for windows
    if type_ == "windows":
        # -- Assume all the windows to be 64-bits
        arch = "amd64"

    # -- Add the architecture, if it exists
    if arch:
        platform_str += f"_{arch}"

    # -- Return the full platform
    return platform_str


def determine_apio_platform() -> ApioPlatform:
    """Determines and returns the platform id based on system info and
    optional override."""
    # -- Use override and get from the underlying system.
    platform_id_override = env_options.get(env_options.APIO_PLATFORM)
    if platform_id_override:
        platform_id = platform_id_override
    else:
        platform_id = _determine_system_platform_id()

    # Stick to the naming conventions we use for boards, fpgas, etc.
    platform_id = platform_id.replace("_", "-")

    # -- Verify it's valid. This can be a user error if the override
    # -- is invalid.
    if platform_id not in _APIO_PLATFORMS.keys():
        cerror(f"Unknown platform id: [{platform_id}]")
        cout(
            "See Apio's documentation for supported platforms.",
            style=INFO,
        )
        sys.exit(1)

    # -- All done ok.
    return _APIO_PLATFORMS[platform_id]


def get_all_apio_platforms() -> Dict[str, ApioPlatform]:
    """Return a dict with all supported platforms."""
    return _APIO_PLATFORMS.copy()


def get_system_info() -> str:
    """Return a short string with additional platform info such as version."""
    return platform.platform()
