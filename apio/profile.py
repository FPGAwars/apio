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
        self.config = {}
        self.packages = {}
        self._profile_path = join(get_home_dir(), 'profile.json')
        self.load()

    def check_package(self, name):
        return (name in self.packages.keys())

    def check_package_version(self, name, version):
        return not (self.check_package(name) and
                    (self.get_package_version(name) >= version))

    def check_exe_apio(self):
        return self.get_config_exe() == 'apio'

    def add_package(self, name, version):
        self.packages[name] = {'version': version}

    def add_config(self, exe):
        self.config = {'exe': exe}

    def remove_package(self, name):
        if name in self.packages.keys():
            del self.packages[name]

    def get_package_version(self, name):
        return self.packages[name]['version']

    def get_config_exe(self):
        if 'exe' in self.config.keys():
            return self.config['exe']
        else:
            return 'apio'

    def load(self):
        data = {}
        if isfile(self._profile_path):
            with open(self._profile_path, 'r') as profile:
                try:
                    data = json.load(profile)
                    if 'config' in data.keys():
                        self.config = data['config']
                    if 'packages' in data.keys():
                        self.packages = data['packages']
                    else:
                        self.packages = data  # Backward compatibility
                except:
                    pass
                profile.close()

    def save(self):
        with open(self._profile_path, 'w') as profile:
            data = {'config': self.config, 'packages': self.packages}
            json.dump(data, profile)
            profile.close()
