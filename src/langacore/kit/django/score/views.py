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

"""langacore.kit.django.score.views
   --------------------------------

   Reusable views for the scoring app."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404

from langacore.kit.django.helpers import render_decorator as render
from langacore.kit.django.helpers import redirect
from langacore.kit.django.score.models import TotalScore, Vote

@render
def show_score(request, content_type, object_id):
    template = 'score/show.html'
    ct = get_object_or_404(ContentType, pk=content_type)
    obj = get_object_or_404(ct.model_class(), pk=object_id)
    score = TotalScore.get_value(obj, ct=ct)
    return locals()

@login_required
def update_score(request, content_type, object_id, value, voter=None):
    if not voter:
        voter_model = Vote.voter.field.rel.to
        if voter_model is User:
            voter = request.user
        else:
            voter = request.user.get_profile()
            if voter_model is not voter.__class__:
                raise ImproperlyConfigured("voter not passed to the"
                    "`update_score()` view. Write a `process_view()` "
                    "middleware to pass it. This is not required if the voter "
                    "model is `User` or `user_instance.get_profile()`.")
    ct = get_object_or_404(ContentType, pk=int(content_type))
    obj = get_object_or_404(ct.model_class(), pk=int(object_id))
    score = TotalScore.update(obj, voter, int(value), ct=ct)
    return redirect(request, reverse('lckd-score:show',
        args=[int(content_type), int(object_id)]))
