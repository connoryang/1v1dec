#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\raven\transport\registry.py
from __future__ import absolute_import
from raven.transport.eventlet import EventletHTTPTransport
from raven.transport.exceptions import DuplicateScheme
from raven.transport.http import HTTPTransport
from raven.transport.gevent import GeventedHTTPTransport
from raven.transport.requests import RequestsHTTPTransport
from raven.transport.threaded import ThreadedHTTPTransport
from raven.transport.threaded_requests import ThreadedRequestsHTTPTransport
from raven.transport.twisted import TwistedHTTPTransport
from raven.transport.tornado import TornadoHTTPTransport
from raven.utils import urlparse

class TransportRegistry(object):

    def __init__(self, transports = None):
        self._schemes = {}
        self._transports = {}
        if transports:
            for transport in transports:
                self.register_transport(transport)

    def register_transport(self, transport):
        if not hasattr(transport, 'scheme') or not hasattr(transport.scheme, '__iter__'):
            raise AttributeError('Transport %s must have a scheme list', transport.__class__.__name__)
        for scheme in transport.scheme:
            self.register_scheme(scheme, transport)

    def register_scheme(self, scheme, cls):
        if scheme in self._schemes:
            raise DuplicateScheme()
        urlparse.register_scheme(scheme)
        self._schemes[scheme] = cls

    def supported_scheme(self, scheme):
        return scheme in self._schemes

    def get_transport(self, parsed_url, **options):
        full_url = parsed_url.geturl()
        if full_url not in self._transports:
            parsed_url = urlparse.urlparse(full_url.split('?')[0])
            self._transports[full_url] = self._schemes[parsed_url.scheme](parsed_url, **options)
        return self._transports[full_url]

    def get_transport_cls(self, scheme):
        return self._schemes[scheme]

    def compute_scope(self, url, scope):
        transport = self._schemes[url.scheme](url)
        return transport.compute_scope(url, scope)


default_transports = [HTTPTransport,
 ThreadedHTTPTransport,
 GeventedHTTPTransport,
 TwistedHTTPTransport,
 RequestsHTTPTransport,
 ThreadedRequestsHTTPTransport,
 TornadoHTTPTransport,
 EventletHTTPTransport]
