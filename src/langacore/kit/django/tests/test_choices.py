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

"""Tests for helpers."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

def setup():
    import os
    os.environ['DJANGO_SETTINGS_MODULE'] = 'langacore.kit.dummy'

def test_dummy():
    """Just see if the import works as expected."""
    from langacore.kit.django import choices

def test_choices_basic():
    from langacore.kit.django.choices import Choices

    class Colors(Choices):
        _ = Choices.Choice

        white = _("White")
        yellow = _("Yellow")
        red = _("Red")
        green = _("Green")
        black = _("Black")

    assert Colors() == [(1, "White"), (2, "Yellow"), (3, "Red"), (4, "Green"),
                        (5, "Black")]
    assert Colors.white.id == 1
    assert Colors.white.desc == "White"
    assert Colors.white.name == "white"
    assert Colors.FromID(1) == Colors.white
    assert Colors.NameFromID(1) == Colors.white.name
    assert Colors.DescFromID(1) == Colors.white.desc
    assert Colors.RawFromID(1) == Colors.white.raw
    assert Colors.FromName("white") == Colors.white
    assert Colors.IDFromName("white") == Colors.white.id
    assert Colors.DescFromName("white") == Colors.white.desc
    assert Colors.RawFromName("white") == Colors.white.raw
    assert Colors.yellow.id == 2
    assert Colors.yellow.desc == "Yellow"
    assert Colors.yellow.name == "yellow"
    assert Colors.FromID(2) == Colors.yellow
    assert Colors.NameFromID(2) == Colors.yellow.name
    assert Colors.DescFromID(2) == Colors.yellow.desc
    assert Colors.RawFromID(2) == Colors.yellow.raw
    assert Colors.FromName("yellow") == Colors.yellow
    assert Colors.IDFromName("yellow") == Colors.yellow.id
    assert Colors.DescFromName("yellow") == Colors.yellow.desc
    assert Colors.RawFromName("yellow") == Colors.yellow.raw
    assert Colors.red.id == 3
    assert Colors.red.desc == "Red"
    assert Colors.red.name == "red"
    assert Colors.FromID(3) == Colors.red
    assert Colors.NameFromID(3) == Colors.red.name
    assert Colors.DescFromID(3) == Colors.red.desc
    assert Colors.RawFromID(3) == Colors.red.raw
    assert Colors.FromName("red") == Colors.red
    assert Colors.IDFromName("red") == Colors.red.id
    assert Colors.DescFromName("red") == Colors.red.desc
    assert Colors.RawFromName("red") == Colors.red.raw
    assert Colors.green.id == 4
    assert Colors.green.desc == "Green"
    assert Colors.green.name == "green"
    assert Colors.FromID(4) == Colors.green
    assert Colors.NameFromID(4) == Colors.green.name
    assert Colors.DescFromID(4) == Colors.green.desc
    assert Colors.RawFromID(4) == Colors.green.raw
    assert Colors.FromName("green") == Colors.green
    assert Colors.IDFromName("green") == Colors.green.id
    assert Colors.DescFromName("green") == Colors.green.desc
    assert Colors.RawFromName("green") == Colors.green.raw
    assert Colors.black.id == 5
    assert Colors.black.desc == "Black"
    assert Colors.black.name == "black"
    assert Colors.FromID(5) == Colors.black
    assert Colors.NameFromID(5) == Colors.black.name
    assert Colors.DescFromID(5) == Colors.black.desc
    assert Colors.RawFromID(5) == Colors.black.raw
    assert Colors.FromName("black") == Colors.black
    assert Colors.IDFromName("black") == Colors.black.id
    assert Colors.DescFromName("black") == Colors.black.desc
    assert Colors.RawFromName("black") == Colors.black.raw

def test_choices_groups():
    from langacore.kit.django.choices import Choices

    class Groupies(Choices):
        _ = Choices.Choice

        GROUP1 = Choices.Group(0)
        entry1 = _("entry1")
        entry2 = _("entry2")
        entry3 = _("entry3")

        GROUP2 = Choices.Group(10)
        entry4 = _("entry4")
        entry5 = _("entry5")
        entry6 = _("entry6")

        GROUP3 = Choices.Group(20)
        entry7 = _("entry7")
        entry8 = _("entry8")
        entry9 = _("entry9")

    assert Groupies() == [(1, u'entry1'), (2, u'entry2'), (3, u'entry3'),
                          (11, u'entry4'), (12, u'entry5'), (13, u'entry6'),
                          (21, u'entry7'), (22, u'entry8'), (23, u'entry9')]
    assert Groupies.entry1.group == Groupies.GROUP1
    assert Groupies.entry2.group == Groupies.GROUP1
    assert Groupies.entry3.group == Groupies.GROUP1
    assert Groupies.entry4.group == Groupies.GROUP2
    assert Groupies.entry5.group == Groupies.GROUP2
    assert Groupies.entry6.group == Groupies.GROUP2
    assert Groupies.entry7.group == Groupies.GROUP3
    assert Groupies.entry8.group == Groupies.GROUP3
    assert Groupies.entry9.group == Groupies.GROUP3
    assert Groupies.GROUP1.choices == [Groupies.entry1, Groupies.entry2,
                                       Groupies.entry3]
    assert Groupies.GROUP2.choices == [Groupies.entry4, Groupies.entry5,
                                       Groupies.entry6]
    assert Groupies.GROUP3.choices == [Groupies.entry7, Groupies.entry8,
                                       Groupies.entry9]

def test_choices_validation():
    from langacore.kit.django.choices import Choices

    class NoChoice(Choices):
        not_a_choice = "Not a Choice() object"

    try:
        NoChoice()
        assert False, "ValueError not raised."
    except ValueError, e:
        assert str(e) == "Choices class declared with no actual choice fields."

def test_choices_filter():
    from langacore.kit.django.choices import Country

    assert len(Country()) == 235
    assert Country(filter=("pl", "gb", "de")) == [(73, u'Germany'),
        (153, u'Poland'), (202, u'United Kingdom')]
