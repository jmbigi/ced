from importlib.metadata import PackageNotFoundError, version as _metadata_version

from ced.app import Ced
from ced.config import Config

__all__ = ["Ced", "Config"]

try:
    __version__ = _metadata_version("ced")
except PackageNotFoundError:
    __version__ = "0.1.0"
