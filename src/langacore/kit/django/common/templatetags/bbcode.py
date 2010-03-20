# -*- coding: utf-8 -*-

"""
BBCode-related template tags.
"""
from django.template import Library
from django.utils.safestring import mark_safe
from postmarkup import render_bbcode

register = Library()

@register.filter
def bbcode(text):
    """
    Simply encode the BBCode within the text.

    Template tag available in ``common`` app's ``bbcode`` library.
    
    :param text: the string to render as BBCode
    """
    return mark_safe(render_bbcode(text))
