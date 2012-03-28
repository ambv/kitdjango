from django.conf.urls.defaults import *

urlpatterns = patterns('lck.django.flatpages.views',
    (r'^(?P<url>.*)$', 'flatpage'),
)
