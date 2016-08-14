# Examples class

from os import rename
from os.path import isdir, join, expanduser

from ..installer import Installer
from ..api import api_request


class ExamplesInstaller(Installer):

    def __init__(self):
        self.packages_dir = join(expanduser('~'), '.apio')

        self.package = 'examples'
        self.version = self._get_version()
        self.name = 'apio-examples-' + str(self.version)
        self.extension = 'zip'

    def install(self, version=None):
        if version:
            self.name = 'apio-examples-' + str(self.version)
        super(ExamplesInstaller, self).install(version)

        # Rename unpacked dir to package dir
        unpack_dir = join(self.packages_dir, self.name)
        package_dir = join(self.packages_dir, self.package)
        if isdir(unpack_dir):
            rename(unpack_dir, package_dir)

    def _get_download_url(self):
        url = '{0}/{1}/{2}'.format(
            'https://github.com/FPGAwars/apio-examples/releases/download',
            self.version,
            self._get_package_name())
        return url

    def _get_package_name(self):
        name = '{0}.{1}'.format(
            self.name,
            self.extension)
        return name

    def _get_version(self):
        releases = api_request('apio-examples/releases/latest')
        if releases is not None and 'tag_name' in releases:
            version = releases['tag_name']
            return version
