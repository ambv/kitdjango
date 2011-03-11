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

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.generic import (GenericForeignKey,
    GenericRelation)
from django.contrib.auth.models import User
from django.db import models as db
from django.db.models.signals import post_delete
from django.utils.translation import ugettext_lazy as _

from langacore.kit.django.choices import Choice
from langacore.kit.django.common.models import Named, Localized, TimeTrackable
from langacore.kit.lang import unset

TAG_AUTHOR_MODEL = getattr(settings, 'TAG_AUTHOR_MODEL', User)

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

def _tag_get_instance(instance, default=unset):
    if isinstance(instance, int):
        return instance
    elif hasattr(instance, 'pk'):
        return instance.pk
    elif default is not unset:
        return default
    raise ValueError("The given instance is neither an int nor "
        "has a `pk` attribute.")


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


class TagStemManager(db.Manager):
    """A regular manager but with a couple additional methods for easier
    stems discovery."""

    def get_all(self, official=False, author=None, language=None):
        """Returns a dictionary of all tagged objects with values being
        sets of stems for the specified object.

        This is basically an overly complex implementation that avoids
        duplicating SQL queries. A straight forward version would be::

            {obj: set(Tag.stems_for(obj.__class__, obj))
                for obj in {t.content_object for t in Tag.objects.all()}
            }
        """
        author = _tag_get_user(author, default=None)
        language = _tag_get_language(language, default=None)
        kwargs = {}
        if official:
            kwargs["official"] = True
        if author is not None:
            kwargs["author"] = author
        if language is not None:
            kwargs["language"] = language

        tagged_cts_oids = set((t.content_type_id, t.object_id)
            for t in Tag.objects.filter(**kwargs))
        tagged_cts = {id for id, _ in tagged_cts_oids}
        tagged_models = {id: ContentType.objects.get(pk=id).model_class()
            for id in tagged_cts}
        tagged_objects = set(tagged_models[ctid].objects.get(pk=oid)
            for ctid, oid in tagged_cts_oids)
        return {obj: set(self.get_queryset_for_model(obj.__class__,
            instance=obj, official=official, author=author, language=language))
            for obj in tagged_objects}

    def get_for_contenttype(self, content_type, official=False, author=None,
        language=None):
        """Returns a dictionary of all tagged objects of a given `content_type`
        with values being sets of stems for the specified object."""
        model = content_type.model_class()
        author = _tag_get_user(author, default=None)
        language = _tag_get_language(language, default=None)
        kwargs = {"content_type": content_type}
        if official:
            kwargs["official"] = True
        if author is not None:
            kwargs["author"] = author
        if language is not None:
            kwargs["language"] = language
        tagged_oids = set(t.object_id
            for t in Tag.objects.filter(**kwargs))
        tagged_objects = set(model.objects.get(pk=oid)
            for oid in tagged_oids)
        return {obj: set(self.get_queryset_for_model(obj.__class__,
            instance=obj, official=official, author=author, language=language))
            for obj in tagged_objects}

    def get_for_model(self, model, official=False, author=None, language=None):
        """Returns a dictionary of all tagged objects of a given `model` with
        values being sets of stems for the specified object. The values
        returned can be cut down to only those which are `official` or made by
        a specific `author` or given in a specific `language`.
        """
        ct = ContentType.objects.get_for_model(model)
        return self.get_for_contenttype(ct, official=official,
            author=author, language=language)

    def get_queryset_for_model(self, model, instance=None, official=False,
        author=None, language=None):
        """Returns a flat QuerySet of distinct tag stems for the given `model`,
        optionally for a specific `instance` which can be filtered only to
        `official` tags and tags by a specific `author`. The QuerySet can be
        further filtered for instance to sort by `name` or `-tag_count`.
        """
        author = _tag_get_user(author, default=None)
        language = _tag_get_language(language, default=None)
        instance = _tag_get_instance(instance, default=None)
        ct = ContentType.objects.get_for_model(model)
        relname = Tag._meta.get_field_by_name('stem')[0].rel.related_name
        kwargs = {"{}__content_type".format(relname): ct}
        if instance is not None:
            kwargs["{}__object_id".format(relname)] = instance
        if official:
            kwargs["{}__official".format(relname)] = True
        if author is not None:
            kwargs["{}__author".format(relname)] = author
        if language is not None:
            kwargs["{}__language".format(relname)] = language
        return self.filter(**kwargs).distinct()


class TagStem(Named.NU, Localized, Taggable):
    """A taggable stem of an existing tag (just the `name` in a specific
    `language`)."""
    tag_count = db.PositiveIntegerField(verbose_name=_("Tag count"), default=0)

    objects = TagStemManager()

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


class Tag(Named.NU, Localized, TimeTrackable):
    """A tag to a generic object done by
    an `author`. If the `author` is a staff member, the tag is
    `official`."""
    stem = db.ForeignKey(TagStem, verbose_name=_("Tag stem"),
        related_name="related_tags", editable=False, blank=True, null=True)
    author = db.ForeignKey(TAG_AUTHOR_MODEL, verbose_name=_("tag author"))
    official = db.BooleanField(verbose_name=_("is tag official?"),
        default=False)
    content_type = db.ForeignKey(ContentType, verbose_name=_("Content type"),
        related_name="%(app_label)s_%(class)s_tags")
    object_id = db.IntegerField(verbose_name=_("Content type instance id"),
        db_index=True)
    content_object = GenericForeignKey()

    def __unicode__(self):
        return "{} ({})".format(self.name, self.get_language_display())

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
        if hasattr(self.author, 'user') and \
            hasattr(self.author.user, 'is_staff'):
            author = self.author.user
        else:
            author = self.author
        if author.is_staff:
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
