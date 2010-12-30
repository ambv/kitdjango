#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2010 Łukasz Langa

"""Various unrelated routines and helper classes."""

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from functools import partial
import re

from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response as _render_to_response
from django.template import RequestContext
from django.utils import simplejson
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext


unset = object()

DOTS_REGEX = re.compile(r'\.\s+')


def render(request, template_name, context, debug=False, mimetype=None):
    """Renders the `context` within for a `request` using a template named
    `template_name` returning the required `mimetype`."""

    if hasattr(settings, 'AUTH_PROFILE_MODULE'):
        if 'user_profile' in context:
            raise KeyError, ("langacore.kit.django.helpers.render() doesn't "
                             "accept contexts with 'user_profile'")
        if 'other_user_profile' in context:
            raise KeyError, ("langacore.kit.django.helpers.render() doesn't "
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


def render_json(obj):
    """Dumps the object in the `obj` param to a JSON string and returns it
    via HTTP using the application/json mimetype."""

    return HttpResponse(simplejson.dumps(obj),
                        mimetype="application/json")


def redirect(request, link='/', override_request=False):
    """A smarter redirect which takes the redirection target from
    GET['redirect_to'] or falls back to the URL from the `link` param.
    If `override_request` is True, `link` is always followed."""

    if not override_request \
       and request.method == 'GET' \
       and 'redirect_to' in request.GET:
        link = request.GET['redirect_to']
    return HttpResponseRedirect(link)


def typical_handler(request, form_class, template, initial={},
                    initial_kwargs={}):
    """A handler for a typical form workflow:

    1. Initialize a form object.
       a.  if there are POSTed data, use them
       b.  otherwise use `initial` as initial data and `initial_kwargs` as
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
    return render(request, template, locals())


def cut(text, length=40, trailing=" (...)"):
    """Cuts text to a predefined length and appends a trailing ellipsis for
    longer sources."""
    if not text:
        return text
    if len(text) <= length:
        trailing = ""
    return text[:length] + trailing


class ChoicesEntry(object):
    global_id = 0

    def __init__(self, description, id, name=None):
        self.id = id
        self.desc = ugettext(description)
        self.global_id = Choice.global_id
        self.name = name
        ChoicesEntry.global_id += 1


class ChoiceGroup(ChoicesEntry):
    def __init__(self, id):
        super(ChoiceGroup, self).__init__('', id=id)
        self.choices = []


class Choice(ChoicesEntry):
    def __init__(self, description):
        super(Choice, self).__init__(description, id=-255)
        self.group = None


def _reverse_impl(cls, id, found=lambda id, k, v: False,
                    getter=lambda id, k, v: None, fallback=unset):
    """Unless fallback is set, raises ValueError if name not present."""
    for k, v in cls.__dict__.items():
        if isinstance(v, ChoicesEntry) and found(id, k, v):
            return getter(id, k, v)
    if fallback is unset:
        raise ValueError("Nothing found for '{}'.".format(id))
    else:
        return fallback


class Choices(list):
    Choice = Choice
    Group = ChoiceGroup

    def __init__(self):
        values = []

        for k, v in self.__class__.__dict__.items():
            if isinstance(v, ChoicesEntry):
                v.name = k
                values.append(v)

        if not values:
            raise ValueError("Choices class declared with no actual "
                             "choice fields.")

        values.sort(lambda x, y: x.global_id - y.global_id)

        last_choice_id = 0
        group = None
        for choice in values:
            if isinstance(choice, ChoiceGroup):
                last_choice_id = choice.id
                group = choice
            else:
                if group:
                    group.choices.append(choice)
                    choice.group = group
                if choice.id == -255:
                    last_choice_id += 1
                    choice.id = last_choice_id
                last_choice_id = choice.id
                self.append((choice.id, choice.desc))

    IDFromName = classmethod(partial(_reverse_impl,
        found=lambda id, k, v: k == id,
        getter=lambda id, k, v: v.id))

    DescFromName = classmethod(partial(_reverse_impl,
        found=lambda id, k, v: k == id,
        getter=lambda id, k, v: v.desc))

    FromName = classmethod(partial(_reverse_impl,
        found=lambda id, k, v: k == id,
        getter=lambda id, k, v: v))

    NameFromID = classmethod(partial(_reverse_impl,
        found=lambda id, k, v: v.id == id,
        getter=lambda id, k, v: k))

    DescFromID = classmethod(partial(_reverse_impl,
        found=lambda id, k, v: v.id == id,
        getter=lambda id, k, v: v.desc))

    FromID = classmethod(partial(_reverse_impl,
        found=lambda id, k, v: v.id == id,
        getter=lambda id, k, v: v))

    @staticmethod
    def ToIDs(func):
        """Converts a sequence of choices to a sequence of choice IDs."""
        def wrapper(self):
            return (elem.id for elem in func(self))
        return wrapper
