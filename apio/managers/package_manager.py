# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2021 FPGAwars
# -- Author Jesús Arroyo
# -- License GPLv2
"""Package install/uninstall functionality.
Used by the 'apio packages' command.
"""

import sys
import os
import json
from dataclasses import dataclass
from typing import Dict, List
from pathlib import Path
import shutil
from apio.common.apio_console import cout, cerror, cstyle
from apio.common.apio_styles import ERROR, SUCCESS, EMPH3, INFO
from apio.managers.downloader import FileDownloader
from apio.managers.unpacker import FileUnpacker
from apio.utils import util
from apio.utils.apio_platforms import ApioPlatform
from apio.managers.profile import Profile
from apio.managers.remote_config import RemoteConfig, PackageRemoteConfig


@dataclass
class PackageScanResults:
    """Represents results of packages scan."""

    # -- Normal and Error. Packages in required_packages that are installed
    # -- regardless if the version matches or not.
    installed_ok_package_names: List[str]
    # -- Error. Packages in required_packages that are installed but with
    # -- version mismatch.
    bad_version_package_names: List[str]
    # -- Normal. Packages in required_packages that are uninstalled properly.
    uninstalled_package_names: List[str]
    # -- Error. Packages in required_packages with broken installation. E.g,
    # -- registered in profile but package directory is missing.
    broken_package_names: List[str]
    # -- Error. Packages that are marked in profile as registered but are not
    # -- in required_packages.
    orphan_package_names: List[str]
    # -- Error. Basenames of directories in packages dir that don't match
    # -- folder_name of packages in required_packages.
    orphan_dir_names: List[str]
    # -- Error. Basenames of all files in packages directory. That directory is
    # -- expected to contain only directories for packages.a
    orphan_file_names: List[str]

    def packages_installed_ok(self) -> bool:
        """Returns true if all packages are installed ok, regardless of
        other fixable errors."""
        return (
            len(self.bad_version_package_names) == 0
            and len(self.uninstalled_package_names) == 0
            and len(self.broken_package_names) == 0
        )

    def num_errors_to_fix(self) -> int:
        """Returns the number of errors that required , having a non installed
        packages is not considered an error that need to be fix."""
        return (
            len(self.bad_version_package_names)
            + len(self.broken_package_names)
            + len(self.orphan_package_names)
            + len(self.orphan_dir_names)
            + len(self.orphan_file_names)
        )

    def is_all_ok(self) -> bool:
        """Return True if all packages are installed properly with no
        issues."""
        return (
            not self.num_errors_to_fix() and not self.uninstalled_package_names
        )

    def dump(self):
        """Dump the content of this object. For debugging."""
        cout()
        cout("Package scan results:")
        cout(f"  Installed     {self.installed_ok_package_names}")
        cout(f"  bad version   {self.bad_version_package_names}")
        cout(f"  Uninstalled   {self.uninstalled_package_names}")
        cout(f"  Broken        {self.broken_package_names}")
        cout(f"  Orphan ids    {self.orphan_package_names}")
        cout(f"  Orphan dirs   {self.orphan_dir_names}")
        cout(f"  Orphan files  {self.orphan_file_names}")


@dataclass(frozen=True)
class PackageManager:
    """Context for package managements operations.
    This class provides the information needed for package management
    operations. This is a subset of the information contained by ApioContext
    and we use it, instead of passing the ApioContext, because we need to
    perform package management operations (e.g. updating packages) before
    the ApioContext object is fully initialized.
    """

    # -- Same as ApioContext.profile
    profile: Profile
    # -- Same as ApioContext.remote_config
    remote_config: RemoteConfig
    # -- Same as ApioContext.required_packages
    required_packages: Dict
    # -- Same as ApioContext.platform
    platform: ApioPlatform
    # -- Same as ApioContext.apio_home_dir
    apio_home_dir: Path
    # -- Same as ApioContext.packages_dir
    packages_dir: Path

    def __post_init__(self):
        """Assert that all fields initialized to actual values."""
        assert isinstance(self.remote_config, RemoteConfig)
        assert self.required_packages
        assert self.platform
        assert self.packages_dir

    def package_dir(self, package_name) -> Path:
        """Return the local root directory of the package with given name"""
        # -- Validate the package name
        assert package_name in self.required_packages, package_name
        # -- Construct the path
        return self.packages_dir / package_name

    def _construct_package_download_url(
        self,
        package_remote_config: PackageRemoteConfig,
    ) -> str:
        """Construct the download URL for the given package name and
        version."""

        # -- Create vars mapping.
        url_vars = {
            "${PLATFORM}": self.platform.id,
            "${YYYYMMDD}": package_remote_config.release_tag.replace("-", ""),
        }
        if util.is_debug(1):
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

        if util.is_debug(1):
            cout(f"package url parts = {url_parts}")

        # -- Concatenate the URL parts.
        url = "".join(url_parts)

        if util.is_debug(1):
            cout(f"Combined package url: {url}")

        # -- Replace placeholders with values.
        for name, val in url_vars.items():
            url = url.replace(name, val)

        if util.is_debug(1):
            cout(f"Resolved package url: {url}")

        # -- All done.
        return url

    def _download_package_file(self, url: str, dir_path: Path) -> Path:
        """Download the given file (url). Return the path of local destination
        file. Exits with a user message and error code if any error.

        * INPUTS:
        * url: File to download
        * OUTPUTS:
        * The path of the destination file
        """

        filepath: Path | None = None

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

    def _unpack_package_file(
        self, package_file: Path, package_dir: Path
    ) -> None:
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

    def _delete_package_dir(self, package_name: str, verbose: bool) -> bool:
        """Delete the directory of the package with given name.  Returns
        True if the packages existed. Exits with an error message on error."""
        package_dir = self.packages_dir / package_name

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

    def scan_and_fix_packages(self) -> bool:
        """Scan the packages and fix if there are errors. Returns true
        if the packages are installed ok."""

        # -- Scan the packages.
        scan = self.scan_packages()

        # -- If there are fixable errors, fix them.
        if scan.num_errors_to_fix() > 0:
            self._fix_packages(scan)

        # -- Return a flag that indicates if all packages are installed ok. We
        # -- use a scan from before the fixing but the fixing does not touch
        # -- installed ok packages.
        return scan.packages_installed_ok()

    def install_missing_packages_on_the_fly(self, verbose=False) -> None:
        """Install on the fly any missing packages. Does not print a thing if
        all packages are already ok. This function is intended for on demand
        package fetching by commands such as apio build, and thus is allowed
        to use fetched remote config instead of fetching a fresh one. Exists
        with error code if any error."""

        # -- Scan and fix broken package.
        # -- Since this is a on-the-fly operation, we don't require a fresh
        # -- remote config file for required packages versions.
        installed_ok = self.scan_and_fix_packages()

        # -- If the packages are installed we are done, we are done.
        if installed_ok:
            # -- Final sanity check of the packages.
            self.check_packages()
            # -- Installed ok.
            return

        # -- Here when we need to install some packages. Since we just fixed
        # -- we can't have broken or packages with version mismatch, just
        # -- installed ok, and not installed.
        # --
        # -- Get lists of installed and required packages.
        installed_packages = self.profile.installed_packages
        required_packages_names = self.required_packages.keys()

        # -- Install any required package that is not installed.
        for package_name in required_packages_names:
            if package_name not in installed_packages:
                self.install_package(
                    package_name=package_name,
                    force_reinstall=False,
                    verbose=verbose,
                )

        # -- Here all packages should be ok but we check again just in case.
        scan_results = self.scan_packages()
        if not scan_results.is_all_ok():
            cerror(
                "Packages issues detected. Use "
                "'apio packages list' to investigate."
            )
            sys.exit(1)

        # -- Final sanity check of the packages.
        self.check_packages()

    def install_package(
        self,
        *,
        package_name: str,
        force_reinstall: bool,
        verbose: bool,
    ) -> None:
        """Install a given package.

        'package_name' is the package name, e.g. 'examples' or 'oss-cad-suite'.
        'force' indicates if to perform the installation even if a matching
            package is already installed.
        'explicit' indicates that the user specified the package name(s)
        explicitly and thus expect more feedback in case of a 'no change'
        'verbose' indicates if to print extra information.

        Returns normally if no error, exits the program with an error status
        and a user message if an error is detected.
        """

        # -- Caller is responsible to check check that package name is valid
        # -- on this platform.
        assert package_name in self.required_packages, package_name

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
        package_config: PackageRemoteConfig = (
            self.remote_config.get_package_config(package_name)
        )

        # -- Get the version we should have.
        target_version = package_config.release_version

        # -- If not forcing and the target version already installed then
        # -- nothing to do and we leave quietly.
        if not force_reinstall:
            # -- Get the version of the installed package, None if not
            # -- installed.
            installed_version, package_platform_id = (
                self.profile.get_installed_package_info(package_name)
            )

            if verbose:
                cout(
                    f"Installed version: {installed_version} "
                    f"({package_platform_id})"
                )

            # -- If the installed and the target versions are the same then
            # -- nothing to do.
            if (
                target_version == installed_version
                and package_platform_id == self.platform.id
            ):
                if verbose:
                    cout(
                        f"Version {target_version} ({package_platform_id}) "
                        "already installed",
                        style=SUCCESS,
                    )
                return

        # -- Here we need to fetch and install so can be more chatty.

        # -- Here we actually do the work. Announce if we haven't done it yet.
        if pending_announcement:
            cout(pending_announcement)
            pending_announcement = True

        cout(f"Fetching version {target_version} ({self.platform.id})")

        # -- Construct the download URL.
        download_url = self._construct_package_download_url(package_config)
        if verbose:
            cout(f"Download URL: {download_url}")

        # -- Prepare the packages directory.
        self.packages_dir.mkdir(exist_ok=True)

        # -- Prepare the package directory.
        package_dir = self.packages_dir / package_name
        cout(f"Package dir: {package_dir}")

        # -- Download the package file from the remote server.
        local_package_file = self._download_package_file(
            download_url, self.packages_dir
        )
        if verbose:
            cout(f"Local package file: {local_package_file}")

        # -- Delete the old package dir, if exists, to avoid name conflicts and
        # -- left over files.
        self._delete_package_dir(package_name, verbose)

        # -- Unpack the package. This creates a new package dir.
        self._unpack_package_file(local_package_file, package_dir)

        # -- Remove the package file. We don't need it anymore.
        if verbose:
            cout(f"Deleting package file {local_package_file}")
        local_package_file.unlink()

        # -- Add package to profile and save.
        self.profile.add_package(
            package_name, target_version, self.platform.id, download_url
        )

        # -- Inform the user!
        cout(f"Package '{package_name}' installed successfully", style=SUCCESS)

    def _fix_packages(self, scan: "PackageScanResults") -> None:
        """If the package scan result contains errors, fix them."""

        for package_name in scan.bad_version_package_names:
            cout(f"Uninstalling incompatible version of '{package_name}'")
            self._delete_package_dir(package_name, verbose=False)
            self.profile.remove_package(package_name)

        for package_name in scan.broken_package_names:
            cout(f"Uninstalling broken package '{package_name}'")
            self._delete_package_dir(package_name, verbose=False)
            self.profile.remove_package(package_name)

        for package_name in scan.orphan_package_names:
            cout(f"Uninstalling unknown package '{package_name}'")
            self.profile.remove_package(package_name)

        for dir_name in scan.orphan_dir_names:
            cout(f"Deleting unknown package dir '{dir_name}'")
            # -- Sanity check. Since package_manager.packages_dir is guaranteed
            # -- to include the word packages, this can fail only due to
            # -- programming error.
            dir_path = self.packages_dir / dir_name
            assert "packages" in str(dir_path).lower(), dir_path
            # -- Delete.
            shutil.rmtree(dir_path)

        for file_name in scan.orphan_file_names:
            cout(f"Deleting unknown package file '{file_name}'")
            # -- Sanity check. Since package_manager.packages_dir is guaranteed
            # -- to include the word packages, this can fail only due to
            # -- programming error.
            file_path = self.packages_dir / file_name
            assert "packages" in str(file_path).lower(), dir_path
            # -- Delete.
            file_path.unlink()

    def read_package_build_info(self, package_name: str) -> str:
        """Returns the BUILD-INFO.json of the package as a dict. Fatal
        error if doesn't exist or can't parse."""

        build_info_path = self.package_dir(package_name) / "BUILD-INFO.json"

        # pylint: disable=broad-exception-caught

        try:
            with open(build_info_path, encoding="utf-8") as f:
                build_info = json.load(f)
        except Exception as e:
            cerror(f"Reading/parsing [{build_info_path}] failed.", str(e))
            sys.exit(1)

        return build_info

    def get_yosys_release_tag(self) -> str:
        """Return the version tag (e.g. "2026-03-21") of the underlying Yosys.
        This value is extract from the BUILD-INFO.json file of the apio
        oss-cad-suite package."""
        build_info = self.read_package_build_info("oss-cad-suite")
        return build_info["yosys-release-tag"]

    def check_packages(self):
        """Called after the Apio packages were installed or fixed and are
        believed to be correct. Performs additional validation of the apio
        packages and exits with an error on any error."""

        # -- Read the build info of the two packages.
        build_info1 = self.read_package_build_info("oss-cad-suite")
        build_info2 = self.read_package_build_info("openxc7")

        # -- Extract the version of the underlying yosys
        yosys_release_tag1 = build_info1["yosys-release-tag"]
        yosys_release_tag2 = build_info2["yosys-release-tag"]

        # -- Compare the versions.
        if yosys_release_tag1 != yosys_release_tag2:
            cerror(
                'The packages "oss-cad-suite" and "openxc7" were built with '
                'different "yosys-release-tag".',
                f"Their respective BUILD-INFO.json files "
                f'contain "{yosys_release_tag1}" vs "{yosys_release_tag2}"',
            )
            cout(
                "This typically happens due to corrupt packages or bad remote "
                "configuration by the Apio team.",
                style=INFO,
            )
            sys.exit(1)

    def package_version_ok(
        self,
        package_name: str,
    ) -> bool:
        """Return true if the package is both in profile and required packages
        and its version in the profile meet the requirements in the
        config.jsonc file. Otherwise return false."""

        # If this package is not applicable to this platform, return False.
        if package_name not in self.required_packages:
            return False

        # -- If the current version is not available, the package is not
        # -- installed.
        current_ver, package_platform_id = (
            self.profile.get_installed_package_info(package_name)
        )
        if not current_ver or package_platform_id != self.platform.id:
            return False

        # -- Get the package remote config.
        package_config: PackageRemoteConfig = (
            self.remote_config.get_package_config(package_name)
        )

        # -- Compare to the required version. We expect the two version to be
        # -- normalized and ths a string comparison is sufficient.
        return current_ver == package_config.release_version

    def scan_packages(self) -> PackageScanResults:
        """Scans the available and installed packages and returns
        the findings as a PackageScanResults object."""

        # pylint: disable=too-many-branches

        # Initialize the result with empty data.
        result = PackageScanResults([], [], [], [], [], [], [])

        # -- A helper set that we populate with the 'folder_name' values of the
        # -- all the packages for this platform.
        platform_folder_names = set()

        # -- Scan packages ids in required_packages and populate
        # -- the installed/uninstall/broken packages lists.
        for package_name in self.required_packages.keys():
            # -- Collect package's folder names in a set. For a later use.
            platform_folder_names.add(package_name)

            # -- Classify the package as one of four cases.
            in_profile = package_name in self.profile.installed_packages
            package_dir = self.packages_dir / package_name
            has_dir = package_dir.is_dir()
            version_ok = self.package_version_ok(package_name)
            if in_profile and has_dir:
                if version_ok:
                    # Case 1: Package installed ok.
                    result.installed_ok_package_names.append(package_name)
                else:
                    # -- Case 2: Package installed but version mismatch.
                    result.bad_version_package_names.append(package_name)
            elif not in_profile and not has_dir:
                # -- Case 3: Package not installed.
                result.uninstalled_package_names.append(package_name)
            else:
                # -- Case 4: Package is broken.
                result.broken_package_names.append(package_name)

        # -- Scan the packages ids that are registered in profile as installed
        # -- the ones that are not required_packages as orphans.
        for package_name in self.profile.installed_packages:
            if package_name not in self.required_packages:
                result.orphan_package_names.append(package_name)

        # -- Scan the packages directory and identify orphan dirs and files.
        for path in self.packages_dir.glob("*"):
            base_name = os.path.basename(path)
            if path.is_dir():
                if base_name not in platform_folder_names:
                    result.orphan_dir_names.append(base_name)
            else:
                # -- Skip the packages installed file, so we don't consider it
                # -- as an orphan file.
                # TODO Make this a const.
                if base_name == "installed_packages.json":
                    continue
                result.orphan_file_names.append(base_name)

        # -- Return results
        if util.is_debug(1):
            result.dump()

        return result
