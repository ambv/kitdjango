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

"""BBCode-related template tags."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.template import Library
from django.utils.safestring import mark_safe
import postmarkup

register = Library()

class NewWindowLinkTag(postmarkup.LinkTag):
    def render_open(self, parser, node_index, *args, **kwargs):
        return super(NewWindowLinkTag, self).render_open(parser, node_index,
            *args, **kwargs).replace('<a href', '<a rel="nofollow" '
                'target="_blank" href')

bb_mark = postmarkup.create()
bb_mark.add_tag(NewWindowLinkTag, 'link')
bb_mark.add_tag(NewWindowLinkTag, 'url')

@register.filter
def bbcode(text):
    """Simply encode the BBCode within the text.

    Template tag available in ``common`` app's ``bbcode`` library.

    :param text: the string to render as BBCode"""
    return mark_safe(bb_mark(text))
