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

from django.conf import settings
from django.test import TestCase
from django.utils.unittest import skipUnless


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


@skipUnless("lck.dummy.defaults" in settings.INSTALLED_APPS,
            "Requires lck.dummy.defaults to be installed.")
class TestModels(TestCase):
    def test_dirty_fields(self):
        from lck.dummy.defaults.models import TimeConscious
        tc1 = TimeConscious(name='tc1')
        last_modified = tc1.modified
        self.assertFalse(tc1.dirty_fields, "object initialized")
        self.assertFalse(tc1.cache_version)
        tc1.save()
        self.assertEqual(tc1.modified, last_modified)
        self.assertFalse(tc1.dirty_fields, "object saved")
        tc1.cache_version = 23
        self.assertIn('cache_version', tc1.dirty_fields,
                      "insignificant fields")
        tc1.name = 'TC1'
        self.assertIn('name', tc1.dirty_fields, "significant fields")
        tc1.save()
        self.assertNotEqual(tc1.modified, last_modified)
        last_modified = tc1.modified
        self.assertFalse(tc1.dirty_fields, "object saved")
        tc1.mark_dirty('name')
        self.assertIn('name', tc1.dirty_fields, "forced dirty")
        self.assertEqual(tc1.dirty_fields['name'], tc1.name)
        tc1.save()
        self.assertNotEqual(tc1.modified, last_modified)
        last_modified = tc1.modified
        self.assertFalse(tc1.dirty_fields, "object saved")
        tc1.mark_dirty('name')
        self.assertIn('name', tc1.dirty_fields, "forced dirty")
        self.assertEqual(tc1.dirty_fields['name'], tc1.name)
        tc1.mark_clean('name')
        self.assertFalse(tc1.dirty_fields, "cleaned forced dirty")
        tc1.save()
        self.assertEqual(tc1.modified, last_modified)
        self.assertFalse(tc1.dirty_fields, "object saved")
        tc1.name = 'tc1'
        self.assertIn('name', tc1.dirty_fields, "significant fields")
        tc1.mark_clean('name')
        self.assertIn('name', tc1.dirty_fields, "clean on a changed field")
        tc1.mark_clean('name', force=True)
        self.assertNotIn('name', tc1.dirty_fields,
                         "forced clean on a changed field")
        tc1.save()
        self.assertEqual(tc1.modified, last_modified)
        tc2 = TimeConscious.objects.get(pk=tc1.pk)
        self.assertEqual(tc2.name, 'tc1', "saved anyway")


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
