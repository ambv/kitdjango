# -*- coding: utf-8 -*-

import os, os.path

local_profile = os.environ.get('DJANGO_SETTINGS_PROFILE', 'local')
local_settings = '%s/settings-%s.py' % (os.environ.get('DJANGO_SETTINGS_DIR', '.'), local_profile)

if os.path.exists(local_settings):
    execfile(local_settings)
elif local_profile != 'local':
    raise ValueError, "%s does not exist." % local_settings
    
def nothing(*args, **kwargs): pass
    
import django.core.mail
#django.core.mail.send_mail = nothing
