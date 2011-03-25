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

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


def parse_tag_input(tagstring):
    """Returns a sorted list of unique tag stems. Parses a specified
    `tagstring`, with multiple word input being activated and
    delineated by commas and double quotes. Quotes take precedence, so
    they may contain commas. If the `tagstring` doesn't contain any commas,
    unquoted spaces are treated as tag divisors as well.

    Ported from Jonathan Buchanan's
    `django-tagging <http://django-tagging.googlecode.com/>`_"""

    if not tagstring:
        return []

    if ',' not in tagstring and '"' not in tagstring:
        words = list(set(split_strip(tagstring, ' ')))
        words.sort()
        return words

    words = []
    buffer = []
    # Defer splitting of non-quoted sections until we know if there are
    # any unquoted commas.
    to_be_split = []
    saw_loose_comma = False
    open_quote = False
    i = iter(tagstring)
    try:
        while True:
            c = i.next()
            if c == '"':
                if buffer:
                    to_be_split.append(''.join(buffer))
                    buffer = []
                # Find the matching quote
                open_quote = True
                c = i.next()
                while c != '"':
                    buffer.append(c)
                    c = i.next()
                if buffer:
                    word = ''.join(buffer).strip()
                    if word:
                        words.append(word)
                    buffer = []
                open_quote = False
            else:
                if not saw_loose_comma and c == ',':
                    saw_loose_comma = True
                buffer.append(c)
    except StopIteration:
        # If we were parsing an open quote which was never closed treat
        # the buffer as unquoted.
        if buffer:
            if open_quote and ',' in buffer:
                saw_loose_comma = True
            to_be_split.append(''.join(buffer))
    if to_be_split:
        if saw_loose_comma:
            delimiter = ','
        else:
            delimiter = ' '
        for chunk in to_be_split:
            words.extend(split_strip(chunk, delimiter))
    words = list(set(words))
    words.sort()
    return words

def split_strip(string, delimiter=','):
    """Splits ``string`` on ``delimiter``, stripping each resulting string
    and returning a list of non-empty strings.

    Ported from Jonathan Buchanan's
    `django-tagging <http://django-tagging.googlecode.com/>`_"""
    if not string:
        return []

    words = [w.strip() for w in string.split(delimiter)]
    return [w for w in words if w]
