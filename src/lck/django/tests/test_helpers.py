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

"""Tests for helpers."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

def setup():
    import os
    os.environ['DJANGO_SETTINGS_MODULE'] = 'lck.dummy'

def test_dummy():
    """Just see if the import works as expected."""
    from lck.django import common
    assert hasattr(common, 'render')

def test_cut():
    from lck.django.common import cut
    assert "123456789" == cut("123456789", length=9)
    assert "123456789 (...)" == cut("123456789ABC", length=9)
    assert "123456789 ..." == cut("123456789ABC", length=9, trailing=" ...")
    assert "123456789ABC" == cut("123456789ABC", length=12, trailing=" ...")
    assert None == cut(None, length=12, trailing=" ...")
    assert "" == cut("", length=12, trailing=" ...")
    assert "" == cut("", length=0, trailing=" ...")
    assert "12345678 (...)" == cut("123456789", length=-1)

def test_lazy_chain_simple():
    from lck.django.common import lazy_chain
    lc = lazy_chain((1,2), [3,4], "56")
    lc.xform = lambda v: int(v)
    assert (1,2,3,4,5,6) == tuple(lc)
    assert 6 == len(lc)
    assert (5,6) == tuple(lc[4:])
    assert 2 == len(lc[4:])
    assert (3,4) == tuple(lc[2:4])
    assert 2 == len(lc[2:4])
    assert (1,2,3,4) == tuple(lc[:4])
    assert 4 == len(lc[:4])
    assert (1,3) == tuple(lc[:4:2])
    assert 2 == len(lc[:4:2])
    assert (1,4) == tuple(lc[::3])
    assert 2 == len(lc[::3])
    assert 6 == lc[5]
    try:
        lc[6]
        assert False, "Index error not raised."
    except IndexError:
        pass
    try:
        lc[-1]
        assert False, "Value error not raised."
    except ValueError:
        pass
    try:
        lc["boo"]
        assert False, "Value error not raised."
    except ValueError:
        pass
    lc.xfilter = lambda v: int(v) % 2 == 0
    assert (2,4,6) == tuple(lc)
    assert 3 == len(lc)
    assert (4,6) == tuple(lc[1:])
    assert 2 == len(lc[1:])
    assert (4,6) == tuple(lc[1:3])
    assert 2 == len(lc[1:3])
    assert (2,4) == tuple(lc[:2])
    assert 2 == len(lc[:2])
    assert (2,) == tuple(lc[:2:2])
    assert 1 == len(lc[:2:2])
    assert (2,6) == tuple(lc[::2])
    assert 2 == len(lc[::2])
    assert 6 == lc[2]
    try:
        lc[3]
        assert False, "Index error not raised."
    except IndexError:
        pass

def test_lazy_chain_sorted():
    from lck.django.common import lazy_chain
    lc = lazy_chain((1,2), [3,4], "56")
    lc.xform = lambda v: int(v)
    lc.xkey = lambda v: -int(v)
    assert (5,6,3,4,1,2) == tuple(lc)
    assert 6 == len(lc)
    assert (1,2) == tuple(lc[4:])
    assert 2 == len(lc[4:])
    assert (3,4) == tuple(lc[2:4])
    assert 2 == len(lc[2:4])
    assert (5,6,3,4) == tuple(lc[:4])
    assert 4 == len(lc[:4])
    assert (5,3) == tuple(lc[:4:2])
    assert 2 == len(lc[:4:2])
    assert (5,4) == tuple(lc[::3])
    assert 2 == len(lc[::3])
    assert 2 == lc[5]
    try:
        lc[6]
        assert False, "Index error not raised."
    except IndexError:
        pass
    try:
        lc[-1]
        assert False, "Value error not raised."
    except ValueError:
        pass
    try:
        lc["boo"]
        assert False, "Value error not raised."
    except ValueError:
        pass
    lc.xfilter = lambda v: int(v) % 2 == 0
    assert (6,4,2) == tuple(lc)
    assert 3 == len(lc)
    assert (4,2) == tuple(lc[1:])
    assert 2 == len(lc[1:])
    assert (4,2) == tuple(lc[1:3])
    assert 2 == len(lc[1:3])
    assert (6,4) == tuple(lc[:2])
    assert 2 == len(lc[:2])
    assert (6,) == tuple(lc[:2:2])
    assert 1 == len(lc[:2:2])
    assert (6,2) == tuple(lc[::2])
    assert 2 == len(lc[::2])
    assert 2 == lc[2]
    try:
        lc[3]
        assert False, "Index error not raised."
    except IndexError:
        pass
