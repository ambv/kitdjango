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

"""lck.django.tags.models
   ----------------------

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
from django.core.exceptions import ImproperlyConfigured
from django.db import models as db
from django.db.models.signals import post_delete
from django.utils.translation import ugettext_lazy as _

from lck.django.choices import Choice, Language
from lck.django.common.models import Named, Localized, TimeTrackable
from lck.django.tags.helpers import parse_tag_input
from lck.lang import unset

TAG_AUTHOR_MODEL = getattr(settings, 'TAG_AUTHOR_MODEL', User)


def _tag_get_user(author, default=unset):
    author_model = Tag.author.field.rel.to
    if isinstance(author, author_model):
        return author
    elif isinstance(author, User) and isinstance(author.get_profile(),
        author_model):
        return author.get_profile()
    elif hasattr(author, 'user') and isinstance(author.user, author_model):
        return author.user
    elif hasattr(author, 'profile') and isinstance(author.profile,
        author_model):
        return author.profile
    elif default is not unset:
        return default
    raise ValueError("The given author is neither of type `{}` nor has "
        "a `user` or `profile` attribute of this type."
        "".format(author_model))

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


class TaggableBase(db.Model):
    """Provides the `tags` generic relation to prettify the API."""
    tags = GenericRelation("Tag")

    def tag(self, name, language, author):
        """Tags this object using a `name` in a specific `language`. The tag
        will be marked as authored by `author`.

        The `name` can be a list of comma-separated tags. Double quotes can be
        used to escape values with spaces or commas. One special case: if there
        are no commas in the input, spaces are treated as tag delimiters."""
        author = _tag_get_user(author)
        language = _tag_get_language(language)
        tags = parse_tag_input(name)
        for tag_name in tags:
            tag = Tag(name=tag_name, language=language, author=author,
                content_object=self)
            tag.save()

    def untag(self, name, language, author):
        """Untags this object from tags in a specific `language`, authored by
        `author`.

        The `name` can be a list of comma-separated tags. Double quotes can be
        used to escape values with spaces or commas. One special case: if there
        are no commas in the input, spaces are treated as tag delimiters."""
        author = _tag_get_user(author)
        language = _tag_get_language(language)
        ct = ContentType.objects.get_for_model(self.__class__)
        tags = parse_tag_input(name)
        for tag_name in tags:
            try:
                tag = Tag.objects.get(name=tag_name, language=language,
                    author=author, content_type=ct, object_id=self.id)
                tag.delete()
            except Tag.DoesNotExist:
                pass # okay, successfully "untagged".

    def untag_all(self, name=None, language=None, author=None):
        """untag_all([name], [language], [author])

        Untags this object from all tags in a specific `language` or authored
        by `author`."""
        author = _tag_get_user(author, default=None)
        language = _tag_get_language(language, default=None)
        ct = ContentType.objects.get_for_model(self.__class__)
        kwargs = dict(content_type=ct, object_id=self.id)
        if name is not None:
            kwargs['name__in'] = parse_tag_input(name)
        if language is not None:
            kwargs['language'] = language
        if author is not None:
            kwargs['author'] = author
        tags = Tag.objects.filter(**kwargs)
        tags.delete()


    def similar_objects(self, same_type=False, official=False):
        """similar_objects([same_type, official]) -> [(obj, distance), (obj, distance), ...]

        Returns a sorted list of similar objects in tuples (the object itself,
        the distance to the `self` object). If there are no similar objects,
        the list returned is empty. Searching for similar objects can be
        constrained to the objects of the same type (if `same_type` is
        True).

        Objects are similar when they share the same tags. Distance is the
        number of tags that are not shared by the two objects (specifically,
        the object has distance 0 to itself). Distance calculation by default
        uses all tags present on the object. If `official` is True, only the
        official tags are taken into account.
        """

        kwargs = {"official": official}
        if same_type:
            kwargs['model'] = self.__class__
        stems = TagStem.objects.get_dictionary(**kwargs)
        distance = []
        if self in stems:
            self_stems = stems[self]
            del stems[self]
        else:
            # may happen if this object is not available through Model.objects,
            # e.g. the model has a custom manager which filters it out
            self_stems = set((i[0] for i in
                TagStem.objects.get_queryset_for_model(self.__class__,
                self).values_list('name')))
        for obj, s in stems.iteritems():
            if not s & self_stems:
                # things without a single common tag are not similar at all
                continue
            distance.append((obj, len(s ^ self_stems)))
        distance.sort(key=lambda elem: elem[1])
        return distance

    def get_tags(self, official=True, author=None, language=None):
        """get_tags([official, author, language]) -> [TagStem, TagStem, ...]

        A convenience getter for tags on the current taggable. By default gets
        the `official` tags by no specific `author` and in any `language`."""
        return TagStem.objects.get_queryset_for_model(self.__class__, self,
            official=official, author=author, language=language).extra(
                select={'lname': 'lower(tags_tagstem.name)'}).order_by('lname')

    class Meta:
        abstract = True


class DefaultTags(db.CharField):
    def __init__(self, *args, **kwargs):
        defaults = dict(verbose_name=_("default tags"), max_length=1000,
            blank=True, default="")
        defaults.update(kwargs)
        super(DefaultTags, self).__init__(*args, **defaults)


class Taggable(TaggableBase):
    """Provides the `tags` generic relation and default tags that can be edited
    straight from the admin."""
    _default_tags = DefaultTags()

    # To be used like Named.NonUnique, etc.
    NoDefaultTags = TaggableBase

    def _get_default_tags_author(self):
        allowed_author_type = Tag.author.field.rel.to
        if hasattr(self, 'default_tags_author'):
            author_lookup_fields = [getattr(self, 'default_tags_author')]
        else:
            author_lookup_fields = ['created_by', 'author', 'user', 'sender']
        for field_name in author_lookup_fields:
            try:
                _author = getattr(self, field_name)
                if isinstance(_author, allowed_author_type):
                    return _author
            except AttributeError:
                continue
        raise ImproperlyConfigured("No compatible author field found for "
            "default tags.")

    def _get_default_tags_language(self):
        if hasattr(self, 'default_tags_language'):
            language_lookup_fields = [getattr(self, self.default_tags_language)]
        else:
            language_lookup_fields = ['language', 'lang']
        for field_name in language_lookup_fields:
            try:
                _language = getattr(self, field_name)
                if isinstance(_language, tuple):
                    _language = _language[0]
                if isinstance(_language, int):
                    return _language
                elif isinstance(_language, basestring):
                    return Language.IDFromName(_language)
            except AttributeError:
                continue
        raise ImproperlyConfigured("No compatible language field found for "
            "default tags.")

    def save(self, *args, **kwargs):
        tag_author = self._get_default_tags_author()
        tag_lang = self._get_default_tags_language()
        self._default_tags = ", ".join(parse_tag_input(self._default_tags))
        new = not bool(self.pk)
        if not new:
            # FIXME: this two-step approach may delete tags on tags
            self.untag_all(author=tag_author)
            self.tag(self._default_tags, tag_lang, tag_author)
        super(Taggable, self).save(*args, **kwargs)
        if new:
            self.tag(self._default_tags, tag_lang, tag_author)

    class Meta:
        abstract = True


class TagStemManager(db.Manager):
    """A regular manager but with a couple additional methods for easier
    stems discovery."""

    def get_dictionary(self, model=None, content_type=None, stem=None,
        stems=None, official=False, author=None, language=None):
        """Returns a dictionary of all tagged objects with values being
        sets of raw stems (strings) for the specified object.

        This is basically an overly complex implementation that avoids
        duplicating SQL queries. A straight forward version would be::

            {obj: set(TagStem.objects.get_queryset_for_model(obj.__class__, obj))
                for obj in {t.content_object for t in Tag.objects.all()}
            }
        """
        tagged_objects = self.get_content_objects(model=model,
            content_type=content_type, stem=stem, stems=stems,
            official=official, author=author, language=language)
        return {obj: set((i[0] for i in self.get_queryset_for_model(
            obj.__class__, instance=obj, official=official, author=author,
            language=language).values_list('name'))) for obj in tagged_objects}

    def get_content_objects(self, model=None, content_type=None, stem=None,
        stems=None, official=False, author=None, language=None):
        """Returns a set of tagged objects."""
        author = _tag_get_user(author, default=None)
        language = _tag_get_language(language, default=None)
        kwargs = {}
        if model:
            if content_type:
                raise ValueError("Both `model` and `content_type` arguments "
                    "specified. Use one.")
            content_type = ContentType.objects.get_for_model(model)
        if content_type:
            kwargs["content_type"] = content_type
            tagged_models = {content_type.id: content_type.model_class()}
        if stem:
            kwargs["stem"] = stem
        if stems:
            if stem:
                raise ValueError("Both `stem` and `stems` arguments specified."
                    " Use one.")
            kwargs["stem__in"] = stems
        if official:
            kwargs["official"] = True
        if author is not None:
            kwargs["author"] = author
        if language is not None:
            kwargs["language"] = language
        tags = Tag.objects.filter(**kwargs)
        tagged_cts_oids = set(tags.values_list('content_type_id',
            'object_id').distinct())
        if not content_type:
            tagged_cts = {t[0] for t in tagged_cts_oids}
            tagged_models = {id: ContentType.objects.get(pk=id).model_class()
                for id in tagged_cts}
        return self._yield_objects_that_exist(tagged_cts_oids,
            tagged_models)

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

    @staticmethod
    def _yield_objects_that_exist(cts_oids, model_table):
        """For models that implement a custom manager to filter out some
        objects (for instance to hide articles which should not be published
        yet) it may be possible that asking for an object that exist
        in the database (and has tags on it) raises DoesNotExist instead.
        Here we silently ignore those."""
        for ctid, table in model_table.iteritems():
            ids = {o[1] for o in filter(lambda x: x[0] == ctid, cts_oids)}
            for obj in table.objects.filter(pk__in=ids):
                yield obj


class TagStem(Named.NonUnique, Localized, Taggable.NoDefaultTags):
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


class Tag(Named.NonUnique, Localized, TimeTrackable):
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

    class Meta:
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")


def clean_stems(sender, instance, **kwargs):
    """Decreases tag count on the stem held by the deleted tag."""
    try:
        instance.stem.dec_count()
    except (TagStem.DoesNotExist, AttributeError):
        pass
post_delete.connect(clean_stems, sender=Tag)
