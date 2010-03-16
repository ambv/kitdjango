# based on http://www.djangosnippets.org/snippets/793/

import time
from threading import RLock

from django.core.cache import cache
from django.conf import settings

from langacore.kit.concurrency import synchronized

# MINT_DELAY is an upper bound on how long any value should take to 
# be generated (in seconds)
CACHE_MINT_DELAY = getattr(settings, 'CACHE_MINT_DELAY', 30)
CACHE_DEFAULT_TIMEOUT = getattr(settings, 'CACHE_DEFAULT_TIMEOUT', 300)
CACHE_FILELOCK_PATH = getattr(settings, 'CACHE_FILELOCK_PATH', '/tmp/langacore_django_cache.lock')


@synchronized(path=CACHE_FILELOCK_PATH)
def get(key):
    packed_val = cache.get(key)
    if packed_val is None:
        return None
    val, refresh_time, is_stale = packed_val
    if (time.time() > refresh_time) and not is_stale:
        # Store the stale value while the cache revalidates for another
        # CACHE_MINT_DELAY seconds.
        set(key, val, timeout=CACHE_MINT_DELAY, is_stale=True)
        return None
    return val


@synchronized(path=CACHE_FILELOCK_PATH)
def set(key, val, timeout=CACHE_DEFAULT_TIMEOUT, is_stale=False):
    refresh_time = timeout + time.time()
    # if not stale, add the mint delay to the actual refresh so we can have
    # the value stored a bit longer in the backend than it would be otherwise
    real_refresh = timeout if is_stale else timeout + CACHE_MINT_DELAY
    packed_val = (val, refresh_time, is_stale)
    return cache.set(key, packed_val, real_refresh)


delete = cache.delete
