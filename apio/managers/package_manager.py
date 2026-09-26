# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2021 FPGAwars
# -- Author Jesús Arroyo
# -- License GPLv2
"""Package install/uninstall functionality.
Used by the 'apio packages' command.
"""

import os
import json
from enum import Enum, unique
from datetime import datetime
from dataclasses import dataclass
from typing import Any
from pathlib import Path
import shutil
from apio.common.apio_console import cout, cstyle, fatal_error
from apio.common.apio_styles import SUCCESS, EMPH3
from apio.common.debug_util import is_debug
from apio.managers.downloader import FileDownloader
from apio.utils import util
from apio.utils.apio_platforms import ApioPlatform
from apio.managers.remote_config import RemoteConfig, PackageRemoteConfig


@unique
class RequiredPackageStatus(Enum):
    """Represents the classification of a required package status."""

    # -- NOTE: The string values here are using facing by the
    # -- 'apio packages list' command.

    PACKAGE_UNINSTALLED = "Uninstalled"
    PACKAGE_DIR_MISSING = "Package dir missing"
    PACKAGE_DIR_IS_A_FILE = "Package dir is a file"
    PACKAGE_VERSION_MISMATCH = "Version mismatch"
    PACKAGE_PLATFORM_MISMATCH = "Platform mismatch"
    PACKAGE_APIO_VERSION_MISMATCH = "Apio version mismatch"
    PACKAGE_URL_MISMATCH = "Source URL mismatch"
    PACKAGE_OK = "OK"

    @property
    def is_ok(self) -> bool:
        """Returns True if the status is of a legit package."""
        return self == self.PACKAGE_OK

    @property
    def is_inconsistency(self) -> bool:
        """Is it an inconsistency that requires fixing before installing the
        uninstalled packages."""
        return self not in (self.PACKAGE_UNINSTALLED, self.PACKAGE_OK)


@unique
class OrphanType(Enum):
    """Represents the types of orphans (leftovers items)."""

    # -- NOTE: The string values here are using facing by the
    # -- 'apio packages list' command.

    # -- Non required package in installed packages index, potentially
    # -- it also has an entry with same name in the packages folder..
    ORPHAN_PACKAGE = "Orphan package"
    # -- Package dir that doesn't match a required or an orphan package.
    ORPHAN_FILE = "Orphan file"
    # -- A file in the packages dir that doesn't match a name of an orphan
    # -- package.
    ORPHAN_DIR = "Orphan dir"


@dataclass
class PackagesScanResults:
    """Represents results of packages scan."""

    # -- Names and statuses of required packages.
    required_packages: dict[str, RequiredPackageStatus]

    # -- Name and types of package, dir, and file orphans.
    orphans: dict[str, OrphanType]

    def packages_installed_ok(self) -> bool:
        """Returns true if all the required packages are installed ok,
        regardless of other fixable errors."""
        return all(status.is_ok for status in self.required_packages.values())

    def num_inconsistencies_to_fix(self) -> int:
        """Returns the number of inconsistencies that require fixing before
        installing any missing package."""
        required_packages_inconsistencies = sum(
            1
            for status in self.required_packages.values()
            if status.is_inconsistency
        )
        # -- All orphan errors are considered to be inconsistencies.
        orphans_errors = len(self.orphans)
        return required_packages_inconsistencies + orphans_errors

    def is_all_ok(self) -> bool:
        """Return True if all packages are installed properly with no
        issues."""
        return self.packages_installed_ok() and len(self.orphans) == 0

    def dump(self):
        """Dump the content of this object. For debugging."""
        cout()
        cout("Package scan results:")
        cout(f"  required  {self.required_packages}")
        cout(f"  orphans   {self.orphans}")


def get_datetime_stamp(dt: datetime | None = None) -> str:
    """Returns a string with time now as yyyy-mm-dd-hh-mm"""
    if dt is None:
        dt = datetime.now()
    return dt.strftime("%Y-%m-%d-%H-%M")


class PackageManager:
    """Context for package managements operations.
    This class provides the information needed for package management
    operations. This is a subset of the information contained by ApioContext
    and we use it, instead of passing the ApioContext, because we need to
    perform package management operations (e.g. updating packages) before
    the ApioContext object is fully initialized.
    """

    def __init__(
        self,
        remote_config: RemoteConfig,
        required_packages: dict,
        platform: ApioPlatform,
        apio_home_dir: Path,
        packages_dir: Path,
    ):

        # pylint: disable=too-many-arguments
        # pylint: disable=too-many-positional-arguments

        # -- Same as ApioContext.remote_config
        self.remote_config = remote_config
        # -- Same as ApioContext.required_packages
        self.required_packages = required_packages
        # -- platform: ApioPlatform
        self.platform = platform
        # -- Same as ApioContext.apio_home_dir
        self.apio_home_dir = apio_home_dir
        # -- Same as ApioContext.packages_dir
        self.packages_dir = packages_dir

        # -- Sanity checks.
        assert isinstance(self.remote_config, RemoteConfig)
        assert self.required_packages
        assert self.platform
        assert self.packages_dir

        # -- Initialized installed packages, a copy of
        # -- installed-packages.json.
        self.installed_packages: dict[str, Any] = {}

        # -- Cache the packages index file path
        # -- Ex. '/home/obijuan/.apio/packages/installed_packages.json'
        self._packages_index_path = packages_dir / "installed_packages.json"

        # -- Read the installed packages file, if exists.
        self._maybe_load_installed_packages_file()

    def required_package_dir(self, package_name: str) -> Path:
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
        if is_debug(1):
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

        if is_debug(1):
            cout(f"package url parts = {url_parts}")

        # -- Concatenate the URL parts.
        url = "".join(url_parts)

        if is_debug(1):
            cout(f"Combined package url: {url}")

        # -- Replace placeholders with values.
        for name, val in url_vars.items():
            url = url.replace(name, val)

        if is_debug(1):
            cout(f"Resolved package url: {url}")

        # -- All done.
        return url

    def _download_package_file(
        self, url: str, dir_path: Path, package_name: str
    ) -> Path:
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

            downloader.download()

        # -- If the user press Ctrl-C (Abort)
        except KeyboardInterrupt:

            # -- Remove the file
            if filepath and filepath.is_file():
                filepath.unlink()

            # -- Inform the user
            fatal_error("User aborted download")

        except IOError as exc:
            fatal_error(
                f"Failed to download package '{package_name}'", cause=exc
            )

        # -- Return the destination path
        return filepath

    def _delete_package_dir(self, package_name: str, verbose: bool) -> None:
        """Delete the directory of the package with given name."""
        package_path = self.packages_dir / package_name

        # -- If doesn't exist, ignore silently.
        if not package_path.exists():
            return

        if verbose:
            cout(f"Deleting {str(package_path)}")

        if package_path.is_dir():
            # -- Sanity check the path and delete.
            assert "packages" in str(package_path).lower(), package_path
            shutil.rmtree(package_path)
        else:
            package_path.unlink()

        # -- Confirm
        if package_path.exists():
            fatal_error(
                f"Package dir deletion failed: {str(package_path.absolute())}"
            )

    def scan_and_fix_inconsistencies(self) -> bool:
        """Scan the packages and fix if there are errors. Returns true
        if the packages are installed ok."""

        # -- Scan the packages.
        scan: PackagesScanResults = self.scan_packages()

        # -- If there are fixable errors, fix them.
        if scan.num_inconsistencies_to_fix() > 0:
            self._fix_inconsistencies(scan)

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
        installed_ok = self.scan_and_fix_inconsistencies()

        # -- If the packages are installed we are done, we are done.
        if installed_ok:
            # -- Final sanity check of the packages.
            self.check_packages_post_install()
            # -- Installed ok.
            return

        # -- Here when we need to install some packages. Since we just fixed
        # -- we can't have broken or packages with version mismatch, just
        # -- installed ok, and not installed.
        # --
        # -- Get lists of installed and required packages.
        installed_packages = self.installed_packages
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
            fatal_error(
                "Packages issues detected. Use "
                + "'apio packages list' to investigate."
            )

        # -- Final sanity check of the packages.
        self.check_packages_post_install()

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

        # -- Force verbose if debug.
        if is_debug(1):
            verbose = True

        # -- Caller is responsible to check check that package name is valid
        # -- on this platform.
        assert package_name in self.required_packages, package_name

        # -- Set up installation announcement
        pending_announcement: str | None = cstyle(
            f"Installing apio package '{package_name}'", style=EMPH3
        )

        # -- If in chatty mode, announce now and clear. Otherwise we will
        # -- announce later only if actually installing.
        if verbose and pending_announcement:
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
            # -- Get the package status
            package_status = self.classify_required_package_status(
                package_name
            )

            if verbose:
                cout(
                    f"Package {package_name} status is"
                    + f" '{package_status.value}'"
                )

            # -- If the package is OK then nothing to do.
            if package_status.is_ok:
                if verbose:
                    cout(
                        f"Package {package_name} version {target_version} "
                        + "is already installed OK",
                        style=SUCCESS,
                    )
                return

        # -- Here we need to fetch and install so can be more chatty.

        # -- Here we actually do the work. Announce if we haven't done it yet.
        if pending_announcement:
            cout(pending_announcement)
            pending_announcement = None

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
            download_url, self.packages_dir, package_name
        )
        if verbose:
            cout(f"Local package file: {local_package_file}")

        # -- Delete the old package dir, if exists, to avoid name conflicts and
        # -- left over files.
        self._delete_package_dir(package_name, verbose)

        # -- Unpack the package. This creates a new package dir.
        util.unpack_tgz(local_package_file, package_dir)

        # -- Remove the package file. We don't need it anymore.
        if verbose:
            cout(f"Deleting package file {local_package_file}")
        local_package_file.unlink()

        # -- Add package and save.
        self.add_package(
            package_name, target_version, self.platform.id, download_url
        )

        # -- Inform the user!
        cout(f"Package '{package_name}' installed successfully", style=SUCCESS)

    def _fix_inconsistencies(self, scan: PackagesScanResults) -> None:
        """If the package scan result contains errors, fix them. This
        does not install missing packages, just fixing inconsistencies."""

        for package_name, package_status in scan.required_packages.items():
            if package_status.is_inconsistency:
                cout(f"Uninstalling broken package '{package_name}'")
                self._delete_package_dir(package_name, verbose=False)
                self.remove_package(package_name)

        for orphan_name, orphan_type in scan.orphans.items():
            # -- Delete an unknown entry in the installed packages index.
            if orphan_type == orphan_type.ORPHAN_PACKAGE:
                cout(f"Uninstalling unknown package '{orphan_name}'")
                self.remove_package(orphan_name)

            # -- Delete an unknown dir in the package dir.
            elif orphan_type == orphan_type.ORPHAN_DIR:
                cout(f"Deleting unknown package dir '{orphan_name}'")
                dir_path = self.packages_dir / orphan_name
                assert "packages" in str(dir_path).lower(), dir_path
                shutil.rmtree(dir_path)

            # -- Delete an unknown file in the packages dir.
            elif orphan_type == orphan_type.ORPHAN_FILE:
                cout(f"Deleting unknown package file '{orphan_name}'")
                file_path = self.packages_dir / orphan_name
                assert "packages" in str(file_path).lower(), dir_path
                file_path.unlink()

            # -- Unexpected orphan type.
            else:
                raise ValueError(f"Unknown orphan type: {orphan_type}")

    def read_package_build_info(self, package_name: str) -> dict[str, Any]:
        """Returns the BUILD-INFO.json of the package as a dict. Fatal
        error if doesn't exist or can't parse."""

        build_info_path = (
            self.required_package_dir(package_name) / "BUILD-INFO.json"
        )

        # pylint: disable=broad-exception-caught

        try:
            with open(build_info_path, encoding="utf-8") as f:
                build_info = json.load(f)
        except Exception as e:
            fatal_error(
                f"Reading/parsing [{build_info_path}] failed.", cause=e
            )

        return build_info

    def get_yosys_release_tag(self) -> str:
        """Return the version tag (e.g. "2026-03-21") of the underlying Yosys.
        This value is extract from the BUILD-INFO.json file of the apio
        oss-cad-suite package."""
        build_info = self.read_package_build_info("oss-cad-suite")
        return build_info["yosys-release-tag"]

    def check_packages_post_install(self):
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
            fatal_error(
                'The packages "oss-cad-suite" and "openxc7" were built with '
                + 'different "yosys-release-tag".',
                "Their respective BUILD-INFO.json files "
                + f'contain "{yosys_release_tag1}" vs "{yosys_release_tag2}"',
                info="This typically happens due to corrupt packages or "
                + "bad remote configuration by the Apio team.",
            )

    def classify_required_package_status(
        self, name: str
    ) -> RequiredPackageStatus:
        """Classify existing or missing entry under the package directory."""

        # pylint: disable=too-many-return-statements

        # -- Check tha the package is a required one.
        assert name in self.required_packages, name

        # -- Construct the package path.
        package_path: Path = self.required_package_dir(name)

        if name not in self.installed_packages:
            return RequiredPackageStatus.PACKAGE_UNINSTALLED

        if not package_path.exists():
            return RequiredPackageStatus.PACKAGE_DIR_MISSING

        if not package_path.is_dir():
            return RequiredPackageStatus.PACKAGE_DIR_IS_A_FILE

        # -- Get installed package info or "" if not installed.
        (
            installed_version,
            installed_platform_id,
            installed_platform_version,
            installed_src_url,
        ) = self.get_installed_package_info(name)

        # -- Get the package's remote config
        package_config: PackageRemoteConfig = (
            self.remote_config.get_package_config(name)
        )

        if (
            not installed_version
            or installed_version != package_config.release_version
        ):
            return RequiredPackageStatus.PACKAGE_VERSION_MISMATCH

        if (
            not installed_platform_id
            or installed_platform_id != self.platform.id
        ):
            return RequiredPackageStatus.PACKAGE_PLATFORM_MISMATCH

        if installed_platform_version != util.get_apio_version_str():
            return RequiredPackageStatus.PACKAGE_APIO_VERSION_MISMATCH

        true_src_url = self._construct_package_download_url(package_config)

        if installed_src_url != true_src_url:
            return RequiredPackageStatus.PACKAGE_URL_MISMATCH

        return RequiredPackageStatus.PACKAGE_OK

    def scan_packages(self) -> PackagesScanResults:
        """Scans the available and installed packages and returns
        the findings as a PackageScanResults object."""

        result = PackagesScanResults({}, {})

        # -- Scan the required packages.
        for package_name in self.required_packages:
            package_status: RequiredPackageStatus = (
                self.classify_required_package_status(package_name)
            )
            result.required_packages[package_name] = package_status

        # -- Scan the installed packages and identify orphan packages.
        for package_name in self.installed_packages:
            if package_name not in self.required_packages:
                result.orphans[package_name] = OrphanType.ORPHAN_PACKAGE

        # -- Scan the packages directory and identify orphan dirs and files.
        for path in self.packages_dir.glob("*"):
            base_name = os.path.basename(path)
            assert isinstance(base_name, str), type(base_name)

            # -- Ignore the installed packages index file.
            if base_name == "installed_packages.json":
                continue

            # -- I the dir entry is of a required or orphan package, skip it,
            # -- it will be covered by the package handling.
            if (
                base_name in result.required_packages
                or base_name in result.orphans
            ):
                continue

            # -- Classify the orphan as a dir or file.
            if path.is_dir():
                result.orphans[base_name] = OrphanType.ORPHAN_DIR
            else:
                result.orphans[base_name] = OrphanType.ORPHAN_FILE

        # -- All done
        if is_debug(1):
            result.dump()

        return result

    def _maybe_load_installed_packages_file(self):
        """Load the installed packages index file if exists, e.g.
        ~/.apio/packages/installed_packages.json, populates
        self.installed_packages with the data read.
        """

        # -- Do nothing if the file doesn't exist.
        if not self._packages_index_path.exists():
            return

        # -- Read the file as a json dict. Handle invalid content
        # -- gracefully, since this runs on every apio command.
        try:
            with open(self._packages_index_path, "r", encoding="utf8") as f:
                self.installed_packages = json.load(f)

            # -- Perform a shallow sanity check.
            # -- TODO: Do a full json validation.
            assert isinstance(
                self.installed_packages, dict
            ), "Install packages not a dict"
            for name, info in self.installed_packages.items():
                assert isinstance(
                    info, dict
                ), f"installed package '{name}' not a dict"

        except (OSError, ValueError, AssertionError) as e:
            fatal_error(
                "Invalid installed packages index file "
                + f"{self._packages_index_path}",
                cause=e,
                info="You can delete the file, "
                + "Apio will recreate it automatically.",
            )

    def _save_installed_packages(self):
        """Save the installed packages file"""

        # -- Create the enclosing folder, if it does not exist yet
        parent = self._packages_index_path.parent
        if not parent.exists():
            parent.mkdir()

        # -- Write to installed packages file.
        with open(self._packages_index_path, "w", encoding="utf8") as f:
            json.dump(self.installed_packages, f, indent=4)

        # -- Dump for debugging.
        if is_debug(1):
            cout("Saved installed packages index:", style=EMPH3)
            cout(json.dumps(self.installed_packages, indent=2))

    def get_installed_package_version(self, package_name: str) -> str:
        """Return the version of the given installed package. Fatal error
        if the package is not installed have its info is corrupt.
        """
        package_info = self.installed_packages.get(package_name)
        assert package_info is not None, package_name
        package_version = package_info.get("version")
        assert package_version is not None
        return package_version

    def get_installed_package_info(
        self, package_name: str
    ) -> tuple[str, str, str, str]:
        """Return (package_version, platform_id) of the given installed
        package. Values are replaced with "" if not installed or a value is
        missing."""
        package_info = self.installed_packages.get(package_name, {})
        package_version = package_info.get("version", "")
        platform_id = package_info.get("platform", "")
        platform_version = package_info.get("loaded-by", "")
        package_source_url = package_info.get("loaded-from", "")
        return (
            package_version,
            platform_id,
            platform_version,
            package_source_url,
        )

    def add_package(self, name: str, version: str, platform_id: str, url: str):
        """Add a package to the installed packages and save."""

        # -- Updated the installed package data.
        self.installed_packages[name] = {
            "version": version,
            "platform": platform_id,
            "loaded-by": util.get_apio_version_str(),
            "loaded-at": get_datetime_stamp(),
            "loaded-from": url,
        }
        # self._save()
        self._save_installed_packages()

    def remove_package(self, name: str):
        """Remove a package from the installed packages file. Do nothing
        if not in installed packages."""

        if name in self.installed_packages.keys():
            del self.installed_packages[name]
            # self._save()
            self._save_installed_packages()

    def get_required_package_spec(self, package_name: str) -> dict:
        """Returns the information of the package with given name.
        The information is a JSON dict originated at packages.json().
        Exits with an error message if the package is not defined.
        """
        package_info = self.required_packages.get(package_name, None)
        if package_info is None:
            fatal_error(f"Unknown package '{package_name}'")

        return package_info
