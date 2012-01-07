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

"""A set of type-converting filters."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from base64 import urlsafe_b64encode, urlsafe_b64decode
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
        ('__never__', ('never', 'never', 'never')),
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
        ('__never__', ('nigdy', 'nigdy', 'nigdy')),
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
    forms = _time_forms[language]
    tense = 'present'
    if timestamp:
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
            months = now.month - timestamp.month
            if months < 0:
                months += 12
            if timestamp.day > now.day:
                months -= 1
        else:
            years, months = 0, 0
        hours = delta.seconds // 3600
        minutes = delta.seconds % 3600 // 60
        for interval in forms:
            if interval in locals() and locals()[interval]:
                return timediff_format(locals()[interval], forms[interval], tense)
        return forms['__now__'][_tenses[tense]]
    return forms['__never__'][_tenses[tense]]

@register.filter
def to_base64(text):
    return urlsafe_b64encode(text.encode('utf8'))

@register.filter
def from_base64(text):
    return urlsafe_b64decode(text.encode('ascii')).decode('utf8')
