"""
Tests of managers/downloader.py
"""

import gc
import requests
from pytest import MonkeyPatch, raises
from apio.managers.downloader import FileDownloader


def test_failed_construction_safe_finalizer(monkeypatch: MonkeyPatch):
    """Tests that a FileDownloader whose construction failed, e.g. on a
    connection timeout, does not raise from its __del__ finalizer. It used
    to raise an AttributeError at garbage collection time, at an arbitrary
    point of the program (pytest reports it as an 'unraisable exception'
    error on an arbitrary test)."""

    # -- Make requests.get raise a connect timeout, as when the server is
    # -- unreachable. We mock it to avoid a dependency on real networking.
    def mock_get(*_args, **_kwargs):
        raise requests.exceptions.ConnectTimeout("test timeout")

    monkeypatch.setattr(requests, "get", mock_get)

    # -- Construct a downloader. The construction should fail before the
    # -- request field is populated.
    with raises(requests.exceptions.ConnectTimeout):
        FileDownloader("http://localhost/no-such-file.tgz")

    # -- Force the collection of the partially constructed object. With a
    # -- broken finalizer, pytest flags an 'unraisable exception' error here.
    gc.collect()
