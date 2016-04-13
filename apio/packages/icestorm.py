# Toolchain icestorm class

import requests
requests.packages.urllib3.disable_warnings()

from os import rename
from os.path import isdir, join

from ..installer import Installer


class IcestormInstaller(Installer):

    def __init__(self):
        self.package = 'toolchain-icestorm'
        self.name = 'toolchain-icestorm'
        self.platform = self._get_platform()
        self.version = self._get_version()
        if 'windows' in self.platform:
            self.extension = 'zip'
        else:
            self.extension = 'tar.gz'

    def install(self):
        super(IcestormInstaller, self).install()

        # Rename unpacked dir to package dir
        unpack_dir = join(self.packages_dir, self.name)
        package_dir = join(self.packages_dir, self.package)
        if isdir(unpack_dir):
            rename(unpack_dir, package_dir)

    def _get_download_url(self):
        url = '{0}/0.{1}/{2}'.format(
            'https://github.com/FPGAwars/toolchain-icestorm/releases/download',
            self.version,
            self._get_package_name())
        return url

    def _get_package_name(self):
        name = '{0}-{1}-{2}.{3}'.format(
            self.name,
            self.platform,
            self.version,
            self.extension)
        return name

    def _get_version(self):
        releases_url = 'https://api.github.com/repos/FPGAwars/toolchain-icestorm/releases/latest'
        response = requests.get(releases_url)
        releases = response.json()
        version = releases['tag_name'].split('.')[1]  # 0.X -> X
        return version
