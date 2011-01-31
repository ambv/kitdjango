#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 Łukasz Langa
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

"""langacore.kit.django.common.templatetags
   ----------------------------------------

   Commonly useful template tags and filters."""
#FIXME: Elaborate what's included.

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from functools import partial

from django.template import Node, RequestContext, Template

from langacore.kit.cache import memoize

def _render(text, context):
    if not context or 'request' not in context:
        raise ValueError("Provided context is empty or doesn't provide "
                "REQUEST.")
    return Template(text).render(RequestContext(context['request'],
        context))

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
