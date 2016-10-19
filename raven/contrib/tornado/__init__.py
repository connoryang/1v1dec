#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\raven\contrib\tornado\__init__.py
from __future__ import absolute_import
from functools import partial
from tornado import ioloop
from tornado.httpclient import AsyncHTTPClient, HTTPError
from tornado.web import HTTPError as WebHTTPError
from raven.base import Client

class AsyncSentryClient(Client):

    def __init__(self, *args, **kwargs):
        self.validate_cert = kwargs.pop('validate_cert', True)
        super(AsyncSentryClient, self).__init__(*args, **kwargs)

    def capture(self, *args, **kwargs):
        if not self.is_enabled():
            return
        data = self.build_msg(*args, **kwargs)
        future = self.send(callback=kwargs.get('callback', None), **data)
        return (data['event_id'], future)

    def send(self, auth_header = None, callback = None, **data):
        message = self.encode(data)
        return self.send_encoded(message, auth_header=auth_header, callback=callback)

    def send_remote(self, url, data, headers = None, callback = None):
        if headers is None:
            headers = {}
        if not self.state.should_try():
            data = self.decode(data)
            self._log_failed_submission(data)
            return
        future = self._send_remote(url=url, data=data, headers=headers, callback=callback)
        ioloop.IOLoop.current().add_future(future, partial(self._handle_result, url, data))
        return future

    def _handle_result(self, url, data, future):
        try:
            future.result()
        except HTTPError as e:
            data = self.decode(data)
            self._failed_send(e, url, data)
        except Exception as e:
            data = self.decode(data)
            self._failed_send(e, url, data)
        else:
            self.state.set_success()

    def _send_remote(self, url, data, headers = None, callback = None):
        if headers is None:
            headers = {}
        return AsyncHTTPClient().fetch(url, callback, method='POST', body=data, headers=headers, validate_cert=self.validate_cert)


class SentryMixin(object):

    def get_sentry_client(self):
        return self.application.sentry_client

    def get_sentry_data_from_request(self):
        return {'request': {'url': self.request.full_url(),
                     'method': self.request.method,
                     'data': self.request.body,
                     'query_string': self.request.query,
                     'cookies': self.request.headers.get('Cookie', None),
                     'headers': dict(self.request.headers)}}

    def get_sentry_user_info(self):
        try:
            user = self.get_current_user()
        except Exception:
            return {}

        return {'user': {'is_authenticated': True if user else False}}

    def get_sentry_extra_info(self):
        return {'extra': {}}

    def get_default_context(self):
        data = {}
        data.update(self.get_sentry_data_from_request())
        data.update(self.get_sentry_user_info())
        data.update(self.get_sentry_extra_info())
        return data

    def _capture(self, call_name, data = None, **kwargs):
        if data is None:
            data = self.get_default_context()
        else:
            default_context = self.get_default_context()
            if isinstance(data, dict):
                default_context.update(data)
            else:
                default_context['extra']['extra_data'] = data
            data = default_context
        client = self.get_sentry_client()
        return getattr(client, call_name)(data=data, **kwargs)

    def captureException(self, exc_info = None, **kwargs):
        return self._capture('captureException', exc_info=exc_info, **kwargs)

    def captureMessage(self, message, **kwargs):
        return self._capture('captureMessage', message=message, **kwargs)

    def log_exception(self, typ, value, tb):
        rv = super(SentryMixin, self).log_exception(typ, value, tb)
        if isinstance(value, WebHTTPError) and (value.status_code < 500 or value.status_code > 599):
            return rv
        self.captureException(exc_info=(typ, value, tb))
        return rv

    def send_error(self, status_code = 500, **kwargs):
        if hasattr(super(SentryMixin, self), 'log_exception'):
            return super(SentryMixin, self).send_error(status_code, **kwargs)
        else:
            rv = super(SentryMixin, self).send_error(status_code, **kwargs)
            if 500 <= status_code <= 599:
                self.captureException(exc_info=kwargs.get('exc_info'))
            return rv
