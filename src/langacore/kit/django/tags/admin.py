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

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.contrib import admin

from langacore.kit.django.tags.models import TagStem, Tag


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
