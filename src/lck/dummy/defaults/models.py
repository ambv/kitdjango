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

"""lck.dummy.defaults
   ------------------

   A minimal sample Django app for documentation generation purposes."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.db import models as db
from django.dispatch import receiver
from lck.django.activitylog.models import MonitoredActivity
from lck.django.common.models import (
    Named,
    TimeTrackable,
    WithConcurrentGetOrCreate,
)
from lck.django.profile.models import BasicInfo


class Profile(BasicInfo, MonitoredActivity):
    class Meta:
        verbose_name = 'profile'
        verbose_name = 'profiles'


class CurrentlyConcurrent(Named, WithConcurrentGetOrCreate):
    field1 = db.PositiveIntegerField()
    field2 = db.PositiveIntegerField()
    field3 = db.PositiveIntegerField()
    field4 = db.PositiveIntegerField()
    field5 = db.PositiveIntegerField()
    field6 = db.PositiveIntegerField()

    class Meta:
        unique_together = (('field1', 'field2'), ('field3', 'field4'))


class TimeConscious(Named, TimeTrackable):
    pass

# workaround for a unit test bug in Django 1.4.x

from django.contrib.auth.tests import models as auth_test_models
del auth_test_models.ProfileTestCase.test_site_profile_not_available
