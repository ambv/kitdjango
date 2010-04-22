Overview
--------
For now the library is still tiny. Functionality gets added or refined as needed. To see what's
already available, let's do a quick tour over each feature group.

Extensions for ``settings.py``
==============================

One of the most often customized parts of a Django project is ``settings.py``. To ease the process
and protect against possible mistakes when doing the same exact modification for the n-th time, a
set of extensions for ``settings.py`` was developed. The extensions are activated by importing them
and executing::

  from langacore.kit.django import current_dir_support
  execfile(current_dir_support)

This is done so to enable the extensions access to the current local namespace of ``settings.py``.
If anyone knows a more elegant way to do that, let me know. For now this seems a good approach
though.

``current_dir_support``
~~~~~~~~~~~~~~~~~~~~~~~

This extension injects a ``CURRENT_DIR`` variable into ``settings.py`` so it is available from the
moment of definitions onwards. ``CURRENT_DIR`` in this context means the root of the project
("current" because most of the time this is the same dir where ``settings.py`` resides). An
additional feature is that it is always ending with ``os.sep`` so it's perfectly safe to do
something like::

  from langacore.kit.django import current_dir_support
  execfile(current_dir_support)

  (...)

  MEDIA_ROOT = CURRENT_DIR + 'media/'

Moreover, ``CURRENT_DIR`` gets set properly also for the projects that use a **package** for
specifying settings, e.g. a structure like that::

  project_dir
  ├── __init__.py
  ├── an_app
  │   ├── __init__.py
  │   └── ...
  ├── an_app
  │   ├── __init__.py
  │   └── ...
  ├── other_app
  │   ├── __init__.py
  │   └── ...
  ├── settings
  │   ├── __init__.py
  │   └── local.py
  └── yet_other_app
      ├── __init__.py
      └── ...

.. _namespace-package-support:

``namespace_package_support``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This extension monkey-patches [1]_ Django so that is supports namespace packages. Not all places are
covered though so if you spot some feature where namespace packages still don't work, file an issue
using our `issue tracker <http://github.com/LangaCore/kitdjango/issues>`_.

Features supported:

* custom commands for manage.py loaded correctly from apps within namespace packages; since 0.1.8

``profile_support``
~~~~~~~~~~~~~~~~~~~

Splitting global settings from instance-specific ones is also a very frequent task that most Django
projects implement in one way or another. There are many reasons why such separation is desirable
but the most important ones are:

* if one global settings file is not enough to run the project, it forces the administrator
  deploying every instance to specify the local settings. This way no incompatible settings are used
  by default

* when global settings are kept separate, adding, deleting or editing entries doesn't cause
  conflicts while using source code version control systems [2]_

So, how do you get to split your ``settings.py`` file? The simplest approach is to create a file
with the local settings as a module and just import it at the end of the global one. This approach
has two significant drawbacks: you cannot use/edit variables specified in the global settings and
the name of the local module is now hard-coded within the global file.

Enter ``profile_support``! With this extension you can have several local-specific settings modules
which are executed in the global settings context. This means you can within your local settings do
things like::

  INSTALLED_APPS += (
    'debug_toolbar',
  )

  MEDIA_ROOT = CURRENT_DIR + 'static'

where you add the debug toolbar to the active apps (notice the ``+=`` operator) and ``CURRENT_DIR``
is the one calculated by enabling ``current_dir_support``. To enable profiles, just add these lines
at the very end of your ``settings.py`` file::

  from langacore.kit.django import profile_support
  execfile(profile_support)

By default, this enables loading settings found in ``settings-local.py``. There are times when you
need more than one config profile though, for instance:

* you might want to have a very verbose debugging configuration for squashing the most persistent of
  bugs; most of the time however this kind of verbosity wouldn't be desirable)

* the live instance of your project is using a database user without database schema modification
  rights but you still want to be able to run ``manage.py syncdb`` and ``manage.py migrate``

* you need to specify separate settings for your unit testing needs

Without ``profile_support`` you would create some "toggle" variables like ``SYNC_DB`` or
``VERBOSE_DEBUG`` and use ``if``/``else`` within the settings. Thanks to ``profile_support`` you
can treat ``settings.py`` files like regular configuration files without any logic and just
use different local profiles. To change to a profile different from *"local"* when running a
command, just specify the ``DJANGO_SETTINGS_PROFILE`` environment variable::

  DJANGO_SETTINGS_PROFILE=syncdb python manage.py migrate

In that case, the local settings will be loaded from ``settings-syncdb.py`` and not from
``settings-local.py``.

If you use profiles heavily, the root project folder gets quite cluttered with ``settings-*.py``
files. In that case you might switch to package based configuration. Just make a directory called
``settings``, move your existing ``settings.py`` to ``settings/__init__.py`` and your
``settings-*.py`` files to ``settings/*.py``. Then your project tree will look something like the
one on the diagram in the ``current_dir_support`` description above. 

Custom ``manage.py`` commands
=============================

By adding ``langacore.kit.django.common`` to your ``INSTALLED_APPS`` you get some additional
second-level commands for ``manage.py``:

* ``shell``: a version of the original `manage.py shell
  <http://docs.djangoproject.com/en/dev/ref/django-admin/#shell>`_ command for lazy people: is using 
  `bpython <http://bpython-interpreter.org/>`_ if installed and imports all models automatically

.. note::
  
  These commands require :ref:`namespace-package-support`.

Filters
=======

The filters below are usable directly from pure Python code and obviously work as templatetags as
well:

.. currentmodule:: langacore.kit.django.filters

.. autosummary::

  numberify
  nullify
  slugify
  strike_empty
  title
  transliterate

To use these filters in your source code, simply import them from ``langacore.kit.django.filters``.
To use them as templatetags, add the ``langacore.kit.django.common`` app to ``INSTALLED_APPS``
within your ``settings.py`` and in the specific template use::

  {%load LIB_NAME%}

where ``LIB_NAME`` is the templatetag library name for the specific filter (available in the filter
description). For instance, for ``strike_empty`` or ``title`` it would be::

 {%load strings%}

There are more filters whose implementation makes them useful only as templatetags. These include:
  
.. currentmodule:: langacore.kit.django.common.templatetags

.. autosummary::
  
  bbcode.bbcode


Module details
==============
For more detailed view on the modules, see the documentation below.

.. currentmodule:: langacore.kit.django

.. autosummary::
  :toctree:

  cache
  filters
  common.forms
  common.models
  common.templatetags.bbcode
  common.templatetags.converters
  common.templatetags.strings

Footnotes
~~~~~~~~~

.. [1] Yup, in the world of Python that's considered dangerous and a sign of bad design. Here it's
  simply a sane way to overcome Django core development inertia. Go ahead and ask for namespace
  package support in vanilla Django.
.. [2] May I kindly suggest `Git <http://git-scm.com/>`_ or `Mercurial <http://mercurial.selenic.com/>`_?
