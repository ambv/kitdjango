# -*- coding: utf-8 -*-

import os.path

SETTINGS_PATH_PREFIX = os.sep.join(os.environ.get('DJANGO_SETTINGS_DIR', CURRENT_DIR), 'settings')

if os.path.isdir(SETTINGS_PATH_PREFIX):
    SETTINGS_PATH_MODE = 'nested'
    CURRENT_DIR = os.path.realpath(os.path.dirname(__file__) + os.path.sep + '..') + os.path.sep
elif os.path.exists(SETTINGS_PATH_PREFIX + '.py'):
    SETTINGS_PATH_MODE = 'flat'
    CURRENT_DIR = os.path.realpath(os.path.dirname(__file__)) + os.path.sep
else:
    raise ValueError, "Django settings structure not recognized."
