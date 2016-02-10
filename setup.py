from setuptools import setup

setup(
    name='apio',
    version='0.0.3b1',
    packages=['apio'],
    include_package_data=True,
    install_requires=[
        'click'
    ],
    entry_points={
        'console_scripts': ['apio=apio:cli']
    }
)
