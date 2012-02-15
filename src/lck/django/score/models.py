#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 by Łukasz Langa
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

"""lck.django.score.models
   -----------------------

   Models holding votes for objects of different types. Usage::

        TotalScore.get_value(object) -> int
        TotalScore.update(object, voter, value, [reason]) -> int
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.generic import GenericForeignKey
from django.db import models as db
from django.utils.translation import ugettext_lazy as _

from lck.django.common.models import TimeTrackable
from lck.django.score.signals import total_score_changed


SCORE_VOTER_MODEL = getattr(settings, 'SCORE_VOTER_MODEL', User)


class TotalScore(db.Model):
    """Holds the integer `value` of the total score for votes on a specific
    `content_object`. The `value` is updated whenever a Vote object is created,
    modified or deleted. Don't alter it directly."""
    value = db.IntegerField(verbose_name=_("value"), default=0, db_index=True)
    content_type = db.ForeignKey(ContentType, verbose_name=_("Content type"),
        related_name="%(app_label)s_%(class)s_scores")
    object_id = db.IntegerField(verbose_name=_("Content type instance id"),
        db_index=True)
    content_object = GenericForeignKey()

    class Meta:
        verbose_name = _("total score")
        verbose_name_plural = _("total scores")

    def __unicode__(self):
        return "Total score for ({}.id={}): {}".format(self.content_type,
            self.object_id, self.value)

    @classmethod
    def get_stats_for_model(cls, cases, model, instance=None, ct=None):
        """Returns a list of stats computed using the specified `cases` which
        are a sequence of filtering arguments for the TotalScore vote_set for
        the specified model (and optionally: instance)."""
        if not ct:
            ct = ContentType.objects.get_for_model(model)
        kwargs = {'total_score__content_type': ct}
        if instance:
            kwargs['total_score__object_id'] = instance.id
        stats = []
        for case in cases:
            case.update(kwargs)
            case_sum = Vote.objects.filter(**case).count()
            stats.append(case_sum)
        return stats

    @classmethod
    def get_value(cls, object, voter=None, ct=None):
        """TotalScore.get_value(object, [voter, ct]) -> int

        Returns the current score for the specific `object` or 0 if no-one
        voted for it yet. Optionally gets value for a specific `voter`."""
        try:
            if not ct:
                ct = ContentType.objects.get_for_model(object.__class__)
            score = cls.objects.get(content_type=ct, object_id=object.id)
            if voter:
                score = Vote.objects.get(total_score=score, voter=voter)
            return score.value
        except (cls.DoesNotExist, Vote.DoesNotExist):
            return 0

    @classmethod
    def update(cls, object, voter, value, reason="", ct=None):
        """TotalScore.update(object, voter, value, [reason, ct]) -> int

        Updates the score on `object` by voting the specific integer `value`
        as user `voter`. Optionally, a `reason` can be added to the vote.
        If the `voter` already voted for this `object`, she can cancel her vote
        by specifying `value` that is the opposite to the one already given.
        Other attempts to vote multiple times for a single `object` will be
        silently ignored.

        Conveniently returns the updated total score for the given object."""
        try:
            if not ct:
                ct = ContentType.objects.get_for_model(object.__class__)
            total_score = cls.objects.get(content_type=ct, object_id=object.id)
        except cls.DoesNotExist:
            # no-one voted before for that object
            total_score = cls(content_object=object)
            total_score.save()
        if isinstance(voter, int):
            voter = Vote.voter.field.rel.to.objects.get(pk=voter)
        # TotalScore values in the database are updated automatically on
        # vote creation, modification and deletion but the `total_score`
        # instance we have will not. To avert returning a stale value we
        # use a helper `result` variable.
        result = total_score.value
        try:
            vote = Vote.objects.get(total_score=total_score,
                voter=voter)
            if -value == vote.value:
                # we let people cancel existing votes
                vote.delete()
                result -= vote.value
        except Vote.DoesNotExist:
            if value: # don't create empty votes in the database
                vote = Vote(total_score=total_score, voter=voter, value=value,
                    reason=reason)
                vote.save()
                result += vote.value
        return result


class Vote(TimeTrackable):
    """A single vote. Total score value is updated upon creation and alteration
    of Vote instances, don't update it directly."""
    total_score = db.ForeignKey(TotalScore, verbose_name=_("total score"))
    voter = db.ForeignKey(SCORE_VOTER_MODEL, verbose_name=_("voter"))
    value = db.IntegerField(verbose_name=_("value"), default=1, db_index=True)
    reason = db.TextField(verbose_name=_("reason"), blank=True, default="")

    class Meta:
        verbose_name = _("vote")
        verbose_name_plural = _("votes")
        unique_together = ['total_score', 'voter']

    def __unicode__(self):
        score_repr = ("+{}" if self.value > 0 else "{}").format(self.value)
        return "Vote {} for ({}.id={}) by {}".format(score_repr,
            self.total_score.content_type, self.total_score.object_id,
            self.voter)


def dispatch_total_score_changed(total_score):
    total_score_changed.send_robust(sender=TotalScore,
        content_object=total_score.content_object, value=total_score.value)


def vote_pre_save(sender, instance, **kwargs):
    """Alters the total score value for the created/modified Vote."""
    try:
        existing = sender.objects.get(pk=instance.id)
        diff = instance.value - existing.value
        # if existing.voter != instance.voter is handled at the
        # `unique_together` level of Vote objects
    except sender.DoesNotExist:
        diff = instance.value
    instance.total_score.value += diff
    instance.total_score.save()
db.signals.pre_save.connect(vote_pre_save, Vote)


def vote_post_save(sender, instance, **kwargs):
    dispatch_total_score_changed(instance.total_score)
db.signals.post_save.connect(vote_post_save, Vote)


def vote_post_delete(sender, instance, **kwargs):
    """Decreases total score value by the value of the currently removed
    object."""
    instance.total_score.value -= instance.value
    instance.total_score.save()
    dispatch_total_score_changed(instance.total_score)
db.signals.post_delete.connect(vote_post_delete, Vote)
