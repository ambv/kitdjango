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

"""Various unrelated routines and helper classes."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from functools import wraps
import re

from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response as _render_to_response
from django.template import RequestContext
from django.utils import simplejson
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext


DOTS_REGEX = re.compile(r'\.\s+')
INTERNAL_IPS = getattr(settings, 'INTERNAL_IPS', set(('127.0.0.1', '::1',
    'localhost')))


def render(request, template_name, context, debug=False, mimetype=None):
    """render(request, template_name, context, [debug, mimetype]) -> HttpResponse

    Renders the `context` within for a `request` using a template named
    `template_name` returning the required `mimetype`."""

    if hasattr(settings, 'AUTH_PROFILE_MODULE'):
        if 'user_profile' in context:
            raise KeyError, ("lck.django.helpers.render() doesn't "
                             "accept contexts with 'user_profile'")
        if 'other_user_profile' in context:
            raise KeyError, ("lck.django.helpers.render() doesn't "
                             "accept contexts with 'other_user_profile'")

        context['user_profile'] = request.user.get_profile() \
                                  if request.user.is_authenticated() else None
        context['other_user_profile'] = context['other_user'].get_profile() \
                                        if 'other_user' in context else None

    if debug:
        for key in context:
            format = (key, str(context[key]), type(context[key]),
                      repr(context[key]))
            print("context['{}'] = {} (type: {}) (repr: {})".format(*format))
    return _render_to_response(template_name,
                               RequestContext(request, context),
                               mimetype=mimetype)


def render_decorator(func):
    """render_decorator(func) -> HttpResponse

    Wraps a view function returning `context` (most conveniently: locals()).
    Renders the `context` for a context['request'] using a template named
    context['template'] returning the required context['mimetype']."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        context = func(*args, **kwargs)
        return _render_to_response(context['template'],
                                   RequestContext(context['request'], context),
                                   mimetype=context.get('mimetype', None))
    return wrapper


def render_json(obj):
    """render_json(obj) -> HttpResponse

    Dumps the object in the `obj` param to a JSON string and returns it
    via HTTP using the application/json mimetype."""

    return HttpResponse(simplejson.dumps(obj),
                        mimetype="application/json")


def redirect(request, link='/', override_request=False):
    """redirect(request, [link, override_request]) -> HttpResponseRedirect

    A smarter redirect which takes the redirection target from a given param.
    The lookup for the redirection target is as follows:

    * 'redirect_to' in GET or POST (in that order)

    * 'next' in GET or POST (in that order)

    * the `link` fallback argument ('/' if not given)

    If `override_request` is ``True``, `link` is always followed."""

    if not override_request:
        link_from_param = None
        for varname in 'redirect_to', 'next':
            for container in request.GET, request.POST:
                if varname in container:
                    link_from_param = container[varname]
                    break
            if link_from_param:
                link = link_from_param
                break
    return HttpResponseRedirect(link)


def typical_handler(request, form_class, template, initial={},
                    initial_kwargs={}, context={}):
    """A handler for a typical form workflow:

    1. Initialize a form object.

       a. if there are POSTed data, use them
       b. otherwise use `initial` as initial data and `initial_kwargs` as \
          keyword arguments for the form object constructor.

    2. If the form validates, save it and override the template name with
       a version using the "_complete.html" suffix.
    3. If there are errors on the form, prepare an additional `error_summary`
       string on the form object (for consumption by the template).
    4. Render the result.
    """
    if request.method == 'POST':
        _kwargs = dict(initial_kwargs)
        _kwargs['data'] = request.POST
    else:
        _kwargs = dict(initial_kwargs)
        _kwargs['initial'] = initial
    form = form_class(**_kwargs)
    if form.is_valid():
        template = template + '_complete.html'
        form.save()
    else:
        template += '.html'
        if form.errors:
            # FIXME: i18n of "Try again" below.
            error = unicode(" ".join(form.errors.setdefault('__all__',
                                    [u'Spróbuj ponownie'])))
            error = DOTS_REGEX.sub('.<br>', error,
                                   len(DOTS_REGEX.findall(error))-1)
            form.error_summary = mark_safe(error)
            del error
    ctx = dict(context)
    ctx.update(locals())
    return render(request, template, ctx)


def cut(text, length=40, trailing=" (...)"):
    """Cuts text to a predefined length and appends a trailing ellipsis for
    longer sources."""
    if not text:
        return text
    if len(text) <= length:
        trailing = ""
    return text[:length] + trailing


def remote_addr(request):
    """If the remote address in request is a localhost, check for
    X_FORWADED_FOR. Which addresses are considered local is defined by the
    ``INTERNAL_IPS`` list in `settings.py`, by default these are 127.0.0.1,
    ::1 and "localhost"."""
    result = request.META['REMOTE_ADDR']
    if result in INTERNAL_IPS:
        try:
            result = request.META['HTTP_X_FORWARDED_FOR'].split(',')[0].strip()
        except (KeyError, IndexError):
            pass
    return result
