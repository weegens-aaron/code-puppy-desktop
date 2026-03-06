"""Tests for utils.system_open.

We absolutely do NOT want to launch real apps during tests.
So we fake out QDesktopServices + QUrl.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from types import SimpleNamespace

from utils.system_open import open_with_default_app


class _FakeQUrl:
    def __init__(self, path: str):
        self.path = path

    @classmethod
    def fromLocalFile(cls, path: str) -> "_FakeQUrl":
        return cls(path)


class _FakeDesktopServices:
    def __init__(self):
        self.opened = []

    def openUrl(self, url: _FakeQUrl) -> bool:
        self.opened.append(url.path)
        return True


def test_open_with_default_app_returns_false_for_missing_path(tmp_path: Path):
    missing = tmp_path / "nope.txt"
    assert open_with_default_app(str(missing)) is False


def test_open_with_default_app_calls_qt_openurl(tmp_path: Path, monkeypatch):
    f = tmp_path / "hello.txt"
    f.write_text("hi")

    desktop = _FakeDesktopServices()

    # Provide the minimal Qt API surface we use.
    monkeypatch.setitem(sys.modules, "PySide6.QtCore", SimpleNamespace(QUrl=_FakeQUrl))
    monkeypatch.setitem(
        sys.modules,
        "PySide6.QtGui",
        SimpleNamespace(QDesktopServices=SimpleNamespace(openUrl=desktop.openUrl)),
    )

    assert open_with_default_app(str(f)) is True
    assert desktop.opened == [str(f)]


def test_open_with_default_app_rejects_empty_path():
    assert open_with_default_app("") is False
