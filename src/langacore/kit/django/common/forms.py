import datetime
import re

from django import forms
from django.forms.widgets import Select
from django.forms.extras.widgets import RE_DATE, SelectDateWidget
from django.utils.dates import MONTHS
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _


GENDER_CHOICES = ((1, _("Female")),
                  (2, _("Male")),
                  (3, _("any")),
                 )

ANY_GENDER = 3


SEARCH_GAME_CHOICES = (('cs16', _("Counter-Strike 1.6")),
                       ('cod4', _("Call of Duty 4")),
                       ('any', _("any")),
                      )


ANY_GAME = 'any'


ACCOUNT_CHOICES = ((1, _("complete")),
                   (2, _("incomplete")),
                   (3, _("any account")),
                  )


ANY_ACCOUNT = 3
COMPLETE_ACCOUNT = 1
INCOMPLETE_ACCOUNT = 2

class PolishSelectDateWidget(SelectDateWidget):
    def __init__(self, attrs=None, years=None):
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
        select_html = Select(choices=year_choices).render(self.year_field % name, year_val, local_attrs)
        output.append(select_html)

        return mark_safe(u'\n'.join(output))


class MassMailingForm(forms.Form):
    gender = forms.ChoiceField(label=_("Gender"), choices=GENDER_CHOICES, initial=ANY_GENDER)
    game = forms.ChoiceField(label=_("Game"), choices=SEARCH_GAME_CHOICES, initial=ANY_GAME)
    account = forms.ChoiceField(label=_("Account"), choices=ACCOUNT_CHOICES, initial=ANY_ACCOUNT, help_text=_("Incomplete accounts don't have Allegro login or Steam ID/PB GUID filled."))
    subject = forms.CharField(label=_("Subject"), max_length=150, required=False)
    content = forms.CharField(label=_("Content"), widget=forms.Textarea)
    force_privacy = forms.BooleanField(label=_("Ignore privacy"), initial=False, required=False)

MassMailingForm.base_fields['force_privacy'].reverse = True
