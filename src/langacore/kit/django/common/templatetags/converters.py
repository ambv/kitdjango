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

"""A set of type-converting filters."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from collections import OrderedDict
from datetime import datetime

from django.template import Library

register = Library()


def numberify(obj, default=0):
    """Converts any type to ``int`` or returns a fallback number for falsy
    values. Except for falsy values, throws traditional ``ValueError`` if the
    input is uncovertable to ``int``.

    Template tag available in ``common`` app's ``converters`` library.

    :param obj: the object to convert

    :param default: a fallback ``int`` for falsy objects
    """

    return int(obj) if obj else default


def nullify(obj):
    """Converts any falsy value to ``None``.

    Template tag available in ``common`` app's ``converters`` library.
    """

    return obj if obj else None


_tenses = {'past': 0, 'present': 1, 'future': 2}
_time_forms = {
    'en': OrderedDict((
        ('years', {
            0: 'years',
            1: 'a year',
        }),
        ('months', {
            0: 'months',
            1: 'a month',
        }),
        ('weeks', {
            0: 'weeks',
            1: 'a week',
        }),
        ('days', {
            0: 'days',
            1: ('yesterday', 'a day', 'tomorrow'),
        }),
        ('hours', {
            0: 'hours',
            1: 'an hour',
        }),
        ('minutes', {
            0: 'minutes',
            1: 'one minute',
        }),
        ('__now__', ('moments ago', 'just now', 'in a moment')),
        ('', {
            'prefixes': ('', '', 'in'),
            'suffixes': ('ago', '', ''),
        }),
    )),
    'pl': OrderedDict((
        ('years', {
            0: 'lat',
            1: 'rok',
            2: 'lata',
            3: 'lata',
            4: 'lata',
            12: '',
            13: '',
            14: '',
        }),
        ('months', {
            0: 'miesięcy',
            1: 'miesiąc',
            2: 'miesiące',
            3: 'miesiące',
            4: 'miesiące',
            12: '',
            13: '',
            14: '',
        }),
        ('weeks', {
            0: 'tygodni',
            1: 'tydzień',
            2: 'tygodnie',
            3: 'tygodnie',
            4: 'tygodnie',
            12: '',
            13: '',
            14: '',
        }),
        ('days', {
            0: 'dni',
            1: ('wczoraj', '1 dzień', 'jutro'),
            2: 'dni',
            3: 'dni',
            4: 'dni',
            12: '',
            13: '',
            14: '',
        }),
        ('hours', {
            0: 'godzin',
            1: ('godzinę temu', 'godzina', 'za godzinę'),
            2: 'godziny',
            3: 'godziny',
            4: 'godziny',
            12: '',
            13: '',
            14: '',
        }),
        ('minutes', {
            0: 'minut',
            1: ('minutę temu', 'minuta', 'za minutę'),
            2: 'minuty',
            3: 'minuty',
            4: 'minuty',
            12: '',
            13: '',
            14: '',
        }),
        ('__now__', ('przed chwilą', 'teraz', 'za chwilę')),
        ('', {
            'prefixes': ('', '', 'za'),
            'suffixes': ('temu', '', ''),
        }),
    )),
}

for lang, forms in _time_forms.iteritems():
    if '' in forms:
        prefixes = forms[''].get('prefixes', None)
        suffixes = forms[''].get('suffixes', None)
    for name, form in forms.iteritems():
        if not name or not isinstance(form, dict):
            continue
        if prefixes and 'prefixes' not in form:
            form['prefixes'] = prefixes
        if suffixes and 'suffixes' not in form:
            form['suffixes'] = suffixes

def timediff_format(value, forms, tense):
    """timediff_format(value, forms) -> string

    `value` holds a number specifying a time interval and `forms` is
    a dictionary where keys are time intervals and values are language
    descriptions for these intervals.

    If a description for a certain `value` is not available in `forms`,
    the remainder from division by ten is looked up as well (with the exception
    that the remainder ``1`` is treated as ``0`` because ``forms[1]`` by design
    holds the description for a singular value.

    If a description for the remainder is still not available, ``forms[0]``
    is used.

    By "not available" we mean either the key not present in `forms` or
    evaluating to False."""
    print_value = True
    v = value
    if v not in forms:
        v = value % 10
        if v == 1:
            v = 0
    elif v == 1:
        print_value = False
    #Note: ``not forms.get(v)`` isn't the same as ``v not in forms``
    if not forms.get(v):
        v = 0
    form = forms[v]
    tense = _tenses[tense]
    if isinstance(form, tuple):
        form = form[tense]
        if print_value:
            form = "{} {}".format(value, form)
    else:
        if 'prefixes' in forms:
            prefix = forms['prefixes'][tense] + ' '
        if 'suffixes' in forms:
            suffix = ' ' + forms['suffixes'][tense]
        form = "{}{}{}{}".format(prefix, ("{} ".format(value)) if
            print_value else "", form, suffix)
    return form

@register.filter
def timediff(timestamp, language='pl'):
    """Returns a string representing a fuzzy time difference
    between now() and the input timestamp.

    The output rounds up to a single most significant value: years, months,
    weeks, days, hours or minutes."""
    tense = 'present'
    now = datetime.now()
    delta = now - timestamp
    if delta.total_seconds < -10:
        tense = 'future'
    elif delta.total_seconds > 10:
        tense = 'past'
    delta = abs(delta)
    days = delta.days
    weeks = days // 7
    if weeks >= 4:
        years = int((days + 1) // 365.25)
        months = 12 * years + now.month - timestamp.month
        if timestamp.day > now.day:
            months -= 1
    else:
        years, months = 0, 0
    hours = delta.seconds//3600
    minutes = delta.seconds%3600//60
    forms = _time_forms[language]
    for interval in forms:
        if interval in locals() and locals()[interval]:
            return timediff_format(locals()[interval], forms[interval], tense)
    return forms['__now__'][_tenses[tense]]
