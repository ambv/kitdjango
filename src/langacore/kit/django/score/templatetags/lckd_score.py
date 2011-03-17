#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2010 Łukasz Langa
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

"""A set of string-related filters."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import re
from django import template
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib import comments
from django.utils.encoding import smart_unicode

from langacore.kit.django.score.models import TotalScore

register = template.Library()

class RenderScoreNode(template.Node):
    """Render the score directly. Some contenttypes related code borrowed from
    contrib.comments."""

    template_dir = "score"
    template_name = "show.html"
    model = TotalScore

    def __init__(self, ctype=None, object_pk_expr=None, object_expr=None):
        if ctype is None and object_expr is None:
            raise template.TemplateSyntaxError("Score nodes must be given "
                "either a literal object or a ctype and object pk.")
        self.ctype = ctype
        self.object_pk_expr = object_pk_expr
        self.object_expr = object_expr

    def get_target_ctype_pk(self, context):
        if self.object_expr:
            try:
                obj = self.object_expr.resolve(context)
            except template.VariableDoesNotExist:
                return None, None
            return ContentType.objects.get_for_model(obj), obj.pk
        else:
            return self.ctype, self.object_pk_expr.resolve(context,
                ignore_failures=True)

    @staticmethod
    def lookup_content_type(token, tagname):
        try:
            app, model = token.split('.')
            return ContentType.objects.get(app_label=app, model=model)
        except ValueError:
            raise template.TemplateSyntaxError("Third argument in %r must be "
                "in the format 'app.model'" % tagname)
        except ContentType.DoesNotExist:
            raise template.TemplateSyntaxError("%r tag has non-existant "
                "content-type: '%s.%s'" % (tagname, app, model))

    def __get_query_set(self, context):
        ctype, object_pk = self.get_target_ctype_pk(context)
        if not object_pk:
            return self.model.objects.none()

        qs = self.model.objects.filter(
            content_type = ctype,
            object_id    = smart_unicode(object_pk),
            # FIXME: sites should probably be present if this is to be really
            #        reusable
            #site__id     = settings.SITE_ID,
        )

    @classmethod
    def handle_token(cls, parser, token):
        """Class method to parse render_score and return a Node."""
        tokens = token.contents.split()
        if tokens[1] != 'for':
            raise template.TemplateSyntaxError("Second argument in %r tag must"
                " be 'for'" % tokens[0])

        # {% render_score for obj %}
        if len(tokens) == 3:
            return cls(object_expr=parser.compile_filter(tokens[2]))

        # {% render_score for app.models pk %}
        elif len(tokens) == 4:
            return cls(ctype = cls.lookup_content_type(tokens[2], tokens[0]),
                       object_pk_expr = parser.compile_filter(tokens[3]))
        raise template.TemplateSyntaxError("%r tag must have 2 or 3 arguments."
            "" % tokens[0])

    def render(self, context):
        ctype, object_pk = self.get_target_ctype_pk(context)
        if object_pk:
            template_search_list = [
                "{}/{}/{}/{}".format(self.template_dir, ctype.app_label,
                    ctype.model, self.template_name),
                "{}/{}/{}".format(self.template_dir, ctype.app_label,
                    self.template_name),
                "{}/{}".format(self.template_dir, self.template_name)
            ]
            vars = {'ct': ctype, 'object_id': object_pk}
            try:
                vars['score'] = self.model.objects.get(content_type=ctype,
                    object_id=smart_unicode(object_pk)).value
            except self.model.DoesNotExist:
                vars['score'] = 0
            context.push()
            resultstr = render_to_string(template_search_list, vars, context)
            context.pop()
            return resultstr
        else:
            return ''

@register.tag
def render_score(parser, token):
    """
    Render the current score along with the plus/minus controls through the
    ``score/show.html`` template.

    Syntax::

        {% render_score for [object] %}
        {% render_score for [app].[model] [object_id] %}

    Example usage::

        {% render_score for comment %}

    """
    return RenderScoreNode.handle_token(parser, token)
