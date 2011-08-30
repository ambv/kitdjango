"""
Albeit useful, this module is still somewhat a mess in a really early state of development. Beware, there be dragons.
"""

import datetime
import re
from subprocess import check_call, CalledProcessError
from tempfile import NamedTemporaryFile
from os.path import join, dirname, basename, getsize, abspath
from os import remove, devnull, O_RDWR
from os import open as os_open
DEVNULL = os_open(devnull, O_RDWR)
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO


from django import forms
from django.forms.extras.widgets import RE_DATE, SelectDateWidget
from django.forms.widgets import Select, RadioFieldRenderer, HiddenInput
from django.forms.util import flatatt
from django.utils.dates import MONTHS
from django.utils.encoding import StrAndUnicode, force_unicode
from django.utils.html import escape, conditional_escape
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _


class JQueryUIRadioInput(StrAndUnicode):
    """
    An object used by RadioFieldRenderer that represents a single
    <input type='radio'>.
    """

    def __init__(self, name, value, attrs, choice, index):
        self.name, self.value = name, value
        self.attrs = attrs
        self.choice_value = force_unicode(choice[0])
        self.choice_label = force_unicode(choice[1])
        self.index = index

    def __unicode__(self):
        if 'id' in self.attrs:
            label_for = ' for="%s_%s"' % (self.attrs['id'], self.index)
        else:
            label_for = ''
        choice_label = conditional_escape(force_unicode(self.choice_label))
        return mark_safe(u'%s<label%s>%s</label>' % (self.tag(), label_for,
            choice_label)) 

    def is_checked(self):
        return self.value == self.choice_value

    def tag(self):
        if 'id' in self.attrs:
            self.attrs['id'] = '%s_%s' % (self.attrs['id'], self.index)
        final_attrs = dict(self.attrs, type='radio', name=self.name,
            value=self.choice_value)
        if self.is_checked():
            final_attrs['checked'] = 'checked'
        return mark_safe(u'<input%s />' % flatatt(final_attrs))

class JQueryUIRenderer(StrAndUnicode):
    """
    A customized renderer for radio fields. 
    """

    def __init__(self, name, value, attrs, choices):
        self.name, self.value, self.attrs = name, value, attrs
        self.choices = choices

    def __iter__(self):
        for i, choice in enumerate(self.choices):
            if not choice[0]:
                continue
            yield JQueryUIRadioInput(self.name,
                                     self.value,
                                     self.attrs.copy(),
                                     choice,
                                     i)

    def __getitem__(self, idx):
        choice = self.choices[idx] # Let the IndexError propogate
        return JQueryUIRadioInput(self.name,
                                  self.value,
                                  self.attrs.copy(),
                                  choice,
                                  idx)

    def __unicode__(self):
        return self.render()

    def render(self):
        return mark_safe('<div class="radio">\n%s\n</div>' \
                  % '\n'.join([force_unicode(w) for w in self]))


class JQueryMobileVerticalRadioGroupRenderer(JQueryUIRenderer):
    data_type = ""

    def render(self):
        return mark_safe('<div data-role="fieldcontain"><fieldset '
            'data-role="controlgroup" %s>\n%s\n</fieldset></div>' %
            (self.data_type, '\n'.join([force_unicode(w) for w in self])))


class JQueryMobileHorizontalRadioGroupRenderer(JQueryMobileVerticalRadioGroupRenderer):
    data_type = 'data-type="horizontal"'


class JQueryUIRadioSelect(forms.RadioSelect):
    renderer = JQueryUIRenderer

    @classmethod
    def id_for_label(cls, id_):
        return id_


class JQueryMobileVerticalRadioGroup(JQueryUIRadioSelect):
    renderer = JQueryMobileVerticalRadioGroupRenderer


class JQueryMobileHorizontalRadioGroup(JQueryUIRadioSelect):
    renderer = JQueryMobileHorizontalRadioGroupRenderer


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

class WebpImageField(forms.ImageField):
    """ Extends the default django ImageField with webp support.

        Converts on the fly the image data to png, so that PIL
        will be able to use it normally.
    """

    def to_python(self, data):
        """ Validates also webp images.

            Calls the default django validation. Converts
            webp images on the fly if applicable.
        """
        try:
            # Hey, it can actually be a real image you know?
            return super(WebpImageField, self).to_python(data)
        except forms.ValidationError, e:
            # Stolen from Django. Convert the data on the fly via
            # the dwebp Google program. Unfortunately this means
            # saving the file somewhere, since the CLI doesn't take
            # STDIN. Also monkey-patch the UploadFile.
            if hasattr(data, 'temporary_file_path'):
                # TemporaryUploadFile, django saved the file
                # on disk. So let's just convert to the same
                # location and if successful, viola!
                source_path = data.temporary_file_path()
                path = dirname(source_path)
                filename = basename(file).rsplit(
                    '.', 1)[0] + '.png'
                abs_path = join(path, filename)
                try:
                    check_call(['dwebp', source_path, '-o', abs_path],
                        stdout=DEVNULL)
                    data.temporary_file_path = abs_path
                    data.name = filename
                    data.size = getsize(abs_path)
                    remove(source_path)
                except CalledProcessError:
                    raise e
            else:
                # Either a StringIO file-like-object in memory,
                # or just th contents in the memory.
                with NamedTemporaryFile() as file:
                    path = dirname(file.name)
                    filename = basename(file.name).rsplit(
                        '.', 1)[0] + '.png'
                    abs_path = join(path, filename)

                    # Write the image data to a tmp file and
                    # input the save field.
                    if hasattr(data, 'read'):
                        # InMemoryUploadFile
                        data.seek(0)
                        file.write(data.read())
                        output = data.file
                    else:
                        file.write(data['content'])
                        output = data['content']

                    # Make sure no buffers stop us.
                    file.flush()

                    try:
                        # Make the actual conversion via the CLI tool.
                        check_call(['dwebp', file.name, '-o', abs_path],
                            stdout=DEVNULL)
                        # Monkey-patch the UploadFile object.
                        data.name = filename
                        data.size = getsize(abs_path)
                        if hasattr(data, 'read'):
                            # InMemoryUploadFile
                            with open(abs_path, 'rb') as image:
                                data.file = StringIO(image.read())
                        else:
                            with open(abs_path, 'r') as image:
                                data['content'] = StringIO(image.read())
                    except CalledProcessError:
                        # Well this wasn't a webp image. Close the file
                        # (thus deleting it in this case) and raise
                        # the original exception.
                        file.close()
                        raise e

            # Return the monkey-patched UploadFile object.
            return data
