# -*- coding: utf-8 -*-
### NOTE:
### This snippet will be executed in the ``settings.py`` context and is not an
### actual Python module that you would import in a traditional sense. When
### you do import its name, you get the path to this file so you can
### ``execfile()`` it.

import os.path
import tempfile

def _get_settings_path_mode(path):
    if os.path.isdir(path):
        return 'nested'
    elif os.path.exists(path + '.py'):
        return 'flat'
    else:
        return None


TEMP_DIR = tempfile.gettempdir() + os.path.sep
CURRENT_DIR = os.path.realpath(os.path.dirname(__file__)) + os.path.sep
_django_settings_dir = os.environ.get('DJANGO_SETTINGS_DIR', CURRENT_DIR)

SETTINGS_PATH_PREFIX = os.path.join(_django_settings_dir, 'settings')
SETTINGS_PATH_MODE = _get_settings_path_mode(SETTINGS_PATH_PREFIX)

if not SETTINGS_PATH_MODE:
    # no settings dir/settings.py file in DJANGO_SETTINGS_DIR or the current
    # directory let's try the parent:
    CURRENT_DIR = os.path.realpath(os.path.dirname(__file__) + os.path.sep +
        '..') + os.path.sep
    SETTINGS_PATH_PREFIX = os.path.join(_django_settings_dir, '..', 'settings')
    SETTINGS_PATH_MODE = _get_settings_path_mode(SETTINGS_PATH_PREFIX)

if not SETTINGS_PATH_MODE:
    raise ValueError, "Django settings structure not recognized."
