#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\raven\transport\gevent.py
from __future__ import absolute_import
from raven.transport.base import AsyncTransport
from raven.transport.http import HTTPTransport
try:
    import gevent
    try:
        from gevent.lock import Semaphore
    except ImportError:
        from gevent.coros import Semaphore

    has_gevent = True
except:
    has_gevent = None

class GeventedHTTPTransport(AsyncTransport, HTTPTransport):
    scheme = ['gevent+http', 'gevent+https']

    def __init__(self, parsed_url, maximum_outstanding_requests = 100, *args, **kwargs):
        if not has_gevent:
            raise ImportError('GeventedHTTPTransport requires gevent.')
        self._lock = Semaphore(maximum_outstanding_requests)
        super(GeventedHTTPTransport, self).__init__(parsed_url, *args, **kwargs)

    def async_send(self, data, headers, success_cb, failure_cb):
        self._lock.acquire()
        return gevent.spawn(super(GeventedHTTPTransport, self).send, data, headers).link(lambda x: self._done(x, success_cb, failure_cb))

    def _done(self, greenlet, success_cb, failure_cb, *args):
        self._lock.release()
        if greenlet.successful():
            success_cb()
        else:
            failure_cb(greenlet.exception)
