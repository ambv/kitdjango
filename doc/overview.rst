Overview
--------

For now the library is still tiny. Functionality gets added or refined as
needed. To see what's already available, let's do a quick tour over each feature
group.

Choices objects
===============

This is a much clearer way to specify choices for fields in models and forms.
A basic example::

    >>> from lck.django.choices import Choices
    >>> class Gender(Choices):
    ...   _ = Choices.Choice
    ...   
    ...   male = _("Male")
    ...   female = _("Female")
    ... 
    >>> Gender()
    [(1, u'Male'), (2, u'Female')]
    >>> Gender.male
    <Choice: male (id: 1)>
    >>> Gender.female
    <Choice: female (id: 2)>
    >>> Gender.male.id
    1
    >>> Gender.male.desc
    u'Male'
    >>> Gender.male.raw
    'Male'
    >>> Gender.male.name
    u'male'
    >>> Gender.FromName("male")
    <Choice: male (id: 1)>
    >>> Gender.IDFromName("male")
    1
    >>> Gender.RawFromName("male")
    'Male'
    >>> Gender.DescFromName("male")
    u'Male'
    >>> Gender.NameFromID(2)
    'female'
    >>> Gender.NameFromID(3)
    Traceback (most recent call last):
    ...
    ValueError: Nothing found for '3'.
    >>> Gender.FromName("perez")
    Traceback (most recent call last):
    ...
    ValueError: Nothing found for 'perez'.

You define a class of choices, specifying each choice as a class attribute.
Those attributes automatically get indexes (starting with 1). The class provides
several features which support the DRY principle:

 * An object created from the choices class is basically a list of ``(id,
   localized_description)`` pairs straight for consumption by Django.

 * Each attribute defined can be retrieved directly from the class.
   
 * Metadata (e.g. attribute name, raw and localized description, numeric ID) of
   each attribute is accessible.

 * Choices which are suffixed by ``_`` to avoid clashing with Python keywords
   have this suffix automatically removed in their ``.name`` attributes

 * Lookup functions are available to help getting attributes or their metadata.

.. note::   
    The ``_ = Choices.Choice`` trick makes it possible for ``django-admin.py
    makemessages`` to find each choice description and include it in ``.po``
    files for localization. It masks ugettext only in the scope of the class so
    the rest of the module can safely use ugettext or ugettext_lazy. Having to
    specify ``_`` each time is not a particularly pretty solution but it's
    explicit. Suggestions for a better approach are welcome.

Grouping choices
~~~~~~~~~~~~~~~~

One of the worst problems with choices is their weak extensibility. For
instance, an application defines a group of possible choices like this::

    >>> class License(Choices):
    ...   _ = Choices.Choice
    ...   
    ...   gpl = _("GPL")
    ...   bsd = _("BSD")
    ...   proprietary = _("Proprietary")
    ... 
    >>> License()
    [(1, u'GPL'), (2, u'BSD'), (3, u'Proprietary')]
   
All is well until the application goes live and after a while the developer
wants to include LGPL. The natural choice would be to add it after ``gpl`` but
when we do that, the indexing would break. On the other hand, adding the new
entry at the end of the definition looks ugly and makes the resulting combo
boxes in the UI sorted in a counter-intuitive way. Grouping lets us solve this
problem by explicitly defining the structure within a class of choices::

    >>> class License(Choices):
    ...   _ = Choices.Choice
    ...   
    ...   COPYLEFT = Choices.Group(0)
    ...   gpl = _("GPL")
    ...   
    ...   PUBLIC_DOMAIN = Choices.Group(100)
    ...   bsd = _("BSD")
    ...   
    ...   OSS = Choices.Group(200)
    ...   apache2 = _("Apache 2")
    ...   
    ...   COMMERCIAL = Choices.Group(300)
    ...   proprietary = _("Proprietary")
    ... 
    >>> License()
    [(1, u'GPL'), (101, u'BSD'), (201, u'Apache 2'), (301, u'Proprietary')]

This enables the developer to include more licenses of each group later on::

    >>> class License(Choices):
    ...   _ = Choices.Choice
    ...   
    ...   COPYLEFT = Choices.Group(0)
    ...   gpl_any = _("GPL, any")
    ...   gpl2 = _("GPL 2")
    ...   gpl3 = _("GPL 3")
    ...   lgpl = _("LGPL")
    ...   agpl = _("Affero GPL")
    ...   
    ...   PUBLIC_DOMAIN = Choices.Group(100)
    ...   bsd = _("BSD")
    ...   public_domain = _("Public domain")
    ...   
    ...   OSS = Choices.Group(200)
    ...   apache2 = _("Apache 2")
    ...   mozilla = _("MPL")
    ...   
    ...   COMMERCIAL = Choices.Group(300)
    ...   proprietary = _("Proprietary")
    ... 
    >>> License()
    [(1, u'GPL, any'), (2, u'GPL 2'), (3, u'GPL 3'), (4, u'LGPL'),
     (5, u'Affero GPL'), (101, u'BSD'), (102, u'Public domain'),
     (201, u'Apache 2'), (202, u'MPL'), (301, u'Proprietary')]

Note the behaviour:

 * the developer renamed the GPL choice but its meaning and ID remained stable

 * BSD, Apache and proprietary choices have their IDs unchanged

 * the resulting class is self-descriptive, readable and extensible

As a bonus, the explicitly specified groups can be used when needed::

    >>> License.COPYLEFT
    <ChoiceGroup: COPYLEFT (id: 0)>
    >>> License.gpl2 in License.COPYLEFT.choices
    True
    >>> [(c.id, c.desc) for c in License.COPYLEFT.choices]
    [(1, u'GPL, any'), (2, u'GPL 2'), (3, u'GPL 3'), (4, u'LGPL'),
     (5, u'Affero GPL')]

Advanced functionality
~~~~~~~~~~~~~~~~~~~~~~

The developer can specify all possible choices for future use and then filter
out only the currently applicable values on choices creation::

    >>> class Language(Choices):
    ...   _ = Choices.Choice
    ...   
    ...   de = _("German")
    ...   en = _("English")
    ...   fr = _("French")
    ...   pl = _("Polish")
    ... 
    >>> Language()
    [(1, u'German'), (2, u'English'), (3, u'French'), (4, u'Polish')]
    >>> Language(filter=("en", "pl"))
    [(2, u'English'), (4, u'Polish')]
    
This has the great advantage of keeping the IDs and sorting intact.

One can also change how the pairs are constructed by providing a factory
function. For instance, to use the class of choices defined above for the
``LANGUAGES`` setting in ``settings.py``, one could specify::

    >>> Language(pair=lambda choice: (choice.name, choice.raw))
    [(u'de', 'German'), (u'en', 'English'), (u'fr', 'French'),
     (u'pl', 'Polish')]

Predefined choices
~~~~~~~~~~~~~~~~~~

There are several classes of choices which are very common in web applications
so they are provided already:

.. currentmodule:: lck.django.choices

.. autosummary::

  Country
  Gender
  Language
 
Extensions for ``settings.py``
==============================

One of the most often customized parts of a Django project is ``settings.py``.
To ease the process and protect against possible mistakes when doing the same
exact modification for the n-th time, a set of extensions for ``settings.py``
was developed. The extensions are activated by importing them and executing::

  from lck.django import current_dir_support
  execfile(current_dir_support)

This is done so to enable the extensions access to the current local namespace
of ``settings.py``.  If anyone knows a more elegant way to do that, let me know.
For now this seems a good approach though.

``current_dir_support``
~~~~~~~~~~~~~~~~~~~~~~~

This extension injects a ``CURRENT_DIR`` variable into ``settings.py`` so it is
available from the moment of definitions onwards. ``CURRENT_DIR`` in this
context means the root of the project ("current" because most of the time this
is the same dir where ``settings.py`` resides). An additional feature is that it
is always ending with ``os.sep`` so it's perfectly safe to do something like::

  from lck.django import current_dir_support
  execfile(current_dir_support)

  (...)

  MEDIA_ROOT = CURRENT_DIR + 'media/'

Moreover, ``CURRENT_DIR`` gets set properly also for the projects that use
a **package** for specifying settings, e.g. a structure like that::

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

To enable this extension, import and execute it in the ``settings.py`` context
(**at the very beginning** of the config file is recommended since
``CURRENT_DIR`` is available only after the extension's initialization).


.. _namespace-package-support:

``namespace_package_support``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This extension monkey-patches [1]_ Django so that is supports namespace
packages. Not all places are covered though so if you spot some feature where
namespace packages still don't work, file an issue using our `issue tracker
<http://github.com/lckdjango/issues>`_.

To enable this extension, import and execute it in the ``settings.py`` context
(anywhere within the config file is fine)::

  from lck.django import namespace_package_support 
  execfile(namespace_package_support)

Features supported:

* custom commands for manage.py loaded correctly from apps within namespace
  packages; since 0.1.8

``profile_support``
~~~~~~~~~~~~~~~~~~~

Splitting global settings from instance-specific ones is also a very frequent
task that most Django projects implement in one way or another. There are many
reasons why such separation is desirable but the most important ones are:

* if one global settings file is not enough to run the project, it forces the
  administrator deploying every instance to specify the local settings. This way
  no incompatible settings are used by default

* when global settings are kept separate, adding, deleting or editing entries
  doesn't cause conflicts while using source code version control systems [2]_

So, how do you get to split your ``settings.py`` file? The simplest approach is
to create a file with the local settings as a module and just import it at the
end of the global one. This approach has two significant drawbacks: you cannot
use/edit variables specified in the global settings and the name of the local
module is now hard-coded within the global file.

Enter ``profile_support``! With this extension you can have several
local-specific settings modules which are executed in the global settings
context. This means you can within your local settings do things like::

  INSTALLED_APPS += (
    'debug_toolbar',
  )

  MEDIA_ROOT = CURRENT_DIR + 'static'

where you add the debug toolbar to the active apps (notice the ``+=`` operator)
and ``CURRENT_DIR`` is the one calculated by enabling ``current_dir_support``.
To enable profiles, just add these lines **at the very end** of your
``settings.py`` file::

  from lck.django import profile_support
  execfile(profile_support)

By default, this enables loading settings found in ``settings-local.py``. There
are times when you need more than one config profile though, for instance:

* you might want to have a very verbose debugging configuration for squashing
  the most persistent of bugs; most of the time however this kind of verbosity
  wouldn't be desirable)

* the live instance of your project is using a database user without database
  schema modification rights but you still want to be able to run ``manage.py
  syncdb`` and ``manage.py migrate``

* you need to specify separate settings for your unit testing needs

Without ``profile_support`` you would create some "toggle" variables like
``SYNC_DB`` or ``VERBOSE_DEBUG`` and use ``if``/``else`` within the settings.
Thanks to ``profile_support`` you can treat ``settings.py`` files like regular
configuration files without any logic and just use different local profiles. To
change to a profile different from *"local"* when running a command, just
specify the ``DJANGO_SETTINGS_PROFILE`` environment variable::

  DJANGO_SETTINGS_PROFILE=syncdb python manage.py migrate

In that case, the local settings will be loaded from ``settings-syncdb.py`` and
not from ``settings-local.py``.

If you use profiles heavily, the root project folder gets quite cluttered with
``settings-*.py`` files. In that case you might switch to package based
configuration. Just make a directory called ``settings``, move your existing
``settings.py`` to ``settings/__init__.py`` and your ``settings-*.py`` files to
``settings/*.py``. Then your project tree will look something like the one on
the diagram in the ``current_dir_support`` description above. 

Custom ``manage.py`` commands
=============================

By adding ``lck.django.common`` to your ``INSTALLED_APPS`` you get
some additional second-level commands for ``manage.py``:

* ``shell``: a version of the original `manage.py shell
  <http://docs.djangoproject.com/en/dev/ref/django-admin/#shell>`_ command for
  lazy people: is using `bpython <http://bpython-interpreter.org/>`_ if
  installed and imports all models automatically

.. note::
  
  These commands require :ref:`namespace-package-support`.

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


Module details
==============
For more detailed view on the modules, see the documentation below.

.. currentmodule:: lck.django

.. autosummary::
  :toctree:

  cache
  choices
  filters
  helpers
  common.forms
  common.middleware
  common.models
  common.templatetags.bbcode
  common.templatetags.converters
  common.templatetags.cycle_filter
  common.templatetags.strings
  common.templatetags.thumbnail
  profile.models

Footnotes
~~~~~~~~~

.. [1] Yup, in the world of Python that's considered dangerous and a sign of bad
    design. Here it's simply a sane way to overcome Django core development inertia.
    Go ahead and ask for namespace package support in vanilla Django.

.. [2] May I kindly suggest `Git <http://git-scm.com/>`_ or `Mercurial
    <http://mercurial.selenic.com/>`_?
