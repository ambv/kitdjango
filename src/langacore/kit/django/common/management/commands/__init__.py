#!/usr/bin/env python
import os
import sys
from optparse import make_option

import django.core.management.base
from django.core.management.base import BaseCommand
from django.core.management.base import handle_default_options as original_default_options 

BaseCommand.option_list = BaseCommand.option_list + (make_option('--profile',
                    help='Name of a settings module, e.g. "debug", "syncdb", etc. If this isn\'t provided, "local" profile is assumed.'),)

def handle_default_options(options):
    if options.profile:
        os.environ['DJANGO_SETTINGS_PROFILE'] = options.profile
    original_default_options(options)

django.core.management.base.handle_default_options = handle_default_options
