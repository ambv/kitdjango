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

"""langacore.kit.django.profile.models
   -----------------------------------

   Contains building blocks for creating user profiles."""

# FIXME: Needs documentation.

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import re

from django.contrib.auth.models import User
from django.db import models as db
from django.utils.translation import ugettext_lazy as _

from langacore.kit.django.choices import Country, Gender

PROXIED_FIELDS = (set([field.name for field in User._meta.fields]) |
                  set(['get_full_name']))

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


class BasicInfo(db.Model):
    user = db.OneToOneField(User)
    nick = db.CharField(verbose_name=_("visible nick"), blank=True, default='',
        max_length=30, help_text=_("Fill this field if you wish to change "
            "your visible nick. You can use Unicode characters and spaces."
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
    db.Model.__getattr__ = db.Model.__getattribute__

    def age(self):
        if not self.birth_date:
            return '?'
        else:
            return int((date.today() - self.birth_date).days / 365.25)

    def is_male(self):
        return self.gender == Gender.male.id

    def is_female(self):
        return self.gender == Gender.female.id

    def has_gender(self):
        return self.is_male() or self.is_female()

    def get_country_display_english(self):
        return Country.RawFromID(self.country)


class ActivationSupport(db.Model):
    activation_token = db.CharField(verbose_name=_("activation token"),
        max_length=40, editable=False, blank=True, default='')

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        super(ActivationSupport, self).save(*args, **kwargs)


class GravatarSupport(db.Model):
    _GRAVATAR_ATTR_REGEX = re.compile(r"^gravatar(\d+)$")

    def gravatar(self, size):
        return "http://www.gravatar.com/avatar/%s.jpg?d=identicon&s=%d" % (
            md5(self.user.email).hexdigest(), size)

    def __getattr__(self, name):
        m = self._GRAVATAR_ATTR_REGEX.match(name)
        if m:
            size = int(m.group(1))
            return self.gravatar(size)
        return super(GravatarSupport, self).__getattr__(name)

    class Meta:
        abstract = True
