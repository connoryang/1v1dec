#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\raven\contrib\django\urls.py
from __future__ import absolute_import
try:
    from django.conf.urls import url
except ImportError:
    from django.conf.urls.defaults import url

import raven.contrib.django.views
urlpatterns = (url('^api/(?:(?P<project_id>[\\w_-]+)/)?store/$', raven.contrib.django.views.report, name='raven-report'), url('^report/', raven.contrib.django.views.report))
