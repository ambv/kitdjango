--------------------
langacore.kit.django
--------------------

This library consists of various Django-related routines that extend or modify
the behaviour of the framework:

 * extensions for ``settings.py`` (current directory resolution, namespace
   package support, settings profile support)

 * ``Choices``: an enum implementation for Django forms and models (with
   predefined classes for languages, countries, etc.)

 * typical filters, template tags, models, form fields, etc.

Complete documentation for the package can be found here:

 * http://packages.python.org/langacore.kit.django/

I believe these routines could successfully be a part of the actual Django
distribution. However, in its current shape the library is too early in the
development state to seriously consider that as an option. Hence it's available
separately. Just as with `langacore.kit.common
<http://packages.python.org/langacore.kit.common/>`_, each bit of functionality
is probably too small to have an entire PyPI package of its own. Together
however, this library represents a Swiss army knife for everyday Django needs
(YMMV).

The latest version can be installed via `PyPI
<http://pypi.python.org/pypi/langacore.kit.django/>`_::

  $ pip install langacore.kit.django
  
or::

  $ easy_install langacore.kit.django


The `source code repository <http://github.com/LangaCore/kitdjango>`_ and `issue
tracker <http://github.com/LangaCore/kitdjango/issues>`_ are maintained on
`GitHub <http://github.com/LangaCore/kitdjango>`_.

**Note:**  Since 0.2.0 ``langacore.kit.django`` requires **Python 2.7** because
it's using the ``absolute_imports``, ``division``, ``print_function`` and
``unicode_literals`` futures. One of the virtues in the creation of this library
is to make the code beautiful. These switches give us a useful transitional
state between the old Python 2.x and the new Python 3.x. You should use them as
well.
