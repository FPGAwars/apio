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
from apio.apio_context import ApioContext, ApioContextScope
from apio import pkg_util, util
from apio.commands import options


# ---------------------------
# -- COMMAND
# ---------------------------
HELP = """
The format command formats verilog source files for consistency and style
but without changing their semantic.  The command accepts the names of the
source files to format or formats all the project source files by default.
The commands is typically used in the root directory
of the project that contains the apio.ini file.

\b
Examples:
  apio format                    # Format all source files.
  apio format -v                 # Same as above but with verbose output.
  apio format main.v main_tb.v   # Format the two tiven files.

The format command uses the format tool of the Verible project which can be
configured by setting its flags in the apio.ini project file.
For example:

\b
format-verible-options =
    --column_limit=80
    --indentation_spaces=4

If you want to protect a group of source code lines from formatting, you
can use the following verible formatter's directives:

\b
// verilog_format: off
... untouched code ...
// verilog_format: on

For the ull list of the verible formatter flags, see its documentation page
online or type 'apio raw -- verible-verilog-format --helpfull'.
"""


@click.command(
    name="format",
    short_help="Format verilog source files.",
    help=HELP,
)
@click.pass_context
@click.argument("files", nargs=-1, required=False)
@options.project_dir_option
@options.verbose_option
def cli(
    _cmd_ctx: click.Context,
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

    # -- Error if the apio verible package is not installed.
    pkg_util.check_required_packages(apio_ctx, ["verible"])

    # -- Get the optional formatter options from apio.ini
    cmd_options = apio_ctx.project.get_as_lines_list(
        "format-verible-options", default=[]
    )

    # -- Add verbose option if needed.
    if verbose and "--verbose" not in cmd_options:
        cmd_options.append("--verbose")

    # -- Set the system envs to access the binaries in the paio packages.
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
        click.secho("Error: No '.v' or '.sv' files to format", fg="red")
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
            click.secho(
                f"Error: '{f}' has an invalid extension, "
                "should be '.v' or '.sv'",
                fg="red",
            )
            sys.exit(1)

        # -- Check that the file exists and is a file.
        if not path.is_file():
            click.secho(f"Error: '{f}' is not a file.", fg="red")
            sys.exit(1)

        # -- Print file name.
        styled_f = click.style(f, fg="magenta")
        click.secho(f"Formatting {styled_f}")

        # -- Construct the formatter command line.
        command = (
            "verible-verilog-format --nofailsafe_success --inplace "
            f' {" ".join(cmd_options)} "{f}"'
        )
        if verbose:
            click.secho(command)

        # -- Execute the formatter command line.
        exit_code = os.system(command)
        if exit_code != 0:
            click.secho(f"Error: formatting of '{f}' failed", fg="red")
            return exit_code

    # -- All done ok.
    click.secho(f"Formatted {util.plurality(files, 'file')}.", fg="green")
    sys.exit(0)
