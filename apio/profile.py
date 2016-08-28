# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016 FPGAwars
# -- Author Jesús Arroyo
# -- Licence GPLv2

import json
from os.path import isfile, join

from apio.util import get_home_dir


class Profile(object):

    def __init__(self):
        self.packages = {}
        self._profile_path = join(get_home_dir(), 'profile.json')
        self.load()

    def check_package(self, name):
        return (name in self.packages.keys())

    def check_version(self, name, version):
        return not ((name in self.packages.keys()) and
                    (self.packages[name]['version'] >= version))

    def add(self, name, version):
        self.packages[name] = {'version': version}

    def remove(self, name):
        if name in self.packages.keys():
            del self.packages[name]

    def get_version(self, name):
        return self.packages[name]['version']

    def load(self):
        self.packages = {}
        if isfile(self._profile_path):
            with open(self._profile_path, 'r') as profile:
                try:
                    self.packages = json.load(profile)
                except:
                    pass
                profile.close()

    def save(self):
        with open(self._profile_path, 'w') as profile:
            json.dump(self.packages, profile)
            profile.close()
