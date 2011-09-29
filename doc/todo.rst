====
TODO
====
  
  Things that would be great to have but I haven't gotten to do them yet.

Code
----

* make the timing middleware store the results somewhere somehow

* custom inlines which set lck-specific readonly fields by default

* future date filter for the admin

* create some ingenious hack which allows Profile-based inlines in User
  ModelAdmins

* Migrate configuration of lck.django.cache to 1.3

* Migrate `django-admin.py shell` to 1.3

* Cleanup of forms would be great
  
* Deprecate execfile()-based settings hacking

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

  * score
    
  * tags

* There is no clear roadmap of where this project is heading

* No FAQ, Tutorial

Community
---------

* There is no community

* Some publicity would be helpful
