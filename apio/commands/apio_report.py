# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- License GPLv2
"""Implementation of 'apio' report' command with export adapters"""

import sys
from typing import Optional
from pathlib import Path
import click
from apio.managers.scons_manager import SConsManager
from apio.commands import options
from apio.apio_context import (
    ApioContext,
    PackagesPolicy,
    ProjectPolicy,
    RemoteConfigPolicy,
)
from apio.common.proto.apio_pb2 import Verbosity
from apio.utils import cmd_util

# New imports for export adapters
from apio.exporters.json import to_json as export_json
from apio.exporters.markdown import to_markdown as export_markdown


# ---------- apio report

# -- Text in the rich-text format of the python rich library.
APIO_REPORT_HELP = """
The command 'apio report' provides information on the utilization and timing \
of the design. It is useful for analyzing utilization bottlenecks and \
verifying that the design can operate at the desired clock speed.

Examples:[code]
  apio report                 # Print report.
  apio report --verbose       # Print extra information.
  apio report --format json   # Export JSON to stdout.
  apio report --format md     # Export Markdown to stdout.
  apio report --format json --out report.json
[/code]
"""


@click.command(
    name="report",
    cls=cmd_util.ApioCommand,
    short_help="Report design utilization and timing.",
    help=APIO_REPORT_HELP,
)
@click.pass_context
@options.env_option_gen()
@options.project_dir_option
@options.verbose_option
@click.option(
    "export_format",
    "--format",
    type=click.Choice(["text", "json", "md"], case_sensitive=False),
    default="text",
    show_default=True,
    help="Output format for the report",
)
@click.option(
    "out_path",
    "--out",
    type=click.Path(dir_okay=False, path_type=Path),
    default=None,
    help="Write output to file instead of stdout",
)
def cli(
    _: click.Context,
    *,
    # Options
    env: Optional[str],
    project_dir: Optional[Path],
    verbose: bool,
    export_format: str,
    out_path: Optional[Path],
):
    """Analyze the design and report timing."""

    # -- Create the apio context.
    apio_ctx = ApioContext(
        project_policy=ProjectPolicy.PROJECT_REQUIRED,
        remote_config_policy=RemoteConfigPolicy.CACHED_OK,
        packages_policy=PackagesPolicy.ENSURE_PACKAGES,
        project_dir_arg=project_dir,
        env_arg=env,
    )

    # -- Create the scons manager.
    scons = SConsManager(apio_ctx)

    # -- Create the verbosity params.
    verbosity = Verbosity(pnr=verbose)

    # Run scons
    exit_code = scons.report(verbosity)

    # -- If only text output requested, preserve existing behavior and exit now.
    if export_format.lower() == "text":
        sys.exit(exit_code)

    # For json/md, read the generated PNR report file and render via exporters.
    # We rely on the standard location used by scons; commonly under env build path.
    candidates = [
        apio_ctx.env_build_path / "pnr.json",
        apio_ctx.env_build_path / "report.json",
    ]
    report_path = next((p for p in candidates if p.exists()), None)
    if report_path is None:
        sys.exit(exit_code)

    # Load structured report
    report_dict = {}
    try:
        import json as _json
        report_dict = _json.loads(report_path.read_text(encoding="utf-8"))
    except Exception:
        sys.exit(exit_code)

    # Render
    if export_format.lower() == "json":
        rendered = export_json(report_dict)
    else:
        rendered = export_markdown(report_dict)

    # Output
    if out_path:
        out_path.write_text(rendered, encoding="utf-8")
    else:
        click.echo(rendered)

    sys.exit(exit_code)
