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

"""lck.django.activitylog.models
   -----------------------------

   Models for storing user activity on site."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from datetime import datetime
import socket
import zlib

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.db import models as db
from django.utils.translation import ugettext_lazy as _
from dj.choices import Choices

from lck.cache import memoize
from lck.django.common.models import TimeTrackable, WithConcurrentGetOrCreate

import logging
LOG = logging.getLogger(__name__)

ACTIVITYLOG_PROFILE_MODEL = getattr(settings, 'ACTIVITYLOG_PROFILE_MODEL',
    getattr(settings, 'AUTH_PROFILE_MODULE', 'auth.User'))


@memoize
def hostname(ip, reverse=False):
    """hostname(ip) -> 'hostname'

    `ip` may be a string or ipaddr.IPAddress instance.
    If no hostname known, returns None."""
    try:
        result = socket.gethostbyaddr(str(ip))
        return result[0] if not reverse else result[2][0]
    except socket.error:
        return None


class MonitoredActivity(db.Model):
    """Describes an abstract model which holds the timestamp of last user
    activity on the site. Activity is logged using the ActivityMiddleware."""
    last_active = db.DateTimeField(verbose_name=_("last active"),
        blank=True, null=True, default=None)

    _is_online_secs = getattr(settings, 'CURRENTLY_ONLINE_INTERVAL', 120)
    _was_online_secs = getattr(settings, 'RECENTLY_ONLINE_INTERVAL', 300)

    class Meta:
        abstract = True

    def is_currently_online(self, time_limit=_is_online_secs):
        """True if the user's last activity was within the last `time_limit`
        seconds (default value 2 minutes, customizable by the
        ``CURRENTLY_ONLINE_INTERVAL`` setting."""
        return (bool(self.last_active) and
            (datetime.now() - self.last_active).seconds <= time_limit)

    def was_recently_online(self, time_limit=_was_online_secs):
        """True if the user's last activity was within the last `time_limit`
        seconds (default value 5 minutes, customizable by the
        ``RECENTLY_ONLINE_INTERVAL`` setting."""
        return self.is_currently_online(time_limit=time_limit)


class UserAgent(TimeTrackable, WithConcurrentGetOrCreate):
    # `names` can be over 350 characters in length. We cannot use `unique`
    # and `db_index` on it because MySQL doesn't support it so we use
    # a separate `hash` column for that.
    name = db.TextField(verbose_name=_("name"), blank=True, default="")
    hash = db.IntegerField(verbose_name=_("hash"), unique=True, db_index=True)
    profiles = db.ManyToManyField(ACTIVITYLOG_PROFILE_MODEL,
        verbose_name=_("profiles"), through="ProfileUserAgent", help_text="")

    class Meta:
        verbose_name = _("user agent")
        verbose_name_plural = _("user agents")

    def __unicode__(self):
        return self.name

    @classmethod
    def concurrent_get_or_create(cls, name):
        hash = cls.hash_for_name(name)
        ua, created = super(UserAgent, cls).concurrent_get_or_create(hash=hash)
        if created:
            ua.name = name
            ua.save()
        elif ua.name != name:
            LOG.warning(_("UserAgent Adler32 conflict with existing "
                "ID {} for name=[[{}]]").format(hash, name))
            return cls.concurrent_get_or_create(name + ' ')
        return ua, created

    @classmethod
    def hash_for_name(cls, name):
        return zlib.adler32(name.encode('utf8'))


class IP(TimeTrackable, WithConcurrentGetOrCreate):
    address = db.IPAddressField(verbose_name=_("IP address"),
        help_text=_("Presented as string."), unique=True,
        blank=True, null=True, default=None, db_index=True)
    number = db.BigIntegerField(verbose_name=_("IP address"),
        help_text=_("Presented as int."), editable=False, unique=True,
        null=True, blank=True, default=None)
    hostname = db.CharField(verbose_name=_("hostname"), max_length=255,
        null=True, blank=True, default=None)
    profiles = db.ManyToManyField(ACTIVITYLOG_PROFILE_MODEL,
        verbose_name=_("profiles"), help_text="", through="ProfileIP")

    class Meta:
        verbose_name = _("IP address")
        verbose_name_plural = _("IP addresses")

    def __unicode__(self):
        return "{} ({})".format(self.hostname, self.address)

    def save(self, *args, **kwargs):
        if not self.address:
            self.address = hostname(self.hostname, reverse=True)
        if not self.hostname:
            self.hostname = hostname(self.address)
        a, b, c, d = self.address.split('.')
        self.number = 0x1000000 * int(a) + \
                      0x0010000 * int(b) + \
                      0x0000100 * int(c) + \
                      0x0000001 * int(d)
        super(IP, self).save(*args, **kwargs)


class BacklinkStatus(Choices):
    _ = Choices.Choice

    unknown = _("unknown")
    verification_failed1 = _("single verification failed")
    verification_failed2 = _("two verifications failed")
    verification_failed3 = _("three verifications failed")
    failed = _("verification terminally failed")
    verified = _("verified")
    merged = _("merged")

    @classmethod
    @Choices.ToIDs
    def is_verifiable(cls):
        return (cls.unknown, cls.verification_failed1, cls.verification_failed2,
            cls.verification_failed3)

    @classmethod
    @Choices.ToIDs
    def is_partially_failed(cls):
        return (cls.verification_failed1, cls.verification_failed2,
            cls.verification_failed3)

    @classmethod
    @Choices.ToIDs
    def can_increment_failure_status(cls):
        return (cls.unknown, cls.verification_failed1, cls.verification_failed2)

    @classmethod
    @Choices.ToIDs
    def is_verified(cls):
        return (cls.verified, cls.merged)


class Backlink(TimeTrackable, WithConcurrentGetOrCreate):
    site = db.ForeignKey(Site, verbose_name=_("site"), blank=True, null=True,
        default=None)
    url = db.URLField(verbose_name=_("URL"), max_length=500, blank=True,
        default="")
    referrer = db.URLField(verbose_name=_("referrer"), max_length=500,
        blank=True, default="")
    hash = db.IntegerField(verbose_name=_("hash"), unique=True, db_index=True)
    visits = db.PositiveIntegerField(verbose_name=_("visits"), default=1)
    status = db.PositiveIntegerField(verbose_name=_("status"),
        choices=BacklinkStatus(), default=BacklinkStatus.unknown.id)

    class Meta:
        verbose_name = _("backlink")
        verbose_name_plural = _("backlinks")
        # PostgreSQL would simply use this:
        #
        #   unique_together = ('site', 'url', 'referrer')
        #
        # but MySQL cries that "Specified key was too long; max key length is
        # 767 bytes" so we have to use the `hash` field just as with the
        # UserAgent model.

    def __unicode__(self):
        return self.url

    @classmethod
    def concurrent_get_or_create(cls, site, url, referrer):
        hash = cls.hash_for_triple(site, url, referrer)
        ua, created = super(Backlink, cls).concurrent_get_or_create(hash=hash)
        if created:
            ua.site = site
            ua.url = url
            ua.referrer = referrer
            ua.save()
        elif ua.site != site or ua.url != url or ua.referrer != referrer:
            LOG.error(_("Backlink not added, Adler32 conflict with existing "
                "ID {}. URL=[[{}]]; REF=[[{}]].").format(hash, url, referrer))
        return ua, created

    @classmethod
    def hash_for_triple(cls, site, url, referrer):
        return zlib.adler32('\n'.join((str(site.id), url, referrer)).encode('utf8'))


class M2M(TimeTrackable, WithConcurrentGetOrCreate):
    user = db.ForeignKey(User, verbose_name=_("user")) # for Django-admin
    profile = db.ForeignKey(ACTIVITYLOG_PROFILE_MODEL,
        verbose_name=_("profile"))

    class Meta:
        abstract = True


class ProfileIP(M2M):
    ip = db.ForeignKey(IP, verbose_name=_("IP address"))

    class Meta:
        unique_together = (('ip', 'user'),
                           ('ip', 'profile'))
        verbose_name = _("IP address")
        verbose_name_plural =_("IP addresses")

    def __unicode__(self):
        return "{} ({})".format(self.ip, self.profile)


class ProfileUserAgent(M2M):
    agent = db.ForeignKey(UserAgent, verbose_name=_("user agent"))

    class Meta:
        unique_together = (('agent', 'user'),
                           ('agent', 'profile'))
        verbose_name = _("user agent")
        verbose_name_plural = _("user agents")

    def __unicode__(self):
        return "{} ({})".format(self.agent, self.profile)
