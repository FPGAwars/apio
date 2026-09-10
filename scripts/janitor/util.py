"""
Utilities used by the Apio Janitor.
"""

import json
import tarfile
import urllib.request
from io import BytesIO
import ssl
import certifi


# -- Used for outgoing https requests.
SSL_REQUEST_CONTEXT = ssl.create_default_context(cafile=certifi.where())


def read_file_from_pypi_apio_release(
    version: str, file_path_in_package: str
) -> str:
    """Read a text file from a pypi apio release"""
    meta_url = f"https://pypi.org/pypi/apio/{version}/json"
    with urllib.request.urlopen(meta_url, context=SSL_REQUEST_CONTEXT) as resp:
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
        tarball_url, context=SSL_REQUEST_CONTEXT
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
