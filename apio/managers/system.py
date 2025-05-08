"""Implementation of the Apio system commands"""

# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2019 FPGAwars
# -- Author Jesús Arroyo
# -- License GPLv2

from dataclasses import dataclass
import re
import sys
from typing import List
from apio.common.apio_console import cout, cerror
from apio.common.apio_styles import INFO, ERROR, EMPH1
from apio.utils import util, pkg_util, snap_util
from apio.apio_context import ApioContext
from apio.managers import installer


@dataclass(frozen=True)
class FtdiDevice:
    """Class to represent a parsed FTDI device from lsftdi output."""

    ftdi_idx: int
    manufacturer: str
    description: str

    def __post_init__(self):
        assert isinstance(self.ftdi_idx, int)
        assert isinstance(self.manufacturer, str)
        assert isinstance(self.description, str)


class System:  # pragma: no cover
    """System class. Managing and execution of the system commands"""

    def __init__(self, apio_ctx: ApioContext):

        self.apio_ctx = apio_ctx

    def _lsftdi_fatal_error(self, result: util.CommandResult) -> None:
        """Handles a failure of a 'lsftdi' command. Print message and exits."""
        #
        assert result.exit_code != 0, result
        cout(result.out_text)
        cerror("The 'lsftdi' command failed.", result.err_text)

        # -- Hint the user about the need to install driver.
        cout(
            "[Hint]: Some platforms require ftdi driver installation "
            "using 'apio drivers install ftdi'.",
            style=INFO,
        )
        if snap_util.is_snap():
            cout(
                "[Hint]: Snap applications may require "
                "'snap connect apio:raw-usb' to access USB devices.",
                style=INFO,
            )

        # -- Exit with an error code.
        sys.exit(1)

    def lsusb(self) -> int:
        """Run the lsusb command. Returns exit code."""

        result = self._run_command("lsusb", silent=False)

        return result.exit_code if result else 1

    def lsftdi(self) -> int:
        """Runs the lsftdi command. Returns exit code."""

        result = self._run_command("lsftdi", silent=True)

        if result.exit_code != 0:
            # -- Print error message and exit.
            self._lsftdi_fatal_error(result)

        cout(result.out_text)
        return 0

    def lsserial(self) -> int:
        """List the serial ports. Returns exit code."""

        serial_ports = util.get_serial_ports()
        cout(f"Number of Serial devices found: {len(serial_ports)}")

        for serial_port in serial_ports:
            port = serial_port.get("port")
            description = serial_port.get("description")
            hwid = serial_port.get("hwid")
            cout(port, style=EMPH1)
            cout(f"Description: {description}")
            cout(f"Hardware info: {hwid}\n")

        return 0

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

    def get_ftdi_devices(self) -> List[FtdiDevice]:
        """Return a list of the connected FTDI devices
         This list is obtained by running the "lsftdi" command

        It raises an exception if the command lsftdi fails.
        """

        # -- Initial empty ftdi devices list
        ftdi_devices = []

        # -- Run the "lsftdi" command.
        result = self._run_command("lsftdi", silent=True)

        # -- Exit if error.
        if result.exit_code != 0:
            self._lsftdi_fatal_error(result)

        # -- Extract the list of FTDI devices from the command output
        ftdi_devices: List[FtdiDevice] = self._parse_lsftdi_devices(
            result.out_text
        )

        # -- Return the devices
        return ftdi_devices

        # -- Print error message and exit.

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
    def _parse_usb_devices(text: str) -> list:
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
        usb_devices = []

        # -- Build the list
        for hwid in hwids:

            # -- Create the Object with the hardware id
            usb_device = {"hwid": hwid}

            # -- Add the object to the output list
            usb_devices.append(usb_device)

        # -- Return the final list
        return usb_devices

    @staticmethod
    def _parse_lsftdi_devices(text: str) -> List[FtdiDevice]:
        """Get a list of FTDI devices from the output text of lsftdi."""

        # -- Dump for debugging.
        if util.is_debug():
            cout(f"lsftdi text:\n{text}")

        num_pattern = r"Number\sof\sFTDI\sdevices\sfound:\s(?P<n>\d+?)\n"
        match = re.search(num_pattern, text)
        num = int(match.group("n")) if match else 0

        # -- NOTE: Since the information of each device is spread over two
        # -- lines, we extract the information by field rather than by device
        # -- line. It's awkward, but it works.

        # TODO: Change the output format from a list of dicts to a list of
        # dataclass objects. Motivation is code quality.

        index_pattern = r".*Checking\sdevice:\s(?P<index>.*?)\n.*"
        indices = re.findall(index_pattern, text)

        manufacturer_pattern = r".*Manufacturer:\s(?P<n>.*?),.*"
        manufacturers = re.findall(manufacturer_pattern, text)

        description_pattern = r".*Description:\s(?P<n>.*?)\n.*"
        descriptions = re.findall(description_pattern, text)

        # -- Dump for debugging.
        if util.is_debug():
            cout(f"Parsed num: {num}")
            cout(f"Parsed indices: {indices}")
            cout(f"Parsed manufacturers: {manufacturers}")
            cout(f"Parsed descriptions: {descriptions}")
            cout()

        # -- Sanity checks.
        assert num == len(indices), f"{num} != {len(indices)}"
        assert num == len(manufacturers), f"{num} != {len(manufacturers)}"
        assert num == len(descriptions), f"{num} != {len(descriptions)}"

        # -- Create the list of FTDI devices.
        ftdi_devices = []
        for i in range(num):
            ftdi_device = FtdiDevice(
                ftdi_idx=int(indices[i]),
                manufacturer=manufacturers[i],
                description=descriptions[i],
            )
            ftdi_devices.append(ftdi_device)

            # -- Dump the device info if in debug mode..
            if util.is_debug():
                cout(f"FTDI device: {ftdi_device}")

        return ftdi_devices
