#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 Łukasz Langa
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

"""langacore.kit.django.tags.models
   --------------------------------

   Tagging-related models. Wouldn't it be great if we just had to::

        obj.tags.all()
        obj.tag('nice', Language.en_gb, author)
        obj.untag('co za asy', Language.pl, author)"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.generic import (GenericForeignKey,
    GenericRelation)
from django.contrib.auth.models import User
from django.db import models as db
from django.db.models.signals import post_delete
from django.utils.translation import ugettext_lazy as _

from langacore.kit.django.choices import Choice
from langacore.kit.django.common.models import Named, Localized
from langacore.kit.lang import unset


def _tag_get_user(author, default=unset):
    if isinstance(author, User):
        return author
    elif hasattr(author, 'user'):
        return author.user
    elif default is not unset:
        return default
    raise ValueError("The given author is neither of type "
        "`django.contrib.auth.models.User` nor has a `user`"
        "attribute.")

def _tag_get_language(language, default=unset):
    if isinstance(language, int):
        return language
    elif isinstance(language, Choice):
        return language.id
    elif default is not unset:
        return default
    raise ValueError("The given language is neither an int nor "
        "a `Choice`.")


class Taggable(db.Model):
    """Provides the `tags` generic relation to prettify the API."""
    tags = GenericRelation("Tag")


    def tag(self, name, language, author):
        author = _tag_get_user(author)
        language = _tag_get_language(language)
        tag = Tag(name=name, language=language, author=author,
            content_object=self)
        tag.save()

    def untag(self, name, language, author):
        author = _tag_get_user(author)
        language = _tag_get_language(language)
        ct = ContentType.objects.get_for_model(self.__class__)
        try:
            tag = Tag.objects.get(name=name, language=language, author=author,
                content_type=ct, object_id=self.id)
            tag.delete()
        except Tag.DoesNotExist:
            pass # okay, successfully "untagged".

    class Meta:
        abstract = True


class TagStem(Named.NU, Localized, Taggable):
    """A taggable stem of an existing tag (just the `name` in a specific
    `language`)."""
    tag_count = db.PositiveIntegerField(verbose_name=_("Tag count"), default=0)

    def __unicode__(self):
        return "{} ({})".format(self.name, self.get_language_display())

    def inc_count(self):
        """Increases the reported tag count."""
        self.tag_count += 1
        self.save()

    def dec_count(self):
        """Decreases the reported tag count. If it reaches zero, deletes
        itself."""
        if self.tag_count > 1:
            self.tag_count -= 1
            self.save()
        else:
            self.delete()

    class Meta:
        verbose_name = _("Tag stem")
        verbose_name_plural = _("Tag stems")


class Tag(Named.NU, Localized):
    """A tag to a generic object done by
    an `author`. If the `author` is a staff member, the tag is
    `official`."""
    stem = db.ForeignKey(TagStem, verbose_name=_("Tag stem"),
        related_name="related_tags", editable=False, blank=True, null=True)
    author = db.ForeignKey(User, verbose_name=_("tag author"))
    official = db.BooleanField(verbose_name=_("is tag official?"),
        default=False)
    content_type = db.ForeignKey(ContentType, verbose_name=_("Content type"),
        related_name="%(app_label)s_%(class)s_tags")
    object_id = db.IntegerField(verbose_name=_("Content type instance id"),
        db_index=True)
    content_object = GenericForeignKey()

    def __unicode__(self):
        return "{} ({})".format(self.name, self.get_language_display())

    @classmethod
    def stems_for(cls, model, instance=None, official=False, author=None,
        language=None):
        """Returns a QuerySet of distinct tag stems for the given `model`,
        optionally for a specific `instance` which can be filtered only to
        `official` tags and tags by a specific `author`.

        The QuerySet can be further filtered for instance to sort by `name` or
        `-tag_count`."""
        author = _tag_get_user(author, default=None)
        language = _tag_get_language(language, default=None)
        ct = ContentType.objects.get_for_model(model)
        relname = cls._meta.get_field_by_name('stem')[0].rel.related_name
        kwargs = {"{}__content_type".format(relname): ct}
        if instance is not None:
            kwargs["{}__object_id".format(relname)] = instance.pk
        if official:
            kwargs["{}__official".format(relname)] = True
        if author:
            kwargs["{}__author".format(relname)] = author
        if language:
            kwargs["{}__language".format(relname)] = language
        return TagStem.objects.filter(**kwargs).distinct()

    def update_stem(self):
        """Sets the correct stem on the object and updates tag counts for
        stems. Automatically invoked during each save() for this model."""
        stem, created = TagStem.objects.get_or_create(name=self.name,
            language=self.language)
        if stem != self.stem:
            # either there wasn't a stem before or self.name or self.language
            # changed
            if self.stem:
                self.stem.dec_count()
            self.stem = stem
            self.stem.inc_count()

    def save(self, *args, **kwargs):
        if self.author.is_staff:
            self.official = True
        self.update_stem()
        return super(Tag, self).save(*args, **kwargs)


def clean_stems(sender, instance, **kwargs):
    """Decreases tag count on the stem held by the deleted tag."""
    try:
        instance.stem.dec_count()
    except (TagStem.DoesNotExist, AttributeError):
        pass
post_delete.connect(clean_stems, sender=Tag)
