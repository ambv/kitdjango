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

"""A set of type-converting filters."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.template import Library

register = Library()


def numberify(obj, default=0):
    """Converts any type to ``int`` or returns a fallback number for falsy
    values. Except for falsy values, throws traditional ``ValueError`` if the
    input is uncovertable to ``int``.

    Template tag available in ``common`` app's ``converters`` library.

    :param obj: the object to convert

    :param default: a fallback ``int`` for falsy objects
    """

    return int(obj) if obj else default


def nullify(obj):
    """Converts any falsy value to ``None``.

    Template tag available in ``common`` app's ``converters`` library.
    """

    return obj if obj else None

