# -*- coding: utf-8 -*-

import os
import json

from setuptools import setup

from apio import (__author__, __description__, __email__, __license__,
                  __title__, __url__, __version__)

# Load extras_require
extras_require = {}
filepath = os.path.join('apio', 'resources', 'distribution.json')
with open(filepath, 'r') as f:
    resource = json.loads(f.read())
    pip_packages = resource.get('pip_packages', {})
    extras_require = {k: [k + v] for k, v in pip_packages.items()}

setup(
    name=__title__,
    version=__version__,
    description=__description__,
    author=__author__,
    author_email=__email__,
    url=__url__,
    license=__license__,
    packages=['apio'],
    package_data={
        'apio': ['commands/*.py',
                 'managers/*.py',
                 'resources/*']
    },
    install_requires=[
        'click>=5,<7',
        'semantic_version>=2.5.0',
        'requests>=2.4.0,<3',
        'pyjwt>=1.5.3,<2',
        'colorama',
        'pyserial>=3,<4'
    ],
    extras_require=extras_require,
    entry_points={
        'console_scripts': ['apio=apio.__main__:cli']
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Programming Language :: Python']
)
