# Rules icestick class

import subprocess

from os.path import join, dirname, isfile


class RulesInstaller(object):

    rules_local_path = join(dirname(__file__), '80-icestick.rules')
    rules_system_path = '/etc/udev/rules.d/80-icestick.rules'

    def install(self):
        print('Install icestick.rules')
        if not isfile(self.rules_system_path):
            subprocess.call(['sudo', 'cp', self.rules_local_path, self.rules_system_path])
        else:
            print('Package icestick.rules is already the newest version')

    def uninstall(self):
        if isfile(self.rules_system_path):
            print('Uninstall package icestick.rules')
            subprocess.call(['sudo', 'rm', self.rules_system_path])
        else:
            print('Package icestick.rules is not installed')
