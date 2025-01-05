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
from click import secho
import requests
from apio import util, pkg_util
from apio.apio_context import ApioContext
from apio.managers.downloader import FileDownloader
from apio.managers.unpacker import FileUnpacker


def _get_remote_version(
    apio_ctx: ApioContext, package_name: str, verbose: bool
) -> str:
    """Get the recommanded package version from the remote release server.
    This version is not necessarily the latest one on the server.

    - INPUTS:
      'apio_ctx' the context object of this apio session.
      'package_name' the package name, e.g. 'oss-cad-suite'.
      'verbose' indicates if to print detailed info.

    - OUTPUT:
      A string with the package version (E.g. '0.0.35'). Exits with a user
      error message and error status code on any error.
    """

    # -- Get package inforation (originated from packages.json)
    package_info = apio_ctx.get_package_info(package_name)

    # -- Get the version file URL. This is a text file with the recomanded
    # -- version for this package.
    version_url = package_info["release"]["url_version"]
    if verbose:
        print(f"Remote version url '{version_url}'")

    # -- Fetch the version info.
    resp: requests.Response = requests.get(version_url, timeout=5)

    # -- Exit if http error.
    if resp.status_code != 200:
        secho("Error downloading the version file", fg="red")
        secho(f"URL {version_url}", fg="red")
        secho(f"Error code {resp.status_code}", fg="red")
        sys.exit(1)

    # -- Here when download was ok.
    if verbose:
        print("Remote version file downloaded")

    # -- Extract the version without the ending \n
    version = resp.text.rstrip("\n")

    if verbose:
        print(f"Remote version {version}")

    # -- Return the version
    return version


def _construct_package_download_url(
    apio_ctx: ApioContext, package_name: str, target_version: str
) -> str:
    """Construct the download URL for the given package name and version.

    Sample output:
    'https://github.com/FPGAwars/tools-oss-cad-suite/releases/download/
                       v0.0.9/tools-oss-cad-suite-darwin_arm64-0.0.9.tar.gz'
    """

    # -- Get the package info (originated from packages.json)
    package_info = apio_ctx.get_package_info(package_name)

    # -- Get the package selector of this platform (the package selectors
    # -- are specified in platforms.json). E.g. 'darwin_arm64'
    platform_id = apio_ctx.platform_id
    package_selector = apio_ctx.platforms[platform_id]["package_selector"]

    # -- Get the compressed name of the package. This is base name of the
    # -- downloaded file. E.g. "tools-oss-cad-suite-%P-%V"
    compressed_name = package_info["release"]["compressed_name"]

    # -- Replace %P, if any, with package selector.
    compressed_name = compressed_name.replace("%P", package_selector)

    # -- Replace %V, if any,  with the package version
    compressed_name = compressed_name.replace("%V", target_version)

    # -- Get the package file name extension. e.g. 'tar.gz'.
    extension = package_info["release"]["extension"]

    # -- Construct the package file name.
    # -- E.g. 'atools-oss-cad-suite-darwin_arm64-0.0.9.tar.gz'
    file_name = f"{compressed_name}.{extension}"

    # -- Get the github user name. E.g. 'FGPAWars'.
    organization = package_info["repository"]["organization"]

    # -- Get the github repo name. e.g. 'tools-oss-cad-tools'
    repo_name = package_info["repository"]["name"]

    # -- Construct the release tag name. E.g 'v0.0.9'.
    version_tag = package_info["release"]["tag_name"].replace(
        "%V", target_version
    )

    # -- Construct the full url.
    download_url = (
        f"https://github.com/{organization}/{repo_name}/releases/"
        f"download/{version_tag}/{file_name}"
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
        secho("User abborted download", fg="red")
        sys.exit(1)

    except IOError as exc:
        secho("I/O error while downloading", fg="red")
        secho(str(exc), fg="red")
        sys.exit(1)

    except util.ApioException:
        secho("Error: package not found", fg="red")
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
        secho(f"Error: failed to unpack package file {package_file}", fg="red")
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
        secho(f"Error: invalid package spec '{package_spec}", fg="red")
        secho("Try 'my_package' or  'my_package@0.1.2'", fg="yellow")
        sys.exit(1)

    package_name = tokens[0]
    package_version = tokens[1] if len(tokens) > 1 else ""

    return (package_name, package_version)


def _delete_package_dir(
    apio_ctx: ApioContext, package_id: str, verbose: bool
) -> bool:
    """Delete the directory of the package with given name.  Returns
    True if the packages existed. Exits with an error message on error."""

    package_dir = apio_ctx.get_package_dir(package_id)

    dir_found = package_dir.is_dir()
    if dir_found:
        if verbose:
            secho(f"Deleting {str(package_dir)}")

        # -- Sanity check the path and delete.
        package_folder_name = apio_ctx.get_package_folder_name(package_id)
        assert "packages" in str(package_dir).lower(), package_dir
        assert package_folder_name in str(package_dir), package_dir
        shutil.rmtree(package_dir)

    if package_dir.exists():
        secho(
            f"Error: directory deletion failed: {str(package_dir.absolute())}",
            fg="yellow",
        )
        sys.exit(1)

    return dir_found


def install_missing_packages(apio_ctx: ApioContext) -> None:
    """Install on the fly any missing packages. Does not print a thing if
    all packages are already ok."""

    # -- Scan the packages for issues.
    scan_results = pkg_util.scan_packages(apio_ctx)

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
                apio_ctx, package_spec=package_name, force=False, verbose=False
            )
            work_done = True

    # -- Here all packages should be ok but we check again just in case.
    if work_done:
        scan_results = pkg_util.scan_packages(apio_ctx)
        if not scan_results.is_all_ok():
            secho(
                "Warning: packages issues detected. Use "
                "'apio packages list' to investigate.",
                fg="red",
            )


# pylint: disable=too-many-branches
def install_package(
    apio_ctx: ApioContext, *, package_spec: str, force: bool, verbose: bool
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
    secho(f"Installing package '{package_spec}'", fg="magenta")

    # Parse the requested package spec.
    package_name, target_version = _parse_package_spec(package_spec)

    # -- Get package information (originated from packages.json)
    package_info = apio_ctx.get_package_info(package_name)

    # -- If the user didn't specify a target version we use the one recomanded
    # -- by the release server.
    # --
    # -- Note that we use the remote version even if the current installed
    # -- version is ok by the version spec in distribution.json.
    if not target_version:
        target_version = _get_remote_version(apio_ctx, package_name, verbose)

    secho(f"Target version {target_version}")

    # -- If not focring and the target version already installed nothing to do.
    if not force:
        # -- Get the version of the installed package, None otherwise.
        installed_version = apio_ctx.profile.get_package_installed_version(
            package_name, default=None
        )

        if verbose:
            print(f"Installed version {installed_version}")

        # -- If the installed and the target versions are the same then
        # -- nothing to do.
        if target_version == installed_version:
            secho(
                f"Version {target_version} was already installed", fg="green"
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

    # -- Get optional package internal wrapper dir name.
    uncompressed_name = package_info["release"].get("uncompressed_name", "")

    # -- Delete the old package dir, if exists, to avoid name conflicts and
    # -- left over files.
    _delete_package_dir(apio_ctx, package_name, verbose)

    if uncompressed_name:

        # -- Case 1: The package include a top level wrapper directory.
        #
        # -- Unpack the package one level up, in the packages directory.
        _unpack_package_file(local_package_file, apio_ctx.packages_dir)

        # -- The uncompressed name may contain a %V placeholder, Replace it
        # -- with target version.
        uncompressed_name = uncompressed_name.replace("%V", target_version)

        # -- Construct the local path of the wrapper dir.
        wrapper_dir = apio_ctx.packages_dir / uncompressed_name

        # -- Rename the wrapper dir to the package dir.
        if verbose:
            print(f"Renaming {wrapper_dir} to {package_dir}")
        if not wrapper_dir.is_dir():
            secho(f"Error: no unpacked dir {wrapper_dir}", fg="red")
            sys.exit(1)
        wrapper_dir.rename(package_dir)

    else:
        # -- Case 2: package does not include a wrapper dir and we can simply
        # -- unpack as the package dir.

        # -- Unpack the package. This creates a new package dir.
        _unpack_package_file(local_package_file, package_dir)

    # -- Remove the package file. We don't need it anymore.
    if verbose:
        print(f"Deleting package file {local_package_file}")
    local_package_file.unlink()

    # -- Add package to profile and save.
    apio_ctx.profile.add_package(package_name, target_version)
    apio_ctx.profile.save()

    # -- Inform the user!
    secho(
        f"Package '{package_name}' installed successfully",
        fg="green",
    )


def uninstall_package(
    apio_ctx: ApioContext, *, package_spec: str, verbose: bool
):
    """Uninstall the apio package"""

    # -- Parse package spec. We ignore the version silently.
    package_name, _ = _parse_package_spec(package_spec)

    package_info = apio_ctx.platform_packages.get(package_name, None)
    if not package_info:
        secho(f"Error: no such package '{package_name}'", fg="red")
        sys.exit(1)

    # package_color = click.style(package_name, fg="cyan")
    secho(f"Uninstalling package '{package_name}'")

    # -- Remove the folder with all its content!!
    dir_existed = _delete_package_dir(apio_ctx, package_name, verbose)

    installed_version = apio_ctx.profile.get_package_installed_version(
        package_name, None
    )

    # -- Remove the package from the profile file
    apio_ctx.profile.remove_package(package_name)
    apio_ctx.profile.save()

    # -- Check that it is a folder...
    if dir_existed or installed_version:

        # -- Inform the user
        secho(
            f"Package '{package_name}' uninstalled successfully",
            fg="green",
        )
    else:
        # -- Package not installed. We treat it as a success.
        secho(f"Package '{package_name}' was not installed", fg="green")


def fix_packages(
    apio_ctx: ApioContext, scan: pkg_util.PackageScanResults
) -> None:
    """If the package scan result contains errors, fix them."""

    # -- Fix broken packages.
    for package_id in scan.installed_bad_version_subset:
        print(f"Uninstalling versin mismatch '{package_id}'")
        _delete_package_dir(apio_ctx, package_id, verbose=False)
        apio_ctx.profile.remove_package(package_id)
        apio_ctx.profile.save()

    for package_id in scan.broken_package_ids:
        print(f"Uninstalling broken package '{package_id}'")
        _delete_package_dir(apio_ctx, package_id, verbose=False)
        apio_ctx.profile.remove_package(package_id)
        apio_ctx.profile.save()

    for package_id in scan.orphan_package_ids:
        print(f"Uninstalling unknown package '{package_id}'")
        apio_ctx.profile.remove_package(package_id)
        apio_ctx.profile.save()

    for dir_name in scan.orphan_dir_names:
        print(f"Deleting unknown dir '{dir_name}'")
        # -- Sanity check. Since apio_ctx.packages_dir is guarranted to include
        # -- the word packages, this can fail only due to programming error.
        dir_path = apio_ctx.packages_dir / dir_name
        assert "packages" in str(dir_path).lower(), dir_path
        # -- Delete.
        shutil.rmtree(dir_path)

    for file_name in scan.orphan_file_names:
        print(f"Deleting unknown file '{file_name}'")
        # -- Sanity check. Since apio_ctx.packages_dir is guarranted to
        # -- include the word packages, this can fail only due to programming
        # -- error.
        file_path = apio_ctx.packages_dir / file_name
        assert "packages" in str(file_path).lower(), dir_path
        # -- Delete.
        file_path.unlink()
