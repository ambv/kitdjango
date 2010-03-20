"""
Contains a small set of useful abstract model base classes that are not application-specific.
"""

from datetime import datetime
from django.db import models as db
from django.utils.translation import ugettext_lazy as _
from django.core.mail import send_mail


class Named(db.Model):
    """
    Describes an abstract model with a ``name`` field.
    """
    name = db.CharField(verbose_name=_("name"), max_length=20, unique=True)

    class Meta:
        abstract = True

    def __unicode__(self):
        return self.name


class TimeTrackable(db.Model):
    """
    Describes an abstract model whose lifecycle is tracked by time. Includes
    a ``created`` field that is set automatically upon object creation and
    a ``modified`` field that is set automatically upon calling ``save()`` on
    the object.
    """
    created = db.DateTimeField(verbose_name=_("date created"), default=datetime.now)
    modified = db.DateTimeField(verbose_name=_("last modified"), default=datetime.now)
    
    class Meta:
        abstract = True

    def save(self):
        self.modified = datetime.now()
        super(TimeTrackable, self).save()


class DisplayCounter(db.Model):
    """
    Describes an abstract model which display count can be incremented by calling
    ``bump()``. Models inheriting from ``DisplayCounter`` can define a special ``bump_save()``
    method which is called instead of the default ``save()`` on each ``bump()`` (for instance
    to circumvent updating the ``modified`` field if the model is also ``TimeTrackable``.
    """
    display_count = db.PositiveIntegerField(verbose_name=_("display count"), default=0, editable=False)

    def bump(self):
        self.display_count += 1
        if not 'bump_save' in dir(self):
            self.save()
        else:
            self.bump_save()

    class Meta:
        abstract = True


class ViewableSoftDeletableManager(db.Manager):
    """
    An objet manager to automatically hide objects that were soft deleted for models
    inheriting ``SoftDeletable``.
    """
    def get_query_set(self):                                                                                                                                                                       
        # get the original query set
        query_set = super(ViewableSoftDeletableManager, self).get_query_set()
        # leave rows which are deleted
        query_set = query_set.filter(deleted=False)
        return query_set


class SoftDeletable(db.Model):
    """
    Describes an abstract models which can be soft deleted, that is instead of actually
    removing objects from the database, they have a ``deleted`` field which is set to ``True``
    and the object is then invisible in normal operations (thanks to ``ViewableSoftDeletableManager``).
    """
    deleted = db.BooleanField(verbose_name=_("deleted"), default=False)
    admin_objects = db.Manager()                                                                                                                                                                         
    objects = ViewableSoftDeletableManager()

    class Meta:
        abstract = True
    

# For now this needs to be at the end of the file.
# FIXME: move it where it's supposed to be.

import os
from time import sleep
from threading import Thread

class MassMailer(Thread):
    """
    A thread that can be used to mail the specified profiles with a certain message.
    After every message it waits a specified time (by default a second).
    """
    def __init__ (self, profiles, subject, content, inverval=1.0, force=False):
        """ Creates the thread.

        :param profiles: a sequence of profiles that are to be mailed

        :param subject: the subject of the message to be sent

        :param content: the actual content to be sent
        
        :param interval: number of seconds to wait after sending every message

        :param force: if ``True``, privacy settings of the users are disregarded
        """

        Thread.__init__(self)
        self.profiles = profiles
        self.subject = subject
        self.content = content
        self.interval = interval
        self.force = force
        
    def run(self):
        print "Mailer subprocess started (%d)." % os.getpid()
        for profile in self.profiles:
            mail = profile.user.email
            # FIXME: check privacy
            send_mail(self.subject, self.content, None, [mail])
            print "Mailer subprocess (%d): sent mail to %s." % (os.getpid(), mail)
            sleep(self.interval)

# NO CODE BEYOND THIS POINT
