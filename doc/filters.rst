Filters
=======

The filters below are usable directly from pure Python code and obviously work
as templatetags as well:

.. currentmodule:: lck.django.filters

.. autosummary::

  nbsp
  numberify
  nullify
  slugify
  strike_empty
  thumbnail
  timediff
  title
  transliterate

To use these filters in your source code, simply import them from
``lck.django.filters``.  To use them as templatetags, add the
``lck.django.common`` app to ``INSTALLED_APPS`` within your
``settings.py`` and in the specific template use::

  {%load LIB_NAME%}

where ``LIB_NAME`` is the templatetag library name for the specific filter
(available in the filter description). For instance, for ``strike_empty`` or
``title`` it would be::

 {%load strings%}

There are more filters whose implementation makes them useful only as
templatetags. These include:
  
.. currentmodule:: lck.django.common.templatetags

.. autosummary::
  
  bbcode.bbcode
