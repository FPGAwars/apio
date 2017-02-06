# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2017 FPGAwars
# -- Author Jesús Arroyo
# -- Licence GPLv2

import json
import click
import semantic_version

from os.path import isfile, isdir

from apio import util


class Profile(object):

    def __init__(self):
        self.config = {'exe': 'default', 'verbose': 0}
        self.labels = {'exe': 'Executable', 'verbose': 'Verbose'}
        self.packages = {}
        self._profile_path = util.safe_join(
            util.get_home_dir(), 'profile.json')
        self.load()

    def check_package(self, name, release_name):
        return (name in self.packages.keys()) or \
               isdir(util.get_package_dir(release_name))

    def check_package_version(self, name, version, release_name=''):
        ret = False
        if self.check_package(name, release_name):
            pkg_version = self.get_package_version(name, release_name)
            pkg_version = self._convert_old_version(pkg_version)
            version = self._convert_old_version(version)
            ret = (semantic_version.Version(pkg_version) <
                   semantic_version.Version(version))
        return ret

    def _convert_old_version(self, version):
        # Convert old versions to new format
        try:
            v = int(version)
            version = '1.{}.0'.format(v)
        except ValueError:
            pass
        return version

    def check_exe_default(self):
        return self.config['exe'] == 'default'

    def add_package(self, name, version):
        self.packages[name] = {'version': version}

    def add_config(self, key, value):
        if self.config[key] != value:
            self.config[key] = value
            self.save()
            click.secho('{0} mode updated: {1}'.format(
                self.labels[key], value), fg='green')
        else:
            click.secho('{0} mode already {1}'.format(
                self.labels[key], value), fg='yellow')

    def remove_package(self, name):
        if name in self.packages.keys():
            del self.packages[name]

    def get_verbose_mode(self):
        return int(self.config['verbose'])

    def get_package_version(self, name, release_name=''):
        version = '0.0.0'
        if name in self.packages.keys():
            version = self.packages[name]['version']
        elif release_name:
            dir_name = util.get_package_dir(release_name)
            if isdir(dir_name):
                filepath = util.safe_join(dir_name, 'package.json')
                with open(filepath, 'r') as json_file:
                    try:
                        tmp_data = json.load(json_file)
                        if 'version' in tmp_data.keys():
                            version = tmp_data['version']
                    except:
                        pass
        return version

    def load(self):
        data = {}
        if isfile(self._profile_path):
            with open(self._profile_path, 'r') as profile:
                try:
                    data = json.load(profile)
                    if 'config' in data.keys():
                        self.config = data['config']
                        if 'exe' not in self.config.keys():
                            self.config['exe'] = 'default'
                        if 'verbose' not in self.config.keys():
                            self.config['verbose'] = 0
                    if 'packages' in data.keys():
                        self.packages = data['packages']
                    else:
                        self.packages = data  # Backward compatibility
                except:
                    pass

    def save(self):
        util.mkdir(self._profile_path)
        with open(self._profile_path, 'w') as profile:
            data = {'config': self.config, 'packages': self.packages}
            json.dump(data, profile)

    def list(self):
        for key in self.config:
            click.secho('{0} mode: {1}'.format(
                self.labels[key], self.config[key]), fg='yellow')
