#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\requests\packages\urllib3\poolmanager.py
from __future__ import absolute_import
import logging
try:
    from urllib.parse import urljoin
except ImportError:
    from urlparse import urljoin

from ._collections import RecentlyUsedContainer
from .connectionpool import HTTPConnectionPool, HTTPSConnectionPool
from .connectionpool import port_by_scheme
from .exceptions import LocationValueError, MaxRetryError, ProxySchemeUnknown
from .request import RequestMethods
from .util.url import parse_url
from .util.retry import Retry
__all__ = ['PoolManager', 'ProxyManager', 'proxy_from_url']
log = logging.getLogger(__name__)
SSL_KEYWORDS = ('key_file', 'cert_file', 'cert_reqs', 'ca_certs', 'ssl_version', 'ca_cert_dir')
pool_classes_by_scheme = {'http': HTTPConnectionPool,
 'https': HTTPSConnectionPool}

class PoolManager(RequestMethods):
    proxy = None

    def __init__(self, num_pools = 10, headers = None, **connection_pool_kw):
        RequestMethods.__init__(self, headers)
        self.connection_pool_kw = connection_pool_kw
        self.pools = RecentlyUsedContainer(num_pools, dispose_func=lambda p: p.close())
        self.pool_classes_by_scheme = pool_classes_by_scheme

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.clear()
        return False

    def _new_pool(self, scheme, host, port):
        pool_cls = self.pool_classes_by_scheme[scheme]
        kwargs = self.connection_pool_kw
        if scheme == 'http':
            kwargs = self.connection_pool_kw.copy()
            for kw in SSL_KEYWORDS:
                kwargs.pop(kw, None)

        return pool_cls(host, port, **kwargs)

    def clear(self):
        self.pools.clear()

    def connection_from_host(self, host, port = None, scheme = 'http'):
        if not host:
            raise LocationValueError('No host specified.')
        scheme = scheme or 'http'
        port = port or port_by_scheme.get(scheme, 80)
        pool_key = (scheme, host, port)
        with self.pools.lock:
            pool = self.pools.get(pool_key)
            if pool:
                return pool
            pool = self._new_pool(scheme, host, port)
            self.pools[pool_key] = pool
        return pool

    def connection_from_url(self, url):
        u = parse_url(url)
        return self.connection_from_host(u.host, port=u.port, scheme=u.scheme)

    def urlopen(self, method, url, redirect = True, **kw):
        u = parse_url(url)
        conn = self.connection_from_host(u.host, port=u.port, scheme=u.scheme)
        kw['assert_same_host'] = False
        kw['redirect'] = False
        if 'headers' not in kw:
            kw['headers'] = self.headers
        if self.proxy is not None and u.scheme == 'http':
            response = conn.urlopen(method, url, **kw)
        else:
            response = conn.urlopen(method, u.request_uri, **kw)
        redirect_location = redirect and response.get_redirect_location()
        if not redirect_location:
            return response
        redirect_location = urljoin(url, redirect_location)
        if response.status == 303:
            method = 'GET'
        retries = kw.get('retries')
        if not isinstance(retries, Retry):
            retries = Retry.from_int(retries, redirect=redirect)
        try:
            retries = retries.increment(method, url, response=response, _pool=conn)
        except MaxRetryError:
            if retries.raise_on_redirect:
                raise
            return response

        kw['retries'] = retries
        kw['redirect'] = redirect
        log.info('Redirecting %s -> %s', url, redirect_location)
        return self.urlopen(method, redirect_location, **kw)


class ProxyManager(PoolManager):

    def __init__(self, proxy_url, num_pools = 10, headers = None, proxy_headers = None, **connection_pool_kw):
        if isinstance(proxy_url, HTTPConnectionPool):
            proxy_url = '%s://%s:%i' % (proxy_url.scheme, proxy_url.host, proxy_url.port)
        proxy = parse_url(proxy_url)
        if not proxy.port:
            port = port_by_scheme.get(proxy.scheme, 80)
            proxy = proxy._replace(port=port)
        if proxy.scheme not in ('http', 'https'):
            raise ProxySchemeUnknown(proxy.scheme)
        self.proxy = proxy
        self.proxy_headers = proxy_headers or {}
        connection_pool_kw['_proxy'] = self.proxy
        connection_pool_kw['_proxy_headers'] = self.proxy_headers
        super(ProxyManager, self).__init__(num_pools, headers, **connection_pool_kw)

    def connection_from_host(self, host, port = None, scheme = 'http'):
        if scheme == 'https':
            return super(ProxyManager, self).connection_from_host(host, port, scheme)
        return super(ProxyManager, self).connection_from_host(self.proxy.host, self.proxy.port, self.proxy.scheme)

    def _set_proxy_headers(self, url, headers = None):
        headers_ = {'Accept': '*/*'}
        netloc = parse_url(url).netloc
        if netloc:
            headers_['Host'] = netloc
        if headers:
            headers_.update(headers)
        return headers_

    def urlopen(self, method, url, redirect = True, **kw):
        u = parse_url(url)
        if u.scheme == 'http':
            headers = kw.get('headers', self.headers)
            kw['headers'] = self._set_proxy_headers(url, headers)
        return super(ProxyManager, self).urlopen(method, url, redirect=redirect, **kw)


def proxy_from_url(url, **kw):
    return ProxyManager(proxy_url=url, **kw)
