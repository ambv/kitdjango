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

"""lck.django.common.templatetags
   ------------------------------

   Commonly useful template tags and filters."""
#FIXME: Elaborate what's included.

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from functools import partial

from django.template import Node, Context, RequestContext, Template,\
    TemplateSyntaxError

from lck.cache import memoize


def validate_param_number(condition, tag_name, fail_text):
    if not condition:
        raise TemplateSyntaxError("%r tag requires %s argument%s" % (tag_name,
            fail_text, "s" if fail_text != "one" else ""))


def _render(text, context):
    if not context:
        raise ValueError("Provided context is empty.")
    elif 'request' in context:
        return Template(text).render(RequestContext(context['request'],
            context))
    else:
        return Template(text).render(Context(context))


class DynamicNode(Node):
    """A Node that provides a rendering method to support dynamic arguments."""

    render = staticmethod(_render)

    @memoize(skip_first=True)
    def dynamic(self, text, load=[], prefix='', suffix=''):
        """Prepares tag attribute `text` to be rendered using the templating
        engine. Returns a callable with a single `context` attribute.

        If `load` is given, it's a list of tag/filter libraries required
        for rendering of the `text`. `prefix` and `suffix` hold boilerplate
        that needs to be added around the provided text.

        If `text` is empty, the returned callable always returns an empty
        string. In this case the templating engine is not used and the
        `prefix`, `suffix` and `load` attributes are ignored.
        """
        if text:
            load = ['{{%load {}%}}'.format(l) for l in load]
            if prefix:
                load.append(prefix)
            load.append(text)
            if suffix:
                load.append(suffix)
            text = "\n".join(load)
            return partial(_render, text)
        else:
            return lambda context: ""

    def static(self, text, prefix='', suffix=''):
        """Prepares tag attribute `text` to be rendered statically. Unless
        `text` is empty, returns a string surrounded by `prefix` and `suffix`.
        Otherwise returns an empty string."""
        if text:
            return prefix + text + suffix
        else:
            return ''
