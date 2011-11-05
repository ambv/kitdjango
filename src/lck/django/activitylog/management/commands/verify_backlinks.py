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

from httplib import HTTPException
from optparse import make_option
from urllib2 import Request, build_opener, URLError

from django.conf import settings
from django.core.management.base import NoArgsCommand
from lck.django.activitylog.models import Backlink, BacklinkStatus


BACKLINK_VERIFICATION_USER_AGENT = getattr(settings,
    'BACKLINK_VERIFICATION_USER_AGENT', 'Mozilla/5.0 (X11; Linux x86_64; '
    'rv:7.0.1) Gecko/20100101 Firefox/7.0.1 lck.django')


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
        if verify_all:
            # Merged backlinks won't probably correctly verify but they have
            # been merged from verified backlinks anyway.
            backlinks = backlinks.exclude(status=BacklinkStatus.merged.id)
        else:
            backlinks = backlinks.filter(status__in=BacklinkStatus.is_verifiable())
        url_opener = build_opener()
        for backlink in backlinks:
            try:
                url = Request(backlink.referrer)
                url.add_header('User-Agent',
                    BACKLINK_VERIFICATION_USER_AGENT)
                data = url_opener.open(url, timeout=20).read()
            except (URLError, IOError, HTTPException):
                verified = False
            else:
                verified = backlink.site.domain.encode('utf8') in data
            if verified:
                # don't have to care about merged since we exclude them anyway
                backlink.status = BacklinkStatus.verified.id
            else:
                if backlink.status in BacklinkStatus.is_verified():
                    backlink.status = BacklinkStatus.verification_failed1.id
                elif backlink.status in BacklinkStatus.can_increment_failure_status():
                    backlink.status += 1
                else:
                    backlink.status = BacklinkStatus.failed.id
            if 'status' in backlink.dirty_fields:
                print(backlink.referrer, 'for URL', backlink.url,
                    '({} visits)'.format(backlink.visits),
                    'is' if backlink.status == BacklinkStatus.verified.id \
                         else 'IS NOT', 'verified.')
                backlink.save()
