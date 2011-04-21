"""
Albeit useful, this module is still somewhat a mess in a really early state of development. Beware, there be dragons.
"""

import datetime
import re

from django import forms
from django.forms.widgets import Select
from django.forms.extras.widgets import RE_DATE, SelectDateWidget
from django.utils.dates import MONTHS
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _


class PolishSelectDateWidget(SelectDateWidget):
    def __init__(self, attrs=None, years=None, reverse_years=False):
        self.reverse_years = reverse_years
        super(PolishSelectDateWidget, self).__init__(attrs, years)

    def render(self, name, value, attrs=None):
        try:
            year_val, month_val, day_val = value.year, value.month, value.day
        except AttributeError:
            year_val = month_val = day_val = None
            if isinstance(value, basestring):
                match = RE_DATE.match(value)
                if match:
                    year_val, month_val, day_val = [int(v) for v in match.groups()]

        output = []

        if 'id' in self.attrs:
            id_ = self.attrs['id']
        else:
            id_ = 'id_%s' % name

        day_choices = [(i, i) for i in range(1, 32)]
        local_attrs = self.build_attrs(id=self.day_field % id_)
        select_html = Select(choices=day_choices).render(self.day_field % name, day_val, local_attrs)
        output.append(select_html)

        month_choices = MONTHS.items()
        month_choices.sort()
        local_attrs['id'] = self.month_field % id_
        select_html = Select(choices=month_choices).render(self.month_field % name, month_val, local_attrs)
        output.append(select_html)

        year_choices = [(i, i) for i in self.years]
        local_attrs['id'] = self.year_field % id_
        if self.reverse_years:
            year_choices.reverse()
        select_html = Select(choices=year_choices).render(self.year_field % name, year_val, local_attrs)
        output.append(select_html)


        return mark_safe(u'\n'.join(output))
