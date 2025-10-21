# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- License GPLv2
"""Implementation of 'apio format' command"""

import sys
import os
from pathlib import Path
from glob import glob
from typing import Tuple, List, Optional
import click
from apio.common.apio_console import cout, cerror, cstyle
from apio.common.apio_styles import EMPH3, SUCCESS, INFO
from apio.common.common_util import PROJECT_BUILD_PATH, sort_files
from apio.apio_context import (
    ApioContext,
    PackagesPolicy,
    ProjectPolicy,
    RemoteConfigPolicy,
)
from apio.commands import options
from apio.utils import util, cmd_util


# -------------- apio format

# -- Text in the rich-text format of the python rich library.
APIO_FORMAT_HELP = """
The command 'apio format' formats the project's source files to ensure \
consistency and style without altering their semantics. The command accepts \
the names of specific source files to format or formats all project source \
files by default.

Examples:[code]
  apio format                    # Format all source files.
  apio format -v                 # Same but with verbose output.
  apio format main.v main_tb.v   # Format the two files.[/code]

[NOTE] The file arguments are relative to the project directory, even if \
the --project-dir option is used.

The format command utilizes the format tool from the Verible project, which \
can be configured by setting its flags in the apio.ini project file \
For example:


[code]format-verible-options =
    --column_limit=80
    --indentation_spaces=4[/code]

If needed, sections of source code can be protected from formatting using \
Verible formatter directives:

[code]// verilog_format: off
... untouched code ...
// verilog_format: on[/code]

For a full list of Verible formatter flags, refer to the documentation page \
online or use the command 'apio raw -- verible-verilog-format --helpfull'.
"""

# -- File types that the format support. 'sv' indicates System Verilog
# -- and 'h' indicates an includes file.
_FILE_TYPES = [".v", ".sv", ".vh", ".svh"]


@click.command(
    name="format",
    cls=cmd_util.ApioCommand,
    short_help="Format verilog source files.",
    help=APIO_FORMAT_HELP,
)
@click.argument("files", nargs=-1, required=False)
@options.env_option_gen()
@options.project_dir_option
@options.verbose_option
def cli(
    # Arguments
    files: Tuple[str],
    env: Optional[str],
    project_dir: Optional[Path],
    verbose: bool,
):
    """Implements the format command which formats given or all source
    files to format.
    """

    # -- Create an apio context with a project object.
    apio_ctx = ApioContext(
        project_policy=ProjectPolicy.PROJECT_REQUIRED,
        remote_config_policy=RemoteConfigPolicy.CACHED_OK,
        packages_policy=PackagesPolicy.ENSURE_PACKAGES,
        project_dir_arg=project_dir,
        env_arg=env,
    )

    # -- Get the optional formatter options from apio.ini
    cmd_options = apio_ctx.project.get_list_option(
        "format-verible-options", default=[]
    )

    # -- Add verbose option if needed.
    if verbose and "--verbose" not in cmd_options:
        cmd_options.append("--verbose")

    # -- Prepare the packages for use.
    apio_ctx.set_env_for_packages(quiet=not verbose)

    # -- Convert the tuple with file names into a list.
    files: List[str] = list(files)

    # -- Change to the project's folder.
    os.chdir(apio_ctx.project_dir)

    # -- If user didn't specify files to format, all all source files to
    # -- the list.
    if not files:
        for ext in _FILE_TYPES:
            files.extend(glob("**/*" + ext, recursive=True))

        # -- Filter out files that are under the _build directory.
        files = [f for f in files if PROJECT_BUILD_PATH not in Path(f).parents]

        # -- Error if no file to format.
        if not files:
            cerror(f"No files of types {_FILE_TYPES}")
            sys.exit(1)

    # -- Sort files, case insensitive.
    files = sort_files(files)

    # -- Iterate the files and format one at a time. We could format
    # -- all of them at once but this way we can make the output more
    # -- user friendly.
    for f in files:
        # -- Convert to a Path object.
        path = Path(f)

        # -- Check the file extension.
        _, ext = os.path.splitext(path)
        if ext not in _FILE_TYPES:
            cerror(f"'{f}' has an unexpected extension.")
            cout(f"Should be one of {_FILE_TYPES}", style=INFO)
            sys.exit(1)

        # -- Check that the file exists and is a file.
        if not path.is_file():
            cerror(f"'{f}' is not a file.")
            sys.exit(1)

        # -- Print file name.
        styled_f = cstyle(f, style=EMPH3)
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
    cout(f"Processed {util.plurality(files, 'file')}.", style=SUCCESS)
    sys.exit(0)
