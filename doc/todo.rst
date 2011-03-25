====
TODO
====
  
  Things that would be great to have but I haven't gotten to do them yet.

Code
----

* Migrate from the overly verbose ``langacore.kit.django`` namespace to
  a shorter one (``lck.django`` looks nice. ``lckd`` would be even shorter
  but I'd like to be consistent with the rest of the ``langacore.kit`` packages)

* Cleanup of forms would be great
  
* There are not enough unit tests

  * in particular, ``py.test`` is used for the existing tests which makes proper
    unit testing for Django-specific bits harder. Struggling with
    ``django-pytest`` did not produce any results as of yet.

* No examples in the code

Docs
----

* Bits documented only by means of API, no proper introduction:

  * forms

  * models

* Bits undocumented:

  * score
    
  * tags

* There is no clear roadmap of where this project is heading

* No FAQ, Tutorial

Community
---------

* There is no community

* Migrate to the MIT license

* Some publicity would be helpful
