__version__ = "undefined"
try:
    from . import _version

    __version__ = _version.version
except ImportError:
    pass

TSEDA_DATA_VERSION = "1"
