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

"""lck.django.common.models
   ------------------------

   Contains a small set of useful abstract model base classes that are not
   application-specific.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from datetime import datetime
from hashlib import sha256

from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ImproperlyConfigured
from django.core.mail import send_mail
from django.db import models as db
from django.template.defaultfilters import urlencode
from django.utils.translation import ugettext_lazy as _

from lck.django.choices import Language
from lck.django.common import monkeys


class Named(db.Model):
    """Describes an abstract model with a unique ``name`` field."""

    name = db.CharField(verbose_name=_("name"), max_length=50, unique=True)

    class Meta:
        abstract = True

    def __unicode__(self):
        return self.name

    @property
    def name_urlencoded(self):
        """Useful as in {%url some-link argument.name_urlencoded%}."""
        return urlencode(self.name, safe="")

    class NonUnique(db.Model):
        """Describes an abstract model with a non-unique ``name`` field."""

        name = db.CharField(verbose_name=_("name"), max_length=50)

        class Meta:
            abstract = True

        def __unicode__(self):
            return self.name

        @property
        def name_urlencoded(self):
            """Useful as in {%url some-link argument.name_urlencoded%}."""
            return urlencode(self.name, safe="")


class Titled(db.Model):
    """Describes an abstract model with a unique ``title`` field."""

    title = db.CharField(verbose_name=_("title"), max_length=100, unique=True)

    class Meta:
        abstract = True

    def __unicode__(self):
        return self.title

    @property
    def title_urlencoded(self):
        return urlencode(self.title, safe="")

    class NonUnique(db.Model):
        """Describes an abstract model with a non-unique ``title`` field."""

        title = db.CharField(verbose_name=_("title"), max_length=100)

        class Meta:
            abstract = True

        def __unicode__(self):
            return self.title

        @property
        def title_urlencoded(self):
            return urlencode(self.title, safe="")


class Slugged(db.Model):
    """Describes an abstract model with a unique ``slug`` field."""

    slug = db.SlugField(verbose_name=_("permalink"), unique=True)

    class Meta:
        abstract = True

    def __unicode__(self):
        return self.slug

    class NonUnique(db.Model):
        """Describes an abstract model with a non-unique ``slug`` field."""

        slug = db.SlugField(verbose_name=_("permalink"))

        class Meta:
            abstract = True

        def __unicode__(self):
            return self.slug


class TimeTrackable(db.Model):
    """Describes an abstract model whose lifecycle is tracked by time. Includes
    a ``created`` field that is set automatically upon object creation and
    a ``modified`` field that is set automatically upon calling ``save()`` on
    the object.
    """
    created = db.DateTimeField(verbose_name=_("date created"),
        default=datetime.now)
    modified = db.DateTimeField(verbose_name=_("last modified"),
        default=datetime.now)

    class Meta:
        abstract = True

    def save(self, update_modified=True, *args, **kwargs):
        if update_modified:
            self.modified = datetime.now()
        super(TimeTrackable, self).save(*args, **kwargs)


class Localized(db.Model):
    """Describes an abstract model which holds data in a specified
    ``language``. The language is chosen from the Language choices class
    but only from those specified in settings.LANGUAGES. The default value
    is settings.LANGUAGE_CODE."""
    language = db.PositiveIntegerField(verbose_name=_("language"),
        choices=Language(filter=set([lang[0] for lang in settings.LANGUAGES])),
            default=Language.IDFromName(settings.LANGUAGE_CODE))

    @property
    def lang(self):
        l = Language.FromID(self.language)
        return (l.name, l.desc)

    class Meta:
        abstract = True


class MonitoredActivity(db.Model):
    """Describes an abstract model which holds the timestamp of last user
    activity on the site. Activity is logged using the ActivityMiddleware."""
    last_active = db.DateTimeField(verbose_name=_("last active"),
        blank=True, null=True, default=None)

    _is_online_secs = getattr(settings, 'CURRENTLY_ONLINE_INTERVAL', 120)
    _was_online_secs = getattr(settings, 'RECENTLY_ONLINE_INTERVAL', 300)

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

    class Meta:
        abstract = True


class DisplayCounter(db.Model):
    """Describes an abstract model which `display_count` can be incremented by
    calling ``bump()``.

    If ``bump()`` is called with some `unique_id` as its argument, Django's
    cache will be used to ensure subsequent invocations with the same
    `unique_id` won't bump the display count. This functionality requires
    `get_absolute_url()` to be defined for the model.

    If the model is also ``TimeTrackable``, bumps won't update the `modified`
    field.
    """
    display_count = db.PositiveIntegerField(verbose_name=_("display count"),
        default=0, editable=False)

    def bump(self, unique_id=None):
        should_update = True
        if unique_id:
            if not hasattr(self, 'get_absolute_url'):
                raise ImproperlyConfigured("{} model doesn't define "
                    "get_absolute_url() required for DisplayCounter.bump() "
                    "to work with a `unique_id` argument.")
            url = self.get_absolute_url()
            hash = sha256(url).hexdigest()
            unique_id = sha256(str(unique_id)).hexdigest()
            key = "displaycounter::bump::{}::{}".format(hash, unique_id)
            should_update = not bool(cache.get(key))
            cache.set(key, True, 60*60)
        if should_update:
            self.display_count += 1
            self.save(update_modified=False)

    class Meta:
        abstract = True


class ViewableSoftDeletableManager(db.Manager):
    """An object manager to automatically hide objects that were soft deleted
    for models inheriting ``SoftDeletable``."""

    def get_query_set(self):
        # get the original query set
        query_set = super(ViewableSoftDeletableManager, self).get_query_set()
        # leave rows which are deleted
        query_set = query_set.filter(deleted=False)
        return query_set


class SoftDeletable(db.Model):
    """
    Describes an abstract models which can be soft deleted, that is instead of
    actually removing objects from the database, they have a ``deleted`` field
    which is set to ``True`` and the object is then invisible in normal
    operations (thanks to ``ViewableSoftDeletableManager``).
    """
    deleted = db.BooleanField(verbose_name=_("deleted"), default=False)
    admin_objects = db.Manager()
    objects = ViewableSoftDeletableManager()

    class Meta:
        abstract = True


# For now this needs to be at the end of the file.
# FIXME: move it where it's supposed to be.

import os
from time import sleep
from threading import Thread

class MassMailer(Thread):
    """
    A thread that can be used to mail the specified profiles with a certain
    message. After every message it waits a specified time (by default
    a second).
    """
    def __init__ (self, profiles, subject, content, inverval=1.0, force=False):
        """Creates the thread.

        :param profiles: a sequence of profiles that are to be mailed

        :param subject: the subject of the message to be sent

        :param content: the actual content to be sent

        :param interval: number of seconds to wait after sending every message

        :param force: if ``True``, privacy settings of the users are
                      disregarded
        """

        Thread.__init__(self)
        self.profiles = profiles
        self.subject = subject
        self.content = content
        self.interval = interval
        self.force = force

    def run(self):
        print("Mailer subprocess started (%d)." % os.getpid())
        for profile in self.profiles:
            mail = profile.user.email
            # FIXME: check privacy
            send_mail(self.subject, self.content, None, [mail])
            print("Mailer subprocess (%d): sent mail to %s." % (os.getpid(), mail))
            sleep(self.interval)

# NO CODE BEYOND THIS POINT
