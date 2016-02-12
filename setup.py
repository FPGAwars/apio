# -*- coding: utf-8 -*-

from setuptools import setup

setup(
    name='apio',
    author='Jesús Arroyo Torrens',
    email='jesus.arroyo@bq.com',
    version='0.0.3.6',
    packages=['apio'],
    package_data={
        'apio': ['rules/*']
    },
    install_requires=[
        'click'
    ],
    data_files=[
        ('/etc/udev/rules.d', ['apio/rules/80-icestick.rules'])
    ],
    entry_points={
        'console_scripts': ['apio=apio:cli']
    },
    classifiers=['Development Status :: 1 - Planning',
                 'Environment :: Console',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
                 'Programming Language :: Python :: 2.7']
)
