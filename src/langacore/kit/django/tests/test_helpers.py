#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2010 Łukasz Langa
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Tests for helpers."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

def setup():
    import os
    os.environ['DJANGO_SETTINGS_MODULE'] = 'langacore.kit.dummy'

def test_dummy():
    """Just see if the import works as expected."""
    from langacore.kit.django import helpers

def test_cut():
    from langacore.kit.django.helpers import cut
    assert "123456789" == cut("123456789", length=9)
    assert "123456789 (...)" == cut("123456789ABC", length=9)
    assert "123456789 ..." == cut("123456789ABC", length=9, trailing=" ...")
    assert "123456789ABC" == cut("123456789ABC", length=12, trailing=" ...")
    assert None == cut(None, length=12, trailing=" ...")
    assert "" == cut("", length=12, trailing=" ...")
    assert "" == cut("", length=0, trailing=" ...")
    assert "12345678 (...)" == cut("123456789", length=-1)
