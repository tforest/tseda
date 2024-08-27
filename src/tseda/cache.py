import pathlib

import appdirs
import daiquiri
import diskcache

logger = daiquiri.getLogger("cache")


def get_cache_dir():
    cache_dir = pathlib.Path(appdirs.user_cache_dir("tseda", "tseda"))
    cache_dir.mkdir(exist_ok=True, parents=True)
    return cache_dir


cache = diskcache.Cache(get_cache_dir())
