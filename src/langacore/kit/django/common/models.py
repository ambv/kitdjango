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

"""langacore.kit.django.common.models
   ----------------------------------

   Contains a small set of useful abstract model base classes that are not
   application-specific.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from datetime import datetime

from django.conf import settings
from django.core.mail import send_mail
from django.db import models as db
from django.utils.translation import ugettext_lazy as _

from langacore.kit.django.choices import Language


class Named(db.Model):
    """Describes an abstract model with a ``name`` field."""

    name = db.CharField(verbose_name=_("name"), max_length=50, unique=True)

    class Meta:
        abstract = True

    def __unicode__(self):
        return self.name


class Titled(db.Model):
    """Describes an abstract model with a ``title`` field."""

    title = db.CharField(verbose_name=_("title"), max_length=100, unique=True)

    class Meta:
        abstract = True

    def __unicode__(self):
        return self.title


class Slugged(db.Model):
    """Describes an abstract model with a ``slug`` field."""

    slug = db.SlugField(verbose_name=_("permalink"), unique=True)

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

    def save(self):
        self.modified = datetime.now()
        super(TimeTrackable, self).save()


class Localized(db.Model):
    """Describes an abstract model which holds data in a specified
    ``language``. The language is chosen from the Language choices class
    but only from those specified in settings.LANGUAGES. The default value
    is settings.LANGUAGE_CODE."""
    language = db.PositiveIntegerField(verbose_name=_("language"),
        choices=Language(filter=set([lang[0] for lang in settings.LANGUAGES])),
            default=Language.IDFromName(settings.LANGUAGE_CODE))

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
    """Describes an abstract model which display count can be incremented by
    calling ``bump()``. Models inheriting from ``DisplayCounter`` can define
    a special ``bump_save()`` method which is called instead of the default
    ``save()`` on each ``bump()`` (for instance to circumvent updating the
    ``modified`` field if the model is also ``TimeTrackable``.
    """
    display_count = db.PositiveIntegerField(verbose_name=_("display count"),
        default=0, editable=False)

    def bump(self):
        self.display_count += 1
        if not 'bump_save' in dir(self):
            self.save()
        else:
            self.bump_save()

    class Meta:
        abstract = True


class ViewableSoftDeletableManager(db.Manager):
    """An objet manager to automatically hide objects that were soft deleted
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
