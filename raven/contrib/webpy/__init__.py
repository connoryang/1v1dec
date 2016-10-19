#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\raven\contrib\webpy\__init__.py
from __future__ import absolute_import
import sys
import web
from raven.conf import setup_logging
from raven.handlers.logging import SentryHandler
from raven.contrib.webpy.utils import get_data_from_request

class SentryApplication(web.application):

    def __init__(self, client, logging = False, **kwargs):
        self.client = client
        self.logging = logging
        if self.logging:
            setup_logging(SentryHandler(self.client))
        web.application.__init__(self, **kwargs)

    def handle_exception(self, *args, **kwargs):
        self.client.captureException(exc_info=kwargs.get('exc_info'), data=get_data_from_request(), extra={'app': self})

    def handle(self):
        try:
            return web.application.handle(self)
        except:
            self.handle_exception(exc_info=sys.exc_info())
            raise

    def captureException(self, *args, **kwargs):
        data = kwargs.get('data')
        if data is None:
            kwargs['data'] = get_data_from_request()
        return self.client.captureException(*args, **kwargs)

    def captureMessage(self, *args, **kwargs):
        data = kwargs.get('data')
        if data is None:
            kwargs['data'] = get_data_from_request()
        return self.client.captureMessage(*args, **kwargs)
