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

import operator

from django import forms
from django.conf import settings
from django.conf.urls.defaults import patterns, url
from django.contrib import admin
from django.contrib.admin.widgets import ForeignKeyRawIdWidget
from django.core.urlresolvers import reverse, NoReverseMatch
from django.db import models as db
from django.db.models.query import QuerySet
from django.forms.widgets import Select
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.template.loader import render_to_string
from django.utils.functional import update_wrapper
from django.utils.encoding import smart_str
from django.utils.safestring import mark_safe
from django.utils.text import get_text_list, truncate_words
from django.utils.translation import ugettext_lazy as _


class LinkedSelect(Select):
    """Just like a Select but adds an "Edit separately" link for foreign
    keys."""

    def __init__(self, model, overrides, *args, **kwargs):
        super(LinkedSelect, self).__init__(*args, **kwargs)
        self.model = model
        self.overrides = overrides

    def render(self, name, value, attrs=None, *args, **kwargs):
        output = super(LinkedSelect, self).render(name, value, attrs=attrs,
            *args, **kwargs)
        if name in self.overrides:
            meta = self.overrides[name]._meta
        else:
            meta = self.model._meta
            for field in meta.fields:
                if field.get_internal_type() != 'ForeignKey' or \
                    field.name != name:
                    continue
                meta = field.related.parent_model._meta
        try:
            if not value:
                raise NoReverseMatch
            view_url = reverse("admin:{}_changelist".format("_".join((meta.app_label,
                meta.module_name)))) + str(value) + '/'
        except NoReverseMatch:
            pass
        else:
            output = mark_safe('<div style="float: left; margin-right: 6px;">'
                '{}<br/><a href="{}">{}</a></div>'.format(output, view_url,
                _("Edit separately")))
        return output


class ForeignKeySearchInput(ForeignKeyRawIdWidget):
    """A Widget for displaying ForeignKeys in an autocomplete search input
    instead in a <select> box.
    """
    # Set in subclass to render the widget with a different template
    widget_template = None
    # Set this to the patch of the search view
    search_path = '../foreignkey_autocomplete/'

    class Media:
        css = {
            'all': ('lckd/autocomplete/css/jquery.autocomplete.css',)
        }
        js = (
            'lckd/autocomplete/js/jquery.js',
            'lckd/autocomplete/js/jquery.bgiframe.min.js',
            'lckd/autocomplete/js/jquery.ajaxQueue.js',
            'lckd/autocomplete/js/jquery.autocomplete.js',
        )

    def label_for_value(self, value):
        key = self.rel.get_related_field().name
        obj = self.rel.to._default_manager.get(**{key: value})
        return truncate_words(obj, 14)

    def __init__(self, rel, search_fields, attrs=None, hide_id=False, instant_lookup=False):
        self.search_fields = search_fields
        self.hide_id = hide_id
        self.instant_lookup = instant_lookup
        super(ForeignKeySearchInput, self).__init__(rel, attrs)

    def render(self, name, value, attrs=None):
        if attrs is None:
            attrs = {}
        output = [super(ForeignKeySearchInput, self).render(name, value, attrs)]
        opts = self.rel.to._meta
        app_label = opts.app_label
        model_name = opts.object_name.lower()
        related_url = '../../../%s/%s/' % (app_label, model_name)
        params = self.url_parameters()
        if params:
            url = '?' + '&amp;'.join(['%s=%s' % (k, v) for k, v in params.items()])
        else:
            url = ''
        if not attrs.has_key('class'):
            attrs['class'] = 'vForeignKeyRawIdAdminField'
        # Call the TextInput render method directly to have more control
        output = [forms.TextInput.render(self, name, value, attrs)]
        if value:
            label = self.label_for_value(value)
        else:
            label = u''
        try:
            if not value:
                raise NoReverseMatch
            view_url = reverse("admin:{}_changelist".format("_".join((app_label,
                model_name)))) + str(value) + '/'
        except NoReverseMatch:
            view_url = None
        context = {
            'url': url,
            'related_url': related_url,
            'admin_media_prefix': settings.ADMIN_MEDIA_PREFIX,
            'search_path': self.search_path,
            'search_fields': ','.join(self.search_fields),
            'model_name': model_name,
            'app_label': app_label,
            'label': label,
            'name': name,
            'hide_id': self.hide_id,
            'instant_lookup': self.instant_lookup,
            'view_url': view_url,
        }
        output.append(render_to_string(self.widget_template or (
            '%s/%s/foreignkey_searchinput.html' % (app_label, model_name),
            '%s/foreignkey_searchinput.html' % app_label,
            'foreignkey_searchinput.html',
        ), context))
        output.reverse()
        output = mark_safe(u''.join(output))
        if view_url:
            output = mark_safe('<div style="float: left; margin-right: 6px;">'
                '{}<br/><a href="{}">{}</a><br/></div>'.format(output, view_url,
                _("Edit separately")))
        return output


class ForeignKeyAutocompleteModelMixin(object):
    """Admin mixin for models using the autocomplete feature.

    There is one additional field:
       - related_string_functions: contains optional functions which
         take target model instance as only argument and return string
         representation. By default __unicode__() method of target
         object is used.

    Adapted from django-extensions.
    """

    related_string_functions = {}

    def foreignkey_autocomplete(self, request):
        """
        Searches in the fields of the given related model and returns the
        result as a simple string to be used by the jQuery Autocomplete plugin
        """
        query = request.GET.get('q', None)
        app_label = request.GET.get('app_label', None)
        model_name = request.GET.get('model_name', None)
        search_fields = request.GET.get('search_fields', None)
        object_pk = request.GET.get('object_pk', None)
        try:
            to_string_function = self.related_string_functions[model_name]
        except KeyError:
            to_string_function = lambda x: x.__unicode__()
        if search_fields and app_label and model_name and (query or object_pk):
            def construct_search(field_name):
                # use different lookup methods depending on the notation
                if field_name.startswith('^'):
                    return "%s__istartswith" % field_name[1:]
                elif field_name.startswith('='):
                    return "%s__iexact" % field_name[1:]
                elif field_name.startswith('@'):
                    return "%s__search" % field_name[1:]
                else:
                    return "%s__icontains" % field_name
            model = db.get_model(app_label, model_name)
            queryset = model._default_manager.all()
            data = ''
            if query:
                for bit in query.split():
                    or_queries = [db.Q(**{construct_search(
                        smart_str(field_name)): smart_str(bit)})
                            for field_name in search_fields.split(',')]
                    other_qs = QuerySet(model)
                    other_qs.dup_select_related(queryset)
                    other_qs = other_qs.filter(reduce(operator.or_, or_queries))
                    queryset = queryset & other_qs
                data = ''.join([u'%s|%s\n' % (
                    to_string_function(f), f.pk) for f in queryset])
            elif object_pk:
                try:
                    obj = queryset.get(pk=object_pk)
                except:
                    pass
                else:
                    data = to_string_function(obj)
            return HttpResponse(data)
        return HttpResponseNotFound()

    def get_urls(self):
        from django.conf.urls.defaults import patterns, url

        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            return update_wrapper(wrapper, view)

        info = self.model._meta.app_label, self.model._meta.module_name

        urlpatterns = patterns('',
            url(r'foreignkey_autocomplete/$',
                wrap(self.foreignkey_autocomplete),
                name='%s_%s_autocomplete' % info),
        ) + super(ForeignKeyAutocompleteModelMixin, self).get_urls()
        return urlpatterns


class ForeignKeyAutocompleteInlineMixin(object):
    """Admin mixin for inlines using the autocomplete feature.

    There are three additional fields:
       - related_search_fields: defines fields of managed model that
         have to be represented by autocomplete input, together with
         a list of target model fields that are searched for
         input string, e.g.:

         related_search_fields = {
            'author': ('first_name', 'email'),
         }

       - hide_id_textfields: defines fields of managed model that won't
         have the ID text field shown in the UI, e.g.:

         hide_id_textfields = ('userprofile', )

       - instant_lookup_fields: defines fields of managed model that
         should instantly be refreshed after initialization, for instance
         because the actual representation is decorated in
         ForeignKeyAutocompleteModelMixin's related_string_functions.

    Adapted from django-extensions.
    """

    related_search_fields = {}
    hide_id_textfields = []
    instant_lookup_fields = []

    def get_help_text(self, field_name, model_name):
        searchable_fields = self.related_search_fields.get(field_name, None)
        if searchable_fields:
            help_kwargs = {
                'model_name': model_name,
                'field_list': get_text_list(searchable_fields, _('and')),
            }
            return _('Use the left field to do %(model_name)s lookups in the fields %(field_list)s.') % help_kwargs
        return ''

    def formfield_for_dbfield(self, db_field, **kwargs):
        """
        Overrides the default widget for Foreignkey fields if they are
        specified in the related_search_fields class attribute.
        """
        if (isinstance(db_field, db.ForeignKey) and
            db_field.name in self.related_search_fields):
            model_name = db_field.rel.to._meta.object_name
            help_text = self.get_help_text(db_field.name, model_name)
            if kwargs.get('help_text'):
                help_text = u'%s %s' % (kwargs['help_text'], help_text)
            kwargs['widget'] = ForeignKeySearchInput(db_field.rel,
                                        self.related_search_fields.get(db_field.name, ('__unicode__',)),
                                        hide_id=db_field.name in self.hide_id_textfields,
                                        instant_lookup=db_field.name in self.instant_lookup_fields)
            kwargs['help_text'] = help_text
        return super(ForeignKeyAutocompleteInlineMixin,
            self).formfield_for_dbfield(db_field, **kwargs)


class ModelAdmin(ForeignKeyAutocompleteModelMixin,
    ForeignKeyAutocompleteInlineMixin, admin.ModelAdmin):
    """Just like admin.ModelAdmin but silently implements a bunch of updates
    for lck.django needs."""

    buttons = ()
    edit_separately = {} # overrides for the "Edit separately" button,
                         # in the form: {'field_name': Model}
    filter_exclude = set()

    def __init__(self, *args, **kwargs):
        super(ModelAdmin, self).__init__(*args, **kwargs)
        self._add_common_fields(('created', 'modified'))
        self._add_common_fields(('created_by', 'modified_by'))

    def _add_common_fields(self, fields):
        fields = tuple([f for f in fields if f not in self.filter_exclude])
        model_fields = [field.name for field, model in
            self.model._meta.get_fields_with_model()]
        model_has_all_fields = all([arg in model_fields for arg in fields])
        if model_has_all_fields:
            self.list_filter = self.list_filter + fields
            self.readonly_fields = self.readonly_fields + fields
        ffo = dict(self.formfield_overrides)
        if db.ForeignKey not in ffo:
            ffo[db.ForeignKey] = {'widget': LinkedSelect(model=self.model,
                overrides=self.edit_separately)}
        self.formfield_overrides = ffo

    def _button_view_dispatcher(self, request, object_id, command):
        obj = self.model._default_manager.get(pk=object_id)
        return getattr(self, command)(request, obj) \
            or HttpResponseRedirect(request.META['HTTP_REFERER'])

    def change_view(self, request, object_id, extra_context=None):
        if extra_context is None:
            extra_context = {}
        extra_context['buttons'] = [(b.func_name, b.short_description)
            for b in self.buttons]
        return super(ModelAdmin, self).change_view(request,
            object_id, extra_context)

    def get_urls(self):
        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            return update_wrapper(wrapper, view)
        return patterns('', *(url(r'^(\d+)/(%s)/$' % but.func_name,
                wrap(self._button_view_dispatcher)) for but in self.buttons)
                ) + super(ModelAdmin, self).get_urls()

    def save_model(self, request, obj, form, change):
        if hasattr(obj, 'pre_save_model'):
            obj.pre_save_model(request, obj, form, change)
        obj.save()


class ForeignKeyAutocompleteTabularInline(ForeignKeyAutocompleteInlineMixin,
                                          admin.TabularInline):
    pass

class ForeignKeyAutocompleteStackedInline(ForeignKeyAutocompleteInlineMixin,
                                          admin.StackedInline):
    pass
