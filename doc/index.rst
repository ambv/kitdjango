.. langacore.kit.django documentation master file, created by
   sphinx-quickstart on Tue Mar 16 23:16:32 2010.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

langacore.kit.django
--------------------

This library consists of various Django-related routines that extend or modify the behaviour of the framework. The notion of having a single kit of all things Django-related is that the authors believe these routines could successfully be a part of the actual Django distribution. To date the library is too early in the development state to seriously consider that as an option, hence it's available separately. Just as with `langacore.kit.common <http://packages.python.org/langacore.kit.common/>`_, each function, decorator or module herein is on its own too simple to dedicate an entire PyPI package for it. Together however, this tiny library represents a Swiss army knife for everyday Django needs [1]_.

The latest version can be installed via `PyPI <http://pypi.python.org/pypi/langacore.kit.django/>`_::

  $ pip install langacore.kit.django
  
or::

  $ easy_install langacore.kit.django


The `source code repository <http://github.com/LangaCore/kitdjango>`_ and `issue tracker <http://github.com/LangaCore/kitdjango/issues>`_ 
are maintained on `GitHub <http://github.com/LangaCore/kitdjango>`_.

This documentation
==================

.. toctree::
   :maxdepth: 2
  
   overview
   todo
   copying

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

Footnotes
~~~~~~~~~
.. [1] YMMV
