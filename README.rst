----------
lck.django
----------

This library consists of various Django-related routines that extend or modify
the behaviour of the framework:

 * extensions for ``settings.py`` (current directory resolution, namespace
   package support, settings profile support)

 * ``Choices``: an enum implementation for Django forms and models (with
   predefined classes for languages, countries, etc.)

 * typical filters, template tags, models, form fields, etc.

Complete documentation for the package can be found here:

 http://packages.python.org/lck.django/

The latest version can be installed via `PyPI
<http://pypi.python.org/pypi/lck.django/>`_::

  $ pip install lck.django
  
or::

  $ easy_install lck.django


The `source code repository <http://github.com/LangaCore/kitdjango>`_ and `issue
tracker <http://github.com/LangaCore/kitdjango/issues>`_ are maintained on
`GitHub <http://github.com/LangaCore/kitdjango>`_.

This package bundles some royalty free static images that are useful in almost
every Django project:

 * `Silk icons 1.3 by FamFamFam <http://www.famfamfam.com/lab/icons/silk/>`_
   - requires attributing the author

 * `Silk Companion 1 by Damien Guard
   <http://damieng.com/creative/icons/silk-companion-1-icons>`_ - requires
   attributing the author

 * `Country Flags by SenojFlags.com <http://www.senojflags.com>`_ - requires
   using the following HTML::

    <a href="http://www.senojflags.com">Country flag</a> image from <a href="http://www.senojflags.com">Flags of all Countries</a>

For the curious, ``lck`` stands for LangaCore Kit. LangaCore is a one man
software development shop of mine.

**Note:**  ``lck.common`` requires **Python 2.7** because all of its code is using
the so-called four futures (``absolute_imports``, ``division``, ``print_function``
and ``unicode_literals``). One of the virtues in the creation of this library
is to make the code beautiful. These switches give a useful transitional
state between the old Python 2.x and the new Python 3.x. You should use them as
well.

**Note:**  Since 0.5.0 ``lck.django`` requires **Django 1.3** because
it makes my monkey-patching efforts much easier. Moreover, 1.3 nicely deprecates
behaviour which I consider ugly.

Change Log
----------

0.5.0
~~~~~

* migrated to the ``lck`` namespace from ``lck``

* migrated licensing from GPL 3 to MIT

* bumped the trove from alpha status to beta, the code is in production for over
  a year now

Ancient history
~~~~~~~~~~~~~~~

* No proper change log was kept before 0.5.0
