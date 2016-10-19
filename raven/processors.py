#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\raven\processors.py
from __future__ import absolute_import
import re
from raven._compat import string_types, text_type
from raven.utils import varmap

class Processor(object):

    def __init__(self, client):
        self.client = client

    def get_data(self, data, **kwargs):
        pass

    def process(self, data, **kwargs):
        resp = self.get_data(data, **kwargs)
        if resp:
            data = resp
        if 'exception' in data:
            if 'values' in data['exception']:
                for value in data['exception'].get('values', []):
                    if 'stacktrace' in value:
                        self.filter_stacktrace(value['stacktrace'])

        if 'request' in data:
            self.filter_http(data['request'])
        if 'extra' in data:
            data['extra'] = self.filter_extra(data['extra'])
        return data

    def filter_stacktrace(self, data):
        pass

    def filter_http(self, data):
        pass

    def filter_extra(self, data):
        return data


class RemovePostDataProcessor(Processor):

    def filter_http(self, data, **kwargs):
        data.pop('data', None)


class RemoveStackLocalsProcessor(Processor):

    def filter_stacktrace(self, data, **kwargs):
        for frame in data.get('frames', []):
            frame.pop('vars', None)


class SanitizePasswordsProcessor(Processor):
    MASK = '********'
    FIELDS = frozenset(['password',
     'secret',
     'passwd',
     'authorization',
     'api_key',
     'apikey',
     'sentry_dsn',
     'access_token'])
    VALUES_RE = re.compile('^(?:\\d[ -]*?){13,16}$')

    def sanitize(self, key, value):
        if value is None:
            return
        if isinstance(value, string_types) and self.VALUES_RE.match(value):
            return self.MASK
        if not key:
            return value
        if isinstance(key, bytes):
            key = key.decode('utf-8', 'replace')
        else:
            key = text_type(key)
        key = key.lower()
        for field in self.FIELDS:
            if field in key:
                return self.MASK

        return value

    def filter_stacktrace(self, data):
        for frame in data.get('frames', []):
            if 'vars' not in frame:
                continue
            frame['vars'] = varmap(self.sanitize, frame['vars'])

    def filter_http(self, data):
        for n in ('data', 'cookies', 'headers', 'env', 'query_string'):
            if n not in data:
                continue
            if isinstance(data[n], string_types) and '=' in data[n]:
                if n == 'cookies':
                    delimiter = ';'
                else:
                    delimiter = '&'
                data[n] = self._sanitize_keyvals(data[n], delimiter)
            else:
                data[n] = varmap(self.sanitize, data[n])
                if n == 'headers' and 'Cookie' in data[n]:
                    data[n]['Cookie'] = self._sanitize_keyvals(data[n]['Cookie'], ';')

    def filter_extra(self, data):
        return varmap(self.sanitize, data)

    def _sanitize_keyvals(self, keyvals, delimiter):
        sanitized_keyvals = []
        for keyval in keyvals.split(delimiter):
            keyval = keyval.split('=')
            if len(keyval) == 2:
                sanitized_keyvals.append((keyval[0], self.sanitize(*keyval)))
            else:
                sanitized_keyvals.append(keyval)

        return delimiter.join(('='.join(keyval) for keyval in sanitized_keyvals))
