# Toolchain scons class

from os import rename
from os.path import isdir, join
from ..installer import Installer


class SconsInstaller(Installer):

    def __init__(self):
        self.package = 'tool-scons'
        self.name = 'scons'
        self.version = '2.4.1'
        self.extension = 'tar.gz'

    def install(self):
        super(SconsInstaller, self).install()

        # Rename unpacked dir to package dir
        unpack_dir = join(self.packages_dir, self.name + '-' + self.version)
        package_dir = join(self.packages_dir, self.package)
        if isdir(unpack_dir):
            rename(unpack_dir, package_dir)

    def _get_download_url(self):
        url = '{0}/{1}/{2}'.format(
            'http://sourceforge.net/projects/scons/files/scons',
            self.version,
            self._get_package_name())
        return url

    def _get_package_name(self):
        name = '{0}-{1}.{2}'.format(
            self.name,
            self.version,
            self.extension)
        return name
