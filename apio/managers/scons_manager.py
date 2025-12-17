"""A manager class for  to dispatch the Apio SCONS targets."""

# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2019 FPGAwars
# -- Author Jesús Arroyo
# -- License GPLv2

import traceback
import os
import sys
import time
import shutil
from functools import wraps
from datetime import datetime
from google.protobuf import text_format
from apio.common import apio_console
from apio.common.apio_console import cout, cerror, cstyle, cunstyle
from apio.common.apio_styles import SUCCESS, ERROR, EMPH3, INFO
from apio.utils import util
from apio.apio_context import ApioContext
from apio.managers.scons_filter import SconsFilter
from apio.common.proto.apio_pb2 import (
    FORCE_PIPE,
    FORCE_TERMINAL,
    Verbosity,
    Environment,
    SconsParams,
    TargetParams,
    FpgaInfo,
    ApioEnvParams,
    Ice40FpgaInfo,
    Ecp5FpgaInfo,
    GowinFpgaInfo,
    ApioArch,
    GraphParams,
    LintParams,
    SimParams,
    ApioTestParams,
    UploadParams,
)

# from apio.common import rich_lib_windows


# W0703: Catching too general exception Exception (broad-except)
# pylint: disable=W0703
#
# -- Based on
# -- https://stackoverflow.com/questions/5929107/decorators-with-parameters
def on_exception(*, exit_code: int):
    """Decorator for functions that return int exit code. If the function
    throws an exception, the error message is printed, and the caller see the
    returned value exit_code instead of the exception.
    """

    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            try:
                return function(*args, **kwargs)
            except Exception as exc:
                if util.is_debug(1):
                    traceback.print_tb(exc.__traceback__)

                if str(exc):
                    cerror(str(exc))

                if not util.is_debug(1):
                    cout(
                        "Running with APIO_DEBUG=1 may provide "
                        "additional diagnostic information.",
                        style=INFO,
                    )
                return exit_code

        return wrapper

    return decorator


class SConsManager:
    """Class for managing the scons tools"""

    def __init__(self, apio_ctx: ApioContext):
        """Initialization."""
        # -- Cache the apio context.
        self.apio_ctx = apio_ctx

        # -- Change to the project's folder.
        os.chdir(apio_ctx.project_dir)

    @on_exception(exit_code=1)
    def graph(self, graph_params: GraphParams, verbosity: Verbosity) -> int:
        """Runs a scons subprocess with the 'graph' target. Returns process
        exit code, 0 if ok."""

        # -- Construct scons params with graph command info.
        scons_params = self.construct_scons_params(
            target_params=TargetParams(graph=graph_params),
            verbosity=verbosity,
        )

        # -- Run the scons process.
        return self._run_scons_subprocess("graph", scons_params=scons_params)

    @on_exception(exit_code=1)
    def lint(self, lint_params: LintParams) -> int:
        """Runs a scons subprocess with the 'lint' target. Returns process
        exit code, 0 if ok."""

        # -- Construct scons params with graph command info.
        scons_params = self.construct_scons_params(
            target_params=TargetParams(lint=lint_params)
        )

        # -- Run the scons process.
        return self._run_scons_subprocess("lint", scons_params=scons_params)

    @on_exception(exit_code=1)
    def sim(self, sim_params: SimParams) -> int:
        """Runs a scons subprocess with the 'sim' target. Returns process
        exit code, 0 if ok."""

        # -- Construct scons params with graph command info.
        scons_params = self.construct_scons_params(
            target_params=TargetParams(sim=sim_params)
        )

        # -- Run the scons process.
        return self._run_scons_subprocess("sim", scons_params=scons_params)

    @on_exception(exit_code=1)
    def test(self, test_params: ApioTestParams) -> int:
        """Runs a scons subprocess with the 'test' target. Returns process
        exit code, 0 if ok."""

        # -- Construct scons params with graph command info.
        scons_params = self.construct_scons_params(
            target_params=TargetParams(test=test_params)
        )

        # -- Run the scons process.
        return self._run_scons_subprocess("test", scons_params=scons_params)

    @on_exception(exit_code=1)
    def build(self, verbosity: Verbosity) -> int:
        """Runs a scons subprocess with the 'build' target. Returns process
        exit code, 0 if ok."""

        # -- Construct the scons params object.
        scons_params = self.construct_scons_params(verbosity=verbosity)

        # -- Run the scons process.
        return self._run_scons_subprocess("build", scons_params=scons_params)

    @on_exception(exit_code=1)
    def report(self, verbosity: Verbosity) -> int:
        """Runs a scons subprocess with the 'report' target. Returns process
        exit code, 0 if ok."""

        # -- Construct the scons params object.
        scons_params = self.construct_scons_params(verbosity=verbosity)

        # -- Run the scons process.
        return self._run_scons_subprocess("report", scons_params=scons_params)

    @on_exception(exit_code=1)
    def upload(self, upload_params: UploadParams) -> int:
        """Runs a scons subprocess with the 'time' target. Returns process
        exit code, 0 if ok.
        """

        # -- Construct the scons params.
        scons_params = self.construct_scons_params(
            target_params=TargetParams(upload=upload_params)
        )

        # -- Execute Scons for uploading!
        exit_code = self._run_scons_subprocess(
            "upload", scons_params=scons_params
        )

        return exit_code

    def construct_scons_params(
        self,
        *,
        target_params: TargetParams = None,
        verbosity: Verbosity = None,
    ) -> SconsParams:
        """Populate and return the SconsParam proto to pass to the scons
        process."""

        # -- Create a shortcut.
        apio_ctx = self.apio_ctx

        # -- Create an empty proto object that will be populated.
        result = SconsParams()

        # -- Populate the timestamp. We use to to make sure scons reads the
        # -- correct version of the scons.params file.
        ts = datetime.now()
        result.timestamp = ts.strftime("%d%H%M%S%f")[:-3]

        # -- Get the project data. All commands that invoke scons are expected
        # -- to be in a project context.
        assert apio_ctx.has_project, "Scons encountered a missing project."
        project = apio_ctx.project

        # -- Get the project resource.s
        pr = apio_ctx.project_resources

        # -- Populate the common values of FpgaInfo.
        result.fpga_info.MergeFrom(
            FpgaInfo(
                fpga_id=pr.fpga_id,
                part_num=pr.fpga_info["part-num"],
                size=pr.fpga_info["size"],
            )
        )

        # - Populate the architecture specific values of result.fpga_info.
        fpga_arch = pr.fpga_info["arch"]
        match fpga_arch:
            case "ice40":
                result.arch = ApioArch.ICE40
                result.fpga_info.ice40.MergeFrom(
                    Ice40FpgaInfo(
                        type=pr.fpga_info["type"], pack=pr.fpga_info["pack"]
                    )
                )
            case "ecp5":
                result.arch = ApioArch.ECP5
                result.fpga_info.ecp5.MergeFrom(
                    Ecp5FpgaInfo(
                        type=pr.fpga_info["type"],
                        pack=pr.fpga_info["pack"],
                        speed=pr.fpga_info["speed"],
                    )
                )
            case "gowin":
                result.arch = ApioArch.GOWIN
                result.fpga_info.gowin.MergeFrom(
                    GowinFpgaInfo(family=pr.fpga_info["type"])
                )
            case _:
                cerror(f"Unexpected fpga_arch value {fpga_arch}")
                sys.exit(1)

        # -- We are done populating The FpgaInfo params..
        assert result.fpga_info.IsInitialized(), result

        # -- Populate the optional Verbosity params.
        if verbosity:
            result.verbosity.MergeFrom(verbosity)
            assert result.verbosity.IsInitialized(), result

        # -- Populate the Environment params.
        assert apio_ctx.platform_id, "Missing platform_id in apio context"
        oss_vars = apio_ctx.all_packages["oss-cad-suite"]["env"]["vars"]

        result.environment.MergeFrom(
            Environment(
                platform_id=apio_ctx.platform_id,
                is_windows=apio_ctx.is_windows,
                terminal_mode=(
                    FORCE_TERMINAL
                    if apio_console.is_terminal()
                    else FORCE_PIPE
                ),
                theme_name=apio_console.current_theme_name(),
                debug_level=util.debug_level(),
                yosys_path=oss_vars["YOSYS_LIB"],
                trellis_path=oss_vars["TRELLIS"],
                scons_shell_id=apio_ctx.scons_shell_id,
            )
        )
        assert result.environment.IsInitialized(), result

        # -- Populate the Project params.
        result.apio_env_params.MergeFrom(
            ApioEnvParams(
                env_name=apio_ctx.project.env_name,
                board_id=pr.board_id,
                top_module=project.get_str_option("top-module"),
                defines=apio_ctx.project.get_list_option(
                    "defines", default=[]
                ),
                yosys_synth_extra_options=apio_ctx.project.get_list_option(
                    "yosys-synth-extra-options", None
                ),
                nextpnr_extra_options=apio_ctx.project.get_list_option(
                    "nextpnr-extra-options", None
                ),
                constraint_file=apio_ctx.project.get_str_option(
                    "constraint-file", None
                ),
            )
        )
        assert result.apio_env_params.IsInitialized(), result

        # -- Populate the optional command specific params.
        if target_params:
            result.target.MergeFrom(target_params)
            assert result.target.IsInitialized(), result

        # -- All done.
        assert result.IsInitialized(), result
        return result

    def _run_scons_subprocess(
        self, scons_command: str, *, scons_params: SconsParams = None
    ):
        """Invoke an scons subprocess."""

        # pylint: disable=too-many-locals

        # -- Create a shortcut.
        apio_ctx = self.apio_ctx

        # -- Pass to the scons process the name of the sconstruct file it
        # -- should use.
        scons_dir = util.get_path_in_apio_package("scons")
        scons_file_path = scons_dir / "SConstruct"
        variables = ["-f", f"{scons_file_path}"]

        # -- Pass the path to the proto params file. The path is relative
        # -- to the project root.
        params_file_path = apio_ctx.env_build_path / "scons.params"
        variables += [f"params={str(params_file_path)}"]

        # -- Pass to the scons process the timestamp of the scons params we
        # -- pass via a file. This is for verification purposes only.
        variables += [f"timestamp={scons_params.timestamp}"]

        # -- We set the env variables also for a command such as 'clean'
        # -- which doesn't use the packages, to satisfy the required env
        # -- variables of the scons arg parser.
        apio_ctx.set_env_for_packages()

        if util.is_debug(1):
            cout("\nSCONS CALL:", style=EMPH3)
            cout(f"* command:       {scons_command}")
            cout(f"* variables:     {variables}")
            cout(f"* scons params: \n{scons_params}")
            cout()

        # -- Get the terminal width (typically 80)
        terminal_width, _ = shutil.get_terminal_size()

        # -- Read the time (for measuring how long does it take
        # -- to execute the apio command)
        start_time = time.time()

        # -- Subtracting 1 to avoid line overflow on windows, Observed with
        # -- Windows 10 and cmd.exe shell.
        if apio_ctx.is_windows:
            terminal_width -= 1

        # -- Print a horizontal line
        cout("-" * terminal_width)

        # -- Create the scons debug options. See details at
        # -- https://scons.org/doc/2.4.1/HTML/scons-man.html
        debug_options = (
            ["--debug=explain,prepare,stacktrace", "--tree=all"]
            if util.is_debug(1)
            else []
        )

        # -- Construct the scons command line.
        # --
        # -- sys.executable is resolved to the full path of the python
        # -- interpreter or to apio if running from a pyinstall setup.
        # -- See https://github.com/orgs/pyinstaller/discussions/9023 for more
        # -- information.
        # --
        # -- We use exec -m SCons instead of scones also for non pyinstaller
        # -- deployment in case the scons binary is not on the PATH.
        cmd = (
            [sys.executable, "-m", "apio", "--scons"]
            + ["-Q", scons_command]
            + debug_options
            + variables
        )

        # -- An output filter that manipulates the scons stdout/err lines as
        # -- needed and write them to stdout.
        scons_filter = SconsFilter(
            colors_enabled=apio_console.is_colors_enabled()
        )

        # -- Write the scons parameters to a temp file in the build
        # -- directory. It will be cleaned up as part of 'apio cleanup'.
        # -- At this point, the project is the current directory, even if
        # -- the command used the --project-dir option.
        os.makedirs(apio_ctx.env_build_path, exist_ok=True)
        with open(params_file_path, "w", encoding="utf8") as f:
            f.write(text_format.MessageToString(scons_params))

        if util.is_debug(1):
            cout(f"\nFull scons command: {cmd}\n\n")

        # -- Execute the scons builder!
        result = util.exec_command(
            cmd,
            stdout=util.AsyncPipe(scons_filter.on_stdout_line),
            stderr=util.AsyncPipe(scons_filter.on_stderr_line),
        )

        # -- Is there an error? True/False
        is_error = result.exit_code != 0

        # -- Calculate the time it took to execute the command
        duration = time.time() - start_time

        # -- Determine status message
        if is_error:
            styled_status = cstyle("ERROR", style=ERROR)
        else:
            styled_status = cstyle("SUCCESS", style=SUCCESS)

        # -- Determine the summary text
        summary = f"Took {duration:.2f} seconds"

        # -- Construct the entire message.
        styled_msg = f" [{styled_status}] {summary} "
        msg_len = len(cunstyle(styled_msg))

        # -- Determine the lengths of the paddings before and after
        # -- the message. Should be correct for odd and even terminal
        # -- widths.
        pad1_len = (terminal_width - msg_len) // 2
        pad2_len = terminal_width - pad1_len - msg_len

        # -- Print the entire line.
        cout(f"{'=' * pad1_len}{styled_msg}{'=' * pad2_len}")

        # -- Return the exit code
        return result.exit_code
