# Toolchain icestorm class

import os
import requests

from ..installer import Installer


class IcestormInstaller(Installer):

    def __init__(self):
        self.package = 'toolchain-icestorm'
        self.platform = 'x86_64'  # self._get_platform()
        self.version = self._get_version()
        self.extension = 'tar.gz'

    def _get_download_url(self):
        url = '{0}/0.{1}/{2}'.format(
            'https://github.com/bqlabs/toolchain-icestorm/releases/download',
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
        releases_url = 'https://api.github.com/repos/bqlabs/toolchain-icestorm/releases/latest'
        response = requests.get(releases_url)
        releases = response.json()
        version = releases['tag_name'].split('.')[1]  # 0.X -> X
        return version
