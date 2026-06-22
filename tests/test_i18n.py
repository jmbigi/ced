from __future__ import annotations

import os

from ced.i18n import _, setup_i18n


def test_setup_i18n_default() -> None:
    """setup_i18n should not raise with no arguments (fallback to en)."""
    setup_i18n()
    assert _("ced") == "ced"


def test_setup_i18n_es() -> None:
    """Spanish translation should load key strings."""
    setup_i18n("es")
    assert _("Save current file") == "Guardar archivo actual"
    assert _("Search in file") == "Buscar en archivo"


def test_setup_i18n_en_fallback() -> None:
    """Unknown locale should fall back to English (passthrough)."""
    setup_i18n("zz")
    assert _("Save current file") == "Save current file"


def test_setup_i18n_from_env() -> None:
    """LANG env var should be used when no language is passed."""
    old = os.environ.get("LANG")
    os.environ["LANG"] = "es_ES.UTF-8"
    try:
        setup_i18n()
        assert _("Quit ced") == "Salir de ced"
    finally:
        if old:
            os.environ["LANG"] = old
        else:
            del os.environ["LANG"]


def test_setup_i18n_from_env_unknown() -> None:
    """Unknown LANG should fall back to English."""
    old = os.environ.get("LANG")
    os.environ["LANG"] = "zz_ZZ"
    try:
        setup_i18n()
        assert _("Quit ced") == "Quit ced"
    finally:
        if old:
            os.environ["LANG"] = old
        else:
            del os.environ["LANG"]
