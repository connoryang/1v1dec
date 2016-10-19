#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\raven\contrib\django\celery\models.py
from __future__ import absolute_import
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
if 'djcelery' not in settings.INSTALLED_APPS:
    raise ImproperlyConfigured("Put 'djcelery' in your INSTALLED_APPS setting in order to use the sentry celery client.")
