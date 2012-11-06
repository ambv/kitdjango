# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.forms.models import BaseInlineFormSet


class ProfileInlineFormSet(BaseInlineFormSet):
    """Enables tying profile-related models to the User admin. To do this,
    extend an inline which model points at ``Profile`` (the model behind
    ``user.get_profile()``) with::

        formset = ProfileInlineFormSet

        def __init__(self, parent_model, admin_site):
            self.fk_name = 'profile'
            super(InlineClass, self).__init__(Profile, admin_site)

    If the ``fk_name`` is different, alter accordingly. Same goes for
    ``InlineClass`` and ``Profile``.
    """

    def __init__(self, data=None, files=None, instance=None,
                 save_as_new=False, prefix=None, queryset=None, **kwargs):
        try:
            instance = instance.get_profile()
        except Exception:
            pass # happens only on object creation
        super(ProfileInlineFormSet, self).__init__(data=data,
            files=files, instance=instance, save_as_new=save_as_new,
            prefix=prefix, queryset=queryset, **kwargs)
