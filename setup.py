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
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    license=__license__,
    url=__url__,
    project_urls={
        'FPGAwars': 'https://FPGAwars.github.io/',
        'Travis CI': 'https://travis-ci.org/FPGAwars/apio',
        'Apio documentation': 'https://apiodoc.readthedocs.io/',
        'Apio source': 'https://github.com/FPGAwars/apio',
    },

    author=__author__,
    author_email=__email__,

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3'
    ],
    keywords=[
        'iot', 'embedded', 'fpga', 'cli', 'verilog', 'hardware',
        'icestorm', 'yosys', 'arachne-pnr', 'iverilog', 'verilator',
        'lattice', 'ice40', 'ecp5'
    ],

    packages=['apio'],
    package_data={
        'apio': [
            'commands/*.py',
            'managers/*.py',
            'resources/*'
        ]
    },
    entry_points={
        'console_scripts': ['apio=apio.__main__:cli']
    },

    install_requires=[
        'click>=5,<7',
        'semantic_version>=2.5.0,<3',
        'requests>=2.4.0,<3',
        'pyjwt>=1.5.3,<2',
        'colorama',
        'pyserial>=3,<4'
    ],
    extras_require=extras_require
)
