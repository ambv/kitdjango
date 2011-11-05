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
from django.utils.translation import ugettext_lazy as _

from lck.django.common.admin import ModelAdmin

from lck.django.activitylog.models import UserAgent, IP, Backlink


class IPAdmin(ModelAdmin):
    def user_list(self):
        return ", ".join([unicode(p) for p in self.profiles.all()])
    user_list.short_description = _("List of users")

    list_display = ('address', 'hostname', user_list)
    search_fields = ('address', 'number', 'hostname',
        'profiles__user__username', 'profiles__user__email')
    readonly_fields = ('number', 'hostname', 'profiles',)

admin.site.register(IP, IPAdmin)


class UserAgentAdmin(ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    readonly_fields = ('profiles',)

admin.site.register(UserAgent, UserAgentAdmin)


class BacklinkAdmin(ModelAdmin):
    list_display = ('url', 'referrer', 'status', 'visits', 'site')
    list_filter = ('site', 'status')
    search_fields = ('url', 'referrer')
    readonly_fields = ('visits',)

admin.site.register(Backlink, BacklinkAdmin)


class UserIPInline(admin.TabularInline):
    def user_ip(self):
        return '<a href="/admin/activitylog/ip/{}/">{}</a>'.format(self.ip.id,
            self.ip)
    user_ip.short_description = _("IP address")
    user_ip.allow_tags = True

    model = IP.profiles.through
    exclude = ('ip', 'profile')
    readonly_fields = (user_ip, 'created', 'modified')
    extra = 0


class UserAgentInline(admin.TabularInline):
    def user_agent(self):
        return ('<a href="/admin/activitylog/useragent/{}/">{}</a>'
            ''.format(self.agent.id, self.agent))
    user_agent.short_description = _("user agent")
    user_agent.allow_tags = True

    model = UserAgent.profiles.through
    exclude = ('agent', 'profile')
    readonly_fields = (user_agent, 'created', 'modified')
    extra = 0
