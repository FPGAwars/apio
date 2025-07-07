# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2018 FPGAwars
# -- Author Jesús Arroyo
# -- License GPLv2
# -- Derived from:
# ---- Platformio project
# ---- (C) 2014-2016 Ivan Kravets <me@ikravets.com>
# ---- License Apache v2
"""Utility functionality for apio click commands."""

import sys
from dataclasses import dataclass
from typing import List, Dict, Union
import click
from click.formatting import HelpFormatter
from apio.common import apio_console
from apio.profile import Profile
from apio.common.apio_styles import CMD_NAME
from apio.common.apio_console import (
    ConsoleCapture,
    cout,
    cerror,
    cstyle,
    docs_text,
)
from apio.utils import util


def fatal_usage_error(cmd_ctx: click.Context, msg: str) -> None:
    """Prints a an error message and command help hint, and exists the program
     with an error status.
    cmd_ctx: The context that was passed to the command.
    msg: A single line short error message.
    """
    assert isinstance(cmd_ctx, ApioCmdContext)

    # Mimicking the usage error message from click/exceptions.py.
    # E.g. "Try 'apio packages -h' for help."
    cout(cmd_ctx.get_usage())
    cout(
        f"Try '{cmd_ctx.command_path} {cmd_ctx.help_option_names[0]}' "
        "for help."
    )
    cout("")
    cerror(f"{msg}")
    sys.exit(1)


def _get_all_params_definitions(
    cmd_ctx: click.Context,
) -> Dict[str, Union[click.Option, click.Argument]]:
    """Return a mapping from param id to param obj, for all options and
    arguments that are defined for the command."""
    result = {}
    for param_obj in cmd_ctx.command.get_params(cmd_ctx):
        assert isinstance(param_obj, (click.Option, click.Argument)), type(
            param_obj
        )
        result[param_obj.name] = param_obj
    return result


def _params_ids_to_aliases(
    cmd_ctx: click.Context, params_ids: List[str]
) -> List[str]:
    """Maps param ids to their respective user facing canonical aliases.
    The order of the params is in the input list is preserved.

    For the definition of param ids see check_exclusive_params().

    The canonical alias of an option is it's longest alias,
    for example "--dir" for the option ["-d", "--dir"]. The canonical
    alias of an argument is the argument name as shown in the command's help,
    e.g. "PACKAGES" for the argument packages.
    """
    # Param id -> param obj.
    params_dict = _get_all_params_definitions(cmd_ctx)

    # Map the param ids to their canonical aliases.
    result = []
    for param_id in params_ids:
        param_obj: Union[click.Option, click.Argument] = params_dict[param_id]
        assert isinstance(param_obj, (click.Option, click.Argument)), type(
            param_obj
        )
        if isinstance(param_obj, click.Option):
            # For options we pick their longest alias
            param_alias = max(param_obj.aliases, key=len)
        else:
            # For arguments we pick its user facing name, e.g. "PACKAGES"
            # for argument packages.
            param_alias = param_obj.human_readable_name
        assert param_obj is not None, param_id
        result.append(param_alias)
    return result


def _is_param_specified(cmd_ctx, param_id) -> bool:
    """Determine if the param with given id was specified in the
    command line."""
    # Mapping: param id -> param obj.
    params_dict = _get_all_params_definitions(cmd_ctx)
    # If this fails, look for spelling error in the param name string in
    # the apio command cli function.
    assert param_id in params_dict, f"Unknown command param_id [{param_id}]."
    # Get the official status.
    param_src = cmd_ctx.get_parameter_source(param_id)
    is_specified = param_src == click.core.ParameterSource.COMMANDLINE
    # A special case for repeating arguments. Click considers the
    # empty tuple value to come with the command line but we consider
    # it to come from the default.
    is_arg = isinstance(params_dict[param_id], click.Argument)
    if is_specified and is_arg:
        arg_value = cmd_ctx.params[param_id]
        if arg_value == tuple():
            is_specified = False
    # All done
    return is_specified


def _specified_params(
    cmd_ctx: click.Context, param_ids: List[str]
) -> List[str]:
    """Returns the subset of param ids that were used in the command line.
    The original order of the list is preserved.
    For definition of params and param ids see check_exclusive_params().
    """
    result = []
    for param_id in param_ids:
        if _is_param_specified(cmd_ctx, param_id):
            result.append(param_id)
    return result


def check_at_most_one_param(
    cmd_ctx: click.Context, param_ids: List[str]
) -> None:
    """Checks that at most one of given params were specified in
    the command line. If more than one param was specified, exits the
    program with a message and error status.

    Param ids are names click options and arguments variables that are passed
    to a command.
    """
    # The the subset of ids of params that where used in the command.
    specified_param_ids = _specified_params(cmd_ctx, param_ids)
    # If more 2 or more print an error and exit.
    if len(specified_param_ids) >= 2:
        canonical_aliases = _params_ids_to_aliases(
            cmd_ctx, specified_param_ids
        )
        aliases_str = util.list_plurality(canonical_aliases, "and")
        fatal_usage_error(
            cmd_ctx, f"{aliases_str} cannot be combined together."
        )


def check_exactly_one_param(
    cmd_ctx: click.Context, param_ids: List[str]
) -> None:
    """Checks that at exactly one of given params is specified in
    the command line. If more or less than one params is specified, exits the
    program with a message and error status.

    Param ids are names click options and arguments variables that are passed
    to a command.
    """
    # The the subset of ids of params that where used in the command.
    specified_param_ids = _specified_params(cmd_ctx, param_ids)
    # If exactly one than we are good.
    if len(specified_param_ids) == 1:
        return
    if len(specified_param_ids) < 1:
        # -- User specified Less flags than required.
        canonical_aliases = _params_ids_to_aliases(cmd_ctx, param_ids)
        aliases_str = util.list_plurality(canonical_aliases, "or")
        fatal_usage_error(cmd_ctx, f"specify one of {aliases_str}.")
    else:
        # -- User specified more flags than allowed.
        canonical_aliases = _params_ids_to_aliases(
            cmd_ctx, specified_param_ids
        )
        aliases_str = util.list_plurality(canonical_aliases, "and")
        fatal_usage_error(
            cmd_ctx, f"{aliases_str} cannot be combined together."
        )


def check_at_least_one_param(
    cmd_ctx: click.Context, param_ids: List[str]
) -> None:
    """Checks that at least one of given params is specified in
    the command line. If none of the params is specified, exits the
    program with a message and error status.

    Param ids are names click options and arguments variables that are passed
    to a command.
    """
    # The the subset of ids of params that where used in the command.
    specified_param_ids = _specified_params(cmd_ctx, param_ids)
    # If more 2 or more print an error and exit.
    if len(specified_param_ids) < 1:
        canonical_aliases = _params_ids_to_aliases(cmd_ctx, param_ids)
        aliases_str = util.list_plurality(canonical_aliases, "or")
        fatal_usage_error(
            cmd_ctx, f"at least one of {aliases_str} must be specified."
        )


class ApioOption(click.Option):
    """Custom class for apio click options. Currently it adds handling
    of deprecated options.
    """

    def __init__(self, *args, **kwargs):
        # Cache a list of option's aliases. E.g. ["-t", "--top-model"].
        self.aliases = [k for k in args[0] if k.startswith("-")]

        # Pass the rest to the base class.
        super().__init__(*args, **kwargs)


@dataclass(frozen=True)
class ApioSubgroup:
    """A class to represent a named group of subcommands. An apio command
    of type group, contains two or more subcommand in one or more subgroups."""

    title: str
    commands: List[click.Command]


def _format_apio_rich_text_help_text(
    rich_text: str, formatter: HelpFormatter
) -> None:
    """Format command's or group's help rich text into a given
    click formatter."""

    # -- Style the metadata text.
    styled_text = None
    with ConsoleCapture() as capture:
        docs_text(rich_text.rstrip("\n"), end="")
        styled_text = capture.value

    # -- Raw write to the output, with indent.
    lines = styled_text.split("\n")
    for line in lines:
        formatter.write(("  " + line).rstrip(" ") + "\n")


class ApioGroup(click.Group):
    """A customized click.Group class that allows apio customized help
    format."""

    def __init__(self, *args, **kwargs):

        # -- Consume the 'subgroups' arg.
        self.subgroups: List[ApioSubgroup] = kwargs.pop("subgroups")
        assert isinstance(self.subgroups, list)
        assert isinstance(self.subgroups[0], ApioSubgroup)

        # -- Override the static variable of the Command class to point
        # -- to our custom ApioCmdContext. This causes the command to use
        # -- contexts of type ApioCmdContext instead of click.Context.
        click.Command.context_class = ApioCmdContext

        # -- Pass the rest of the arg to init the base class.
        super().__init__(*args, **kwargs)

        # -- Register the commands of the subgroups as subcommands of this
        # -- group.
        for subgroup in self.subgroups:
            for cmd in subgroup.commands:
                self.add_command(cmd=cmd, name=cmd.name)

    # @override
    def format_help_text(
        self, ctx: click.Context, formatter: HelpFormatter
    ) -> None:
        """Overrides the parent method that formats the command's help text."""
        assert isinstance(ctx, ApioCmdContext)
        _format_apio_rich_text_help_text(self.help, formatter)

    # @override
    def format_options(
        self, ctx: click.Context, formatter: HelpFormatter
    ) -> None:
        """Overrides the parent method which formats the options and sub
        commands."""
        assert isinstance(ctx, ApioCmdContext)

        # -- Call the grandparent method which formats the options without
        # -- the subcommands.
        click.Command.format_options(self, ctx, formatter)

        # -- Format the subcommands, grouped by the apio defined subgroups
        # -- in self._subgroups.
        formatter.write("\n")

        # -- Get a flat list of all subcommand names.
        cmd_names = [
            cmd.name
            for subgroup in self.subgroups
            for cmd in subgroup.commands
        ]

        # -- Find the length of the longest name.
        max_name_len = max(len(name) for name in cmd_names)

        # -- Generate the subcommands short help, grouped by subgroup.
        for subgroup in self.subgroups:
            assert isinstance(subgroup, ApioSubgroup), subgroup
            formatter.write(f"{subgroup.title}:\n")
            # -- Print the commands that are in this subgroup.
            for cmd in subgroup.commands:
                # -- We pad for field width and then apply color.
                styled_name = cstyle(
                    f"{cmd.name:{max_name_len}}", style=CMD_NAME
                )
                formatter.write(
                    f"  {ctx.command_path} {styled_name}  {cmd.short_help}\n"
                )
            formatter.write("\n")

    # @override
    def get_command(self, ctx, cmd_name) -> click.Command:
        """Overrides the method that matches a token in the command line to
        a sub-command. This alternative implementation allows to specify also
        a prefix of the command name, as long as it matches exactly one
        sub command. For example 'pref' or 'p' for 'preferences'.

        Returns the Command or Group (a subclass of Command) of the matching
        sub command or None if not match.
        """

        assert isinstance(ctx, ApioCmdContext)

        # -- First priority is for exact match. For this we use the click
        # -- default implementation from the parent class.
        cmd: click.Command = click.Group.get_command(self, ctx, cmd_name)
        if cmd is not None:
            return cmd

        # -- Here when there was no exact match, we will try partial matches.
        sub_cmds = self.list_commands(ctx)
        matches = [x for x in sub_cmds if x.startswith(cmd_name)]
        # -- Handle no matches.
        if not matches:
            return None
        # -- Handle multiple matches.
        if len(matches) > 1:
            ctx.fail(f"Command prefix '{cmd_name}' is ambagious: {matches}.")
            # cout(f"Command '{cmd_name}' is ambagious: {matches}", style=INFO)
            return None
        # -- Here when exact match. We are good.
        cmd = click.Group.get_command(self, ctx, matches[0])
        return cmd


class ApioCommand(click.Command):
    """A customized click.Command class that allows apio customized help
    format and proper handling of command shortcuts."""

    # @override
    def format_help_text(
        self, ctx: click.Context, formatter: HelpFormatter
    ) -> None:
        """Overrides the parent method that formats the command's help text."""
        assert isinstance(ctx, ApioCmdContext), type(ctx)
        _format_apio_rich_text_help_text(self.help, formatter)


class ApioCmdContext(click.Context):
    """A custom click.Context class."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # -- Replace the potentially partial command name the user specified
        # -- with the full command name. This will cause usage messages to
        # -- include the full command names.
        self.info_name = self.command.name

        # -- If this the top command context, apply user color preferences
        # -- to the apio console.
        if self.parent is None:
            Profile.apply_color_preferences()

        # -- Synchronize the click color output setting to the apio console
        # -- setting. The self.color flag affects output of help and
        # -- usage text by click.
        self.color = apio_console.is_terminal()

    # @override
    def get_help(self) -> str:
        # IMPORTANT:
        # This implementation behaves differently than the parent method
        # it overrides.
        #
        # Instead of returning the help text, we print it using the rich
        # library and exit and just return an empty string. This avoids
        # the default printing using the click library which strips some
        # colors on windows.
        #
        # The empty string we return is printed by click as an black line
        # which adds a nice separation line. Otherwise we would pass None.
        cout(self.command.get_help(self))
        return ""
