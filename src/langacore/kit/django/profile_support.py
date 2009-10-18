# -*- coding: utf-8 -*-

if 'CURRENT_DIR' in locals():
    import os, os.path
    import sys
    from optparse import make_option
    import django.core.management.base
    from django.core.management.base import BaseCommand
    from django.core.management.base import handle_default_options as original_default_options 

    local_profile = os.environ.get('DJANGO_SETTINGS_PROFILE', 'local')
    local_settings = '%s/settings-%s.py' % (os.environ.get('DJANGO_SETTINGS_DIR', CURRENT_DIR), local_profile)

    if os.path.exists(local_settings):
        execfile(local_settings)
    elif local_profile != 'local':
        raise ValueError, "%s does not exist." % local_settings

    def nothing(*args, **kwargs): pass
        
    import django.core.mail
    #django.core.mail.send_mail = nothing

    if not hasattr(BaseCommand, '_langacore_patched'):
        BaseCommand.option_list = BaseCommand.option_list + (make_option('--profile',
                            help='Name of a settings module, e.g. "debug", "syncdb", etc. If this isn\'t provided, "local" profile is assumed.'),)
        BaseCommand._langacore_patched = True

        def handle_default_options(options):
            if options.profile:
                os.environ['DJANGO_SETTINGS_PROFILE'] = options.profile
            original_default_options(options)
        
        django.core.management.base.handle_default_options = handle_default_options
else:
    raise ValueError, "langacore.kit.django.profile_support requires current_dir_support."
