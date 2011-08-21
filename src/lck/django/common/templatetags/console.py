#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2010 Łukasz Langa

"""Allplay filters."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from functools import partial
import re

from django.conf import settings
from django.template import Library
from django.utils.safestring import mark_safe

from lck.cache import memoize
from lck.django.common.templatetags import DynamicNode, validate_param_number


register = Library()
COLOR_MAP = {
    'red': '31',
    'green': '32',
    'blue': '34',
}


@register.tag
def color(parser, token):
    args = token.split_contents()
    is_simple = len(args) == 2
    is_complex = len(args) == 4 and  args[2] == 'in'
    is_valid = is_simple or is_complex
    validate_param_number(is_valid, args[0], "one or three arguments")
    return ColorNode(args[1], args[3] if is_complex else None)


class ColorNode(DynamicNode):
    def __init__(self, color, from_map=None):
        if not from_map:
            self.color_name = lambda ctx: color
            self.color_map = lambda ctx: COLOR_MAP
        else:
            self.color_name = self.dynamic(color)
            self.color_map = lambda ctx: ctx.get(from_map, {})

    def render(self, context):
        if 'no_color' in context and context['no_color']:
            return ""
        else:
            color = self.color_map(context).get(self.color_name(context),
                '00')
            return "\033[{}m".format(color)
