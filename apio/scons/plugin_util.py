# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2018 FPGAwars
# -- Author Jesús Arroyo
# -- Licence GPLv2
# -- Derived from:
# ---- Platformio project
# ---- (C) 2014-2016 Ivan Kravets <me@ikravets.com>
# ---- Licence Apache v2
"""Helper functions for apio scons plugins.
"""

import sys
import os
import re
from pathlib import Path
from typing import List
from click import secho
from SCons import Scanner
from SCons.Node.FS import File
from SCons.Script.SConscript import SConsEnvironment
import debugpy
from apio.scons.apio_env import ApioEnv


def unused(*_):
    """Fake a use of an unused variable or argument."""
    # pass


def maybe_wait_for_remote_debugger(env_var_name: str):
    """A rendezvous point for a remote debger. If the environment variable
    of given name is set, the function will block until a remote
    debugger (e.g. from Visual Studio Code) is attached.
    """
    if os.getenv(env_var_name) is not None:
        secho(f"Env var '{env_var_name}' was detected.")
        port = 5678
        secho(f"Apio SCons for remote debugger on port localhost:{port}.")
        debugpy.listen(port)
        secho(
            "Attach Visual Studio Code python remote python debugger "
            f"to port {port}.",
            fg="magenta",
            color=True,
        )
        # -- Block until the debugger connetcs.
        debugpy.wait_for_client()
        # -- Here the remote debugger is attached and the program continues.
        secho(
            "Remote debugger is attached, program continues...",
            fg="green",
            color=True,
        )


def get_constraint_file(
    apio_env: ApioEnv, file_ext: str, top_module: str
) -> str:
    """Returns the name of the constrain file to use.

    env is the sconstrution environment.

    file_ext is a string with the constrained file extension.
    E.g. ".pcf" for ice40.

    top_module is the top module name. It's is used to construct the
    default file name.

    Returns the file name if found or a default name otherwise otherwise.
    """
    # Files in alphabetical order.
    files = apio_env.env.Glob(f"*{file_ext}")
    n = len(files)
    # Case 1: No matching files.
    if n == 0:
        result = f"{top_module.lower()}{file_ext}"
        secho(
            f"Warning: No {file_ext} constraints file, assuming '{result}'.",
            fg="yellow",
            color=True,
        )
        return result
    # Case 2: Exactly one file found.
    if n == 1:
        result = str(files[0])
        return result
    # Case 3: Multiple matching files.
    secho(
        f"Error: Found multiple '*{file_ext}' "
        "constrain files, expecting exactly one.",
        fg="red",
        color=True,
    )
    sys.exit(1)


def verilog_src_scanner(apio_env: ApioEnv) -> Scanner.Base:
    """Creates and returns a scons Scanner object for scanning verilog
    files for dependencies.
    """
    # A Regex to icestudio propriaetry references for *.list files.
    # Example:
    #   Text:      ' parameter v771499 = "v771499.list"'
    #   Captures:  'v771499.list'
    icestudio_list_re = re.compile(r"[\n|\s][^\/]?\"(.*\.list?)\"", re.M)

    # A regex to match a verilog include.
    # Example
    #   Text:     `include "apio_testing.vh"
    #   Capture:  'apio_testing.vh'
    verilog_include_re = re.compile(
        r'`\s*include\s+["]([a-zA-Z_./]+)["]', re.M
    )

    # A regex for inclusion via $readmemh()
    # Example
    #   Test:      '$readmemh("my_data.hex", State_buff);'
    #   Capture:   'my_data.hex'
    readmemh_reference_re = re.compile(
        r"\$readmemh\([\'\"]([^\'\"]+)[\'\"]", re.M
    )

    # -- List of required and optional files that may require a rebuild if
    # -- changed.
    core_dependencies = [
        "apio.ini",
        "boards.json",
        "fpgas.json",
        "programmers.json",
    ]

    def verilog_src_scanner_func(
        file_node: File, env: SConsEnvironment, ignored_path
    ) -> List[str]:
        """Given a Verilog file, scan it and return a list of references
        to other files it depends on. It's not require to report dependency
        on another .v file in the project since scons loads anyway
        all the .v files in the project.

        Returns a list of files. Dependencies that don't have an existing
        file are ignored and not returned. This is to avoid references in
        commented out code to break scons dependencies.
        """
        unused(env)

        # Sanity check. Should be called only to scan verilog files. If
        # this fails, this is a programming error rather than a user error.
        assert apio_env.is_verilog_src(
            file_node.name
        ), f"Not a src file: {file_node.name}"

        # Create the initial set with the core dependencies.
        candidates_set = set()
        candidates_set.update(core_dependencies)

        # Read the file. This returns [] if the file doesn't exist.
        file_content = file_node.get_text_contents()

        # Get verilog includes references.
        candidates_set.update(verilog_include_re.findall(file_content))

        # Get $readmemh() function references.
        candidates_set.update(readmemh_reference_re.findall(file_content))

        # Get IceStudio references.
        candidates_set.update(icestudio_list_re.findall(file_content))

        # Filter out candidates that don't have a matching files to prevert
        # breakign the build. This handle for example the case where the
        # file references is in a comment or non reachable code.
        # See also https://stackoverflow.com/q/79302552/15038713
        dependencies = []
        for dependency in candidates_set:
            if Path(dependency).exists():
                dependencies.append(dependency)
            elif apio_env.is_debug:
                secho(
                    f"Dependency candidate {dependency} does not exist, "
                    "droping."
                )

        # Sort the strings for determinism.
        dependencies = sorted(list(dependencies))

        # Debug info.
        if apio_env.is_debug:
            secho(f"Dependencies of {file_node.name}:", fg="blue", color=True)
            for dependency in dependencies:
                secho(f"  {dependency}", fg="blue", color=True)

        # All done
        return apio_env.env.File(dependencies)

    return apio_env.env.Scanner(function=verilog_src_scanner_func)
