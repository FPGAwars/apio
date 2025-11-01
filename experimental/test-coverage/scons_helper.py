import os
import os
from SCons.Environment import Environment
from SCons.Builder import Builder
import scons_helper


def called_from_scons():
    """Called from SConstruct to print a message"""
    print("*** Child: called from SCOnstruct")
    print(f"*** Child: current dir: {os.getcwd()}")

    env = Environment(ENV=os.environ, tools=[])

    touch_builder = Builder(
        action=['pwd', 'touch $TARGET'],
        suffix='.txt'  # Ensures target ends in .txt even if source doesn't
    )

    env['BUILDERS']['Touch'] = touch_builder

    dummy_target = env.Touch('dummy', source=[])  # source='dummy', target='dummy.txt'

    env.Alias('build', dummy_target)

