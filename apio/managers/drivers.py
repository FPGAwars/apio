# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2019 FPGAwars
# -- Author Jesús Arroyo
# -- License GPLv2
"""Manage board drivers"""


import os
import shutil
import subprocess
from pathlib import Path
from apio.utils import util
from apio.common.apio_console import cout, cerror, cprint
from apio.common.styles import INFO, SUCCESS, EMPH3
from apio.apio_context import ApioContext
from apio.managers import installer

# -- Style shortcuts
E3 = f"[{EMPH3}]"

# -- Text in the markdown format of the python rich library.
FTDI_INSTALL_INSTRUCTIONS_WINDOWS = f"""
Please follow these steps:

  1. Make sure your FPGA board is connected to the computer.

  2. Accept the Zadig request to make changes to your computer.

  3. Find the Zadig window on your screen.

  4. Select your FPGA board from the drop down list, For example
    'Alhambra II v1.0A - B09-335 (Interface 0)'.

    {E3}IMPORTANT - \
    If your board appears multiple time, select the 'interface 0' entry.[/]

  5. Make sure that 'WinUSB' is selected. For example
     'WinUSB (v6.1.7600.16385)'.

  6. Click the 'Replace Driver' button and wait for a successful
     completion, this can take a minute or two.

  7. Close the Zadig window.

  8. Disconnect and reconnect your FPGA board for the new driver
     to take affect.

  9. Run the command 'apio system lsftdi' and verify that
     your board is listed.
"""

# -- Text in the markdown format of the python rich library.
FTDI_UNINSTALL_INSTRUCTIONS_WINDOWS = f"""
Please follow these steps:

  1. Make sure your FPGA board is NOT connected to the computer.

  2. If asked, allow the Device Manager to make changes to your system.

  3. Find the Device Manager window.

  4. Connect the board to your computer and a new entry will be added
     to the device list (though sometimes it may be collapsed and
     hidden).

  5. Identify the entry of your board (e.g. in the 'Universal Serial
     Bus Devices' section).

     {E3}NOTE: Boards with FT2232 ICs have two channels, 'interface 0'
     and 'interface 1'. Here we care only about 'interface 0' and
     ignore 'interface 1' if it appears as a COM port.[/]

  6. Right click on your board entry and select 'Uninstall device'.

  7. If available, check the box 'Delete the driver software for this
     device'.

  8. Click the 'Uninstall' button.

  9. Close the Device Manager window.
"""

# -- Text in the markdown format of the python rich library.
SERIAL_INSTALL_INSTRUCTIONS_WINDOWS = """
Please follow these steps:

  1. Make sure your FPGA board is connected to the computer.

  2. Accept the Serial Installer request to make changes to your computer.

  3. Find the Serial installer window and follow the instructions.

  4. To verify, disconnect and reconnect the board and run the command
      'apio system lsserial'.
"""

# -- Text in the markdown format of the python rich library.
SERIAL_UNINSTALL_INSTRUCTIONS_WINDOWS = f"""
Please follow these steps:

  1. Make sure your FPGA board is NOT connected to the computer.

  2. If asked, allow the Device Manager to make changes to your system.

  3. Find the Device Manager window.

  4. Connect the board to your computer and a new entry will be added
     to the device list (though sometimes it may be collapsed).

  5. Identify the entry of your board (typically in the Ports section).

     {E3} NOTE: If your board does not show up as a COM port, it may not
     have the 'apio drivers --serial-install' applied to it.[/]

  6. Right click on your board entry and select 'Uninstall device'.

  7. If available, check the box 'Delete the driver software for this device'.

  8. Click the 'Uninstall' button.

  9. Close the Device Manager window.
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

    def pre_upload(self):
        """Operations to do before uploading a design
        Only for mac platforms"""

        if self.apio_ctx.is_darwin:
            self._pre_upload_darwin()

    def post_upload(self):
        """Operations to do after uploading a design
        Only for mac platforms"""

        if self.apio_ctx.is_darwin:
            self._post_upload_darwin()

    def _ftdi_install_linux(self) -> int:
        """Drivers install on Linux. It copies the .rules file into
        the corresponding folder. Return process exit code."""

        cout("Configure FTDI drivers for FPGA")

        # -- Check if the target rules file already exists
        if not self.ftdi_rules_system_path.exists():

            # -- The file does not exist. Copy!
            # -- Execute the cmd: sudo cp src_file target_file
            subprocess.call(
                [
                    "sudo",
                    "cp",
                    str(self.ftdi_rules_local_path),
                    str(self.ftdi_rules_system_path),
                ]
            )

            # -- Execute the commands for reloading the udev system
            self._reload_rules_linux()

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

            # -- Execute the sudo rm rules_file command
            subprocess.call(["sudo", "rm", str(self.ftdi_rules_system_path)])

            # -- # -- Execute the commands for reloading the udev system
            self._reload_rules_linux()

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
            # -- Add the user to the dialout group for
            # -- having access to the serial port
            group_added = self._add_dialout_group_linux()

            # -- The file does not exist. Copy!
            # -- Execute the cmd: sudo cp src_file target_file
            subprocess.call(
                [
                    "sudo",
                    "cp",
                    str(self.serial_rules_local_path),
                    str(self.serial_rules_system_path),
                ]
            )

            # -- Execute the commands for reloading the udev system
            self._reload_rules_linux()

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

            # -- Execute the sudo rm rule_file cmd
            subprocess.call(["sudo", "rm", str(self.serial_rules_system_path)])

            # -- Execute the commands for reloading the udev system
            self._reload_rules_linux()
            cout("Serial drivers uninstalled", style=SUCCESS)
            cout("Unplug and reconnect your board", style=INFO)
        else:
            cout("Already uninstalled", style=INFO)

        return 0

    def _reload_rules_linux(self):
        """Execute the commands for reloading the udev system"""

        # -- These are Linux commands that should be executed on
        # -- the shell
        subprocess.call(["sudo", "udevadm", "control", "--reload-rules"])
        subprocess.call(["sudo", "udevadm", "trigger"])
        subprocess.call(["sudo", "service", "udev", "restart"])

    def _add_dialout_group_linux(self):
        """Add the current user to the dialout group on Linux systems"""

        # -- This operation is needed for granting access to the serial port

        # -- Get the current groups of the user
        groups = subprocess.check_output("groups")

        # -- If it does not belong to the dialout group, add it!!
        if "dialout" not in groups.decode():
            # -- Command for adding the user to the dialout group
            subprocess.call("sudo usermod -a -G dialout $USER", shell=True)
            return True
        return None

    def _ftdi_install_darwin(self) -> int:
        """Installs FTDI driver on darwin. Returns process status code."""
        # Check homebrew
        brew = subprocess.call("which brew > /dev/null", shell=True)
        if brew != 0:
            cerror("Homebrew is required")
            return 1

        cout("Install FTDI drivers for FPGA")
        subprocess.call(["brew", "update"])
        self._brew_install_darwin("libffi")
        self._brew_install_darwin("libftdi")
        self.apio_ctx.profile.add_setting("macos_ftdi_drivers", True)
        cout("FTDI drivers installed", style=SUCCESS)
        return 0

    def _ftdi_uninstall_darwin(self):
        """Uninstalls FTDI driver on darwin. Returns process status code."""
        cout("Uninstall FTDI drivers configuration")
        self.apio_ctx.profile.add_setting("macos_ftdi_drivers", False)
        cout("FTDI drivers uninstalled", style=SUCCESS)
        return 0

    def _serial_install_darwin(self):
        """Installs serial driver on darwin. Returns process status code."""
        # Check homebrew
        brew = subprocess.call("which brew > /dev/null", shell=True)
        if brew != 0:
            cerror("Homebrew is required")
            return 1

        cout("Install Serial drivers for FPGA")
        subprocess.call(["brew", "update"])
        self._brew_install_darwin("libffi")
        self._brew_install_darwin("libusb")
        # self._brew_install_serial_drivers_darwin()
        cout("Serial drivers installed", style=SUCCESS)
        return 0

    def _serial_uninstall_darwin(self):
        """Uninstalls serial driver on darwin. Returns process status code."""
        cout("Uninstall Serial drivers configuration")
        cout("Serial drivers uninstalled", style=SUCCESS)
        return 0

    def _brew_install_darwin(self, brew_package):
        subprocess.call(["brew", "install", "--force", brew_package])
        subprocess.call(["brew", "unlink", brew_package])
        subprocess.call(["brew", "link", "--force", brew_package])

    # def _brew_install_serial_drivers_darwin(self):
    #     subprocess.call(
    #         [
    #             "brew",
    #             "tap",
    #             "mengbo/ch340g-ch34g-ch34x-mac-os-x-driver",
    #             "https://github.com/mengbo/ch340g-ch34g-ch34x-mac-os-x-driver",
    #         ]
    #     )
    #     subprocess.call(
    #         ["brew", "cask", "install", "wch-ch34x-usb-serial-driver"]
    #     )

    def _pre_upload_darwin(self):
        if self.apio_ctx.profile.settings.get("macos_ftdi_drivers", False):
            # Check and unload the drivers
            driver_a = "com.FTDI.driver.FTDIUSBSerialDriver"
            driver_b = "com.apple.driver.AppleUSBFTDI"
            if self._check_ftdi_driver_darwin(driver_a):
                subprocess.call(["sudo", "kextunload", "-b", driver_a])
                self.driver_c = driver_a
            elif self._check_ftdi_driver_darwin(driver_b):
                subprocess.call(["sudo", "kextunload", "-b", driver_b])
                self.driver_c = driver_b

    def _post_upload_darwin(self):
        if self.apio_ctx.profile.settings.get("macos_ftdi_drivers", False):
            # Restore previous driver configuration
            if self.driver_c:
                subprocess.call(["sudo", "kextload", "-b", self.driver_c])

    def _check_ftdi_driver_darwin(self, driver):
        return driver in str(subprocess.check_output(["kextstat"]))

    # W0703: Catching too general exception Exception (broad-except)
    # pylint: disable=W0703
    def _ftdi_install_windows(self) -> int:
        # -- Check that the required packages are installed.
        installer.install_missing_packages_on_the_fly(self.apio_ctx)

        # -- Get the drivers apio package base folder
        drivers_base_dir = self.apio_ctx.get_package_dir("drivers")

        # -- Path to the zadig.ini file
        # -- It is the zadig config file
        zadig_ini_src = drivers_base_dir / "share" / "zadig.ini"
        zadig_ini_dst = Path("zadig.ini")

        # -- copy the zadig.ini file to the current working folder
        # -- so that zadig open it when executed
        shutil.copyfile(zadig_ini_src, zadig_ini_dst)

        # -- Zadig exe file with full path:
        zadig_exe = drivers_base_dir / "bin" / "zadig.exe"

        # -- Show messages for the user
        cout(
            "\nStarting the interactive config tool zadig.exe.", style=SUCCESS
        )
        cprint(FTDI_INSTALL_INSTRUCTIONS_WINDOWS)

        # -- Execute zadig!
        # -- We execute it using os.system() rather than by
        # -- util.exec_command() because zadig required permissions
        # -- elevation.
        exit_code = os.system(str(zadig_exe))
        cout("FTDI drivers configuration finished", style=SUCCESS)

        # -- Remove zadig.ini from the current folder. It is no longer
        # -- needed
        if zadig_ini_dst.exists():
            zadig_ini_dst.unlink()

        return exit_code

    def _ftdi_uninstall_windows(self) -> int:
        # -- Check that the required packages exist.
        installer.install_missing_packages_on_the_fly(self.apio_ctx)

        cout("\nStarting the interactive Device Manager.", style=SUCCESS)
        cprint(FTDI_UNINSTALL_INSTRUCTIONS_WINDOWS)

        # -- We launch the device manager using os.system() rather than with
        # -- util.exec_command() because util.exec_command() does not support
        # -- elevation.
        exit_code = os.system("mmc devmgmt.msc")
        return exit_code

    # W0703: Catching too general exception Exception (broad-except)
    # pylint: disable=W0703
    def _serial_install_windows(self) -> int:
        # -- Check that the required packages exist.
        installer.install_missing_packages_on_the_fly(self.apio_ctx)

        drivers_base_dir = self.apio_ctx.get_package_dir("drivers")
        drivers_bin_dir = drivers_base_dir / "bin"

        cout("\nStarting the interactive Serial Installer.", style=SUCCESS)
        cprint(SERIAL_INSTALL_INSTRUCTIONS_WINDOWS)

        # -- We launch the device manager using os.system() rather than with
        # -- util.exec_command() because util.exec_command() does not support
        # -- elevation.
        exit_code = os.system(
            str(Path(drivers_bin_dir) / "serial_install.exe")
        )

        return exit_code

    def _serial_uninstall_windows(self) -> int:
        # -- Check that the required packages exist.
        installer.install_missing_packages_on_the_fly(self.apio_ctx)

        cout("\nStarting the interactive Device Manager.", style=SUCCESS)
        cprint(SERIAL_UNINSTALL_INSTRUCTIONS_WINDOWS)

        # -- We launch the device manager using os.system() rather than with
        # -- util.exec_command() because util.exec_command() does not support
        # -- elevation.
        exit_code = os.system("mmc devmgmt.msc")
        return exit_code
