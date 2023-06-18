try:
    from ._version import version as __version__
except ImportError:
    __version__ = "unknown"

from ._reader import napari_get_reader
from ._widget import config_magic_widget

__all__ = (
    "napari_get_reader",
    "config_magic_widget",
)
