#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\ccpraven\session_proxy.py
from __future__ import absolute_import
import logging
from raven.transport.base import AsyncTransport
from raven.transport.http import HTTPTransport
from uthread2 import StartTasklet
try:
    import requests
    has_requests = True
except ImportError:
    has_requests = False

class RequestsSessionProxyHTTPTransport(AsyncTransport, HTTPTransport):
    scheme = ['requests+http', 'requests+https']
    session = None

    def __init__(self, *args, **kwargs):
        if not has_requests:
            raise ImportError('RequestsSessionProxyHTTPTransport requires requests.')
        super(RequestsSessionProxyHTTPTransport, self).__init__(*args, **kwargs)
        self.session = requests.Session()
        proxies = None
        try:
            http_proxy = prefs.GetValue('sentry_http_proxy', None)
            https_proxy = prefs.GetValue('sentry_https_proxy', None)
            proxies = {}
            if http_proxy:
                proxies['http'] = http_proxy
            if https_proxy:
                proxies['https'] = https_proxy
            if http_proxy is None and https_proxy is None:
                proxies = None
        except Exception as e:
            pass

        if proxies:
            self.session.proxies.update(proxies)

    def send(self, data, headers):
        if self.verify_ssl:
            self.verify_ssl = self.ca_certs
        try:
            self.session.post(self._url, data=data, headers=headers, verify=self.verify_ssl, timeout=self.timeout)
        except Exception as e:
            logging.warn('Sentry send failed: {0}'.format(e))

    def async_send(self, data, headers, success_cb, failure_cb):
        StartTasklet(self.send, data, headers)
        success_cb()
