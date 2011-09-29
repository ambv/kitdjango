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
