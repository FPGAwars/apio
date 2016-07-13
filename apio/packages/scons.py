# Toolchain scons class

from os import rename
from os.path import isdir, join

from ..installer import Installer
from ..api import api_request


class SconsInstaller(Installer):

    def __init__(self):
        self.package = 'tool-scons'
        self.name = 'scons'
        self.version = self._get_version()
        self.extension = 'tar.gz'

    def install(self):
        super(SconsInstaller, self).install()

        # Rename unpacked dir to package dir
        unpack_dir = join(self.packages_dir, self.name + '-' + self.version)
        package_dir = join(self.packages_dir, self.package)
        if isdir(unpack_dir):
            rename(unpack_dir, package_dir)

    def _get_download_url(self):
        url = '{0}/v{1}/{2}'.format(
            'https://github.com/FPGAwars/tool-scons/releases/download',
            self.version,
            self._get_package_name())
        return url

    def _get_package_name(self):
        name = '{0}-{1}.{2}'.format(
            self.name,
            self.version,
            self.extension)
        return name

    def _get_version(self):
        releases = api_request('tool-scons/releases/latest')
        if releases is not None and 'tag_name' in releases:
            version = releases['tag_name'][1:] # vX -> X
            return version
