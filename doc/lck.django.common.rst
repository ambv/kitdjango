:mod:`lck.django.common`
========================

.. automodule:: lck.django.common


Rendering functions
-------------------

.. autofunction:: redirect

.. autofunction:: render

.. autofunction:: render_json

.. autofunction:: typical_handler

Decorators
----------

.. autofunction:: nested_commit_on_success

Misc
----

.. autofunction:: cut

.. autoclass:: lazy_chain
   :members:

.. note::

  The legacy ``lazy_chain`` name will be removed in lck.django 1.0. Use
  `dj.chain <http://pypi.python.org/pypi/dj.chain>`_.

.. autofunction:: remote_addr
