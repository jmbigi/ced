from __future__ import annotations

import gettext
import os
from pathlib import Path

_LOCALE_DIR = Path(__file__).resolve().parent.parent.parent / "locale"


def setup_i18n(language: str | None = None) -> None:
    """Initialize gettext translations for the given language (or LANG env)."""
    lang = language or os.environ.get("LANG", "en_US").split(".")[0]
    try:
        t = gettext.translation(
            "ced", localedir=str(_LOCALE_DIR), languages=[lang], fallback=True
        )
        t.install()
    except Exception:
        import builtins
        builtins._ = lambda s: s


def _(message: str) -> str:
    """Translate *message* using the installed gettext translations."""
    import builtins
    if hasattr(builtins, "_") and callable(builtins._):
        return builtins._(message)
    return message
