"""
A set of type-converting filters.
"""
from django.template import Library

register = Library()


def numberify(obj, default=0):
    """
    Converts any type to ``int`` or returns a fallback number for falsy values. Except for
    falsy values, throws traditional ``ValueError`` if the input is uncovertable to ``int``.

    Template tag available in ``common`` app's ``converters`` library.
    
    :param obj: the object to convert

    :param default: a fallback ``int`` for falsy objects
    """

    return int(obj) if obj else default


def nullify(obj):
    """
    Converts any falsy value to ``None``.
 
    Template tag available in ``common`` app's ``converters`` library.
    """
    
    return obj if obj else None

