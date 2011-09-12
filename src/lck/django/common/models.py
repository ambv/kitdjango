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
import re

from django.conf import settings
from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.exceptions import ImproperlyConfigured
from django.core.mail import send_mail
from django.db import IntegrityError, transaction
from django.db import models as db
from django.forms import fields
from django.template.defaultfilters import urlencode
from django.utils.translation import ugettext_lazy as _

from lck.django.choices import Language
from lck.django.common import monkeys, nested_commit_on_success


EDITOR_TRACKABLE_MODEL = getattr(settings, 'EDITOR_TRACKABLE_MODEL', User)
MAC_ADDRESS_REGEX = re.compile(r'^([0-9a-fA-F]{2}([:-]?|$)){6}$')


class Named(db.Model):
    """Describes an abstract model with a unique ``name`` field."""

    name = db.CharField(verbose_name=_("name"), max_length=50, unique=True,
        db_index=True)

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

    title = db.CharField(verbose_name=_("title"), max_length=100, unique=True,
        db_index=True)

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
    cache_version = db.PositiveIntegerField(verbose_name=_("cache version"),
        default=0, editable=False)

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        super(TimeTrackable, self).__init__(*args, **kwargs)
        self._update_field_state()

    def save(self, update_modified=True, *args, **kwargs):
        if self.significant_fields_updated:
            self.cache_version += 1
            if update_modified:
                self.modified = datetime.now()
        super(TimeTrackable, self).save(*args, **kwargs)
        self._update_field_state()

    def update_cache_version(self, force=False):
        if force or self.significant_fields_updated:
            # we're not using save() to bypass signals etc.
            self.__class__.objects.filter(pk = self.pk).update(cache_version=
                db.F("cache_version") + 1)

    def _update_field_state(self):
        self._field_state = self._fields_as_dict()

    def _fields_as_dict(self):
        fields = []
        for f in self._meta.fields:
            _name = f.name
            if f.rel:
                _name += '_id'
            fields.append((_name, getattr(self, _name)))
        return dict(fields)

    @property
    def significant_fields_updated(self):
        return bool(set(self.dirty_fields.keys()) - {'cache_version',
            'modified', 'modified_by', 'display_count', 'last_active'})

    @property
    def dirty_fields(self):
        new_state = self._fields_as_dict()
        diff = []
        for k, v in self._field_state.iteritems():
            try:
                if v == new_state.get(k):
                    continue
            except (TypeError, ValueError):
                pass # offset-naive and offset-aware datetimes, etc.
            diff.append((k, v))
        return dict(diff)


class EditorTrackable(db.Model):
    created_by = db.ForeignKey(EDITOR_TRACKABLE_MODEL,
        verbose_name=_("created by"), null=True, blank=True, default=None,
        related_name='+', on_delete=db.SET_NULL)
    modified_by = db.ForeignKey(EDITOR_TRACKABLE_MODEL,
        verbose_name=_("modified by"), null=True, blank=True, default=None,
        related_name='+', on_delete=db.SET_NULL)

    class Meta:
        abstract = True

    def get_editor_from_request(self, request):
        return request.user

    def pre_save_model(self, request, obj, form, change):
        if not change:
            if not obj.created_by:
                obj.created_by = self.get_editor_from_request(request)
        else:
            obj.modified_by = self.get_editor_from_request(request)


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

    @property
    def lang(self):
        l = Language.FromID(self.language)
        return (l.name, l.desc)


class Archivable(db.Model):
    archived = db.BooleanField(verbose_name=_("is archived?"), default=False,
        db_index=True)

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

    class Meta:
        abstract = True

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
            # we're not using save() to bypass signals etc.
            self.__class__.objects.filter(pk = self.pk).update(display_count=
                db.F("display_count") + 1)


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
    deleted = db.BooleanField(verbose_name=_("deleted"), default=False,
        help_text=_("if selected, this element is not available on the "
        "website"), db_index=True)
    admin_objects = db.Manager()
    objects = ViewableSoftDeletableManager()

    class Meta:
        abstract = True


class WithConcurrentGetOrCreate(object):
    """
    The built-in ``Model.objects.get_or_create()`` doesn't work well in
    concurrent environments. This tiny mixin solves the problem.
    """
    @classmethod
    @nested_commit_on_success
    def concurrent_get_or_create(cls, **kwargs):
        try:
            obj = cls.objects.create(**kwargs)
            created = True
        except IntegrityError, e1:
            transaction.commit()
            try:
                obj = cls.objects.get(**kwargs)
            except cls.DoesNotExist, e2:
                raise e1 # there is an object with a partial argument match
            created = False
        return obj, created


class MACAddressFormField(fields.RegexField):
    default_error_messages = {
        'invalid': _(u'Enter a valid MAC address.'),
    }

    def __init__(self, *args, **kwargs):
        super(MACAddressFormField, self).__init__(MAC_ADDRESS_REGEX,
            *args, **kwargs)


class MACAddressField(db.Field):
    empty_strings_allowed = False

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 17
        super(MACAddressField, self).__init__(*args, **kwargs)

    def get_internal_type(self):
        return "CharField"

    def formfield(self, **kwargs):
        defaults = {'form_class': MACAddressFormField}
        defaults.update(kwargs)
        return super(MACAddressField, self).formfield(**defaults)

    def get_db_prep_value(self, value):
        return filter(lambda ch: ch not in ':-', value).upper()


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
