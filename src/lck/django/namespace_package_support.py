# -*- coding: utf-8 -*-
### NOTE:
### This snippet will be executed in the ``settings.py`` context and is not an
### actual Python module that you would import in a traditional sense. When you
### do import its name, you get the path to this file so you can ``execfile()``
### it.

import django.core.management
import django.utils.translation
import django.utils.translation.trans_real


def django_core_management__find_management_module(app_name):
    """
    Determines the path to the management module for the given app_name,
    without actually importing the application or the management module.

    Raises ImportError if the management module cannot be found for any reason.

    Supports namespace packages. Based on Django 1.4.2.
    """
    import os.path

    parts = app_name.split('.')
    parts.append('management')
    parts = [str(p) for p in parts]

    management_module = __import__(app_name + '.management', fromlist=parts)
    path = management_module.__file__

    if path.endswith(('__init__.py', '__init__.pyc')):
        path = os.path.split(path)[0]

    return path


class Trans(object):
    """
    The purpose of this class is to store the actual translation function upon
    receiving the first call to that function. After this is done, changes to
    USE_I18N will have no effect to which function is served upon request. If
    your tests rely on changing USE_I18N, you can delete all the functions
    from _trans.__dict__.

    Note that storing the function with setattr will have a noticeable
    performance effect, as access to the function goes the normal path,
    instead of using __getattr__.

    Supports namespace packages. Based on Django 1.4.2.
    """

    def __getattr__(self, real_name):
        from os import path
        import warnings
        from django.conf import settings
        from django.utils.importlib import import_module
        if settings.USE_I18N:
            from django.utils.translation import trans_real as trans
            # Make sure the project's locale dir isn't in LOCALE_PATHS
            if settings.SETTINGS_MODULE is not None:
                parts = settings.SETTINGS_MODULE.split('.')
                for index in xrange(1, len(parts)):
                    project = import_module(".".join(parts[0:index]))
                    if hasattr(project, '__file__'):
                        break
                else:
                    project = import_module("django")
                project_locale_path = path.normpath(
                    path.join(path.dirname(project.__file__), 'locale'))
                normalized_locale_paths = [path.normpath(locale_path)
                    for locale_path in settings.LOCALE_PATHS]
                if (path.isdir(project_locale_path) and
                        not project_locale_path in normalized_locale_paths):
                    warnings.warn("Translations in the project directory "
                                  "aren't supported anymore. Use the "
                                  "LOCALE_PATHS setting instead.",
                                  DeprecationWarning)
        else:
            from django.utils.translation import trans_null as trans
        setattr(self, real_name, getattr(trans, real_name))
        return getattr(trans, real_name)


class Translations(dict):
    """Overrides the default dictionary of translations so that the broken
    built-in implementation of django.utils.translation.trans_real.translation()
    doesn't need to be invoked.

    Supports namespace packages. Based on Django 1.4.2.
    """

    def get(self, language, default=None):
        """django.utils.translation.trans_real.translation() with a few changes."""
        import gettext
        import os.path
        import sys
        from django.utils.importlib import import_module

        t = dict.get(self, language)
        if t:
            return t

        from django.conf import settings

        globalpath = os.path.join(os.path.dirname(sys.modules[settings.__module__].__file__), 'locale')

        if settings.SETTINGS_MODULE is not None:
            parts = settings.SETTINGS_MODULE.split('.')
            for index in xrange(1, len(parts)):
                project = import_module(".".join(parts[0:index]))
                if hasattr(project, '__file__'):
                    break
            else:
                project = import_module("django")
            projectpath = os.path.join(os.path.dirname(project.__file__), 'locale')
        else:
            projectpath = None

        def _fetch(lang, fallback=None):

            global _translations

            res = dict.get(self, lang, None)
            if res is not None:
                return res

            loc = django.utils.translation.trans_real.to_locale(lang)

            def _translation(path):
                try:
                    t = gettext.translation('django', path, [loc], django.utils.translation.trans_real.DjangoTranslation)
                    t.set_language(lang)
                    return t
                except IOError:
                    return None

            res = _translation(globalpath)

            # We want to ensure that, for example,  "en-gb" and "en-us" don't share
            # the same translation object (thus, merging en-us with a local update
            # doesn't affect en-gb), even though they will both use the core "en"
            # translation. So we have to subvert Python's internal gettext caching.
            base_lang = lambda x: x.split('-', 1)[0]
            if base_lang(lang) in [base_lang(trans) for trans in dict.keys(self)]:
                res._info = res._info.copy()
                res._catalog = res._catalog.copy()

            def _merge(path):
                t = _translation(path)
                if t is not None:
                    if res is None:
                        return t
                    else:
                        res.merge(t)
                return res

            for appname in reversed(settings.INSTALLED_APPS):
                app = import_module(appname)
                apppath = os.path.join(os.path.dirname(app.__file__), 'locale')

                if os.path.isdir(apppath):
                    res = _merge(apppath)

            localepaths = [os.path.normpath(path) for path in settings.LOCALE_PATHS]
            if (projectpath and os.path.isdir(projectpath) and
                    os.path.normpath(projectpath) not in localepaths):
                res = _merge(projectpath)

            for localepath in reversed(settings.LOCALE_PATHS):
                if os.path.isdir(localepath):
                    res = _merge(localepath)

            if res is None:
                if fallback is not None:
                    res = fallback
                else:
                    return gettext.NullTranslations()
            self[lang] = res
            return res

        default_translation = _fetch(settings.LANGUAGE_CODE)
        current_translation = _fetch(language, fallback=default_translation)

        return current_translation


# PATCH: a more generic find_management_module that supports namespace
# packages.
# COMPATIBILITY: Django 1.1.0 - 1.4.0
django.core.management.find_management_module = \
    django_core_management__find_management_module

# PATCH: a more generic _trans object that supports namespace
# packages.
# COMPATIBILITY: Django 1.3.0 - 1.4.2
django.utils.translation._trans = Trans()

# PATCH: django.utils.translation.trans_real.translation() uses globals and is
# generally tricky to patch. We patch the data structure used for holding
# translations instead so that the translation() method successfully gets
# an object out it and returns early (before raising an exception due to its
# lack of support for namespace packages).
# COMPATIBILITY: Django 1.3.0 - 1.4.2
django.utils.translation.trans_real._translations = Translations()
