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

"""A set of string-related filters."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


import re
from django.template import Library
from django.template.defaultfilters import slugify as crippled_slugify
from django.utils.safestring import mark_safe

from lck.i18n import translit

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
def upperfirst(text):
    """Removes leading whitespace and ups the first letter in the string."""
    text = text.lstrip()
    return text[0].upper() + text[1:]


@register.filter
def transliterate(text, country_code, text_lang=''):
    """If the country with the specified code is using Cyrillic alphabet,
    transliterates Latin strings using ``lck.i18n.translit``.

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
