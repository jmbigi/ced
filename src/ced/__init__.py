from importlib.metadata import version as _metadata_version

from ced.app import Ced
from ced.config import Config
from ced.i18n import _, setup_i18n

__all__ = ["Ced", "Config", "_", "setup_i18n"]


def _get_version() -> str:
    try:
        return _metadata_version("ced")
    except Exception:
        return "0.1.0"


__version__ = _get_version()
