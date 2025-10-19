# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- License GPLv2
"""Implementation of 'apio clean' command"""

import os
import shutil
import sys
from glob import glob
from typing import Optional, List
from pathlib import Path
import click
from apio.commands import options
from apio.utils import cmd_util, util
from apio.common.apio_console import cout, cerror
from apio.common.apio_styles import SUCCESS, ERROR
from apio.common.common_util import PROJECT_BUILD_PATH
from apio.apio_context import (
    ApioContext,
    PackagesPolicy,
    ProjectPolicy,
    RemoteConfigPolicy,
)


# ----------- apio clean


def _delete_candidates(candidates: List[str]):
    """Delete given files and dirs."""

    # pylint: disable=broad-exception-caught

    # -- Dump for debugging.
    if util.is_debug(1):
        cout(f"\nDeletion candidates: {candidates}")

    # -- Delete candidates that exists.
    items_deleted = False
    for path in candidates:
        item_deleted = False
        try:
            # -- Delete a file.
            if os.path.isfile(path):
                os.remove(path)
                item_deleted = True

            # -- Delete a directory.
            elif os.path.isdir(path):
                # -- Sanity check to make sure we don't delete the entire
                # -- hard drive.
                assert "_build" in str(path), path
                shutil.rmtree(path)
                item_deleted = True

        # -- Handle deletion exceptions, e.g. permissions issues.
        except Exception as e:
            cout(f"{e}", style=ERROR)
            sys.exit(1)

        # -- Check that the item was indeed deleted (e.g if it's not a file
        # -- neither a directory).
        if os.path.exists(path):
            cerror(f"Failed to delete '{path}'")
            sys.exit(1)

        # -- Report item deletion.
        if item_deleted:
            items_deleted = True
            cout(f"- Removed {path}")

    # -- Print a summary.
    if items_deleted:
        cout("Cleanup completed", style=SUCCESS)
    else:
        cout("Already clean", style=SUCCESS)


# -- Text in the rich-text format of the python rich library.
APIO_CLEAN_HELP = """
The command 'apio clean' removes all the output files previously generated \
by apio commands.

Example:[code]
  apio clean[/code]
"""


@click.command(
    name="clean",
    cls=cmd_util.ApioCommand,
    short_help="Delete the apio generated files.",
    help=APIO_CLEAN_HELP,
)
@options.project_dir_option
def cli(
    # Options
    project_dir: Optional[Path],
):
    """Implements the apio clean command. It deletes temporary files generated
    by apio commands.
    """

    # -- Create the apio context.
    # -- We suppress the message with the env and board ids since it's
    # -- not relevant for this command.
    apio_ctx = ApioContext(
        project_policy=ProjectPolicy.PROJECT_REQUIRED,
        remote_config_policy=RemoteConfigPolicy.CACHED_OK,
        packages_policy=PackagesPolicy.ENSURE_PACKAGES,
        project_dir_arg=project_dir,
        report_env=False,
    )

    # -- Change to the project's folder.
    os.chdir(apio_ctx.project_dir)

    # -- TODO: Remove the cleanup of legacy files after releasing the first
    # -- release with the _build directory.
    # --
    # --
    # -- Until apio 0.9.6, the build artifacts were created in the project
    # -- directory rather than the _build directory. To simplify the
    # -- transition we clean here also left over files from 0.9.5.
    candidates = glob("hardware.*")
    candidates += glob("*_tb.vcd")
    candidates += glob("*_tb.out")

    # -- Clean the root build directory.
    candidates.append(PROJECT_BUILD_PATH)

    # -- Clean and report.
    _delete_candidates(candidates)

    sys.exit(0)
