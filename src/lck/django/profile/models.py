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

"""lck.django.profile.models
   -------------------------

   Contains building blocks for creating user profiles."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from datetime import date
from functools import partial
from hashlib import md5
import re

from django.contrib.auth.models import User
from django.db import models as db
from django.utils.translation import ugettext_lazy as _

from lck.django.choices import Country, Gender
from lck.django.common.templatetags.thumbnail import thumbnail

PROXIED_FIELDS = (set([field.name for field in User._meta.fields]) |
                  set(['check_password', 'get_full_name', 'has_perm',
                       'has_perms', 'set_password']))

TZ_CHOICES = [(float(x[0]), x[1]) for x in (
    (-12, '-12'), (-11, '-11'), (-10, '-10'), (-9.5, '-09.5'), (-9, '-09'),
    (-8.5, '-08.5'), (-8, '-08 PST'), (-7, '-07 MST'), (-6, '-06 CST'),
    (-5, '-05 EST'), (-4, '-04 AST'), (-3.5, '-03.5'), (-3, '-03 ADT'),
    (-2, '-02'), (-1, '-01'), (0, '00 GMT'), (1, '+01 CET'), (2, '+02'),
    (3, '+03'), (3.5, '+03.5'), (4, '+04'), (4.5, '+04.5'), (5, '+05'),
    (5.5, '+05.5'), (6, '+06'), (6.5, '+06.5'), (7, '+07'), (8, '+08'),
    (9, '+09'), (9.5, '+09.5'), (10, '+10'), (10.5, '+10.5'), (11, '+11'),
    (11.5, '+11.5'), (12, '+12'), (13, '+13'), (14, '+14'),
)]

AVATAR_ATTR_REGEX = re.compile(r"^avatar_([whms])(\d+)$")


class BasicInfo(db.Model):
    """Describes a basic user profile that links through a one-to-one field
    to ``django.contrib.auth.models.User``. Provides fields to store nicks,
    birth dates, genders, countries of origin, cities and time zones.

    This model is also a transparent proxy to the User object enabling most
    of the functionality that would require explicitly getting the user model.
    This enables for enhanced duck typing in scenarios where user objects
    are expected."""
    user = db.OneToOneField(User)
    nick = db.CharField(verbose_name=_("visible nick"), blank=True, default='',
        max_length=30, help_text=_("Fill this field if you wish to change "
            "your visible nick. You can use Unicode characters and spaces. "
            "Keep in mind that your original username (the one you use to "
            "log into the site) will remain unchanged."))
    birth_date = db.DateField(verbose_name=_("birth date"), blank=True,
        null=True)
    gender = db.PositiveIntegerField(verbose_name=_("gender"),
        choices=Gender(), default=Gender.male.id)
    country = db.PositiveIntegerField(verbose_name=_("country"),
        choices=Country(), default=Country.pl.id)
    city = db.CharField(verbose_name=_("city"), max_length=30, blank=True)
    time_zone = db.FloatField(_('Time zone'), choices=TZ_CHOICES,
        default=1.0)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.nick.strip():
            self.nick = self.user.username
        super(BasicInfo, self).save(*args, **kwargs)

    def __getattr__(self, name):
        if name in PROXIED_FIELDS:
            return getattr(User.objects.get(id=self.__dict__['user_id']), name)
        return super(BasicInfo, self).__getattr__(name)

    def age(self):
        """age() -> numeric_age"""
        if not self.birth_date:
            return '?'
        else:
            return int((date.today() - self.birth_date).days / 365.25)

    def is_male(self):
        """True if the gender is male."""
        return self.gender == Gender.male.id

    def is_female(self):
        """True if the gender is female."""
        return self.gender == Gender.female.id

    def has_gender(self):
        """True if the gender is set."""
        return self.is_male() or self.is_female()

    def get_country_display_english(self):
        """Displays the country of origin in its English form. This is useful
        for distionary lookups."""
        return Country.RawFromID(self.country)

    def get_profile(self):
        return self

    @property
    def profile(self):
        return self

    def is_authenticated(self):
        return True


class ActivationSupport(db.Model):
    """Adds an ``activation_token`` field."""
    activation_token = db.CharField(verbose_name=_("activation token"),
        max_length=40, editable=False, blank=True, default='')

    class Meta:
        abstract = True


class AvatarSupport(db.Model):
    """Enables getting the user's gravatar by using the ``model.avatar_{size}``
    attribute notation. Works in both code and templates.

    Possible values for `size`:

    * h{height} - scale to match the height given. Example: "h100" scales to
                  100px in height. Width is scaled proportionally, may exceed
                  100px.

    * w{width} - scale to match the width given. Example: "w312" scales to
                 312px in width. Height is scaled proportionally, may exceed
                 312px.

    * m{max_size} - scale to match the greater dimension to the value given.
                    Example: "m50" would scale an 80x50 image to 50x31, and
                    an 40x120 image to 17x50.

    * s{max_size} - cuts a square from the image and scales it to the value
                    given. Example: "s48" would scale a 50x80 image to 48x48
                    based on the top 50x50 square.

    When inheriting, create a new `avatar` field like this::

        avatar = AvatarSupport.avatar_field(upload_to='upload_directory')

    To have gravatar fallback, specify `GravatarSupport` **after**
    `AvatarSupport` in your model inheritance list.
    """
    avatar_height = db.PositiveIntegerField(verbose_name=_("height"),
        default=None, blank=True, null=True, editable=False)
    avatar_width = db.PositiveIntegerField(verbose_name=_("width"),
        default=None, blank=True, null=True, editable=False)
    avatar_field = partial(db.ImageField, verbose_name=_("custom avatar"),
        height_field='avatar_height', width_field='avatar_width',
        null=True, blank=True, max_length=255)

    def __getattr__(self, name):
        m = AVATAR_ATTR_REGEX.match(name)
        if m and self.avatar:
            mode_size = "{}{}".format(m.group(1), m.group(2))
            return thumbnail(self.avatar, mode_size)
        return super(AvatarSupport, self).__getattr__(name)

    class Meta:
        abstract = True


class GravatarSupport(db.Model):
    """Enables getting the user's gravatar by using the ``model.avatar_{size}``
    attribute notation. Works in both code and templates.

    Possible values for `size` are the same as in ``AvatarSupport`` but the
    modifier is always treated as "s".
    """
    def get_gravatar(self, size):
        email = self.email if hasattr(self, 'email') else self.user.email
        return "http://www.gravatar.com/avatar/%s.jpg?d=identicon&s=%d" % (
            md5(email).hexdigest(), size)

    def __getattr__(self, name):
        m = AVATAR_ATTR_REGEX.match(name)
        if m:
            size = int(m.group(2))
            return self.get_gravatar(size)
        return super(GravatarSupport, self).__getattr__(name)

    class Meta:
        abstract = True
