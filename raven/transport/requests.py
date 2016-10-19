#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\raven\transport\requests.py
from __future__ import absolute_import
from raven.transport.http import HTTPTransport
try:
    import requests
    has_requests = True
except ImportError:
    has_requests = False

class RequestsHTTPTransport(HTTPTransport):
    scheme = ['requests+http', 'requests+https']

    def __init__(self, *args, **kwargs):
        if not has_requests:
            raise ImportError('RequestsHTTPTransport requires requests.')
        super(RequestsHTTPTransport, self).__init__(*args, **kwargs)

    def send(self, data, headers):
        if self.verify_ssl:
            self.verify_ssl = self.ca_certs
        requests.post(self._url, data=data, headers=headers, verify=self.verify_ssl, timeout=self.timeout)
