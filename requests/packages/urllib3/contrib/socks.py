#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\requests\packages\urllib3\contrib\socks.py
from __future__ import absolute_import
try:
    import socks
except ImportError:
    import warnings
    from ..exceptions import DependencyWarning
    warnings.warn('SOCKS support in urllib3 requires the installation of optional dependencies: specifically, PySocks.  For more information, see https://urllib3.readthedocs.org/en/latest/contrib.html#socks-proxies', DependencyWarning)
    raise

from socket import error as SocketError, timeout as SocketTimeout
from ..connection import HTTPConnection, HTTPSConnection
from ..connectionpool import HTTPConnectionPool, HTTPSConnectionPool
from ..exceptions import ConnectTimeoutError, NewConnectionError
from ..poolmanager import PoolManager
from ..util.url import parse_url
try:
    import ssl
except ImportError:
    ssl = None

class SOCKSConnection(HTTPConnection):

    def __init__(self, *args, **kwargs):
        self._socks_options = kwargs.pop('_socks_options')
        super(SOCKSConnection, self).__init__(*args, **kwargs)

    def _new_conn(self):
        extra_kw = {}
        if self.source_address:
            extra_kw['source_address'] = self.source_address
        if self.socket_options:
            extra_kw['socket_options'] = self.socket_options
        try:
            conn = socks.create_connection((self.host, self.port), proxy_type=self._socks_options['socks_version'], proxy_addr=self._socks_options['proxy_host'], proxy_port=self._socks_options['proxy_port'], proxy_username=self._socks_options['username'], proxy_password=self._socks_options['password'], timeout=self.timeout, **extra_kw)
        except SocketTimeout as e:
            raise ConnectTimeoutError(self, 'Connection to %s timed out. (connect timeout=%s)' % (self.host, self.timeout))
        except socks.ProxyError as e:
            if e.socket_err:
                error = e.socket_err
                if isinstance(error, SocketTimeout):
                    raise ConnectTimeoutError(self, 'Connection to %s timed out. (connect timeout=%s)' % (self.host, self.timeout))
                else:
                    raise NewConnectionError(self, 'Failed to establish a new connection: %s' % error)
            else:
                raise NewConnectionError(self, 'Failed to establish a new connection: %s' % e)
        except SocketError as e:
            raise NewConnectionError(self, 'Failed to establish a new connection: %s' % e)

        return conn


class SOCKSHTTPSConnection(SOCKSConnection, HTTPSConnection):
    pass


class SOCKSHTTPConnectionPool(HTTPConnectionPool):
    ConnectionCls = SOCKSConnection


class SOCKSHTTPSConnectionPool(HTTPSConnectionPool):
    ConnectionCls = SOCKSHTTPSConnection


class SOCKSProxyManager(PoolManager):
    pool_classes_by_scheme = {'http': SOCKSHTTPConnectionPool,
     'https': SOCKSHTTPSConnectionPool}

    def __init__(self, proxy_url, username = None, password = None, num_pools = 10, headers = None, **connection_pool_kw):
        parsed = parse_url(proxy_url)
        if parsed.scheme == 'socks5':
            socks_version = socks.PROXY_TYPE_SOCKS5
        elif parsed.scheme == 'socks4':
            socks_version = socks.PROXY_TYPE_SOCKS4
        else:
            raise ValueError('Unable to determine SOCKS version from %s' % proxy_url)
        self.proxy_url = proxy_url
        socks_options = {'socks_version': socks_version,
         'proxy_host': parsed.host,
         'proxy_port': parsed.port,
         'username': username,
         'password': password}
        connection_pool_kw['_socks_options'] = socks_options
        super(SOCKSProxyManager, self).__init__(num_pools, headers, **connection_pool_kw)
        self.pool_classes_by_scheme = SOCKSProxyManager.pool_classes_by_scheme
