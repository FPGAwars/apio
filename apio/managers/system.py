"""Implementation of the Apio system commands"""

# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2019 FPGAwars
# -- Author Jesús Arroyo
# -- License GPLv2

import re
from typing import List
from apio.common.apio_console import cout
from apio.common.apio_styles import ERROR
from apio.utils import util, pkg_util
from apio.apio_context import ApioContext
from apio.managers import installer


class System:  # pragma: no cover
    """System class. Managing and execution of the system commands"""

    def __init__(self, apio_ctx: ApioContext):

        self.apio_ctx = apio_ctx

    def get_usb_devices(self) -> list:
        """Return a list of the connected USB devices
         This list is obtained by running the "lsusb" command

         * OUTPUT:  A list of objects with the usb devices
        Ex. [{'hwid':'1d6b:0003'}, {'hwid':'8087:0aaa'}, ...]

        It raises an exception in case of not being able to
        execute the "lsusb" command
        """

        # -- Initial empty usb devices list
        usb_devices = []

        # -- Run the "lsusb" command!
        result = self._run_command("lsusb", silent=True)

        if result.exit_code != 0:
            cout(result.out_text)
            cout(result.err_text, style=ERROR)
            raise RuntimeError("Error executing lsusb")

        # -- Get the list of the usb devices. It is read
        # -- from the command stdout
        # -- Ex: [{'hwid':'1d6b:0003'}, {'hwid':'04f2:b68b'}...]
        usb_devices = self._parse_usb_devices(result.out_text)

        # -- Return the devices
        return usb_devices

    def _run_command(
        self, command: str, *, silent: bool
    ) -> util.CommandResult:
        """Execute the given system command
        * INPUT:
          * command: Command to execute  (Ex. "lsusb")
          * silent: What to do with the command output
            * False --> Do not print on the console
            * True  --> Print on the console

        * OUTPUT: An ExecResult with the command's outcome.
        """

        # -- Check that the required package exists.
        # pkg_util.check_required_packages(self.apio_ctx, ["oss-cad-suite"])

        # -- Set system env for using the packages.
        installer.install_missing_packages_on_the_fly(self.apio_ctx)
        pkg_util.set_env_for_packages(self.apio_ctx, quiet=True)

        # TODO: Is this necessary or does windows accepts commands without
        # the '.exe' extension?
        if self.apio_ctx.is_windows:
            command = command + ".exe"

        # -- Set the stdout and stderr callbacks, when executing the command
        # -- Silent mode (True): No callback
        on_stdout = None if silent else self._on_stdout
        on_stderr = None if silent else self._on_stderr

        # -- Execute the command!
        result = util.exec_command(
            command,
            stdout=util.AsyncPipe(on_stdout),
            stderr=util.AsyncPipe(on_stderr),
        )

        # -- Return the result of the execution
        return result

    @staticmethod
    def _on_stdout(line):
        """Callback function. It is executed when the command prints
        information on the standard output
        """
        cout(line)

    @staticmethod
    def _on_stderr(line):
        """Callback function. It is executed when the command prints
        information on the standard error
        """
        cout(line, style=ERROR)

    @staticmethod
    def _parse_usb_devices(text: str) -> list[dict]:
        """Get a list of usb devices from the input string
        * INPUT: string that contains usb devices
            (Ex. "... 1d6b:0003 ... 8087:0aaa ...")
        * OUTPUT: A list of objects with the usb devices
          Ex. [{'hwid':'1d6b:0003'}, {'hwid':'8087:0aaa'}, ...]
        """

        # -- Build the regular expression for representing
        # -- patterns like '1d6b:0003'
        pattern = r"(?P<hwid>[a-f0-9]{4}:[a-f0-9]{4}?)\s"

        # -- Get the list of strings with that patter
        # -- Ex. ['1d6b:0003','8087:0aaa'...]
        hwids = re.findall(pattern, text)

        # -- Output empty list
        usb_devices: List[dict] = []

        # -- Build the list
        for hwid in hwids:

            # -- Create the Object with the hardware id
            usb_device = {"hwid": hwid}

            # -- Add the object to the output list
            usb_devices.append(usb_device)

        # -- Return the final list
        return usb_devices
