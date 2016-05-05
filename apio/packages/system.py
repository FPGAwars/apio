# System class

from os import rename
from os.path import isdir, join, expanduser

from ..installer import Installer
from ..api import api_request


class SystemInstaller(Installer):
    """Support for FPGA in platformio(pio) plug-in installer"""

    def __init__(self):
        self.packages_dir = join(expanduser('~'), '.apio', 'system')

        self.package = 'tools-usb-ftdi'
        self.name = 'bin'
        self.platform = self._get_platform()
        self.version = self._get_version()
        if 'windows' in self.platform:
            self.extension = 'zip'
        else:
            self.extension = 'tar.bz2'

    def install(self):
        super(SystemInstaller, self).install()

        # Rename unpacked dir to package dir
        unpack_dir = join(self.packages_dir, self.name)
        package_dir = join(self.packages_dir, self.package)
        if isdir(unpack_dir):
            rename(unpack_dir, package_dir)

    def _get_download_url(self):
        url = '{0}/v0.{1}/{2}'.format(
            'https://github.com/FPGAwars/tools-usb-ftdi/releases/download',
            self.version,
            self._get_package_name())
        return url

    def _get_package_name(self):
        name = '{0}-{1}-{2}.{3}'.format(
            self.package,
            self.platform,
            self.version,
            self.extension)
        return name

    def _get_version(self):
        releases = api_request('tools-usb-ftdi/releases/latest')
        if releases is not None and 'tag_name' in releases:
            version = releases['tag_name'].split('.')[1]  # v0.X -> X
            return version
