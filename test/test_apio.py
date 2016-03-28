import os
import apio

scons = apio.SCons()


def test_apio_debug():
    apio.get_systype()


def test_apio_init():
    filename = 'SConstruct'
    _secure_remove(filename)
    scons.create_sconstruct()
    assert os.path.isfile(filename)
    _secure_remove(filename)


def _secure_remove(filename):
    if os.path.isfile(filename):
        os.remove(filename)


def test_apio_clean():
    scons.run(['-c'])


def test_apio_build():
    scons.run()


def test_apio_upload():
    scons.run(['upload'])
