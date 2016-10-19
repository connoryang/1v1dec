#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\raven\transport\twisted.py
from __future__ import absolute_import
import io
from raven.transport.base import AsyncTransport
from raven.transport.http import HTTPTransport
try:
    from twisted.web.client import Agent, FileBodyProducer, HTTPConnectionPool, ResponseNeverReceived, readBody
    from twisted.web.http_headers import Headers
    has_twisted = True
except:
    has_twisted = False

class TwistedHTTPTransport(AsyncTransport, HTTPTransport):
    scheme = ['twisted+http', 'twisted+https']

    def __init__(self, parsed_url, *args, **kwargs):
        if not has_twisted:
            raise ImportError('TwistedHTTPTransport requires twisted.web.')
        super(TwistedHTTPTransport, self).__init__(parsed_url, *args, **kwargs)
        from twisted.internet import reactor
        self._agent = Agent(reactor, pool=HTTPConnectionPool(reactor))

    def async_send(self, data, headers, success_cb, failure_cb):
        d = self._agent.request('POST', self._url, bodyProducer=FileBodyProducer(io.BytesIO(data)), headers=Headers(dict(((k, [v]) for k, v in headers.items()))))

        def on_failure(failure):
            ex = failure.check(ResponseNeverReceived)
            if ex:
                failure_cb([ f.value for f in failure.value.reasons ])
            else:
                failure_cb(failure.value)

        def on_success(response):
            if response.code == 200:
                success_cb()
            else:

                def on_error_body(body):
                    failure_cb(Exception(response.code, response.phrase, body))

                return readBody(response).addCallback(on_error_body)

        d.addCallback(on_success).addErrback(on_failure)
