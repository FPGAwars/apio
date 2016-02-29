# Rules icestick class

import subprocess

from os.path import join, dirname, isfile

from ..util import get_systype

platform = get_systype()


class DriverInstaller(object):

    rules_local_path = join(dirname(__file__), '80-icestick.rules')
    rules_system_path = '/etc/udev/rules.d/80-icestick.rules'

    def install(self):
        if 'linux' in platform:
            self._install_linux()
        elif 'darwin' in platform:
            self._install_darwin()
        elif 'windows' in platform:
            self._install_windows()

    def uninstall(self):
        if 'linux' in platform:
            self._uninstall_linux()
        elif 'darwin' in platform:
            self._uninstall_darwin()
        elif 'windows' in platform:
            self._uninstall_windows()

    def _install_linux(self):
        print('Install icestick.rules')
        if not isfile(self.rules_system_path):
            subprocess.call(['sudo', 'cp', self.rules_local_path, self.rules_system_path])
        else:
            print('Package icestick.rules is already the newest version')

    def _uninstall_linux(self):
        if isfile(self.rules_system_path):
            print('Uninstall package icestick.rules')
            subprocess.call(['sudo', 'rm', self.rules_system_path])
        else:
            print('Package icestick.rules is not installed')

    def _install_darwin(self):
        # TODO: return if brew is not installed
        subprocess.call(['brew', 'install', 'libftdi0'])
        subprocess.call(['sudo', 'kextunload', '-b', 'com.FTDI.driver.FTDIUSBSerialDriver'])
        subprocess.call(['sudo', 'kextunload', '-b', 'com.apple.driver.AppleUSBFTDI'])

    def _uninstall_darwin(self):
        pass

    def _install_windows(self):
        pass

    def _uninstall_windows(self):
        pass
