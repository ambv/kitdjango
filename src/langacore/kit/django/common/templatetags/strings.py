# -*- coding: utf-8 -*-
"""
A set of string-related filters.
"""

import re
from django.template import Library
from django.template.defaultfilters import slugify as crippled_slugify

from langacore.kit.i18n import translit

register = Library()


@register.filter
def title(text):
    """
    Like built-in \\|title filter but leaves existing caps alone, eg.
    ``'I work for the FBI'`` -> ``'I Work For The FBI'``.

    Template tag available in ``common`` app's ``strings`` library.
    """
    pattern=re.compile(r"(\s|^)\w")
    cap=lambda x: x.group().upper()

    return pattern.sub(cap, text + u'') #+ u'' to handle proxy objects


@register.filter
def transliterate(text, country_code, text_lang=''):
    """
    If the country with the specified code is using Cyrillic alphabet,
    transliterates Latin strings using ``langacore.kit.i18n.translit``.

    Template tag available in ``common`` app's ``strings`` library.
    """
    return translit.any(country_code, text, input_lang=text_lang)


@register.filter
def slugify(text, fallback='untitled-0'):
    """
    A version of the builtin ``django.template.defaultfilters`` which doesn't let empty
    strings as outcomes.

    Template tag available in ``common`` app's ``strings`` library.
    
    :param text: the text to slugify

    :param fallback: the text to return in case the builtin slugify returns an empty value
    """
 
    slug = crippled_slugify(text)
    return slug if slug else fallback


@register.filter
def strike_empty(obj):
    """
    Converts any falsy value to ``u"---"``.
    
    Template tag available in ``common`` app's ``strings`` library.
    """

    return obj if obj else u"---"
