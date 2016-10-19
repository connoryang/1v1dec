#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\raven\transport\base.py
from __future__ import absolute_import

class Transport(object):
    async = False
    scheme = []

    def send(self, data, headers):
        raise NotImplementedError


class AsyncTransport(Transport):
    async = True

    def async_send(self, data, headers, success_cb, error_cb):
        raise NotImplementedError
