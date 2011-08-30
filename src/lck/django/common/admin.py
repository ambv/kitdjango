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

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from lck.django.common.forms import WebpImageField

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _


class ModelAdmin(admin.ModelAdmin):
    """Just like admin.ModelAdmin but silently implements a bunch of updates
    for lck.django needs."""

    def __init__(self, *args, **kwargs):
        super(ModelAdmin, self).__init__(*args, **kwargs)
        self._add_common_fields(('created', 'modified'))
        self._add_common_fields(('created_by', 'modified_by'))

    def _add_common_fields(self, fields):
        parent = super(ModelAdmin, self)
        model_fields = [field.name for field, model in
            self.model._meta.get_fields_with_model()]
        model_has_all_fields = all([arg in model_fields for arg in fields])
        if model_has_all_fields:
            self.list_filter = self.list_filter + fields
            self.readonly_fields = self.readonly_fields + fields

    def save_model(self, request, obj, form, change):
        if hasattr(obj, 'pre_save_model'):
            obj.pre_save_model(request, obj, form, change)
        obj.save()

class WebpModelAdmin(admin.ModelAdmin):
    """ Monkey patched to support webp images. """
    def formfield_for_dbfield(self, db_field, **kwargs):
        """ Any image field will have webp support out of the box. """
        if (db_field.name == 'image'):
            kwargs['form_class'] = WebpImageField
        return super(WebpModelAdmin, self).formfield_for_dbfield(
            db_field, **kwargs)

