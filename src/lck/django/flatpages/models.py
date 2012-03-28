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


from django.db import models as db
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _
from lck.django.common.models import Titled, Localized, TimeTrackable


class FlatPage(Titled.NonUnique, Localized, TimeTrackable):
    url = db.CharField(_('URL'), max_length=100, db_index=True)
    content = db.TextField(_('content'), blank=True)
    enable_comments = db.BooleanField(_('enable comments'))
    template_name = db.CharField(_('template name'), max_length=70, blank=True,
        help_text=_("Example: 'flatpages/contact_page.html'. If this isn't "
            "provided, the system will use 'flatpages/default.html'."))
    registration_required = db.BooleanField(_('registration required'),
        help_text=_("If this is checked, only logged-in users will be able to "
            "view the page."))
    sites = db.ManyToManyField(Site)

    class Meta:
        verbose_name = _('flat page')
        verbose_name_plural = _('flat pages')
        ordering = ('url', 'language')
        unique_together = ('url', 'language')

    def __unicode__(self):
        return u"{} ({}) -- {}".format(self.url, self.get_language_display(),
            self.title)

    def get_absolute_url(self):
        return self.url
