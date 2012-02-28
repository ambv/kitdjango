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
from zlib import adler32, crc32

from django.conf import settings
from django.core.exceptions import FieldError
from django.db import transaction
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader, RequestContext
from django.utils import simplejson
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
from lck.lang import unset

DOTS_REGEX = re.compile(r'\.\s+')
INTERNAL_IPS = getattr(settings, 'INTERNAL_IPS', set(('127.0.0.1', '::1',
    'localhost')))


def render(request, template_name, context, debug=False, mimetype=None,
    compute_etag=True):
    """render(request, template_name, context, [debug, mimetype]) -> HttpResponse

    Renders the `context` within for a `request` using a template named
    `template_name` returning the required `mimetype`."""

    if hasattr(settings, 'AUTH_PROFILE_MODULE'):
        if 'user_profile' in context:
            raise KeyError, ("lck.django.common.render() doesn't "
                             "accept contexts with 'user_profile'")
        if 'other_user_profile' in context:
            raise KeyError, ("lck.django.common.render() doesn't "
                             "accept contexts with 'other_user_profile'")

        context['user_profile'] = request.user.get_profile() \
                                  if request.user.is_authenticated() else None
        context['other_user_profile'] = context['other_user'].get_profile() \
                                        if 'other_user' in context else None

    http_response_kwargs = {'mimetype': mimetype}
    response = loader.render_to_string(template_name, RequestContext(request,
        context)).encode('utf8')
    if compute_etag:
        etag = b"-".join((hex(crc32(response)), hex(adler32(response))))
        if etag == request.environ.get('HTTP_IF_NONE_MATCH', 'X'):
            response = ""
            http_response_kwargs['status'] = 304
    http_response = HttpResponse(response, **http_response_kwargs)
    if compute_etag:
        http_response['ETag'] = etag
    return http_response


def render_decorator(func):
    """render_decorator(func) -> HttpResponse

    Wraps a view function returning `context` (most conveniently: locals()).
    Renders the `context` for a context['request'] using a template named
    context['template'] returning the required context['mimetype']."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        context = func(*args, **kwargs)
        return render(context['request'],
                      context['template'],
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
                    initial_kwargs={}, context={}, redirect_on_success=None):
    """A handler for a typical form workflow:

    1. Initialize a form object.

       a. if there are POSTed data and/or files, use them
       b. otherwise use `initial` as initial data and `initial_kwargs` as \
          keyword arguments for the form object constructor.

    2. If the form validates, save it and
       either: override the template name with a version using the \
          "_complete.html" suffix.
       or: redirect using the `redirect_on_success` arguments
    3. If there are errors on the form, prepare an additional `error_summary`
       string on the form object (for consumption by the template).
    4. Render the result.
    """
    if request.method == 'POST':
        _kwargs = dict(initial_kwargs)
        _kwargs['data'] = request.POST
        _kwargs['files'] = request.FILES
    else:
        _kwargs = dict(initial_kwargs)
        _kwargs['initial'] = initial
    form = form_class(**_kwargs)
    if form.is_valid():
        template = template + '_complete.html'
        if hasattr(form, 'save'):
            form.request = request
            form.save()
        if redirect_on_success:
            return redirect(request, **redirect_on_success)
    else:
        template += '.html'
        if form.errors:
            error = unicode(" ".join(form.errors.get("__all__",
                                    [_("Try again")])))
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


def nested_commit_on_success(func):
    """Like commit_on_success, but doesn't commit existing transactions.

    This decorator is used to run a function within the scope of a
    database transaction, committing the transaction on success and
    rolling it back if an exception occurs.

    Unlike the standard transaction.commit_on_success decorator, this
    version first checks whether a transaction is already active.  If so
    then it doesn't perform any commits or rollbacks, leaving that up to
    whoever is managing the active transaction.

    Taken from: http://djangosnippets.org/snippets/1343/
    """
    _commit_on_success = transaction.commit_on_success(func)
    def _nested_commit_on_success(*args, **kwds):
        if transaction.is_managed():
            return func(*args,**kwds)
        else:
            return _commit_on_success(*args,**kwds)
    return transaction.wraps(func)(_nested_commit_on_success)


class lazy_chain(object):
    """Enables chaining multiple iterables to serve them lazily as
    a queryset-compatible object. Supports collective ``count()``, ``exists()``,
    ``exclude``, ``filter`` and ``order_by`` methods.

    Provides special overridable static methods used while yielding values:

      * ``xfilter(value)`` - yield a value only if ``xfilter(value)`` returns
                             ``True``. See known issues belowe.

      * ``xform(value)`` - transforms the value JIT before yielding it back.
                           It is only called for values within the specified
                           slice and those which passed ``xfilter``.

      * ``xkey(value)`` - returns a value to be used in comparison between
                          elements if sorting should be used. Individual
                          iterables should be presorted for the complete result
                          to be sorted properly.

    Known issues:

    1. If slicing or ``xfilter`` is used, reported ``len()`` is computed by
       iterating over all iterables so performance is weak.

    2. Indexing on lazy chains uses iteration underneath so performance
       is weak. This feature is only available as a last resort. Slicing on the
       other hand is also lazy."""

    def __init__(self, *iterables):
        self.iterables = iterables
        self.start = None
        self.stop = None
        self.step = None

    @staticmethod
    def xform(value):
        """Transform the ``value`` just-in-time before yielding it back.
        Default implementation simply returns the ``value`` as is."""
        return value

    @staticmethod
    def xfilter(value=unset):
        """xfilter(value) -> bool

        Only yield the ``value`` if this method returns ``True``.
        Skip to the next iterator value otherwise. Default implementation
        always returns ``True``."""
        return True

    @staticmethod
    def xkey(value=unset):
        """xkey(value) -> comparable value

        Return a value used in comparison between elements if sorting
        should be used."""
        return value

    def copy(self, *iterables):
        """Returns a copy of this lazy chain. If `iterables` are provided,
        they are used instead of the ones in the current object."""
        if not iterables:
            iterables = self.iterables
        result = lazy_chain(*iterables)
        result.xfilter = self.xfilter
        result.xform = self.xform
        result.xkey = self.xkey
        result.start = self.start
        result.stop = self.stop
        result.step = self.step
        return result

    def _filtered_next(self, iterator):
        """Raises StopIteration just like regular iterator.next()."""
        result = iterator.next()
        while not self.xfilter(result):
            result = iterator.next()
        return result

    def __iter__(self):
        try:
            sorting = self.xkey() is not unset
        except TypeError:
            sorting = True
        if sorting:
            def _gen():
                candidates = {}
                for iterable in self.iterables:
                    iterator = iter(iterable)
                    try:
                        candidates[iterator] = [self._filtered_next(iterator),
                            iterator]
                    except StopIteration:
                        continue
                while candidates:
                    try:
                        to_yield, iterator = min(candidates.viewvalues(),
                            key=lambda x: self.xkey(x[0]))
                        yield to_yield
                    except ValueError:
                        # sequence empty
                        break
                    try:
                        candidates[iterator] = [self._filtered_next(iterator),
                            iterator]
                    except StopIteration:
                        del candidates[iterator]
        else:
            def _gen():
                for it in self.iterables:
                    for element in it:
                        if not self.xfilter(element):
                            continue
                        yield element
        for index, element in enumerate(_gen()):
            if self.start and index < self.start:
                continue
            if self.step and index % self.step:
                continue
            if self.stop and index >= self.stop:
                break
            yield self.xform(element)

    def __getitem__(self, key):
        if isinstance(key, slice):
            if any((key.start and key.start < 0,
                    key.stop and key.stop < 0,
                    key.step and key.step < 0)):
                raise ValueError("lazy chains do not support negative indexing")
            result = self.copy()
            result.start = key.start
            result.stop = key.stop
            result.step = key.step
        elif isinstance(key, int):
            if key < 0:
                raise ValueError("lazy chains do not support negative indexing")
            self_without_transform = self.copy()
            self_without_transform.xform = lambda x: x
            for index, elem in enumerate(self_without_transform):
                if index == key:
                    return self.xform(elem)
            raise IndexError("lazy chain index out of range")
        else:
            raise ValueError("lazy chain supports only integer indexing and "
                "slices.")

        return result

    def __len_parts__(self):
        for iterable in self.iterables:
            try:
                yield iterable.count()
            except:
                try:
                    yield len(iterable)
                except TypeError:
                    yield len(list(iterable))

    def __len__(self):
        try:
            if all((self.xfilter(),
                    not self.start,
                    not self.stop,
                    not self.step or self.step == 1)):
                # fast __len__
                sum = 0
                for sub in self.__len_parts__():
                    sum += sub
                return sum
        except TypeError:
            pass
        # slow __len__ if xfilter or slicing was used
        length = 0
        for length, _ in enumerate(self):
            pass
        return length+1

    def _django_factory(self, _method, *args, **kwargs):
        new_iterables = []
        for it in self.iterables:
            try:
                new_iterables.append(getattr(it, _method)(**kwargs))
            except (AttributeError, ValueError, FieldError):
                new_iterables.append(it)
        return self.copy(new_iterables)

    def all(self):
        return self

    def count(self):
        """Queryset-compatible ``count`` method. Supports multiple iterables.
        """
        return len(self)

    def exclude(self, *args, **kwargs):
        """Queryset-compatible ``filter`` method. Will silently skip filtering
        for incompatible iterables."""
        return self._django_factory('exclude', *args, **kwargs)

    def exists(self):
        """Queryset-compatible ``exists`` method. Supports multiple iterables.
        """
        return bool(len(self))

    def filter(self, *args, **kwargs):
        """Queryset-compatible ``filter`` method. Will silently skip filtering
        for incompatible iterables."""
        return self._django_factory('filter', *args, **kwargs)

    def none(self, *args, **kwargs):
        return lazy_chain()

    def order_by(self, *args, **kwargs):
        """Queryset-compatible ``order_by`` method. Will silently skip ordering
        for incompatible iterables."""
        return self._django_factory('order_by', *args, **kwargs)
