#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2012 by Łukasz Langa
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

"""Test for common routines and models."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.test import TestCase


class TestHelpers(TestCase):
    def test_cut(self):
        from lck.django.common import cut
        self.assertEqual(cut("123456789", length=9), "123456789")
        self.assertEqual(cut("123456789ABC", length=9), "123456789 (...)")
        self.assertEqual(cut("123456789ABC", length=9, trailing=" ..."), "123456789 ...")
        self.assertEqual(cut("123456789ABC", length=12, trailing=" ..."), "123456789ABC")
        self.assertEqual(cut(None, length=12, trailing=" ..."), None)
        self.assertEqual(cut("", length=12, trailing=" ..."), "")
        self.assertEqual(cut("", length=0, trailing=" ..."), "")
        self.assertEqual(cut("123456789", length=-1), "12345678 (...)")


class TestModels(TestCase):
    def test_concurrent_get_or_create(self):
        from lck.dummy.defaults.models import CurrentlyConcurrent
        existing = CurrentlyConcurrent(
            name='existing',
            field1=0,
            field2=0,
            field3=0,
            field4=0,
            field5=0,
            field6=0,
        )
        existing.save()
        self.assertEqual(existing.id, 1)
        # use all unique fields properly and separate others to `defaults`
        existing2, created = CurrentlyConcurrent.concurrent_get_or_create(
            name='existing',
            field1=0,
            field2=0,
            field3=0,
            field4=0,
            defaults=dict(
                field5=0,
                field6=0,
            ),
        )
        self.assertFalse(created)
        self.assertEqual(existing, existing2)
        # try to throw non-unique fields to the arguments list
        with self.assertRaises(AssertionError):
            existing2, created = CurrentlyConcurrent.concurrent_get_or_create(
                name='existing',
                field1=0,
                field2=0,
                field3=0,
                field4=0,
                field5=0,
                field6=0,
            )
        # try to not use all unique fields in the arguments list
        with self.assertRaises(AssertionError):
            existing2, created = CurrentlyConcurrent.concurrent_get_or_create(
                name='existing',
                field1=0,
                field4=0,
            )
