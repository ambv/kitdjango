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

"""lck.django.badges.models
   ------------------------

   Models holding badges."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import importlib
from os.path import splitext

from django.db import models as db
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.generic import GenericForeignKey
from django.utils.translation import ugettext_lazy as _
from lck.django.common.models import Named, TimeTrackable, EditorTrackable,\
    ImageModel


class BadgeMetadata(Named.NonUnique, TimeTrackable):
    key = db.CharField(verbose_name=_("key"), max_length=75, primary_key=True)
    description = db.TextField(verbose_name=_("description"),
        null=True, blank=True, default=None)
    callback = db.CharField(verbose_name=_("Python callback"), max_length=100,
        help_text=_("path to a Python function that will award/discard badges"),
        blank=True, default="")

    class Meta:
        abstract = True


class BadgeGroup(BadgeMetadata):
    """Owners can be awarded only a single badge of a specified group at
    a time."""
    multiple_allowed = db.BooleanField(verbose_name=_("multiple badges of "
        "this group allowed?"), default=False)

    class Meta:
        verbose_name = _("badge group")
        verbose_name_plural = _("badge groups")


class BadgeIcon(ImageModel):
    """Image representation of the badge."""
    image = ImageModel.image_field(upload_to='badge_icons')

    class Meta:
        verbose_name = _("badge icon")
        verbose_name_plural = _("badge icons")


class BadgeType(BadgeMetadata):
    """Describes a specific badge type."""
    group = db.ForeignKey(BadgeGroup, verbose_name=_("badge group"))
    icon = db.ForeignKey(BadgeIcon, verbose_name=_("badge icon"),
        blank=True, null=True, default=None)

    class Meta:
        verbose_name = _("badge type")
        verbose_name_plural = _("badge types")

    def get_description(self):
        return self.description or self.group.description or ""


class Badge(TimeTrackable, EditorTrackable):
    """A single badge given to an `owner` for a certain action on
    a `subject`."""
    type = db.ForeignKey(BadgeType, verbose_name=_("badge type"))
    owner_ct = db.ForeignKey(ContentType, verbose_name=_("owner (content type)"),
        related_name="%(app_label)s_%(class)s_owned_received")
    owner_oid = db.IntegerField(verbose_name=_("owner (instance id)"),
        db_index=True)
    owner = GenericForeignKey('owner_ct', 'owner_oid')
    subject_ct = db.ForeignKey(ContentType, verbose_name=_("subject (content type)"),
        related_name="%(app_label)s_%(class)s_badges_given",
        null=True, blank=True, default=None)
    subject_oid = db.IntegerField(verbose_name=_("subject (instance id)"),
        db_index=True, null=True, blank=True, default=None)
    subject = GenericForeignKey('subject_ct', 'subject_oid')
    comment = db.TextField(verbose_name=_("editor comment"),
        null=True, blank=True, default=None)

    class Meta:
        verbose_name = _("badge")
        verbose_name_plural = _("badges")

    def __unicode__(self):
        return "{} (o: {}, s: {})".format(self.type, self.owner, self.subject) 

    @classmethod
    def find_by_group(cls, group, owner, subject=None):
        return cls._find_badge('type__group__key', group, owner, subject)

    @classmethod
    def find_by_type(cls, type, owner, subject=None):
        return cls._find_badge('type__key', type, owner, subject)

    @classmethod
    def find_by_owner(cls, owner, subject=None):
        return cls._find_badge(None, None, owner, subject)

    @classmethod
    def _find_badge(cls, key, value, owner, subject=None):
        filter = {
            'owner_ct': ContentType.objects.get_for_model(owner.__class__),
            'owner_oid': owner.pk,
        }
        if value is not None:
            filter[key] = value
        if subject:
            filter['subject_ct'] = ContentType.objects.get_for_model(
                subject.__class__)
            filter['subject_oid'] = subject.pk
        badge = Badge.objects.filter(**filter)
        badge_count = badge.count()
        if badge_count > 1:
            return badge # queryset
        if badge_count == 1:
            return badge[0] # a single object
        return None

    @classmethod
    def _create(cls, type, owner, subject):
        # convoluted because of Django bugs #7551 and #12316
        badge = Badge(type=type)
        badge.owner = owner
        if subject:
            badge.subject = subject
        return badge

    @classmethod
    def award(cls, type, owner, subject=None, duplicate=False):
        """Award a badge of a specified `type` to an `owner` for actions
        on a specific `subject`.

        If there is an existing badge of the same group and the same type,
        no other badge is awarded unless `multiple_allowed` is set on the
        badge group and `duplicate` is ``True``.

        If there is an existing badge of the same group but of a different
        type, it is "upgraded" to the current type unless `multiple_allowed`
        is set on the badge and `duplicate` is ``True``. In the latter case
        a duplicate badge is awarded.
        """
        badge_type = BadgeType.objects.get(pk=type)
        old_badge = Badge.find_by_group(badge_type.group.key, owner=owner,
            subject=subject)
        if (not old_badge or old_badge.subject != subject) or \
           (badge_type.group.multiple_allowed and duplicate):
            badge = Badge._create(type=badge_type, owner=owner, subject=subject)
            badge.save()
            return badge
        if old_badge.type != badge_type:
            old_badge.delete()
            badge = Badge._create(type=badge_type, owner=owner, subject=subject)
            badge.save()
            return badge
        return None


def update_type(type, **kwargs):
    """Send a badge type callback task through Celery."""
    badge_type = BadgeType.objects.get(pk=type)
    _do_update(badge_type.callback or badge_type.group.callback, **kwargs)


def update_group(group, **kwargs):
    """Send a badge group callback task through Celery."""
    _do_update(BadgeGroup.objects.get(pk=group).callback, **kwargs)


def _do_update(callback, **kwargs):
    module, function = splitext(callback)
    mod = importlib.import_module(module)
    try:
        eval('mod{}.delay(**kwargs)'.format(function))
    except (NameError, AttributeError):
        raise ValueError("Cannot find badge callback `{}`".format(callback))
