"""DOC: TODO"""
# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2019 FPGAwars
# -- Author Jesús Arroyo, Juan González
# -- Licence GPLv2

import os
import glob
import codecs
import shutil
from os.path import sep, isdir, isfile, dirname, basename
import click

from apio import util
from apio.profile import Profile
from apio.resources import Resources

# -- Error messages
EXAMPLE_NOT_FOUND_MSG = """
Warning: this example does not exist
Use `apio examples -l` for listing all the available examples"""

EXAMPLE_OF_USE_CAD = """
Example of use:
   apio examples -f leds
Copy the leds example files to the current directory"""

EXAMPLE_DIR_FILE = """
To get an example, use the command:
   apio examples -d/-f name"""


class Examples:
    """DOC: TODO"""

    def __init__(self):
        profile = Profile()
        resources = Resources()

        self.name = "examples"
        self.examples_dir = util.get_package_dir(self.name)
        self.version = util.get_package_version(self.name, profile)
        self.spec_version = util.get_package_spec_version(self.name, resources)

    def list_examples(self):
        """DOC: TODO"""

        if util.check_package(
            self.name, self.version, self.spec_version, self.examples_dir
        ):
            # examples = sorted(os.listdir(self.examples_dir))
            examples = [
                dirname(y).replace(self.examples_dir + sep, "")
                for x in os.walk(self.examples_dir)
                for y in glob.glob(util.safe_join(x[0], "info"))
            ]
            click.secho("")
            for example in examples:
                example_dir = util.safe_join(self.examples_dir, example)
                if isdir(example_dir):
                    info_path = util.safe_join(example_dir, "info")
                    info = ""
                    if isfile(info_path):
                        with codecs.open(info_path, "r", "utf-8") as info_file:
                            info = info_file.read().replace("\n", "")
                    click.secho(" " + example, fg="blue", bold=True)
                    click.secho("-" * shutil.get_terminal_size()[0])
                    click.secho(" " + info)
                    click.secho("")
            click.secho(EXAMPLE_DIR_FILE, fg="green")
            click.secho(EXAMPLE_OF_USE_CAD, fg="green")
        else:
            return 1
        return 0

    def copy_example_dir(self, example, project_dir, sayno):
        """DOC: TODO"""

        if util.check_package(
            self.name, self.version, self.spec_version, self.examples_dir
        ):
            project_dir = util.check_dir(project_dir)
            example_path = util.safe_join(project_dir, example)
            local_example_path = util.safe_join(self.examples_dir, example)

            if isdir(local_example_path):
                if isdir(example_path):

                    # -- If sayno, do not copy anything
                    if not sayno:
                        click.secho(
                            "Warning: "
                            + example
                            + " directory already exists",
                            fg="yellow",
                        )

                        if click.confirm("Do you want to replace it?"):
                            shutil.rmtree(example_path)
                            self._copy_dir(
                                example, local_example_path, example_path
                            )
                elif isfile(example_path):
                    click.secho(
                        "Warning: " + example + " is already a file",
                        fg="yellow",
                    )
                else:
                    self._copy_dir(example, local_example_path, example_path)
            else:
                click.secho(EXAMPLE_NOT_FOUND_MSG, fg="yellow")
        else:
            return 1
        return 0

    def copy_example_files(self, example, project_dir, sayno):
        """DOC: TODO"""

        if util.check_package(
            self.name, self.version, self.spec_version, self.examples_dir
        ):
            project_dir = util.check_dir(project_dir)
            example_path = project_dir
            local_example_path = util.safe_join(self.examples_dir, example)

            if isdir(local_example_path):
                self._copy_files(
                    example, local_example_path, example_path, sayno
                )
            else:
                click.secho(EXAMPLE_NOT_FOUND_MSG, fg="yellow")
        else:
            return 1
        return 0

    @staticmethod
    def _copy_files(example, src_path, dest_path, sayno):
        click.secho("Copying " + example + " example files ...")
        example_files = glob.glob(util.safe_join(src_path, "*"))
        for file in example_files:
            filename = basename(file)
            if filename != "info":
                filepath = util.safe_join(dest_path, filename)
                if isfile(filepath):

                    # -- If sayno, do not copy the file. Move to the next
                    if sayno:
                        continue

                    click.secho(
                        "Warning: " + filename + " file already exists",
                        fg="yellow",
                    )
                    if click.confirm("Do you want to replace it?"):
                        shutil.copy(file, dest_path)
                elif isdir(filepath):
                    click.secho(
                        "Warning: " + filename + " is already a directory",
                        fg="yellow",
                    )
                    return
                else:
                    shutil.copy(file, filepath)
        click.secho(
            "Example files '{}' have been successfully created!".format(
                example
            ),
            fg="green",
        )

    @staticmethod
    def _copy_dir(example, src_path, dest_path):
        click.secho("Creating " + example + " directory ...")
        shutil.copytree(src_path, dest_path)
        click.secho(
            "Example '" + example + "' has been successfully created!",
            fg="green",
        )

    @staticmethod
    def examples_of_use_cad():
        """DOC: TODO"""

        return EXAMPLE_OF_USE_CAD
