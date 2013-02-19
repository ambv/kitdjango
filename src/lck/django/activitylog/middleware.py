#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 by Łukasz Langa

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

from datetime import datetime
from time import time

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.cache import cache
from django.core.exceptions import ImproperlyConfigured
from django.db import models as db
from django.db import transaction

try:
    from django.utils.timezone import now
except ImportError:
    now = datetime.now

from lck.django.activitylog.models import UserAgent, IP, ProfileIP,\
    ProfileUserAgent, Backlink, ACTIVITYLOG_PROFILE_MODEL
from lck.django.common import model_is_user, remote_addr

class OptionBag(object): pass
_backlink_url_max_length = Backlink._meta.get_field_by_name(
    'url')[0].max_length
_backlink_referrer_max_length = Backlink._meta.get_field_by_name(
    'referrer')[0].max_length
BACKLINKS_LOCAL_SITES = getattr(
    settings, 'BACKLINKS_LOCAL_SITES', 'current',
)
CURRENTLY_ONLINE_INTERVAL = getattr(
    settings, 'CURRENTLY_ONLINE_INTERVAL', 120,
)
ACTIVITYLOG_MODE = getattr(
    settings, 'ACTIVITYLOG_MODE', 'sync',
)
ACTIVITYLOG_TASK_EXPIRATION = getattr(
    settings, 'ACTIVITYLOG_TASK_EXPIRATION', 30,
)
if ACTIVITYLOG_MODE == 'sync':
    def maybe_async(function):
        result = OptionBag()
        result.delay = function
        return result
    serial_execution = False
elif ACTIVITYLOG_MODE == 'rq':
    from django_rq import job
    maybe_async = job(
        'activitylog',
        timeout=ACTIVITYLOG_TASK_EXPIRATION,
        result_ttl=ACTIVITYLOG_TASK_EXPIRATION,
    )
    serial_execution = True
elif ACTIVITYLOG_MODE == 'celery':
    import celery
    maybe_async = celery.task(
        expires=ACTIVITYLOG_TASK_EXPIRATION,
    )
    serial_execution = True


@maybe_async
@transaction.commit_on_success
def update_activity(user_id, address, agent, _now_dt):
    ip, _ = IP.concurrent_get_or_create(
        address=address, fast_mode=serial_execution,
    )
    if agent:
        agent, _ = UserAgent.concurrent_get_or_create(
            name=agent, fast_mode=serial_execution,
        )
    else:
        agent = None
    if user_id:
        profile = User.objects.get(pk=user_id)
        if not model_is_user(ACTIVITYLOG_PROFILE_MODEL):
            profile = profile.get_profile()
        last_active = profile.last_active
        if not last_active or CURRENTLY_ONLINE_INTERVAL <= 3 * (_now_dt -
                last_active).seconds:
            # we're not using save() to bypass signals etc.
            profile.__class__.objects.filter(pk=profile.pk).update(
                last_active=_now_dt)
        pip, _ = ProfileIP.concurrent_get_or_create(
            ip=ip, profile=profile, fast_mode=serial_execution,
        )
        ProfileIP.objects.filter(pk=pip.pk).update(modified=_now_dt)
        if agent:
            pua, _ = ProfileUserAgent.concurrent_get_or_create(
                agent=agent, profile=profile, fast_mode=serial_execution,
            )
            ProfileUserAgent.objects.filter(pk=pua.pk).update(
                modified=_now_dt,
            )
    return ip, agent


@maybe_async
@transaction.commit_on_success
def update_backlinks(path_info, referrer, current_site):
    backlink, backlink_created = Backlink.concurrent_get_or_create(
        site=current_site,
        url=path_info[:_backlink_url_max_length],
        referrer=referrer[:_backlink_referrer_max_length],
        fast_mode=serial_execution,
    )
    if not backlink_created:
        # we're not using save() to bypass signals etc.
        Backlink.objects.filter(id=backlink.id).update(
            modified=now(), visits=db.F('visits') + 1,
        )


class ActivityMiddleware(object):
    """Updates the `last_active` profile field for every logged in user with
    the current timestamp. It pragmatically stores a new value every 40 seconds
    (one third of the seconds specified ``CURRENTLY_ONLINE_INTERVAL`` setting).
    """

    def process_request(self, request):
        _now_dt = now()
        _now_ts = int(time())
        delta = _now_ts - CURRENTLY_ONLINE_INTERVAL
        users_online = cache.get('users_online', {})
        guests_online = cache.get('guests_online', {})
        users_touched = False
        guests_touched = False
        if request.user.is_authenticated():
            users_online[request.user.id] = _now_ts
            users_touched = True
            user_id = request.user.id
        else:
            guest_sid = request.COOKIES.get(settings.SESSION_COOKIE_NAME)
            if guest_sid:
                guests_online[guest_sid] = _now_ts
                guests_touched = True
            user_id = None
        for uid in users_online.keys():
            try:
                is_stale_key = users_online[uid] < delta
            except TypeError:
                is_stale_key = True
            if is_stale_key:
                users_touched = True
                del users_online[uid]
        if users_touched:
            cache.set('users_online', users_online, 60 * 60 * 24)
        for gid in guests_online.keys():
            try:
                is_stale_key = guests_online[gid] < delta
            except TypeError:
                is_stale_key = True
            if is_stale_key:
                guests_touched = True
                del guests_online[gid]
        if guests_touched:
            cache.set('guests_online', guests_online, 60 * 60 * 24)
        address = remote_addr(request)
        agent = request.META.get('HTTP_USER_AGENT')
        request.activity = update_activity.delay(
            user_id, address, agent, _now_dt,
        )

    if BACKLINKS_LOCAL_SITES == 'current':
        def process_response(self, request, response):
            current_site = Site.objects.get(id=settings.SITE_ID)
            try:
                ref = request.META.get('HTTP_REFERER', '').split('//')[1]
                if response.status_code // 100 == 2 and not \
                    (ref == current_site.domain or ref.startswith(
                        current_site.domain + '/')):
                    update_backlinks.delay(
                        request.META['PATH_INFO'],
                        request.META['HTTP_REFERER'],
                        current_site,
                    )
            except (IndexError, UnicodeDecodeError):
                pass
            return response
    elif BACKLINKS_LOCAL_SITES == 'all':
        def process_response(self, request, response):
            try:
                ref = request.META.get('HTTP_REFERER', '').split('//')[1]
                if response.status_code // 100 == 2:
                    for site in Site.objects.all():
                        if ref == site.domain or \
                                ref.startswith(site.domain + '/'):
                            break
                        if site.id == settings.SITE_ID:
                            current_site = site
                    else:
                        update_backlinks.delay(
                            request.META['PATH_INFO'],
                            request.META['HTTP_REFERER'],
                            current_site,
                        )
            except (IndexError, UnicodeDecodeError):
                pass
            return response
    else:
        raise ImproperlyConfigured(
            "Unsupported value for BACKLINKS_LOCAL_SITES: {!r}"
            "".format(BACKLINKS_LOCAL_SITES),
        )
