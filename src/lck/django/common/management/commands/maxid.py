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

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.core.management.base import NoArgsCommand

class Command(NoArgsCommand):
    help = ("Returns the maximum value of the primary key for every registered "
        "model.")

    requires_model_validation = False

    def handle_noargs(self, **options):
        from django.db.models.loading import get_models, get_apps
        from django.db import models as db
        loaded_models = get_models()

        for app_mod in get_apps():
            app_models = get_models(app_mod)
            if not app_models:
                continue
            print("Models from '{}':".format(app_mod.__name__.split('.')[-2]))
            for model in app_models:
                name = model.__name__
                pk = model._meta.pk.name
                obj_count = model._default_manager.count()
                try:
                    obj_max = model._default_manager.aggregate(
                        db.Max(pk))['{}__max'.format(pk)]
                except ValueError:
                    obj_max = '?'
                print(" {} = {} ({} objects)".format(name, obj_max, obj_count))
