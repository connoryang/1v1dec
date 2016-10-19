#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\requests\packages\urllib3\util\url.py
from __future__ import absolute_import
from collections import namedtuple
from ..exceptions import LocationParseError
url_attrs = ['scheme',
 'auth',
 'host',
 'port',
 'path',
 'query',
 'fragment']

class Url(namedtuple('Url', url_attrs)):
    slots = ()

    def __new__(cls, scheme = None, auth = None, host = None, port = None, path = None, query = None, fragment = None):
        if path and not path.startswith('/'):
            path = '/' + path
        return super(Url, cls).__new__(cls, scheme, auth, host, port, path, query, fragment)

    @property
    def hostname(self):
        return self.host

    @property
    def request_uri(self):
        uri = self.path or '/'
        if self.query is not None:
            uri += '?' + self.query
        return uri

    @property
    def netloc(self):
        if self.port:
            return '%s:%d' % (self.host, self.port)
        return self.host

    @property
    def url(self):
        scheme, auth, host, port, path, query, fragment = self
        url = ''
        if scheme is not None:
            url += scheme + '://'
        if auth is not None:
            url += auth + '@'
        if host is not None:
            url += host
        if port is not None:
            url += ':' + str(port)
        if path is not None:
            url += path
        if query is not None:
            url += '?' + query
        if fragment is not None:
            url += '#' + fragment
        return url

    def __str__(self):
        return self.url


def split_first(s, delims):
    min_idx = None
    min_delim = None
    for d in delims:
        idx = s.find(d)
        if idx < 0:
            continue
        if min_idx is None or idx < min_idx:
            min_idx = idx
            min_delim = d

    if min_idx is None or min_idx < 0:
        return (s, '', None)
    return (s[:min_idx], s[min_idx + 1:], min_delim)


def parse_url(url):
    if not url:
        return Url()
    scheme = None
    auth = None
    host = None
    port = None
    path = None
    fragment = None
    query = None
    if '://' in url:
        scheme, url = url.split('://', 1)
    url, path_, delim = split_first(url, ['/', '?', '#'])
    if delim:
        path = delim + path_
    if '@' in url:
        auth, url = url.rsplit('@', 1)
    if url and url[0] == '[':
        host, url = url.split(']', 1)
        host += ']'
    if ':' in url:
        _host, port = url.split(':', 1)
        if not host:
            host = _host
        if port:
            if not port.isdigit():
                raise LocationParseError(url)
            port = int(port)
        else:
            port = None
    elif not host and url:
        host = url
    if not path:
        return Url(scheme, auth, host, port, path, query, fragment)
    if '#' in path:
        path, fragment = path.split('#', 1)
    if '?' in path:
        path, query = path.split('?', 1)
    return Url(scheme, auth, host, port, path, query, fragment)


def get_host(url):
    p = parse_url(url)
    return (p.scheme or 'http', p.hostname, p.port)
