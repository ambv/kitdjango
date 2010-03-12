# -*- coding: utf-8 -*-
import re
from django.template import Library

register = Library()
pattern=re.compile(r"(\s|^)\w")
cap=lambda x: x.group().upper()

@register.filter
def proper_title(text):
    """ Like built-in |title filter but leaves existing caps alone, eg.
    'I work for the FBI' -> 'I Work For The FBI'. """
    return pattern.sub(cap, text + u'') #+ u'' to handle proxy objects

@register.filter
def transliterate(text, country_code, text_lang=''):
    from langacore.kit.i18n import translit
    
    return translit.any(country_code, text, input_lang=text_lang)
