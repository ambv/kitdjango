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


class ScoreNode(template.Node):
    """Base score node. Some contenttypes related code taken from
    contrib.comments."""

    def __init__(self, ctype=None, object_pk_expr=None, object_expr=None,
            as_varname=None):
        if ctype is None and object_expr is None:
            raise template.TemplateSyntaxError("Score nodes must be given "
                "either a literal object or a ctype and object pk.")
        self.ctype = ctype
        self.object_pk_expr = object_pk_expr
        self.object_expr = object_expr
        self.as_varname = as_varname

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

    @classmethod
    def handle_token(cls, parser, token):
        """Class method to parse get_score* and return a Node."""
        tokens = token.contents.split()
        if tokens[1] != 'for':
            raise template.TemplateSyntaxError("Second argument in %r tag must"
                " be 'for'" % tokens[0])

        # {% get_whatever for obj as varname %}
        if len(tokens) == 5:
            if tokens[3] != 'as':
                raise template.TemplateSyntaxError("Third argument in %r must "
                    "be 'as'" % tokens[0])
            return cls(
                object_expr = parser.compile_filter(tokens[2]),
                as_varname = tokens[4],
            )

        # {% get_whatever for app.model pk as varname %}
        elif len(tokens) == 6:
            if tokens[4] != 'as':
                raise template.TemplateSyntaxError("Fourth argument in %r must"
                    " be 'as'" % tokens[0])
            return cls(
                ctype = BaseCommentNode.lookup_content_type(tokens[2],
                    tokens[0]),
                object_pk_expr = parser.compile_filter(tokens[3]),
                as_varname = tokens[5]
            )

        else:
            raise template.TemplateSyntaxError("%r tag requires 4 or 5 "
                "arguments" % tokens[0])

    def render(self, context):
        return ''

    def get_score_value(self, ctype, object_pk):
        return self.model.objects.get(content_type=ctype,
            object_id=smart_unicode(object_pk)).value


class GetScoreValueNode(ScoreNode):
    """Inject score value to context."""
    model = TotalScore

    def render(self, context):
        ctype, object_pk = self.get_target_ctype_pk(context)
        if object_pk:
            context[self.as_varname] = self.get_score_value(ctype, object_pk)
        return ''


class RenderScoreNode(ScoreNode):
    """Render the score directly."""

    template_dir = "score"
    template_name = "show.html"
    model = TotalScore

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
                vars['score'] = self.get_score_value(ctype, object_pk)
            except self.model.DoesNotExist:
                vars['score'] = 0
            context.push()
            resultstr = render_to_string(template_search_list, vars, context)
            context.pop()
            return resultstr
        else:
            return ''

@register.tag
def get_score_value(parser, token):
    """
    Gets the score value for the given params and populates the template
    context with a variable containing that value, whose name is defined by the
    'as' clause.

    Syntax::

        {% get_score_value for [object] as [varname]  %}
        {% get_score_value for [app].[model] [object_id] as [varname]  %}

    Example usage::

        {% get_score_value for event as score_value %}
        {% get_score_value for calendar.event event.id as score_value %}
        {% get_score_value for calendar.event 17 as score_value %}

    """
    return GetScoreValueNode.handle_token(parser, token)

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
