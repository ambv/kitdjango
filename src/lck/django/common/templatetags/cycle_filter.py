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

"""The cycle filter."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os

from django import template
from PIL import Image

from lck.django.common.templatetags import DynamicNode, validate_param_number

register = template.Library()


@register.filter
def cycle(counter, rule):
    """Returns True when a given forloop.counter is conforming to the
    specified `rule`. The rules are given as strings using the syntax
    "{step}/{scale}", for example:

    * ``forloop.counter|cycle:"1/2"`` returns True for even values
    * ``forloop.counter|cycle:"2/2"`` returns True for odd values

    What's interesting about this filter is that it works also for more
    complex steppings:

    * ``forloop.counter|cycle:"1/3"`` returns True every third value
    * ``forloop.counter|cycle:"2/3"`` returns True every third value but one
      step after 1/3 would
    * ``forloop.counter|cycle:"3/3"`` returns True every third value but two
      steps after 1/3 would
    """
    step, scale = (int(elem) for elem in rule.split("/"))
    result = (counter - 1) % scale == step - 1
    return result


@register.tag(name="set")
def _set(parser, token):
    args = token.split_contents()
    is_valid = len(args) == 3
    validate_param_number(is_valid, args[0], "two arguments")
    return SetNode(args[1], args[2])


class SetNode(DynamicNode):
    def __init__(self, attr, value):
        self.attr = attr
        self.value = int(value)

    def render(self, context):
        context[self.attr] = self.value
        return ""


@register.tag
def incr(parser, token):
    args = token.split_contents()
    is_valid = len(args) == 2
    validate_param_number(is_valid, args[0], "one argument")
    return IncrNode(args[1])


class IncrNode(DynamicNode):
    def __init__(self, attr):
        self.attr = attr

    def render(self, context):
        if self.attr in context:
            context[self.attr] += 1
        return ""
