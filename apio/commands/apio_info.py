# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- License GPLv2
"""Implementation of 'apio info' command"""

import sys
import re
import click
from rich.table import Table
from rich import box
from rich.color import ANSI_COLOR_NAMES
from apio.common.apio_styles import BORDER, EMPH1, EMPH3, TITLE, INFO
from apio.utils import util, cmd_util
from apio.utils.cmd_util import check_at_most_one_param
from apio.apio_context import ApioContext, ApioContextScope
from apio.utils.cmd_util import ApioGroup, ApioSubgroup, ApioCommand
from apio.managers import project
from apio.common.apio_console import (
    PADDING,
    docs_text,
    docs_rule,
    cout,
    cerror,
    cstyle,
    cprint,
)

# -- apio info cli

# -- Text in the rich-text format of the python rich library.
APIO_INFO_CLI_HELP = """
The command 'apio info cli' provides information the Apio's command line \
conventions and features.  \

Examples:[code]
  apio info cli        # Shoe the cli documentation text.
"""

# -- Text in the rich-text format of the python rich library.
APIO_INFO_CLI_TEXT = """
This page describes the conventions and features of the apio command line \
interface.

------

[apio.title]1. APIO'S COMMANDS TREE[/]
Apio commands are organized as a tree of command that start with the root \
command 'apio'. Some command such as 'apio build' has only two level of \
commands while other such as 'apio preferences set' have three and maybe \
more levels. To explore the available commands at each level, type it with \
'-h' to invoke its help message. For example:

[code]  apio -h
  apio info -h
  apio info cli -h[/code]

------

[apio.title]2. APIO'S COMMANDS OPTIONS[/]
Most Apio's commands have options that allow to control their operation. For \
example, the command 'apio build' that has options to control the verbosity \
of its output:

[code]  apio build --verbose
  apio build --verbose-synth[/code]

For the list of options of each command type it with a '-h' option:

[code]  apio build -h[/code]

------

[apio.title]3. APIO'S COMMANDS SHORTCUTS[/]
When typing apio commands, it's sufficient to type enough of the command to \
make the selection non ambiguous. For example, the commands below are \
equivalent.

[code]  apio preferences
  apio pref
  apio pr[/code]

However, the command 'apio p' is ambiguous because it matched both  \
'apio preferences' and 'apio packages'.

------

[apio.title]4. APIO'S SHELL AUTO COMPLETION[/]
Apio's command line processor is based on the Python Click package which \
supports auto completion with some shells. While the were able to make \
it work as a proof of concept, this feature is experimental and is not \
guaranteed to work. More information is available in the Click's \
documentation at https://tinyurl.com/click-shell-completion.

"""


@click.command(
    name="cli",
    cls=cmd_util.ApioCommand,
    short_help="Command line conventions.",
    help=APIO_INFO_CLI_HELP,
)
def _cli_cli():
    """Implements the 'apio info cli' command."""
    sections = re.split("[-]{3,}", APIO_INFO_CLI_TEXT)
    cout()
    for section in sections:
        section = section.strip()
        docs_text(section)
        cout()
        docs_rule()
        cout()


# -- apio info apio.ini

# -- Text in the rich-text format of the python rich library.
APIO_INFO_APIO_INO_HELP = """
The command 'apio info apio.ini' provides information about the required \
project file 'apio.ini'.

Examples:[code]
  apio info apio.ini              # List an overview and all options.
  apio info apio.ini top-module   # List a single option.[/code]
"""

# -- Text in the rich-text format of the python rich library.
APIO_INI_DOC = f"""
[{TITLE}]APIO PROJECT CONFIGURATION FILE[/]

Every Apio project is required to have in its root directory a text file \
named [b]apio.ini[/] that contains the project configuration. At minimum, \
the file looks like the example below with a single 'env' section that with \
the require configuration options.

Example:[code]
  \\[env:default]
  board = alhambra-ii   # Board id
  top-module = my_main  # Top module name[/code]

The apio.ini file can contains multiple named env sections, a common section \
with options that are shared between envs and a section called apio which \
allow to define the default env.

Example:[code]
  ; Optional \\[apio] section.
  \\[apio]
  default-env = env2

  ; Optional \\[common] section.
  \\[common]
  board = alhambra-ii
  top-module = main

  ; Required first env section.
  \\[env:env1]
  default-testbench = main_tb.v

  ; Optional additional env section(s).
  \\[env:env2]
  default-testbench = io_module_tb.v[/code]

The above example defines two environments, called 'env1' and 'env2' \
(default), each with the options in the \\[common] section and the additional \
options from their respective sections.

At runtime, apio select the environment to use based on this rules in \
[b]decreasing[/b] levels of priorities:

- User specified environment name using the --env command line option.
- The value of default-env if exists in the \\[apio] section.
- The first env section that is listed in apio.ini.

When apio determines the environment to use, it collects its options from the \
\\[common] and the env section, with options in the env section having higher \
priority, and executes the command with these expanded environment options.

Following is a list of the options that can appear in the \\[common] and \
the \\[env:*] section. The terms 'required' and 'optional' refers to the \
presence of the options in the options expanded from the \\[common] and the \
\\[env:name] sections.
"""


@click.command(
    name="apio.ini",
    cls=cmd_util.ApioCommand,
    short_help="Apio.ini options.",
    help=APIO_INFO_APIO_INO_HELP,
)
@click.argument("option", nargs=1, required=False)
def _apio_ini_cli(
    # Argument
    option: str,
):
    """Implements the 'apio info apio.ini' command."""

    # -- If option was specified, validate it.
    if option:
        if option not in project.ENV_OPTIONS:
            cerror(f"No such api.ini option: '{option}'")
            cout(
                "For the list of all apio.ini options, type "
                "'apio info apio.ini'.",
                style=INFO,
            )
            sys.exit(1)

    # -- If printing all the options, print first the overview.
    if not option:
        docs_text(APIO_INI_DOC)

    # -- Determine options to print
    options = [option] if option else project.ENV_OPTIONS.keys()

    # -- Print the initial separator line.
    docs_rule()
    for opt in options:
        # -- Print option's title.
        is_required = opt in project.ENV_REQUIRED_OPTIONS
        req = "REQUIRED" if is_required else "OPTIONAL"
        styled_option = cstyle(opt.upper(), style=TITLE)
        cout()
        cout(f"{styled_option} option ({req})")

        # -- Print the option's text.
        text = project.ENV_OPTIONS[opt]
        docs_text(text)
        docs_rule()


# -- apio info files

# -- Text in the rich-text format of the python rich library.
APIO_INFO_FILES_HELP = """
The command 'apio info files' provides information about the various \
files types used in an Apio project.

Examples:[code]
  apio info files
"""

# -- Text in the rich-text format of the python rich library.
APIO_INFO_FILES_DOC = """
Following are apio conventions for project file names. The list does not \
include files that are specific to a particular architecture or toolchain.

[b]apio.ini[/] - This is a required project configuration configuration. \
Run 'apio info apio.ini' for the list of supported options.

[b]*.v, *.sv[/] - Verilog and System Verilog synthesis sources files \
(unless they match the testbench patterns below).

[b]*_tb.v, *_tb.sv[/] - Verilog and System Verilog testbench files.

[b]*.vh, *.svh[/] - Verilog and System Verilog include files.

[b]_build[/] - This is an auto created directory that contains the generated \
files. The directory '_build' is removed when the command 'apio clean' is run.

[b].sconsign.dblite[/] - This is a cache info file that is created by the \
Apio in the project directory and can be ignored and removed. The file \
`.sconsign.dblite` is removed when the command 'apio clean' is run.

[NOTE] If using git for your project, it is recommended to have the following \
entires in your '.gitignore' file:
[code]
  _build
  .sconsign.dblite[/code]
"""


@click.command(
    name="files",
    cls=cmd_util.ApioCommand,
    short_help="Apio project files types.",
    help=APIO_INFO_FILES_HELP,
)
def _files_cli():
    """Implements the 'apio info files' command."""

    # -- Print the text.
    docs_text(APIO_INFO_FILES_DOC)


# -- apio info resources

# -- Text in the rich-text format of the python rich library.
APIO_INFO_RESOURCES_HELP = """
The command 'apio info resources' provides information about apio \
related online resources.

Examples:[code]
  apio info resources   # Provides resources information[/code]
"""

# -- Text in rich-text in rich library format.
APIO_INFO_RESOURCES_SUMMARY = """
The table below provides a few Apio and FPGA design-related resources.

For additional information about specific boards, FPGAs, or tools such as \
[b]yosys[/] and [b]verible[/], consult their respective documentation.

[b]Shawn Hymel's[/] excellent video series on YouTube is based on an older \
version of Apio with a slightly different command set that achieves the \
same functionality.
"""


@click.command(
    name="resources",
    cls=ApioCommand,
    short_help="Additional resources.",
    help=APIO_INFO_RESOURCES_HELP,
)
def _resources_cli():
    """Implements the 'apio info resources' command."""

    docs_text(APIO_INFO_RESOURCES_SUMMARY, width=73)

    # -- Define the table.
    table = Table(
        show_header=True,
        show_lines=True,
        padding=PADDING,
        box=box.SQUARE,
        border_style=BORDER,
        title="Apio Related Resources",
        title_justify="left",
    )

    table.add_column("RESOURCE", no_wrap=True)
    table.add_column("RESOURCE LOCATION", no_wrap=True, style=EMPH1)

    # -- Add rows
    table.add_row(
        "Apio documentation", "https://github.com/FPGAwars/apio/wiki"
    )

    table.add_row(
        "Shwan Hymel series", "https://www.youtube.com/watch?v=lLg1AgA2Xoo"
    )
    table.add_row("Apio repository", "https://github.com/FPGAwars/apio")
    table.add_row(
        "Apio requests and bugs", "https://github.com/FPGAwars/apio/issues"
    )
    table.add_row("Apio Pypi package", "https://pypi.org/project/apio")
    table.add_row("IceStudio (Apio with GUI)", "https://icestudio.io")
    table.add_row("FPGAwars (FPGA resources)", "https://fpgawars.github.io")
    table.add_row(
        "Alhambra-ii FPGA board.", "https://alhambrabits.com/alhambra"
    )

    # -- Render the table.
    cout()
    cprint(table)


# ------ apio info system

# -- Text in the rich-text format of the python rich library.
APIO_INFO_INFO_HELP = """
The command 'apio info system' provides general information about your \
system and Apio installation, which is useful for diagnosing Apio \
installation issues.

Examples:[code]
  apio info system   # System info.[/code]

[b][Advanced][/b] The default location of the Apio home directory, \
where apio saves preferences and packages, is in the '.apio' directory \
under the user home directory but can be changed using the system \
environment variable 'APIO_HOME'.
"""


@click.command(
    name="system",
    cls=ApioCommand,
    short_help="Show system information.",
    help=APIO_INFO_INFO_HELP,
)
def _system_cli():
    """Implements the 'apio info system' command."""

    # Create the apio context.
    apio_ctx = ApioContext(scope=ApioContextScope.NO_PROJECT)

    # -- Define the table.
    table = Table(
        show_header=True,
        show_lines=True,
        padding=PADDING,
        box=box.SQUARE,
        border_style=BORDER,
        title="Apio System Information",
        title_justify="left",
    )

    table.add_column("ITEM", no_wrap=True, min_width=20)
    table.add_column("VALUE", no_wrap=True, style=EMPH1)

    # -- Add rows
    table.add_row("Apio version", util.get_apio_version())
    table.add_row("Python version", util.get_python_version())
    table.add_row("Platform id", apio_ctx.platform_id)
    table.add_row("Python package", str(util.get_path_in_apio_package("")))
    table.add_row("Apio home", str(apio_ctx.home_dir))
    table.add_row("Apio packages", str(apio_ctx.packages_dir))
    table.add_row(
        "Veriable language server",
        str(apio_ctx.packages_dir / "verible/bin/verible-verilog-ls"),
    )

    # -- Render the table.
    cout()
    cprint(table)


# ------ apio info platforms

APIO_INFO_PLATFORMS_HELP = """
The command 'apio info platforms' lists the platform IDs supported by Apio, \
with the effective platform ID of your system highlighted.

[code]Examples:
  apio info platforms   # List supported platform ids.[/code]

[Advanced] The automatic platform ID detection of Apio can be overridden by \
defining a different platform ID using the APIO_PLATFORM environment variable.
"""


@click.command(
    name="platforms",
    short_help="Supported platforms.",
    help=APIO_INFO_PLATFORMS_HELP,
)
def _platforms_cli():
    """Implements the 'apio info platforms' command."""

    # Create the apio context.
    apio_ctx = ApioContext(scope=ApioContextScope.NO_PROJECT)

    # -- Define the table.
    table = Table(
        show_header=True,
        show_lines=True,
        padding=PADDING,
        box=box.SQUARE,
        border_style=BORDER,
        title="Apio Supported Platforms",
        title_justify="left",
    )

    table.add_column("PLATFORM ID", min_width=20, no_wrap=True)
    table.add_column("DESCRIPTION", min_width=30, no_wrap=True)

    # -- Add rows.
    for platform_id, platform_info in apio_ctx.platforms.items():
        description = platform_info.get("description")

        # -- Mark the current platform.
        if platform_id == apio_ctx.platform_id:
            style = EMPH3
            marker = "* "
        else:
            style = None
            marker = "  "

        table.add_row(f"{marker}{platform_id}", f"{description}", style=style)

    # -- Render the table.
    cout()
    cprint(table)


# ------ apio info colors

# -- Text in the rich-text format of the python rich library.
APIO_INFO_COLORS_HELP = """
The command 'apio info colors' shows how ansi colors are rendered on \
the platform, and is typically used to diagnose color related issues. \
While the color name and styling is always handled by the Python Rich \
library, the output is done via three different libraries, based on \
the user's selection.

[code]
Examples:
  apio info colors          # Rich library output (default)
  apio info colors --rich   # Same as above.
  apio info colors --click  # Click library output.
  apio info colors --print  # Python's print() output.
  apio sys col -p             # Using shortcuts.[/code]
"""

rich_option = click.option(
    "rich_",  # Var name.
    "-r",
    "--rich",
    is_flag=True,
    help="Output using the rich lib.",
    cls=cmd_util.ApioOption,
)

click_option = click.option(
    "click_",  # Var name.
    "-c",
    "--click",
    is_flag=True,
    help="Output using the click lib.",
    cls=cmd_util.ApioOption,
)

print_option = click.option(
    "print_",  # Var name.
    "-p",
    "--print",
    is_flag=True,
    help="Output using python's print().",
    cls=cmd_util.ApioOption,
)


@click.command(
    name="colors",
    cls=ApioCommand,
    short_help="Colors table.",
    help=APIO_INFO_COLORS_HELP,
)
@click.pass_context
@rich_option
@click_option
@print_option
def _colors_cli(
    cmd_ctx: click.Context,
    # options
    rich_: bool,
    click_: bool,
    print_: bool,
):
    """Implements the 'apio info colors' command."""

    # pylint: disable=too-many-locals

    # -- Make pylint happy.
    _ = (rich_,)

    # -- Allow at most one of --click and --print.
    check_at_most_one_param(cmd_ctx, ["rich_", "click_", "print_"])

    # -- Select by output type.
    if click_:
        mode = "CLICK"
        output_func = click.echo
    elif print_:
        mode = "PRINT"
        output_func = print
    else:
        mode = "RICH"
        output_func = cout

    # -- Print title.
    cout("", f"ANSI Colors [{mode} mode]", "")

    # -- Create a reversed num->name map
    lookup = {}
    for name, num in ANSI_COLOR_NAMES.items():
        assert 0 <= num <= 255
        lookup[num] = name

    # -- Print the table.
    num_rows = 64
    num_cols = 4
    for row in range(num_rows):
        values = []
        for col in range(num_cols):
            num = row + (col * num_rows)
            name = lookup.get(num, None)
            if name is None:
                # -- No color name.
                values.append(" " * 24)
            else:
                # -- Color name is available.
                # -- Note that the color names and styling is always done by
                # -- the rich library regardless of the choice of output.
                s = f"{num:3} {name:20}"
                values.append(cstyle(s, style=name))

        # -- Construct the line.
        line = "   ".join(values)

        # -- Output the line.
        output_func(line)

    cout()


# ------ apio info

# -- Text in the rich-text format of the python rich library.
APIO_INFO_HELP = """
The command group 'apio info' contains subcommands that provide \
various information about Apio usage, Apio's installation, and your system.
"""

# -- We have only a single group with the title 'Subcommands'.
SUBGROUPS = [
    ApioSubgroup(
        "Documentation",
        [
            _apio_ini_cli,
            _cli_cli,
            _files_cli,
            _resources_cli,
        ],
    ),
    ApioSubgroup(
        "Information",
        [
            _platforms_cli,
            _system_cli,
            _colors_cli,
        ],
    ),
]


@click.command(
    name="info",
    cls=ApioGroup,
    subgroups=SUBGROUPS,
    short_help="Apio's info and info.",
    help=APIO_INFO_HELP,
)
def cli():
    """Implements the 'apio info' command group."""

    # pass
