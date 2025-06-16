# Installing Apio as a Python Pip Package

Apio can be installed either as a Pip package that relies on a Python installation, or as a standalone package using installers or file bundles that include all required files. This page describes the Python-based Pip package installation.

### Install

1. Run `python --version` and verify that it matches the [Apio system requirements](system-requirements.md).

2. Uninstall any previous version of Apio, following its uninstall instructions.

3. Install the latest Apio code by running the following command:

    ```
    pip install --force-reinstall -U \
      git+https://github.com/FPGAwars/apio.git@develop#egg=apio
    ```

4. Open a new shell window and type `apio system info` to test your installation.

### Uninstall

1. Delete the `apio` pip package by running:

    ```
    pip uninstall apio
    ```

2. Delete the Apio settings directory `.apio` located in your home directory.
