#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\raven\contrib\django\handlers.py
from __future__ import absolute_import
import logging
from raven.handlers.logging import SentryHandler as BaseSentryHandler
from raven.utils import memoize

class SentryHandler(BaseSentryHandler):

    def __init__(self, *args, **kwargs):
        self.tags = kwargs.pop('tags', None)
        logging.Handler.__init__(self, level=kwargs.get('level', logging.NOTSET))

    @memoize
    def client(self):
        from raven.contrib.django.models import client
        return client

    def _emit(self, record):
        request = getattr(record, 'request', None)
        return super(SentryHandler, self)._emit(record, request=request)
