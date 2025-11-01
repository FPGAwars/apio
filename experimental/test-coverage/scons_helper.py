import os


def called_from_scons():
    """Called from SConstruct to print a message"""
    print("*** Child: called from scons")
    print(f"*** Child: current dir: {os.getcwd()}")
