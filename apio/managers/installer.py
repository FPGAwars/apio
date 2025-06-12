# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2021 FPGAwars
# -- Author Jesús Arroyo
# -- License GPLv2
"""Package install/uninstall functionality.
Used by the 'apio packages' command.
"""

import sys
from pathlib import Path
import shutil
from apio.common.apio_console import cout, cerror, cstyle
from apio.common.apio_styles import WARNING, ERROR, SUCCESS, EMPH3
from apio.apio_context import ApioContext
from apio.managers.downloader import FileDownloader
from apio.managers.unpacker import FileUnpacker
from apio.utils import util, pkg_util
from apio.profile import PackageRemoteConfig


def _construct_package_download_url(
    apio_ctx: ApioContext,
    target_version: str,
    package_remote_config: PackageRemoteConfig,
) -> str:
    """Construct the download URL for the given package name and version."""

    # -- Get platform ID.
    platform_id = apio_ctx.platform_id

    # -- Get the platform tag.
    platform_info = apio_ctx.platforms[platform_id]
    platform_tag = platform_info["platform-tag"]

    # -- Convert the version to "YYYY-MM-DD"
    # -- Move to a function in util.py.
    version_tokens = target_version.split(".")
    assert len(version_tokens) == 3, version_tokens
    yyyy_mm_dd = (
        f"{int(version_tokens[0]):04d}"
        + "-"
        + f"{int(version_tokens[1]):02d}"
        + "-"
        + f"{int(version_tokens[2]):02d}"
    )

    # -- Create vars mapping.
    url_vars = {
        "${PLATFORM}": platform_tag,
        "${YYYY-MM-DD}": yyyy_mm_dd,
        "${YYYYMMDD}": yyyy_mm_dd.replace("-", ""),
    }
    if util.is_debug():
        cout(f"Package URL vars: {url_vars}")

    # -- Define the url parts.
    url_parts = [
        "https://github.com/",
        package_remote_config.repo_organization,
        "/",
        package_remote_config.repo_name,
        "/releases/download/",
        package_remote_config.release_tag,
        "/",
        package_remote_config.release_file,
    ]

    if util.is_debug():
        cout(f"package url parts = {url_parts}")

    # -- Concatanate the URL parts.
    url = "".join(url_parts)

    if util.is_debug():
        cout(f"Combined package url: {url}")

    # -- Replace placeholders with values.
    for name, val in url_vars.items():
        url = url.replace(name, val)

    if util.is_debug():
        cout(f"Resolved package url: {url}")

    # -- All done.
    return url


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
        cout("User aborted download", style=ERROR)
        sys.exit(1)

    except IOError as exc:
        cout("I/O error while downloading", style=ERROR)
        cout(str(exc), style=ERROR)
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


def scan_and_fix_packages(
    apio_ctx: ApioContext, cached_config_ok: bool, verbose=False
) -> bool:
    """Scan the packages and fix if there are errors. Returns true
    if the packages are installed ok."""

    # -- Scan the packages.
    scan = pkg_util.scan_packages(
        apio_ctx, cached_config_ok=cached_config_ok, verbose=verbose
    )

    # -- If there are fixable errors, fix them.
    if scan.num_errors_to_fix() > 0:
        _fix_packages(apio_ctx, scan)

    # -- Return a flag that indicates if all packages are installed ok. We
    # -- use a scan from before the fixing but the fixing does not touch
    # -- installed ok packages.
    return scan.packages_installed_ok()


def install_missing_packages_on_the_fly(apio_ctx: ApioContext) -> None:
    """Install on the fly any missing packages. Does not print a thing if
    all packages are already ok. This function is intended for on demand
    package fetching by commands such as apio build, and thus is allowed
    to use fetched remote config instead of fetching a fresh one."""

    # -- Scan and fix broken package.
    # -- Since this is a on-the-fly operation, we don't require a fresh
    # -- remote config file for required packages versions.
    installed_ok = scan_and_fix_packages(
        apio_ctx, cached_config_ok=True, verbose=False
    )

    # -- If all the packages are installed, we are done.
    if installed_ok:
        return

    # -- Here when we need to install some packages. Since we just fixed
    # -- we can't have broken or packages with version mismatch, just
    # -- installed ok, and not installed.
    # --
    # -- Get lists of installed and required packages.
    installed_packages = apio_ctx.profile.packages
    required_packages_names = apio_ctx.platform_packages.keys()

    # -- Install any required package that is not installed.
    for package_name in required_packages_names:
        if package_name not in installed_packages:
            install_package(
                apio_ctx,
                package_name=package_name,
                force_reinstall=False,
                cached_config_ok=False,
                verbose=False,
            )

    # -- Here all packages should be ok but we check again just in case.
    scan_results = pkg_util.scan_packages(
        apio_ctx, cached_config_ok=False, verbose=False
    )
    if not scan_results.is_all_ok():
        cout(
            "Warning: packages issues detected. Use "
            "'apio packages list' to investigate.",
            style=WARNING,
        )


def install_package(
    apio_ctx: ApioContext,
    *,
    package_name: str,
    force_reinstall: bool,
    cached_config_ok: bool,
    verbose: bool,
) -> None:
    """Install a given package.

    'apio_ctx' is the context object of this apio invocation.
    'package_name' is the package name, e.g. 'examples' or 'oss-cad-suite'.
    'force' indicates if to perform the installation even if a matching
        package is already installed.
    'explicit' indicates that the user specified the package name(s) explicitly
    and thus expect more feedback in case of a 'no change'
    'verbose' indicates if to print extra information.

    Returns normally if no error, exits the program with an error status
    and a user message if an error is detected.
    """

    # -- Caller is responsible to check check that package name is valid
    # -- on this platform.
    assert package_name in apio_ctx.platform_packages, package_name

    # -- Set up installation announcement
    pending_announcement = cstyle(
        f"Installing apio package '{package_name}'", style=EMPH3
    )

    # -- If in chatty mode, announce now and clear. Otherwise we will
    # -- announce later only if actually installing.
    if verbose:
        cout(pending_announcement)
        pending_announcement = None

    # -- Get package remote config from the cache. Caller can refresh the
    # -- cache with the latest remote config if desired.
    package_config: PackageRemoteConfig = apio_ctx.profile.get_package_config(
        package_name, cached_config_ok=cached_config_ok, verbose=verbose
    )

    # -- Get the version we should have.
    target_version = package_config.release_version

    # -- If not forcing and the target version already installed then
    # -- nothing to do and we leave quietly.
    if not force_reinstall:
        # -- Get the version of the installed package, None if not installed.
        installed_version = apio_ctx.profile.get_package_installed_version(
            package_name, default=None
        )

        if verbose:
            cout(f"Installed version: {installed_version}")

        # -- If the installed and the target versions are the same then
        # -- nothing to do.
        if target_version == installed_version:
            if verbose:
                cout(
                    f"Version {target_version} is already installed",
                    style=SUCCESS,
                )
            return

    # -- Here we need to fetch and install so can be more chatty.

    # -- Here we actually do the work. Announce if we haven't done it yet.
    if pending_announcement:
        cout(pending_announcement)
        pending_announcement = True

    cout(f"Fetching version {target_version}")

    # -- Construct the download URL.
    download_url = _construct_package_download_url(
        apio_ctx, target_version, package_config
    )
    if verbose:
        cout(f"Download URL: {download_url}")

    # -- Prepare the packages directory.
    apio_ctx.packages_dir.mkdir(exist_ok=True)

    # -- Prepare the package directory.
    package_dir = apio_ctx.get_package_dir(package_name)
    cout(f"Package dir: {package_dir}")

    # -- Download the package file from the remote server.
    local_package_file = _download_package_file(
        download_url, apio_ctx.packages_dir
    )
    if verbose:
        cout(f"Local package file: {local_package_file}")

    # -- Delete the old package dir, if exists, to avoid name conflicts and
    # -- left over files.
    _delete_package_dir(apio_ctx, package_name, verbose)

    # -- Unpack the package. This creates a new package dir.
    _unpack_package_file(local_package_file, package_dir)

    # -- Remove the package file. We don't need it anymore.
    if verbose:
        cout(f"Deleting package file {local_package_file}")
    local_package_file.unlink()

    # -- Add package to profile and save.
    apio_ctx.profile.add_package(package_name, target_version)
    # apio_ctx.profile.save()

    # -- Inform the user!
    cout(f"Package '{package_name}' installed successfully", style=SUCCESS)


def _fix_packages(
    apio_ctx: ApioContext, scan: pkg_util.PackageScanResults
) -> None:
    """If the package scan result contains errors, fix them."""

    for package_name in scan.bad_version_package_names:
        cout(f"Uninstalling bad version of '{package_name}'", style=EMPH3)
        _delete_package_dir(apio_ctx, package_name, verbose=False)
        apio_ctx.profile.remove_package(package_name)

    for package_name in scan.broken_package_names:
        cout(f"Uninstalling broken package '{package_name}'", style=EMPH3)
        _delete_package_dir(apio_ctx, package_name, verbose=False)
        apio_ctx.profile.remove_package(package_name)

    for package_name in scan.orphan_package_names:
        cout(f"Uninstalling unknown package '{package_name}'", style=EMPH3)
        apio_ctx.profile.remove_package(package_name)

    for dir_name in scan.orphan_dir_names:
        cout(f"Deleting unknown package dir '{dir_name}'", style=EMPH3)
        # -- Sanity check. Since apio_ctx.packages_dir is guaranteed to include
        # -- the word packages, this can fail only due to programming error.
        dir_path = apio_ctx.packages_dir / dir_name
        assert "packages" in str(dir_path).lower(), dir_path
        # -- Delete.
        shutil.rmtree(dir_path)

    for file_name in scan.orphan_file_names:
        cout(f"Deleting unknown package file '{file_name}'", style=EMPH3)
        # -- Sanity check. Since apio_ctx.packages_dir is guaranteed to
        # -- include the word packages, this can fail only due to programming
        # -- error.
        file_path = apio_ctx.packages_dir / file_name
        assert "packages" in str(file_path).lower(), dir_path
        # -- Delete.
        file_path.unlink()
