----------
lck.django
----------

This library consists of various Django-related routines that extend or modify
the behaviour of the framework:

 * lots of abstract models to use

 * a user activity log app storing users' IP addresses and user agents (useful
   for hunting down multi-accounts)

 * a simple ``score`` app

 * a ``tags`` app which is unlike other popular tagging applications for Django
   in the fact that it supports tagging by users and localized tags

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

0.6.6
~~~~~

* ``MACAddressField`` MAC address normalization ignores empty values, supports
  Cisco ``0000.0000.0000`` notation and fixes a minor regression from 0.6.5

* ``SessionAwareLanguageMiddleware`` introduced

* a convenient tag getter for taggables, improved compatibility with
  ``EditorTrackable``

0.6.5
~~~~~

* more rigorous normalization of MAC addresses in ``MACAddressField``

0.6.4
~~~~~

* ``ImageModel`` introduced

* ``Named`` models name field extended to 75 characters of length

0.6.3
~~~~~

* fixed an embarassing bug with the human-readable ``timediff`` filter

0.6.2
~~~~~

* ``MACAddressField`` normalization bug fixed

0.6.1
~~~~~

* buttonable Django admin with ``ModelAdmin``

* "Edit separately" links for ForeignKey fields supported in ``ModelAdmin``

* compressing ``PyLibMCCache`` backend in ``lck.django.cache_backends``

* backlinks support in ``activitylog``

* images crushed and optimized

* use Pillow instead of PIL

0.6.0
~~~~~

Oh boy, lots of changes!

* ``TimeTrackable`` just got a lot smarter. Includes ``cache_version``
  attribute automatically updated on significant changes to the object.
  ``modified`` gets updated only when there are actual changes to the object.
  ``dirty_fields`` property shows changed attributes from last save (works also
  for objects composed from multiple models, including abstract ones).
    
  Inspired by David Cramer and Simon Willison at EuroPython 2011.

* The dogpile-safe ``lck.django.cache`` now supports custom invalidators which
  enables invalidation not only by time but also by e.g. model changes (think
  ``TimeTrackable.cache_version``).

* Settings profile support now requires a modified ``manage.py`` script in the
  Django project. This is forced by the unfortunate design of how Django loads
  settings.

* Activity logging moved to its own app, ``lck.activitylog``, which now also
  tracks IPs and user agents of logged-in visitors (useful in hunting
  multi-accounts). 

* Introduced a ``SavePrioritized`` abstract model which adds priorities to
  saves on models. Various parts of the application can specify which priority
  they use. If they update an attribute which was first saved by something with
  higher priority, the update is silently ignored.

* Introduced a concurrency-aware variant of the popular
  ``Model.objects.get_or_create`` (unsurprisingly called
  ``concurrent_get_or_create``)

* Introduced a ``commit_on_success`` variant that supports nesting
  (unsurprisingly called ``nested_commit_on_success``)

* Introduced ``BasicAuthMiddleware`` for simplistic private URL protecting.

* ``EditorTrackable`` is now safe in terms of foreign key cascading (content
  authored or modified by a user won't get deleted after this user is removed
  from the DB). Plus some nice admin refinements.

* Now ``TimingMiddleware`` doesn't break other middlewares using
  ``process_view()`` and is generally smarter.

* Added ``X-Slo`` header in responses for ``TimingMiddleware``.

* ``render()`` now calculates and emits ETags based on the rendering output.

* ``typical_handler()`` can now ``redirect_on_success``.

* Links from the BBCode filter now open in a new window and have
  ``rel="nofollow"`` set.

* Introduced a ``{%settings KEY%}`` templatetag.

* Introduced a ``{%git_version%}`` templatetag which returns a short string
  useful to present as an app version. This is based on the latest commit in
  the Git repository where the Django project lies in.

* The ``cycle_filter`` template filter now supports explicit counter settings
  and incrementation.

* Introduced template filters converting to and from Base64.

* Introduced JQuery UI and JQueryMobile integrated radio widgets.

* Improved documentation.

* More complete translations.

0.5.8
~~~~~

* Simplistic ``TimingMiddleware`` introduced.

* Profiles based on ``BaseProfile`` now return ``self`` for ``get_profile()``.

* Trophy icons added.

* Console tag library introduced with the {%color%} tag.

* Allow rendering non-request contexts.

* ``Choices.ToNames`` decorator introduced.

* Pre-importing in ``manage.py shell`` works also for models with
  a custom``app_model``.

0.5.7
~~~~~

* ``EditorTrackable`` introduced

* Choices can be rendered in grouped form. Currently requires adding
  ``'--keyword=Group:2 '`` to xgettext invocations in
  django/core/managemenet/commands/makemessages.py. Cleaning that up is planned
  for 0.6.0.

* ``typical_handler`` works now with forms w/o a ``save()`` method

* ``upperfirst`` filter introduced: ups only the first character

* Square thumbnails for wide images now work properly

* moved contents of helpers to common (enables i18n and cleans up the API), the
  helpers module is therefore deprecated

* some i18n updates

0.5.6
~~~~~

* in the thumbnail filter, support for automatic cropping to square introduced

* minor translation updates

0.5.5
~~~~~

* group members inherit shifted attributes

0.5.4
~~~~~

* minor updates to ``PolishDateWidget``

0.5.3
~~~~~ 

* ``AvatarSupport`` abstract model for custom avatars. ``GravatarSupport`` can
  be used as fallback or independently.

* ``typical_handler`` now properly supports file uploads

* bugfixes: objects without any score don't cause exceptions anymore
  
* leftovers from namespace changes cleaned up

0.5.2
~~~~~

* monkey patches of core Django annotated and regrouped for easier management in
  the future (yup, more to come)

* a stats calculator

* minor bugfixes

0.5.1
~~~~~

* tags now support models with custom managers

* for Named and Titled models a read-only ``name_urlencoded`` and
  ``title_urlencoded`` properties were introduced. Useful as arguments in
  template tags.

* support for setting additional attributes on choices using an unholy ``<<``
  operator overload

* in tags, support for getting objects marked with specific stems

0.5.0
~~~~~

* migrated to the ``lck`` namespace from ``langacore.kit``

* migrated licensing from GPL 3 to MIT

* bumped the trove from alpha status to beta, the code is in production for over
  a year now

Ancient history
~~~~~~~~~~~~~~~

* No proper change log was kept before 0.5.0
