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

from django.template import Library, Node, TemplateSyntaxError
from django.conf import settings

register = Library()

class SettingsNode( Node ):
    """Taken from http://www.nomadjourney.com/2009/04/how-to-make-the-django-500-server-error-view-useful/"""
    def __init__( self, setting_names ):
        self.setting_names = setting_names

    def render( self, context ):
        for setting_name in self.setting_names:
            try:
                val = settings.__getattr__( setting_name )
            except AttributeError:
                val = None
            context[ setting_name ] = val
        return ''

def do_settings( parser, token ):
    bits = token.split_contents()
    if not len( bits ) > 1:
        raise TemplateSyntaxError( '%r tag requires at least one argument' % bits[ 0 ] )
    return SettingsNode( bits[ 1: ] )

do_settings = register.tag( 'settings', do_settings )

