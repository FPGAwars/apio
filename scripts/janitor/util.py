"""
Utilities used by the Apio Janitor.
"""

import os
from io import BytesIO
from typing import Dict
from datetime import date, datetime
from dataclasses import dataclass
from urllib.request import Request, urlopen
import json
import tarfile
import urllib.request
import ssl
import certifi
import requests
from scripts.janitor import models

# -- Used for outgoing https requests.
SSL_REQUEST_CONTEXT = ssl.create_default_context(cafile=certifi.where())


def github_headers() -> Dict[str, str]:
    """Returns headers with an optional github token."""
    headers = {}
    # -- This env var is set by the Janitor workflow to elevate the github
    # -- quota of API calls.
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def to_json_text(root: Dict) -> str:
    """Called during serialization as json text to convert this object
    to a json serializable dict.
    """

    def json_default(obj):
        # print(f"****json_default() called for {obj}")
        to_json_dict = getattr(obj, "to_json_dict", None)
        # print(f"** {to_json_dict=}")
        if to_json_dict is not None:
            # print("** to_json_dict found")
            return to_json_dict()
        # print("** to_json_dict not found")
        return str(obj)

    return json.dumps(root, indent=2, default=json_default)


def download_file_from_pypi_apio_release(
    version: str, file_path_in_package: str
) -> str:
    """Read a text file from a pypi apio release"""
    meta_url = f"https://pypi.org/pypi/apio/{version}/json"
    with urllib.request.urlopen(
        meta_url, context=SSL_REQUEST_CONTEXT, timeout=30
    ) as resp:
        data = json.load(resp)
    tarball_url = next(
        (
            item["url"]
            for item in data["urls"]
            if item["packagetype"] == "sdist"
        ),
        None,
    )

    assert tarball_url, meta_url

    with urllib.request.urlopen(
        tarball_url, context=SSL_REQUEST_CONTEXT, timeout=30
    ) as resp:
        blob = resp.read()
    with tarfile.open(fileobj=BytesIO(blob), mode="r:gz") as tf:
        suffix = "/" + file_path_in_package
        member = next(
            (
                m
                for m in tf.getmembers()
                if m.name.endswith(suffix) and m.isfile()
            ),
            None,
        )
        if member is None:
            raise FileNotFoundError(file_path_in_package)
        with tf.extractfile(member) as f:
            return f.read().decode("utf-8")


@dataclass(frozen=True)
class AssetMetadata:
    """Contains metadata of a single release asset."""

    url: str
    size: int
    updated: date


@dataclass(frozen=True)
class ReleaseMetadata:
    """Contains metadata of a single release."""

    is_draft: bool
    is_prerelease: bool
    assets: Dict[str, AssetMetadata]


def download_release_metadata(
    release: models.GithubReleaseRef,
) -> ReleaseMetadata:
    """Downloads metadata of given repo release."""
    # -- Construct the githug API request.
    url = (
        f"https://api.github.com/repos/{release.repo}/"
        f"releases/tags/{release.tag}"
    )

    req = Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "apio-script",
            **github_headers(),
        },
    )

    # -- Fetch the json response.
    with urlopen(req, context=SSL_REQUEST_CONTEXT, timeout=30) as resp:
        json_resp = json.loads(resp.read().decode("utf-8"))

    # -- Collect the assets metadata
    assets_metadata: Dict[str, AssetMetadata] = {}
    for json_asset in json_resp["assets"]:
        assets_metadata[json_asset["name"]] = AssetMetadata(
            json_asset["browser_download_url"],
            int(json_asset["size"]),
            datetime.fromisoformat(json_asset["updated_at"]).date(),
        )

    # -- All done
    return ReleaseMetadata(
        json_resp["draft"], json_resp["prerelease"], assets_metadata
    )


def download_release_asset(
    release: models.GithubReleaseRef,
    asset_name: str,
) -> bytes:
    """Download a release asset into an in-memory buffer."""
    url = (
        f"https://github.com/{release.repo}/releases/download/"
        f"{release.tag}/{asset_name}"
    )
    print(f"Downloading {url}")
    headers = {
        "Accept": "application/octet-stream",
        "User-Agent": "apio",
        **github_headers(),
    }
    buffer = BytesIO()
    with requests.get(
        url,
        headers=headers,
        stream=True,
        allow_redirects=True,
        timeout=(10, 60),
    ) as resp:
        resp.raise_for_status()
        for chunk in resp.iter_content(chunk_size=1024 * 1024):
            if chunk:
                buffer.write(chunk)
    buffer.seek(0)
    return buffer.getvalue()
