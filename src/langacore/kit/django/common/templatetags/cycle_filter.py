#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2010 Łukasz Langa

"""The thumbnail filter."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os

from django import template
from PIL import Image


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
    return (counter - 1) % scale == step - 1
