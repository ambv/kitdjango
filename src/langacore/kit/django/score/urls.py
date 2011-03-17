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

from django.conf.urls.defaults import *

urlpatterns = patterns('langacore.kit.django.score.views',
    url(r'^(?P<content_type>\d+)/(?P<object_id>\d+)/$', 'show_score', name='show'),
    url(r'^(?P<content_type>\d+)/(?P<object_id>\d+)/(?P<value>-?\d+)/$', 'update_score', name='update'),
)
