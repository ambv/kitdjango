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

"""A set of string-related filters."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


import re
from django.template import Library
from django.template.defaultfilters import slugify as crippled_slugify
from django.utils.safestring import mark_safe

from langacore.kit.i18n import translit

register = Library()


@register.filter
def title(text):
    """Like built-in \\|title filter but leaves existing caps alone, eg.
    ``'I work for the FBI'`` -> ``'I Work For The FBI'``.

    Template tag available in ``common`` app's ``strings`` library.
    """
    pattern=re.compile(r"(\s|^)\w")
    cap=lambda x: x.group().upper()

    return pattern.sub(cap, text + '') #+ '' to handle proxy objects


@register.filter
def transliterate(text, country_code, text_lang=''):
    """If the country with the specified code is using Cyrillic alphabet,
    transliterates Latin strings using ``langacore.kit.i18n.translit``.

    Template tag available in ``common`` app's ``strings`` library.
    """
    return translit.any(country_code, text, input_lang=text_lang)


@register.filter
def slugify(text, fallback='untitled-0'):
    """A version of the builtin ``django.template.defaultfilters`` which
    doesn't let empty strings as outcomes.

    Template tag available in ``common`` app's ``strings`` library.

    :param text: the text to slugify

    :param fallback: the text to return in case the builtin slugify returns an
                     empty value
    """

    slug = crippled_slugify(text)
    return slug if slug else fallback


@register.filter
def strike_empty(obj):
    """Converts any falsy value to ``u"---"``.

    Template tag available in ``common`` app's ``strings`` library.
    """

    return obj if obj else "---"


@register.filter
def nbsp(obj):
    """Converts spaces to nbsp entities.

    Template tag available in ``common`` app's ``strings`` library.
    """

    return mark_safe(re.sub(r"\s+", "&nbsp;", obj))
