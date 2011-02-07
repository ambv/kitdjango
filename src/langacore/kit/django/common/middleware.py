#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2010 Łukasz Langa
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from datetime import datetime, timedelta

from django.conf import settings
from django.core.cache import cache
from django.utils import translation

class AdminForceLanguageCodeMiddleware:
    """Add this middleware to force the admin to always use the language
    specified in ``settings.LANGUAGE_CODE`` instead of sniffing it from
    the user agent."""

    def process_request(self, request):
        if request.path.startswith('/admin'):
            request.LANG = settings.LANGUAGE_CODE
            translation.activate(request.LANG)
            request.LANGUAGE_CODE = request.LANG

class ActivityMiddleware(object):
    """Updates the `last_active` profile field for every logged in user with
    the current timestamp. It pragmatically stores a new value every 40 seconds
    (one third of the seconds specified ``CURRENTLY_ONLINE_INTERVAL`` setting).
    """

    def process_request(self, request):
        now = datetime.now()
        seconds = getattr(settings, 'CURRENTLY_ONLINE_INTERVAL', 120)
        delta = now - timedelta(seconds=seconds)
        users_online = cache.get('users_online', {})
        guests_online = cache.get('guests_online', {})
        if request.user.is_authenticated():
            users_online[request.user.id] = now
            profile = request.user.get_profile()
            last_active = profile.last_active
            if not last_active or 3 * (now - last_active).seconds > seconds:
                profile.last_active = now
                profile.save()
        else:
            guest_sid = request.COOKIES.get(settings.SESSION_COOKIE_NAME, '')
            guests_online[guest_sid] = now

        for user_id in users_online.keys():
            if users_online[user_id] < delta:
                del users_online[user_id]

        for guest_id in guests_online.keys():
            if guests_online[guest_id] < delta:
                del guests_online[guest_id]

        cache.set('users_online', users_online, 60*60*24)
        cache.set('guests_online', guests_online, 60*60*24)
