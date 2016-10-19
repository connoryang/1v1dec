#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\raven\contrib\django\middleware\wsgi.py
from __future__ import absolute_import
from raven.middleware import Sentry
from raven.utils import memoize

class Sentry(Sentry):

    def __init__(self, application):
        self.application = application

    @memoize
    def client(self):
        from raven.contrib.django.models import client
        return client
