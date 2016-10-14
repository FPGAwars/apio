# -*- coding: utf-8 -*-

from setuptools import setup

setup(
    name='apio',
    version='0.1.7.2',
    description='Experimental micro-ecosystem for open FPGAs',
    author='Jesús Arroyo Torrens',
    author_email='jesus.jkhlg@gmail.com',
    url='https://github.com/FPGAwars/apio',
    license='GPLv2',
    packages=['apio'],
    package_data={
        'apio': ['commands/*.py',
                 'managers/*.py',
                 'resources/*']
    },
    install_requires=[
        'click',
        'requests'
    ],
    entry_points={
        'console_scripts': ['apio=apio:cli']
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Programming Language :: Python']
)
