# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2021 FPGAwars
# -- Author Jesús Arroyo
# -- Licence GPLv2
"""Package install/uninstall functionality.
Used by the 'apio packages' command.
"""

import sys
from pathlib import Path
from typing import Tuple
import shutil
from apio.utils.apio_console import cout, cerror
from apio.apio_context import ApioContext
from apio.managers.downloader import FileDownloader
from apio.managers.unpacker import FileUnpacker
from apio.utils import util, pkg_util


def _construct_package_download_url(
    apio_ctx: ApioContext, package_name: str, target_version: str
) -> str:
    """Construct the download URL for the given package name and version.

    Sample output:
    'https://github.com/FPGAwars/tools-oss-cad-suite/releases/download/
                       v0.0.9/tools-oss-cad-suite-darwin_arm64-0.0.9.tar.gz'
    """

    # -- Get the package info (originated from packages.jsonc)
    package_info = apio_ctx.get_package_info(package_name)

    # -- Get the package selector of this platform (the package selectors
    # -- are specified in platforms.jsonc). E.g. 'darwin_arm64'
    platform_id = apio_ctx.platform_id
    package_selector = apio_ctx.platforms[platform_id]["package_selector"]

    # -- Get the compressed name of the package. This is base name of the
    # -- downloaded file. E.g. "tools-oss-cad-suite-%P-%V"
    file_name = package_info["release"]["file_name"]

    # -- Replace %P, if any, with package selector.
    file_name = file_name.replace("%P", package_selector)

    # -- Replace %V, if any,  with the package version
    file_name = file_name.replace("%V", target_version)

    # -- Get the package file name extension. e.g. 'tar.gz'.
    extension = package_info["release"]["extension"]

    # -- Construct the package file name.
    # -- E.g. 'atools-oss-cad-suite-darwin_arm64-0.0.9.tar.gz'
    file_name = f"{file_name}.{extension}"

    # -- Get the github user name. E.g. 'FGPAWars'.
    organization = package_info["repository"]["organization"]

    # -- Get the github repo name. e.g. 'tools-oss-cad-tools'
    repo_name = package_info["repository"]["name"]

    # -- Construct the release tag name. E.g 'v0.0.9'.
    release_tag = package_info["release"]["release_tag"].replace(
        "%V", target_version
    )

    # -- Construct the full url.
    download_url = (
        f"https://github.com/{organization}/{repo_name}/releases/"
        f"download/{release_tag}/{file_name}"
    )

    return download_url


def _download_package_file(url: str, dir_path: Path) -> str:
    """Download the given file (url). Return the path of local destination
    file. Exits with a user message and error code if any error.

    * INPUTS:
      * url: File to download
    * OUTPUTS:
      * The path of the destination file
    """

    filepath = None

    try:
        # -- Object for downloading the file
        downloader = FileDownloader(url, dir_path)

        # -- Get the destination path
        filepath = downloader.destination

        downloader.start()

    # -- If the user press Ctrl-C (Abort)
    except KeyboardInterrupt:

        # -- Remove the file
        if filepath and filepath.is_file():
            filepath.unlink()

        # -- Inform the user
        cout("User abborted download", style="red")
        sys.exit(1)

    except IOError as exc:
        cout("I/O error while downloading", style="red")
        cout(str(exc), style="red")
        sys.exit(1)

    except util.ApioException:
        cerror("Package not found")
        sys.exit(1)

    # -- Return the destination path
    return filepath


def _unpack_package_file(package_file: Path, package_dir: Path) -> None:
    """Unpack the package_file in the package_dir directory.
    Exit with an error message and error status if any error."""

    # -- Create the unpacker.
    operation = FileUnpacker(package_file, package_dir)

    # -- Perform the operation.
    ok = operation.start()

    # -- Exit if error.
    if not ok:
        cerror(f"Failed to unpack package file {package_file}")
        sys.exit(1)


def _parse_package_spec(package_spec: str) -> Tuple[str, str]:
    """Parse package spec into package name and optional version.
    Returns a tuple (name, version || None), exits with error message if
    any error.

    E.g.
      'my_package@1.2.3' -> ('my_package', '1.2.3')
      'my_package'       -> ('my_package', None)
    """
    tokens = package_spec.split("@")
    if len(tokens) not in [1, 2]:
        cerror(f"Invalid package spec '{package_spec}")
        cout("Try 'my_package' or  'my_package@0.1.2'", style="yellow")
        sys.exit(1)

    package_name = tokens[0]
    package_version = tokens[1] if len(tokens) > 1 else ""

    return (package_name, package_version)


def _delete_package_dir(
    apio_ctx: ApioContext, package_name: str, verbose: bool
) -> bool:
    """Delete the directory of the package with given name.  Returns
    True if the packages existed. Exits with an error message on error."""

    package_dir = apio_ctx.get_package_dir(package_name)

    dir_found = package_dir.is_dir()
    if dir_found:
        if verbose:
            cout(f"Deleting {str(package_dir)}")

        # -- Sanity check the path and delete.
        assert "packages" in str(package_dir).lower(), package_dir
        shutil.rmtree(package_dir)

    if package_dir.exists():
        cerror(f"Directory deletion failed: {str(package_dir.absolute())}")
        sys.exit(1)

    return dir_found


def install_missing_packages_on_the_fly(apio_ctx: ApioContext) -> None:
    """Install on the fly any missing packages. Does not print a thing if
    all packages are already ok. This function is intended for on demand
    package fetching by commands such as apio build, and thus is allowed
    to use fetched remote config instead of fetching a fresh one."""

    # -- Scan the packages for issues. Since it's an 'on the fly' installation,
    # -- We want to reduce its footprint and the connectivity requirements nad
    # -- let it use a cached remote config, if available.
    scan_results = pkg_util.scan_packages(
        apio_ctx, cached_config_ok=True, verbose=False
    )

    # -- If all ok, we are done.
    if scan_results.is_all_ok():
        return

    # -- Tracks if we made any change.
    work_done = False

    # -- Before we check or install, delete all issues, if any.
    if scan_results.num_errors_to_fix():
        fix_packages(apio_ctx, scan_results)
        work_done = True

    # -- Get lists of installed and required packages.
    installed_packages = apio_ctx.profile.packages
    required_packages_names = apio_ctx.platform_packages.keys()

    # -- Install any required package that is not installed.
    for package_name in required_packages_names:
        if package_name not in installed_packages:
            install_package(
                apio_ctx,
                package_spec=package_name,
                force_reinstall=False,
                cached_config_ok=False,
                verbose=False,
            )
            work_done = True

    # -- Here all packages should be ok but we check again just in case.
    if work_done:
        scan_results = pkg_util.scan_packages(
            apio_ctx, cached_config_ok=False, verbose=False
        )
        if not scan_results.is_all_ok():
            cout(
                "Warning: packages issues detected. Use "
                "'apio packages list' to investigate.",
                style="red",
            )


# pylint: disable=too-many-branches
def install_package(
    apio_ctx: ApioContext,
    *,
    package_spec: str,
    force_reinstall: bool,
    cached_config_ok,
    verbose: bool,
) -> None:
    """Install a given package.

    'apio_ctx' is the context object of this apio invocation.
    'package_spec' is a package name with optional version suffix
        e.b. 'drivers', 'drivers@1.2.0'.
    'force' indicates if to perform the installation even if a matching
        package is already installed.
    `verbose` indicates if to print extra information.

    Returns normally if no error, exits the program with an error status
    and a user message if an error is detected.
    """

    # -- Parse the requested package spec.
    package_name, target_version = _parse_package_spec(package_spec)

    # -- Exit if no such package for this platform.
    if package_name not in apio_ctx.platform_packages:
        cerror(f"No such package '{package_name}'")
        sys.exit(1)

    cout(f"Installing package '{package_spec}'", style="magenta")

    # -- If the user didn't specify a target version we use the one specified
    # -- in the remote config.
    if not target_version:
        target_version = apio_ctx.profile.get_package_required_version(
            package_name, cached_config_ok=cached_config_ok, verbose=verbose
        )

    cout(f"Target version {target_version}")

    # -- If not focring and the target version already installed nothing to do.
    if not force_reinstall:
        # -- Get the version of the installed package, None otherwise.
        installed_version = apio_ctx.profile.get_package_installed_version(
            package_name, default=None
        )

        if verbose:
            print(f"Installed version {installed_version}")

        # -- If the installed and the target versions are the same then
        # -- nothing to do.
        if target_version == installed_version:
            cout(
                f"Version {target_version} was already installed",
                style="green",
            )
            return

    # -- Construct the download URL.
    download_url = _construct_package_download_url(
        apio_ctx, package_name, target_version
    )
    if verbose:
        print(f"Download URL: {download_url}")

    # -- Prepare the packages directory.
    apio_ctx.packages_dir.mkdir(exist_ok=True)

    # -- Prepare the package directory.
    package_dir = apio_ctx.get_package_dir(package_name)
    print(f"Package dir: {package_dir}")

    # -- Downlod the package file from the remote server.
    local_package_file = _download_package_file(
        download_url, apio_ctx.packages_dir
    )
    if verbose:
        print(f"Local package file: {local_package_file}")

    # -- Delete the old package dir, if exists, to avoid name conflicts and
    # -- left over files.
    _delete_package_dir(apio_ctx, package_name, verbose)

    # -- Unpack the package. This creates a new package dir.
    _unpack_package_file(local_package_file, package_dir)

    # -- Remove the package file. We don't need it anymore.
    if verbose:
        print(f"Deleting package file {local_package_file}")
    local_package_file.unlink()

    # -- Add package to profile and save.
    apio_ctx.profile.add_package(package_name, target_version)
    # apio_ctx.profile.save()

    # -- Inform the user!
    cout(f"Package '{package_name}' installed successfully", style="green")


def uninstall_package(
    apio_ctx: ApioContext, *, package_spec: str, verbose: bool
):
    """Uninstall the apio package"""

    # -- Parse package spec. We ignore the version silently.
    package_name, _ = _parse_package_spec(package_spec)

    package_info = apio_ctx.platform_packages.get(package_name, None)
    if not package_info:
        cerror(f"No such package '{package_name}'")
        sys.exit(1)

    cout(f"Uninstalling package '{package_name}'")

    # -- Remove the folder with all its content!!
    dir_existed = _delete_package_dir(apio_ctx, package_name, verbose)

    installed_version = apio_ctx.profile.get_package_installed_version(
        package_name, None
    )

    # -- Remove the package from the profile file
    apio_ctx.profile.remove_package(package_name)
    # apio_ctx.profile.save()

    # -- Check that it is a folder...
    if dir_existed or installed_version:

        # -- Inform the user
        cout(
            f"Package '{package_name}' uninstalled successfully", style="green"
        )
    else:
        # -- Package not installed. We treat it as a success.
        cout(
            f"Package '{package_name}' was already uninstalled", style="green"
        )


def fix_packages(
    apio_ctx: ApioContext, scan: pkg_util.PackageScanResults
) -> None:
    """If the package scan result contains errors, fix them."""

    # -- Fix broken packages.
    for package_name in scan.bad_version_package_names_subset:
        print(f"Uninstalling versin mismatch '{package_name}'")
        _delete_package_dir(apio_ctx, package_name, verbose=False)
        apio_ctx.profile.remove_package(package_name)

    for package_name in scan.broken_package_names:
        print(f"Uninstalling broken package '{package_name}'")
        _delete_package_dir(apio_ctx, package_name, verbose=False)
        apio_ctx.profile.remove_package(package_name)

    for package_name in scan.orphan_package_names:
        print(f"Uninstalling unknown package '{package_name}'")
        apio_ctx.profile.remove_package(package_name)

    for dir_name in scan.orphan_dir_names:
        print(f"Deleting unknown package dir '{dir_name}'")
        # -- Sanity check. Since apio_ctx.packages_dir is guarranted to include
        # -- the word packages, this can fail only due to programming error.
        dir_path = apio_ctx.packages_dir / dir_name
        assert "packages" in str(dir_path).lower(), dir_path
        # -- Delete.
        shutil.rmtree(dir_path)

    for file_name in scan.orphan_file_names:
        print(f"Deleting unknown package file '{file_name}'")
        # -- Sanity check. Since apio_ctx.packages_dir is guarranted to
        # -- include the word packages, this can fail only due to programming
        # -- error.
        file_path = apio_ctx.packages_dir / file_name
        assert "packages" in str(file_path).lower(), dir_path
        # -- Delete.
        file_path.unlink()
