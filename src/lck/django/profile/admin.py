# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.contrib import admin
from django.forms.models import BaseInlineFormSet


class ProfileInlineFormSet(BaseInlineFormSet):
    def __init__(self, data=None, files=None, instance=None,
                 save_as_new=False, prefix=None, queryset=None, **kwargs):
        try:
            instance = instance.get_profile()
        except Exception:
            pass # happens only on object creation
        super(ProfileInlineFormSet, self).__init__(data=data,
            files=files, instance=instance, save_as_new=save_as_new,
            prefix=prefix, queryset=queryset, **kwargs)
