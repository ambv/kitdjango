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

from django.core.management.base import NoArgsCommand
from optparse import make_option
from urllib2 import urlopen, URLError

from lck.django.activitylog.models import Backlink


class Command(NoArgsCommand):
    option_list = NoArgsCommand.option_list + (
        make_option('--all', action='store_true', dest='all',
            help='Verifies also previously verified backlinks.'),
    )
    help = ("Verifies backlinks by following the URL and checking whether "
            "a link back actually exists.")

    def handle_noargs(self, **options):
        verify_all = options.get('all', False)
        backlinks = Backlink.objects.select_related()
        if not verify_all:
            backlinks = backlinks.filter(verified=False)
        for backlink in backlinks:
            try:
                url = urlopen(backlink.referrer, timeout=30)
                data = url.read()
            except URLError:
                continue
            else:
                backlink.verified = backlink.site.domain in data
                if 'verified' in backlink.dirty_fields:
                    print(backlink.referrer, 'for URL', backlink.url,
                        '({} visits)'.format(backlink.visits),
                        'is' if backlink.verified else 'IS NOT', 'verified.')
                    backlink.save()
