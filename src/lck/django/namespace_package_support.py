# -*- coding: utf-8 -*-
### NOTE:
### This snippet will be executed in the ``settings.py`` context and is not an
### actual Python module that you would import in a traditional sense. When you
### do import its name, you get the path to this file so you can ``execfile()``
### it.

import django.core.management


def django_core_management__find_management_module(app_name):
    """
    Determines the path to the management module for the given app_name,
    without actually importing the application or the management module.

    Raises ImportError if the management module cannot be found for any reason.

    Supports namespace packages.
    """
    import sys
    import os.path

    parts = app_name.split('.')
    parts.append('management')

    management_module = __import__(app_name + '.management', fromlist=parts)
    path = management_module.__file__

    if path.endswith(('__init__.py', '__init__.pyc')):
        path = os.path.split(path)[0]

    return path


# PATCH: a more generic find_management_module that supports namespace
# packages.
# COMPATIBILITY: Django 1.1.0 - 1.3.0
django.core.management.find_management_module = \
    django_core_management__find_management_module
