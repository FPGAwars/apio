# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2019 FPGAwars
# -- Author Jesús Arroyo
# -- License GPLv2
"""Manage board drivers"""


import getpass
import os
import shlex
import shutil
import subprocess
from pathlib import Path
from apio.utils import util
from apio.common.apio_console import cout, cerror, cmarkdown
from apio.common.apio_styles import INFO, SUCCESS, EMPH1, EMPH3
from apio.apio_context import ApioContext


# -- Style shortcuts
E1 = f"[{EMPH1}]"
E3 = f"[{EMPH3}]"

# -- A message to print when trying to install/uninstall apio drivers
# -- on platforms that don't require it.
NO_DRIVERS_MSG = "No driver installation is required on this platform."

# -- Text in the rich-text format of the python rich library.
FTDI_INSTALL_INSTRUCTIONS_WINDOWS = f"""
{E3}Please follow these steps:[/]

  1. Make sure your {E1}FPGA board is connected[/] to the computer.

  2. {E1}Accept the Zadig request[/] to make changes to your computer.

  3. {E1}Find the Zadig window[/] on your screen. You may need to click
    on its icon in the task bar for it to appear.

  4. {E1}Select your FPGA board[/] from the drop down list, For example
    'Alhambra II v1.0A - B09-335 (Interface 0)'.

  {E3}VERY IMPORTANT - If your board appears multiple time, make sure
  to select its 'interface 0' entry.[/]

  5. {E1}Select the 'WinUSB' driver[/] as the target driver. For example
     'WinUSB (v6.1.7600.16385)'.

  6. {E1}Click 'Replace Driver'[/] and wait for a successful
     completion, this can take a minute or two.

  7. {E1}Close the Zadig window.[/]

  8. {E1}Disconnect and reconnect[/] your FPGA board for the new driver
     to take affect.

  9. {E1}Run the command 'apio devices scan-usb'[/] and verify that
     your board is listed.
"""

# -- Text in the rich-text format of the python rich library.
FTDI_UNINSTALL_INSTRUCTIONS_WINDOWS = f"""
{E3}Please follow these steps:[/]

  1. Make sure your FPGA {E1}board is NOT connected[/] to the computer.

  2. If asked, {E1}allow the Device Manager to make changes to your system.[/]

  3. {E1}Find the Device Manager window.[/]

  4. {E1}Connect the board[/] to your computer and a new entry will be added
     to the device list (though sometimes it may be collapsed and
     hidden).

  5. {E1}Identify the entry of your board[/] (e.g. in the 'Universal Serial
     Bus Devices' section).

     {E3}NOTE: Boards with FT2232 ICs have two channels, 'interface 0'
     and 'interface 1'. Here we care only about 'interface 0' and
     ignore 'interface 1' if it appears as a COM port.[/]

  6. {E1}Right click[/] on your board entry and \
{E1}select 'Uninstall device'.[/]

  7. If available, check the box {E1}'Delete the driver software for this
     device'.[/]

  8. Click the {E1}'Uninstall' button[/].

  9. {E1}Close[/] the Device Manager window.
"""

# -- Text in the rich-text format of the python rich library.
SERIAL_INSTALL_INSTRUCTIONS_WINDOWS = f"""
{E3}Please follow these steps:[/]

  1. Make sure your FPGA {E1}board is connected[/] to the computer.

  2. {E1}Accept the Serial Installer request[/] to make changes to your \
computer.

  3. Find the Serial installer window and {E1}follow the instructions.[/]

  4. To verify, {E1}disconnect and reconnect the board[/] and run the command
      {E1}'apio devices scan-serial'.[/]
"""

# -- Text in the rich-text format of the python rich library.
SERIAL_UNINSTALL_INSTRUCTIONS_WINDOWS = f"""
{E3}Please follow these steps:[/]

  1. Make sure your FPGA {E1}board is NOT connected[/] to the computer.

  2. If asked, {E1}allow the Device Manager to make changes[/] to your system.

  3. {E1}Find the Device Manager window.[/]

  4. {E1}Connect the board[/] to your computer and a new entry will be added
     to the device list (though sometimes it may be collapsed).

  5. {E1}Identify the entry of your board[/] (typically in the Ports section).

     {E3} NOTE: If your board does not show up as a COM port, it may not
     have the 'apio drivers --serial-install' applied to it.[/]

  6. {E1}Right click[/] on your board entry \
and {E1}select 'Uninstall device'.[/]

  7. If available, check the box \
{E1}'Delete the driver software for this device'.[/]

  8. Click the {E1}'Uninstall' button.[/]

  9. {E1}Close the Device Manager window.[/]
"""


class Drivers:
    """Class for managing the board drivers"""

    # -- The driver installation on linux consist of copying the rule files
    # -- to the /etc/udev/rules.d folder

    # -- FTDI source rules file paths
    resources_dir = util.get_path_in_apio_package("resources")
    ftdi_rules_local_path = resources_dir / "80-fpga-ftdi.rules"

    # -- Target rule file
    ftdi_rules_system_path = Path("/etc/udev/rules.d/80-fpga-ftdi.rules")

    # Serial rules files paths
    serial_rules_local_path = resources_dir / "80-fpga-serial.rules"
    serial_rules_system_path = Path("/etc/udev/rules.d/80-fpga-serial.rules")

    # Driver to restore: mac os
    driver_c = ""

    def __init__(self, apio_ctx: ApioContext) -> None:

        self.apio_ctx = apio_ctx

    def ftdi_install(self) -> int:
        """Installs the FTDI driver. Function is platform dependent.
        Returns a process exit code.
        """

        if self.apio_ctx.is_linux:
            return self._ftdi_install_linux()

        if self.apio_ctx.is_darwin:
            return self._ftdi_install_darwin()

        if self.apio_ctx.is_windows:
            return self._ftdi_install_windows()

        cerror(f"Unknown platform type '{self.apio_ctx.platform_id}'.")
        return 1

    def ftdi_uninstall(self) -> int:
        """Uninstalls the FTDI driver. Function is platform dependent.
        Returns a process exit code.
        """
        if self.apio_ctx.is_linux:
            return self._ftdi_uninstall_linux()

        if self.apio_ctx.is_darwin:
            return self._ftdi_uninstall_darwin()

        if self.apio_ctx.is_windows:
            return self._ftdi_uninstall_windows()

        cerror(f"Unknown platform '{self.apio_ctx.platform_id}'.")
        return 1

    def serial_install(self) -> int:
        """Installs the serial driver. Function is platform dependent.
        Returns a process exit code.
        """

        if self.apio_ctx.is_linux:
            return self._serial_install_linux()

        if self.apio_ctx.is_darwin:
            return self._serial_install_darwin()

        if self.apio_ctx.is_windows:
            return self._serial_install_windows()

        cerror(f"Unknown platform '{self.apio_ctx.platform_id}'.")
        return 1

    def serial_uninstall(self) -> int:
        """Uninstalls the serial driver. Function is platform dependent.
        Returns a process exit code.
        """
        if self.apio_ctx.is_linux:
            return self._serial_uninstall_linux()

        if self.apio_ctx.is_darwin:
            return self._serial_uninstall_darwin()

        if self.apio_ctx.is_windows:
            return self._serial_uninstall_windows()

        cerror(f"Unknown platform '{self.apio_ctx.platform_id}'.")
        return 1

    def _ftdi_install_linux(self) -> int:
        """Drivers install on Linux. It copies the .rules file into
        the corresponding folder. Return process exit code."""

        cout("Configure FTDI drivers for FPGA")

        # -- Check if the target rules file already exists
        if not self.ftdi_rules_system_path.exists():

            # -- Copy the rules file and reload udev, all in ONE sudo
            # -- invocation (a single password prompt).
            steps = [
                (
                    "cp "
                    f"{shlex.quote(str(self.ftdi_rules_local_path))} "
                    f"{shlex.quote(str(self.ftdi_rules_system_path))}",
                    "install the FTDI udev rules file",
                ),
            ] + self._udev_reload_steps()
            exit_code = self._sudo_steps_linux(steps)
            if exit_code != 0:
                return exit_code

            cout("FTDI drivers installed", style=SUCCESS)
            cout("Unplug and reconnect your board", style=INFO)
        else:
            cout("Already installed", style=INFO)

        return 0

    def _ftdi_uninstall_linux(self):
        """Uninstall the FTDI drivers on linux. Returns process exist code."""

        # -- For disabling the FTDI driver the .rules files should be
        # -- removed from the /etc/udev/rules.d/ folder

        # -- Remove the .rules file, if it exists
        if self.ftdi_rules_system_path.exists():
            cout("Revert FTDI drivers configuration")

            # -- Remove the rules file and reload udev in ONE sudo call.
            steps = [
                (
                    f"rm {shlex.quote(str(self.ftdi_rules_system_path))}",
                    "remove the FTDI udev rules file",
                ),
            ] + self._udev_reload_steps()
            exit_code = self._sudo_steps_linux(steps)
            if exit_code != 0:
                return exit_code

            cout("FTDI drivers uninstalled", style=SUCCESS)
            cout("Unplug and reconnect your board", style=INFO)
        else:
            cout("Already uninstalled", style=INFO)

        return 0

    def _serial_install_linux(self):
        """Serial drivers install on Linux. Returns process exit code."""

        cout("Configure Serial drivers for FPGA")

        # -- Check if the target rules file already exists
        if not self.serial_rules_system_path.exists():
            steps = []

            # -- Add the user to the dialout group for having access to the
            # -- serial port, if not a member yet.
            group_added = self._needs_dialout_group_linux()
            if group_added:
                steps.append(
                    (
                        "usermod -a -G dialout "
                        f"{shlex.quote(getpass.getuser())}",
                        "add the user to the dialout group",
                    )
                )

            # -- Copy the rules file and reload udev; everything runs in
            # -- ONE sudo invocation (a single password prompt).
            steps += [
                (
                    "cp "
                    f"{shlex.quote(str(self.serial_rules_local_path))} "
                    f"{shlex.quote(str(self.serial_rules_system_path))}",
                    "install the serial udev rules file",
                ),
            ] + self._udev_reload_steps()
            exit_code = self._sudo_steps_linux(steps)
            if exit_code != 0:
                return exit_code

            cout("Serial drivers installed", style=SUCCESS)
            cout("Unplug and reconnect your board", style=INFO)
            if group_added:
                cout(
                    "Restart your machine to install the dialout group",
                    style=INFO,
                )
        else:
            cout("Already installed", style=INFO)

        return 0

    def _serial_uninstall_linux(self) -> int:
        """Uninstall the serial driver on Linux. Return process exit code."""

        # -- For disabling the serial driver the corresponding .rules file
        # -- should be removed, it it exists
        if self.serial_rules_system_path.exists():
            cout("Revert Serial drivers configuration")

            # -- Remove the rules file and reload udev in ONE sudo call.
            steps = [
                (
                    f"rm {shlex.quote(str(self.serial_rules_system_path))}",
                    "remove the serial udev rules file",
                ),
            ] + self._udev_reload_steps()
            exit_code = self._sudo_steps_linux(steps)
            if exit_code != 0:
                return exit_code

            cout("Serial drivers uninstalled", style=SUCCESS)
            cout("Unplug and reconnect your board", style=INFO)
        else:
            cout("Already uninstalled", style=INFO)

        return 0

    # -- Exit code of the first step of a _sudo_steps_linux() script; the
    # -- following steps use consecutive codes. High enough to not collide
    # -- with sudo's own exit codes (1 = auth failure).
    _FIRST_STEP_EXIT_CODE = 10

    def _sudo_steps_linux(self, steps) -> int:
        """Run the given root steps as a SINGLE sudo invocation, so the
        user is prompted for the password at most once. 'steps' is a list
        of (shell_command, action_description) tuples; each command gets a
        distinct exit code so a failure is reported precisely (their
        stderr also reaches the console). Returns the process exit code,
        0 on success."""

        cout(
            "This one-time setup needs administrator privileges "
            "(a single sudo prompt)",
            style=INFO,
        )

        # -- Build 'cmd1 || exit 10; cmd2 || exit 11; ...'
        script = "; ".join(
            f"{cmd} || exit {self._FIRST_STEP_EXIT_CODE + i}"
            for i, (cmd, _) in enumerate(steps)
        )
        exit_code = subprocess.call(["sudo", "sh", "-c", script])
        if exit_code == 0:
            return 0

        # -- Map the exit code back to the step that failed.
        step = exit_code - self._FIRST_STEP_EXIT_CODE
        if 0 <= step < len(steps):
            cerror(f"Failed to {steps[step][1]}.")
        else:
            # -- sudo itself failed (wrong password, no sudo rights, ...)
            cerror("Could not get administrator privileges (sudo failed).")
        return exit_code

    def _udev_reload_steps(self):
        """The root steps for reloading the udev rules, for
        _sudo_steps_linux(). Restarting the udev daemon is NOT needed for
        rule changes and the legacy unit name it used ('udev') only exists
        on distros with the Debian/Ubuntu compat alias (issue #899 on
        other distros: "Failed to restart udev.service: Unit udev.service
        not found")."""

        return [
            ("udevadm control --reload-rules", "reload the udev rules"),
            (
                "udevadm trigger",
                "apply the udev rules to the connected devices",
            ),
        ]

    def _needs_dialout_group_linux(self):
        """True if the user must be added to the dialout group (needed for
        access to the serial port)."""

        # -- Get the current groups of the user
        groups = subprocess.check_output("groups")

        # -- True if it does not belong to the dialout group yet.
        return "dialout" not in groups.decode()

    def _ftdi_install_darwin(self) -> int:
        """Installs FTDI driver on darwin. Returns process status code."""
        # Check homebrew
        cout(NO_DRIVERS_MSG, style=SUCCESS)
        return 0

    def _ftdi_uninstall_darwin(self):
        """Uninstalls FTDI driver on darwin. Returns process status code."""
        cout(NO_DRIVERS_MSG, style=SUCCESS)
        return 0

    def _serial_install_darwin(self):
        """Installs serial driver on darwin. Returns process status code."""
        cout(NO_DRIVERS_MSG, style=SUCCESS)
        return 0

    def _serial_uninstall_darwin(self):
        """Uninstalls serial driver on darwin. Returns process status code."""
        cout(NO_DRIVERS_MSG, style=SUCCESS)
        return 0

    def _ftdi_install_windows(self) -> int:

        # -- Get the drivers apio package base folder
        drivers_base_dir = self.apio_ctx.get_package_dir("drivers")

        # NOTE: Zadig documentation:
        # https://github.com/pbatard/libwdi/wiki/Zadig?utm_source=chatgpt.com

        # -- Path to the config file zadig.ini.
        zadig_ini_src = drivers_base_dir / "share" / "zadig.ini"

        # -- Execute in a tmp directory, this way we don't contaminate the
        # -- current with zadig.ini, in case the program crashes.
        # -- Using a fix tmp location prevents accumulation of leftover
        # -- zadig.ini in case the are not cleaned up properly.
        # -- We can't store zadig under _build since we don't necessarily
        # -- run in a context of a project..
        with util.pushd(self.apio_ctx.get_tmp_dir()):
            # -- Bring a copy of zadig.ini
            shutil.copyfile(zadig_ini_src, "zadig.ini")

            # -- Zadig exe file with full path:
            zadig_exe = drivers_base_dir / "bin" / "zadig.exe"

            # -- Show messages for the user
            cout("", "Launching zadig.exe.")
            cmarkdown(FTDI_INSTALL_INSTRUCTIONS_WINDOWS)

            # -- Execute zadig!
            # -- We execute it using os.system() rather than by
            # -- util.exec_command() because zadig required permissions
            # -- elevation.
            exit_code = os.system(str(zadig_exe))

            # -- All done.
            return exit_code

    def _ftdi_uninstall_windows(self) -> int:
        # -- Check that the required packages exist.
        # packages.install_missing_packages_on_the_fly(
        #     self.apio_ctx.packages_context
        # )

        cout("", "Launching the interactive Device Manager.")
        cmarkdown(FTDI_UNINSTALL_INSTRUCTIONS_WINDOWS)

        # -- We launch the device manager using os.system() rather than with
        # -- util.exec_command() because util.exec_command() does not support
        # -- elevation.
        exit_code = os.system("mmc devmgmt.msc")
        return exit_code

    def _serial_install_windows(self) -> int:

        drivers_base_dir = self.apio_ctx.get_package_dir("drivers")
        drivers_bin_dir = drivers_base_dir / "bin"

        cout("", "Launching the interactive Serial Installer.")
        cmarkdown(SERIAL_INSTALL_INSTRUCTIONS_WINDOWS)

        # -- We launch the device manager using os.system() rather than with
        # -- util.exec_command() because util.exec_command() does not support
        # -- elevation.
        exit_code = os.system(
            str(Path(drivers_bin_dir) / "serial_install.exe")
        )

        return exit_code

    def _serial_uninstall_windows(self) -> int:

        cout("", "Launching the interactive Device Manager.")
        cmarkdown(SERIAL_UNINSTALL_INSTRUCTIONS_WINDOWS)

        # -- We launch the device manager using os.system() rather than with
        # -- util.exec_command() because util.exec_command() does not support
        # -- elevation.
        exit_code = os.system("mmc devmgmt.msc")
        return exit_code
