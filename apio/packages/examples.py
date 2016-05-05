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

    def install(self):
        super(ExamplesInstaller, self).install()

        # Rename unpacked dir to package dir
        unpack_dir = join(self.packages_dir, self.name)
        package_dir = join(self.packages_dir, self.package)
        if isdir(unpack_dir):
            rename(unpack_dir, package_dir)

    def _get_download_url(self):
        url = '{0}/{1}.zip'.format(
            'https://github.com/FPGAwars/apio-examples/archive',
            self.version)
        return url

    def _get_package_name(self):
        name = '{0}.{1}'.format(
            self.version,
            self.extension)
        return name

    def _get_version(self):
        tags = api_request('apio-examples/tags')
        if tags is not None and type(tags) == list and \
           len(tags) > 0 and 'name' in tags[0]:
            version = tags[0]['name']
            return version
