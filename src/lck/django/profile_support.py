# -*- coding: utf-8 -*-
### NOTE:
### This snippet will be executed in the ``settings.py`` context and is not an
### actual Python module that you would import in a traditional sense. When you
### do import its name, you get the path to this file so you can ``execfile()``
### it.

if 'CURRENT_DIR' not in locals():
    raise ValueError, ("lck.django.profile_support requires "
                       "current_dir_support.")

import os, os.path
import sys
from optparse import make_option
import django.core.management.base
from django.core.management.base import BaseCommand
from django.core.management.base import handle_default_options as \
                                        original_default_options

local_profile = os.environ.get('DJANGO_SETTINGS_PROFILE', 'local')

if SETTINGS_PATH_MODE == 'flat':
    local_settings = '%s-%s.py' % (SETTINGS_PATH_PREFIX, local_profile)
elif SETTINGS_PATH_MODE == 'nested':
    local_settings = '%s%s%s.py' % (SETTINGS_PATH_PREFIX, os.sep,
                                    local_profile)
else:
    raise ValueError, ("Unsupported settings path mode '%s'"
                       "" % SETTINGS_PATH_MODE)

if os.path.exists(local_settings):
    execfile(local_settings)
elif local_profile != 'local':
    raise ValueError, "%s does not exist." % local_settings

if not hasattr(BaseCommand, '_lck_patched'):
    BaseCommand.option_list = (BaseCommand.option_list +
        (make_option('--profile', help='Name of a settings module, e.g. '
            '"debug", "syncdb", etc. If this isn\'t provided, "local" profile '
            'is assumed.'),))
    BaseCommand._lck_patched = True

    def handle_default_options(options):
        if options.profile:
            os.environ['DJANGO_SETTINGS_PROFILE'] = options.profile
        original_default_options(options)

    django.core.management.base.handle_default_options = handle_default_options
