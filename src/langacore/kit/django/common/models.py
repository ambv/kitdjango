from datetime import datetime
from django.db import models as db
from django.utils.translation import ugettext_lazy as _
from django.core.mail import send_mail


class Named(db.Model):
    name = db.CharField(verbose_name=_("name"), max_length=20, unique=True)

    class Meta:
        abstract = True

    def __unicode__(self):
        return self.name


class TimeTrackable(db.Model):
    created = db.DateTimeField(verbose_name=_("date created"), default=datetime.now)
    modified = db.DateTimeField(verbose_name=_("last modified"), default=datetime.now)
    
    class Meta:
        abstract = True

    def save(self):
        self.modified = datetime.now()
        super(TimeTrackable, self).save()


class DisplayCounter(db.Model):
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
    def get_query_set(self):                                                                                                                                                                       
        # get the original query set
        query_set = super(ViewableSoftDeletableManager, self).get_query_set()
        # leave rows which are deleted
        query_set = query_set.filter(deleted=False)
        return query_set


class SoftDeletable(db.Model):
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
    def __init__ (self, profiles, subject, content, force):
        Thread.__init__(self)
        self.profiles = profiles
        self.subject = subject
        self.content = content
        self.force =force
        
    def run(self):
        print "Mailer subprocess started (%d)." % os.getpid()
        for profile in self.profiles:
            mail = profile.user.email
            # FIXME: check privacy
            send_mail(self.subject, self.content, None, [mail])
            print "Mailer subprocess (%d): sent mail to %s." % (os.getpid(), mail)
            sleep(1)

# NO CODE BEYOND THIS POINT
