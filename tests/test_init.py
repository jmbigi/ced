from __future__ import annotations

from unittest.mock import patch

import ced
from ced.__init__ import _get_version


def test_version_is_string() -> None:
    assert isinstance(ced.__version__, str)
    assert len(ced.__version__) > 0


def test_all_exports() -> None:
    assert hasattr(ced, "Ced")
    assert hasattr(ced, "Config")
    assert hasattr(ced, "_")
    assert hasattr(ced, "setup_i18n")
    assert ced.__all__ == ["Ced", "Config", "_", "setup_i18n"]


def test_get_version_success() -> None:
    v = _get_version()
    assert isinstance(v, str)
    assert len(v) > 0


def test_get_version_fallback() -> None:
    with patch("ced.__init__._metadata_version", side_effect=Exception("fail")):
        assert _get_version() == "0.2.0"
