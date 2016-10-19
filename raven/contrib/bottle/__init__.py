#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\raven\contrib\bottle\__init__.py
from __future__ import absolute_import
import sys
from bottle import request
from raven.conf import setup_logging
from raven.contrib.bottle.utils import get_data_from_request
from raven.handlers.logging import SentryHandler

class Sentry(object):

    def __init__(self, app, client, logging = False):
        self.app = app
        self.client = client
        self.logging = logging
        if self.logging:
            setup_logging(SentryHandler(self.client))
        self.app.sentry = self

    def handle_exception(self, *args, **kwargs):
        self.client.captureException(exc_info=kwargs.get('exc_info'), data=get_data_from_request(request), extra={'app': self.app})

    def __call__(self, environ, start_response):

        def session_start_response(status, headers, exc_info = None):
            if exc_info is not None:
                self.handle_exception(exc_info=exc_info)
            return start_response(status, headers, exc_info)

        try:
            return self.app(environ, session_start_response)
        except Exception:
            self.handle_exception(exc_info=sys.exc_info())
            raise

    def captureException(self, *args, **kwargs):
        data = kwargs.get('data')
        if data is None:
            try:
                kwargs['data'] = get_data_from_request(request)
            except RuntimeError:
                pass

        return self.client.captureException(*args, **kwargs)

    def captureMessage(self, *args, **kwargs):
        data = kwargs.get('data')
        if data is None:
            try:
                kwargs['data'] = get_data_from_request(request)
            except RuntimeError:
                pass

        return self.client.captureMessage(*args, **kwargs)
