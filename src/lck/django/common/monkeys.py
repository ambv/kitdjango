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

"""lck.django.monkeys.models
   -------------------------

   Includes all model-related monkey patches required by lck.django. This is
   included in a separate module so it's easy to review and update if
   necessary."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.db import models

# PATCH: models.Model.save() that ignores extra kwargs.
# COMPATIBILITY: Django 1.3.0
# USED IN: common.models.DisplayCounter.bump
models.Model._lck_save = models.Model.save
models.Model.save = lambda self, force_insert=False, force_update=False, \
    using=None, *args, **kwargs: self._lck_save(force_insert, force_update, \
    using)

# PATCH: tying models.Model.__getattribute__ to models.Model.__getattr__ so
# that multiple abstract models can (but don't have to) implement __getattr__
# for advanced functionality.
# COMPATIBILITY: Django 1.3.0
# USED IN: profile.models.BasicInfo.__getattr__
models.Model.__getattr__ = models.Model.__getattribute__
