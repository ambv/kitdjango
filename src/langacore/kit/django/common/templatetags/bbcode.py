# -*- coding: utf-8 -*-

from django.template import Library
from django.utils.safestring import mark_safe
from postmarkup import render_bbcode

register = Library()

@register.filter
def bbcode(text):
    return mark_safe(render_bbcode(text))
