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

"""lck.django.score.views
   ----------------------

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

from lck.django.common import render_decorator as render
from lck.django.common import redirect
from lck.django.score.models import TotalScore, Vote

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
