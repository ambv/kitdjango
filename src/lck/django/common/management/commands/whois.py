#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2013 by Łukasz Langa
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

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from datetime import datetime
import sys

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session


class Command(BaseCommand):
    help = ("Returns the username and e-mail given a session ID.")

    requires_model_validation = False

    def handle(self, *args, **options):
        session_key = None
        for session_key in args:
            try:
                s = Session.objects.get(session_key=session_key)
            except Session.DoesNotExist:
                print("error: Session {} not found.".format(session_key),
                      file=sys.stderr)
            else:
                d = s.get_decoded()
                print("{session.session_key}\n"
                        "expires {session.expire_date}".format(
                            session=s
                        )
                )
                if '_auth_user_id' in d:
                    user = User.objects.get(pk=d['_auth_user_id'])
                    print("userid={user.id}\n"
                          "username={user.username}\nemail={user.email}\n"
                          "".format(user=user)
                    )
                else:
                    print("anonymous\n")
        if session_key is None:
            now = datetime.now()
            for s in Session.objects.filter(expire_date__gte=now).order_by(
                    '-expire_date'):
                print(s.get_decoded())
