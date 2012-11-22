====
TODO
====

Roadmap
-------

Version 0.9
~~~~~~~~~~~

Convert unit tests to base on unittest2. Create introductory material for common
models, activitylog, score and tags: tutorials, examples and FAQ.

Version 1.0
~~~~~~~~~~~

Drop support for Django 1.3.

Separate some of the more useful things as their own packages.  Currently these
are already separated:

* `dj.chain <http://pypi.python.org/pypi/dj.chain>`_

* `dj.choices <http://pypi.python.org/pypi/dj.choices>`_

These would be great to separate:

* cache (needs updating first)

* namespace package support (so that all other dj.* packages work out of the box
  for users)

* thumbnail filter

Make all separated packages compatible with Python 3.x.

Unit test the rest, remove what's supported out of the box in Django 1.4.

Clean up forms.

Random ideas
------------

* make the timing middleware store the results somewhere somehow

* custom inlines which set lck-specific readonly fields by default

* future date filter for the admin

* Migrate configuration of lck.django.cache to the 1.3+ variant

* Base `django-admin.py shell` on 1.4

* Deprecate execfile()-based settings hacking

* There are not enough unit tests

  * in particular, ``py.test`` is used for the existing tests which makes proper
    unit testing for Django-specific bits harder. Struggling with
    ``django-pytest`` did not produce any results as of yet.

* No examples in the code

* Bits documented only by means of API, some proper introduction would be handy:

  * forms

  * models

  * score
    
  * tags

* No FAQ, Tutorial
