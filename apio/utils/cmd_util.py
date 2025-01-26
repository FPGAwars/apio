# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2018 FPGAwars
# -- Author Jesús Arroyo
# -- Licence GPLv2
# -- Derived from:
# ---- Platformio project
# ---- (C) 2014-2016 Ivan Kravets <me@ikravets.com>
# ---- Licence Apache v2
"""Utility functionality for apio click commands. """

import sys
from dataclasses import dataclass
from typing import List, Dict, Union
import click
from apio.utils.apio_console import cout, cerror, cstyle
from apio.utils import util
from apio.profile import Profile


def fatal_usage_error(cmd_ctx: click.Context, msg: str) -> None:
    """Prints a an error message and command help hint, and exists the program
     with an error status.
    cmd_ctx: The context that was passed to the command.
    msg: A single line short error message.
    """
    # Mimiking the usage error message from click/exceptions.py.
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
    The order of the params is in the inptut list is preserved.

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

    Params are click options and arguments that are passed to a command.
    Param ids are the names of variables that are used to pass options and
    argument values to the command. A safe way to construct param_ids
    is nameof(param_var1, param_var2, ...)
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

    Params are click options and arguments that are passed to a command.
    Param ids are the names of variables that are used to pass options and
    argument values to the command. A safe way to construct param_ids
    is nameof(param_var1, param_var2, ...)
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

    Params are click options and arguments that are passed to a command.
    Param ids are the names of variables that are used to pass options and
    argument values to the command. A safe way to construct param_ids
    is nameof(param_var1, param_var2, ...)
    """
    # The the subset of ids of params that where used in the command.
    specified_param_ids = _specified_params(cmd_ctx, param_ids)
    # If more 2 or more print an error and exit.
    if len(specified_param_ids) < 1:
        canonical_aliases = _params_ids_to_aliases(cmd_ctx, param_ids)
        aliases_str = util.list_plurality(canonical_aliases, "or")
        fatal_usage_error(
            cmd_ctx, f"at list one of {aliases_str} must be specified."
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


class ApioGroup(click.Group):
    """A customized click.Group class that allow to group subcommand by
    categories."""

    def __init__(self, *args, **kwargs):
        # -- Consume the 'subgroups' arg.
        self._subgroups: List[ApioSubgroup] = kwargs.pop("subgroups")
        assert isinstance(self._subgroups, list)
        assert isinstance(self._subgroups[0], ApioSubgroup)

        # -- Pass the rest of the arg to init the base class.
        super().__init__(*args, **kwargs)

        # -- Register the commands of the subgroups as subcommands of this
        # -- group.
        for subgroup in self._subgroups:
            for cmd in subgroup.commands:
                self.add_command(cmd=cmd, name=cmd.name)

    # @override
    def get_help(self, ctx: click.Context) -> str:
        """Formats the help into a string and returns it. We override the
        base class method to list the subcommands by categories.
        """

        # -- Apply the color prefernece. This is required because the -h
        # -- options bypasses the command handler so we don't get to create
        # -- an apio context.
        Profile.apply_color_preferences()

        # -- Get the default help text for this command.
        original_help = super().get_help(ctx)

        # -- The auto generated click help lines (apio --help)
        help_lines = original_help.split("\n")

        # -- Extract the header of the text help. We will generate ourselves
        # -- and append the command list.
        index = help_lines.index("Commands:")
        result_lines = help_lines[:index]

        # -- Get a flat list of all subcommand names.
        cmd_names = [
            cmd.name
            for subgroup in self._subgroups
            for cmd in subgroup.commands
        ]

        # -- Find the length of the longerst name.
        max_name_len = max(len(name) for name in cmd_names)

        # -- Generate the subcommands short help, grouped by subgroup.
        for subgroup in self._subgroups:
            result_lines.append(f"{subgroup.title}:")
            for cmd in subgroup.commands:
                # -- We pad for field width and then apply color.
                styled_name = cstyle(
                    f"{cmd.name:{max_name_len}}", style="magenta"
                )
                result_lines.append(
                    f"  {ctx.command_path} {styled_name}  {cmd.short_help}"
                )
            result_lines.append("")

        return "\n".join(result_lines)
