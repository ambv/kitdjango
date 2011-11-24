#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 by Łukasz Langa
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

"""lck.django.cache_backends
   -------------------------

   Alternative backends for caching in Django."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from threading import local

from django.conf import settings
from django.core.cache.backends.memcached import BaseMemcachedCache


CACHE_MIN_COMPRESS_LEN = getattr(settings, 'CACHE_MIN_COMPRESS_LEN', 131072)


class PyLibMCCache(BaseMemcachedCache):
    "An implementation of the cache binding using pylibmc with compression, etc."
    def __init__(self, server, params):
        import pylibmc
        self._local = local()
        super(PyLibMCCache, self).__init__(server, params,
                                           library=pylibmc,
                                           value_not_found_exception=pylibmc.NotFound)

    @property
    def _cache(self):
        # PylibMC uses cache options as the 'behaviors' attribute.
        # It also needs to use threadlocals, because some versions of
        # PylibMC don't play well with the GIL.
        client = getattr(self._local, 'client', None)
        if client:
            return client

        client = self._lib.Client(self._servers)
        if self._options:
            client.behaviors = self._options

        self._local.client = client

        return client

    def add(self, key, value, timeout=0, version=None):
        key = self.make_key(key, version=version)
        return self._cache.add(key, value, self._get_memcache_timeout(timeout),
            min_compress_len=CACHE_MIN_COMPRESS_LEN)

    def set(self, key, value, timeout=0, version=None):
        key = self.make_key(key, version=version)
        self._cache.set(key, value, self._get_memcache_timeout(timeout),
            min_compress_len=CACHE_MIN_COMPRESS_LEN)

    def set_many(self, data, timeout=0, version=None):
        safe_data = {}
        for key, value in data.items():
            key = self.make_key(key, version=version)
            safe_data[key] = value
        self._cache.set_multi(safe_data, self._get_memcache_timeout(timeout),
            min_compress_len=CACHE_MIN_COMPRESS_LEN)

