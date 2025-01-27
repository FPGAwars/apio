# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- Licence GPLv2
"""Implementation of 'apio format' command"""

import sys
import os
from pathlib import Path
from glob import glob
from typing import Tuple, List
import click
from apio.common.apio_console import cout, cerror, cstyle
from apio.apio_context import ApioContext, ApioContextScope
from apio.commands import options
from apio.managers import installer
from apio.utils import util, pkg_util


# ---------------------------
# -- COMMAND
# ---------------------------
APIO_FORMAT_HELP = """
The command ‘apio format’ formats Verilog source files to ensure consistency
and style without altering their semantics. The command accepts the names of
pecific source files to format or formats all project source files by default.

\b
Examples:
  apio format                    # Format all source files.
  apio format -v                 # Same as above but with verbose output.
  apio format main.v main_tb.v   # Format the two tiven files.

The format command utilizes the format tool from the Verible project, which
can be configured by setting its flags in the apio.ini project file
For example:

\b
format-verible-options =
    --column_limit=80
    --indentation_spaces=4

If needed, sections of source code can be protected from formatting using
Verible formatter directives:

\b
// verilog_format: off
... untouched code ...
// verilog_format: on

For a full list of Verible formatter flags, refer to the documentation page
online or use the command 'apio raw -- verible-verilog-format --helpful'.
"""


@click.command(
    name="format",
    short_help="Format verilog source files.",
    help=APIO_FORMAT_HELP,
)
@click.argument("files", nargs=-1, required=False)
@options.project_dir_option
@options.verbose_option
def cli(
    # Arguments
    files: Tuple[str],
    project_dir: Path,
    verbose: bool,
):
    """Implements the format command which formats given or all source
    files to format.
    """

    # -- Create an apio context with a project object.
    apio_ctx = ApioContext(
        scope=ApioContextScope.PROJECT_REQUIRED, project_dir_arg=project_dir
    )

    # -- Get the optional formatter options from apio.ini
    cmd_options = apio_ctx.project.get_as_lines_list(
        "format-verible-options", default=[]
    )

    # -- Add verbose option if needed.
    if verbose and "--verbose" not in cmd_options:
        cmd_options.append("--verbose")

    # -- Prepare the packages for use.
    installer.install_missing_packages_on_the_fly(apio_ctx)
    pkg_util.set_env_for_packages(apio_ctx)

    # -- Convert the tuple with file names into a list.
    files: List[str] = list(files)

    # -- If user didn't specify files to firmat, all all source files to
    # -- the list.
    if not files:
        files.extend(glob(str(apio_ctx.project_dir / "*.v")))
        files.extend(glob(str(apio_ctx.project_dir / "*.sv")))

    # -- Error if no file to format.
    if not files:
        cerror("No '.v' or '.sv' files to format")
        sys.exit(1)

    # -- Sort files, case insensitive.
    files = sorted(files, key=str.casefold)

    # -- Iterate the files and format one at a time. We could format
    # -- all of them at once but this way we can make the output more
    # -- user friendly.
    for f in files:
        # -- Convert to a Path object.
        path = Path(f)

        # -- Check the file extension.
        _, ext = os.path.splitext(path)
        if ext not in [".v", ".sv"]:
            cerror(
                f"'{f}' has an invalid extension, " "should be '.v' or '.sv'"
            )
            sys.exit(1)

        # -- Check that the file exists and is a file.
        if not path.is_file():
            cerror(f"'{f}' is not a file.")
            sys.exit(1)

        # -- Print file name.
        styled_f = cstyle(f, style="magenta")
        cout(f"Formatting {styled_f}")

        # -- Construct the formatter command line.
        command = (
            "verible-verilog-format --nofailsafe_success --inplace "
            f' {" ".join(cmd_options)} "{f}"'
        )
        if verbose:
            cout(command)

        # -- Execute the formatter command line.
        exit_code = os.system(command)
        if exit_code != 0:
            cerror(f"Formatting of '{f}' failed")
            return exit_code

    # -- All done ok.
    cout(f"Formatted {util.plurality(files, 'file')}.", style="green")
    sys.exit(0)
