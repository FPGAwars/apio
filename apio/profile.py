# Profile class

import json
from os import makedirs
from os.path import isdir, isfile, join, expanduser


class Profile(object):

    def __init__(self):
        self.packages = {}
        self._apio_dir = join(expanduser("~"), '.apio/')
        self._profile_path = join(self._apio_dir, 'profile.json')
        self.load()

    def check_version(self, name, version):
        return not ((name in self.packages.keys()) and (self.packages[name]['version'] >= version))

    def add(self, name, version):
        self.packages[name] = {'version': version}

    def remove(self, name):
        if name in self.packages.keys():
            del self.packages[name]

    def get_version(self, name):
        return self.packages[name]['version']

    def load(self):
        if isfile(self._profile_path):
            with open(self._profile_path, 'r') as profile:
                try:
                    self.packages = json.load(profile)
                except:
                    self.packages = {}
                profile.close()

    def save(self):
        if not isdir(self._apio_dir):
            makedirs(self._apio_dir)
        with open(self._profile_path, 'w') as profile:
            json.dump(self.packages, profile)
            profile.close()
