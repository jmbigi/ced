from __future__ import annotations

import os
from unittest.mock import patch

from ced.themes.manager import detect_dark_mode


class TestDetectDarkMode:
    def test_detect_dark_mode_classmethod(self) -> None:
        result = detect_dark_mode()
        assert isinstance(result, bool)

    def test_detect_dark_mode_windows_import_fails(self) -> None:
        with patch("os.name", "nt"):
            with patch("builtins.__import__", side_effect=ImportError("no winreg")):
                result = detect_dark_mode()
                assert isinstance(result, bool)

    def test_detect_dark_mode_windows_registry_error(self) -> None:
        with patch("os.name", "nt"):
            # winreg imports but raises
            class FakeWinreg:
                HKEY_CURRENT_USER = 1
                @staticmethod
                def OpenKey(*args):
                    raise OSError("registry error")
                @staticmethod
                def QueryValueEx(*args):
                    raise OSError("registry error")
            with patch("builtins.__import__", return_value=FakeWinreg):
                result = detect_dark_mode()
                assert result is True

    def test_detect_dark_mode_via_colorfgbg_dark(self) -> None:
        with patch("os.name", "posix"):
            with patch.dict(os.environ, {"COLORFGBG": "0;0;15;0"}):
                result = detect_dark_mode()
                assert result is True

    def test_detect_dark_mode_via_colorfgbg_light(self) -> None:
        with patch("os.name", "posix"):
            with patch.dict(os.environ, {"COLORFGBG": "0;0;15;15"}):
                result = detect_dark_mode()
                assert result is False

    def test_detect_dark_mode_fallback_missing_env(self) -> None:
        with patch("os.name", "posix"):
            with patch.dict(os.environ, {}, clear=True):
                result = detect_dark_mode()
                assert result is True

    def test_detect_dark_mode_exception_fallback(self) -> None:
        with patch("os.name", "nt"):
            with patch("builtins.__import__", side_effect=Exception):
                result = detect_dark_mode()
                assert result is True
