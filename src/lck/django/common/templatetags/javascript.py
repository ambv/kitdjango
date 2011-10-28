from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

def varname(value):
    return value.lower().replace("-","_")

register.filter(varname)
