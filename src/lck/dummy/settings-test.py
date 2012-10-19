# Required changes so that ``python manage.py test`` runs without glitches.
#
# You will need to export ``DJANGO_SETTINGS_PROFILE=test`` for this profile to
# be picked up.

LANGUAGE_CODE = 'en-us'
USE_TZ = False

ADMINS = MANAGERS = ()
