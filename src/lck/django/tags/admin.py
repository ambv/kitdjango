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

from django.contrib import admin

from lck.django.tags.models import TagStem, Tag


class TagInline(admin.TabularInline):
    readonly_fields = ('official',)
    model = Tag


class TagStemAdmin(admin.ModelAdmin):
    list_display = ('name', 'language', 'tag_count')
    readonly_fields = ('name', 'language', 'tag_count',)
    search_fields = ('name', 'language')
    inlines = [TagInline]


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'language', 'author', 'content_type', 'official',
        'created')
    search_fields = ('name', 'language', 'author')
    list_filter = ('official', 'created', 'modified', 'language',
        'content_type')
    readonly_fields = ('stem', 'official', 'created', 'modified')


admin.site.register(TagStem, TagStemAdmin)
admin.site.register(Tag, TagAdmin)
