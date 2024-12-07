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
from typing import Mapping, List, Tuple, Any, Dict, Union
import click
from apio import util


# This text marker is inserted into the help text to indicates
# deprecated options.
DEPRECATED_MARKER = "[DEPRECATED]"


def fatal_usage_error(cmd_ctx: click.Context, msg: str) -> None:
    """Prints a an error message and command help hint, and exists the program
     with an error status.
    cmd_ctx: The context that was passed to the command.
    msg: A single line short error message.
    """
    # Mimiking the usage error message from click/exceptions.py.
    # E.g. "Try 'apio packages -h' for help."
    click.secho(cmd_ctx.get_usage())
    click.secho(
        f"Try '{cmd_ctx.command_path} {cmd_ctx.help_option_names[0]}' "
        "for help."
    )
    click.secho()
    click.secho(f"Error: {msg}", fg="red")
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
        # Consume the "deprecated" arg is specified. This args is
        # added by this class and is not passed to super.
        self.deprecated = kwargs.pop("deprecated", False)
        # Tweak the help text to have a [DEPRECATED] prefix.
        if self.deprecated:
            kwargs["help"] = (
                DEPRECATED_MARKER + " " + kwargs.get("help", "").strip()
            )
        super().__init__(*args, **kwargs)

    # @override
    def handle_parse_result(
        self, ctx: click.Context, opts: Mapping[str, Any], args: List[str]
    ) -> Tuple[Any, List[str]]:
        """Overides the parent method to print a deprecated option message."""
        if self.deprecated and self.name in opts:
            click.secho(f"Info: {self.aliases} is deprecated.", fg="yellow")
        return super().handle_parse_result(ctx, opts, args)


DEPRECATION_NOTE = f"""
[Note] Flags marked with {DEPRECATED_MARKER} are not recomanded for use.
For project configuration, use an apio.ini project file and if neaded,
project specific 'boards.json' and 'fpga.json' definition files.
"""


class ApioCommand(click.Command):
    """Override click.Command with Apio specific behavior.
    Currently it adds a clarification note to the help text of
    commands that contains deprecated ApioOptions.
    """

    def _num_deprecated_options(self, cmd_ctx: click.Context) -> None:
        """Returns the number of deprecated options of this command."""
        deprecated_options = 0
        for param in self.get_params(cmd_ctx):
            if isinstance(param, ApioOption) and param.deprecated:
                deprecated_options += 1
        return deprecated_options

    # @override
    def format_help_text(
        self, ctx: click.Context, formatter: click.HelpFormatter
    ) -> None:
        super().format_help_text(ctx, formatter)
        deprecated = self._num_deprecated_options(ctx)
        if deprecated > 0:
            formatter.write_paragraph()
            with formatter.indentation():
                formatter.write_text(DEPRECATION_NOTE)
