#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\requests\packages\urllib3\connectionpool.py
from __future__ import absolute_import
import errno
import logging
import sys
import warnings
from socket import error as SocketError, timeout as SocketTimeout
import socket
try:
    from queue import LifoQueue, Empty, Full
except ImportError:
    from Queue import LifoQueue, Empty, Full
    import Queue as _unused_module_Queue

from .exceptions import ClosedPoolError, ProtocolError, EmptyPoolError, HeaderParsingError, HostChangedError, LocationValueError, MaxRetryError, ProxyError, ReadTimeoutError, SSLError, TimeoutError, InsecureRequestWarning, NewConnectionError
from .packages.ssl_match_hostname import CertificateError
from .packages import six
from .connection import port_by_scheme, DummyConnection, HTTPConnection, HTTPSConnection, VerifiedHTTPSConnection, HTTPException, BaseSSLError
from .request import RequestMethods
from .response import HTTPResponse
from .util.connection import is_connection_dropped
from .util.response import assert_header_parsing
from .util.retry import Retry
from .util.timeout import Timeout
from .util.url import get_host, Url
xrange = six.moves.xrange
log = logging.getLogger(__name__)
_Default = object()

class ConnectionPool(object):
    scheme = None
    QueueCls = LifoQueue

    def __init__(self, host, port = None):
        if not host:
            raise LocationValueError('No host specified.')
        self.host = host.strip('[]')
        self.port = port

    def __str__(self):
        return '%s(host=%r, port=%r)' % (type(self).__name__, self.host, self.port)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False

    def close():
        pass


_blocking_errnos = set([errno.EAGAIN, errno.EWOULDBLOCK])

class HTTPConnectionPool(ConnectionPool, RequestMethods):
    scheme = 'http'
    ConnectionCls = HTTPConnection

    def __init__(self, host, port = None, strict = False, timeout = Timeout.DEFAULT_TIMEOUT, maxsize = 1, block = False, headers = None, retries = None, _proxy = None, _proxy_headers = None, **conn_kw):
        ConnectionPool.__init__(self, host, port)
        RequestMethods.__init__(self, headers)
        self.strict = strict
        if not isinstance(timeout, Timeout):
            timeout = Timeout.from_float(timeout)
        if retries is None:
            retries = Retry.DEFAULT
        self.timeout = timeout
        self.retries = retries
        self.pool = self.QueueCls(maxsize)
        self.block = block
        self.proxy = _proxy
        self.proxy_headers = _proxy_headers or {}
        for _ in xrange(maxsize):
            self.pool.put(None)

        self.num_connections = 0
        self.num_requests = 0
        self.conn_kw = conn_kw
        if self.proxy:
            self.conn_kw.setdefault('socket_options', [])

    def _new_conn(self):
        self.num_connections += 1
        log.info('Starting new HTTP connection (%d): %s', self.num_connections, self.host)
        conn = self.ConnectionCls(host=self.host, port=self.port, timeout=self.timeout.connect_timeout, strict=self.strict, **self.conn_kw)
        return conn

    def _get_conn(self, timeout = None):
        conn = None
        try:
            conn = self.pool.get(block=self.block, timeout=timeout)
        except AttributeError:
            raise ClosedPoolError(self, 'Pool is closed.')
        except Empty:
            if self.block:
                raise EmptyPoolError(self, 'Pool reached maximum size and no more connections are allowed.')

        if conn and is_connection_dropped(conn):
            log.info('Resetting dropped connection: %s', self.host)
            conn.close()
            if getattr(conn, 'auto_open', 1) == 0:
                conn = None
        return conn or self._new_conn()

    def _put_conn(self, conn):
        try:
            self.pool.put(conn, block=False)
            return
        except AttributeError:
            pass
        except Full:
            log.warning('Connection pool is full, discarding connection: %s', self.host)

        if conn:
            conn.close()

    def _validate_conn(self, conn):
        pass

    def _prepare_proxy(self, conn):
        pass

    def _get_timeout(self, timeout):
        if timeout is _Default:
            return self.timeout.clone()
        elif isinstance(timeout, Timeout):
            return timeout.clone()
        else:
            return Timeout.from_float(timeout)

    def _raise_timeout(self, err, url, timeout_value):
        if isinstance(err, SocketTimeout):
            raise ReadTimeoutError(self, url, 'Read timed out. (read timeout=%s)' % timeout_value)
        if hasattr(err, 'errno') and err.errno in _blocking_errnos:
            raise ReadTimeoutError(self, url, 'Read timed out. (read timeout=%s)' % timeout_value)
        if 'timed out' in str(err) or 'did not complete (read)' in str(err):
            raise ReadTimeoutError(self, url, 'Read timed out. (read timeout=%s)' % timeout_value)

    def _make_request(self, conn, method, url, timeout = _Default, chunked = False, **httplib_request_kw):
        self.num_requests += 1
        timeout_obj = self._get_timeout(timeout)
        timeout_obj.start_connect()
        conn.timeout = timeout_obj.connect_timeout
        try:
            self._validate_conn(conn)
        except (SocketTimeout, BaseSSLError) as e:
            self._raise_timeout(err=e, url=url, timeout_value=conn.timeout)
            raise

        if chunked:
            conn.request_chunked(method, url, **httplib_request_kw)
        else:
            conn.request(method, url, **httplib_request_kw)
        read_timeout = timeout_obj.read_timeout
        if getattr(conn, 'sock', None):
            if read_timeout == 0:
                raise ReadTimeoutError(self, url, 'Read timed out. (read timeout=%s)' % read_timeout)
            if read_timeout is Timeout.DEFAULT_TIMEOUT:
                conn.sock.settimeout(socket.getdefaulttimeout())
            else:
                conn.sock.settimeout(read_timeout)
        try:
            try:
                httplib_response = conn.getresponse(buffering=True)
            except TypeError:
                httplib_response = conn.getresponse()

        except (SocketTimeout, BaseSSLError, SocketError) as e:
            self._raise_timeout(err=e, url=url, timeout_value=read_timeout)
            raise

        http_version = getattr(conn, '_http_vsn_str', 'HTTP/?')
        log.debug('"%s %s %s" %s %s', method, url, http_version, httplib_response.status, httplib_response.length)
        try:
            assert_header_parsing(httplib_response.msg)
        except HeaderParsingError as hpe:
            log.warning('Failed to parse headers (url=%s): %s', self._absolute_url(url), hpe, exc_info=True)

        return httplib_response

    def _absolute_url(self, path):
        return Url(scheme=self.scheme, host=self.host, port=self.port, path=path).url

    def close(self):
        old_pool, self.pool = self.pool, None
        try:
            while True:
                conn = old_pool.get(block=False)
                if conn:
                    conn.close()

        except Empty:
            pass

    def is_same_host(self, url):
        if url.startswith('/'):
            return True
        scheme, host, port = get_host(url)
        if self.port and not port:
            port = port_by_scheme.get(scheme)
        elif not self.port and port == port_by_scheme.get(scheme):
            port = None
        return (scheme, host, port) == (self.scheme, self.host, self.port)

    def urlopen(self, method, url, body = None, headers = None, retries = None, redirect = True, assert_same_host = True, timeout = _Default, pool_timeout = None, release_conn = None, chunked = False, **response_kw):
        if headers is None:
            headers = self.headers
        if not isinstance(retries, Retry):
            retries = Retry.from_int(retries, redirect=redirect, default=self.retries)
        if release_conn is None:
            release_conn = response_kw.get('preload_content', True)
        if assert_same_host and not self.is_same_host(url):
            raise HostChangedError(self, url, retries)
        conn = None
        if self.scheme == 'http':
            headers = headers.copy()
            headers.update(self.proxy_headers)
        err = None
        clean_exit = False
        try:
            timeout_obj = self._get_timeout(timeout)
            conn = self._get_conn(timeout=pool_timeout)
            conn.timeout = timeout_obj.connect_timeout
            is_new_proxy_conn = self.proxy is not None and not getattr(conn, 'sock', None)
            if is_new_proxy_conn:
                self._prepare_proxy(conn)
            httplib_response = self._make_request(conn, method, url, timeout=timeout_obj, body=body, headers=headers, chunked=chunked)
            response_conn = conn if not release_conn else None
            response = HTTPResponse.from_httplib(httplib_response, pool=self, connection=response_conn, **response_kw)
            clean_exit = True
        except Empty:
            raise EmptyPoolError(self, 'No pool connections are available.')
        except (BaseSSLError, CertificateError) as e:
            clean_exit = False
            raise SSLError(e)
        except SSLError:
            clean_exit = False
            raise
        except (TimeoutError,
         HTTPException,
         SocketError,
         ProtocolError) as e:
            clean_exit = False
            if isinstance(e, (SocketError, NewConnectionError)) and self.proxy:
                e = ProxyError('Cannot connect to proxy.', e)
            elif isinstance(e, (SocketError, HTTPException)):
                e = ProtocolError('Connection aborted.', e)
            retries = retries.increment(method, url, error=e, _pool=self, _stacktrace=sys.exc_info()[2])
            retries.sleep()
            err = e
        finally:
            if not clean_exit:
                conn = conn and conn.close()
                release_conn = True
            if release_conn:
                self._put_conn(conn)

        if not conn:
            log.warning("Retrying (%r) after connection broken by '%r': %s", retries, err, url)
            return self.urlopen(method, url, body, headers, retries, redirect, assert_same_host, timeout=timeout, pool_timeout=pool_timeout, release_conn=release_conn, **response_kw)
        redirect_location = redirect and response.get_redirect_location()
        if redirect_location:
            if response.status == 303:
                method = 'GET'
            try:
                retries = retries.increment(method, url, response=response, _pool=self)
            except MaxRetryError:
                if retries.raise_on_redirect:
                    response.release_conn()
                    raise
                return response

            log.info('Redirecting %s -> %s', url, redirect_location)
            return self.urlopen(method, redirect_location, body, headers, retries=retries, redirect=redirect, assert_same_host=assert_same_host, timeout=timeout, pool_timeout=pool_timeout, release_conn=release_conn, **response_kw)
        if retries.is_forced_retry(method, status_code=response.status):
            try:
                retries = retries.increment(method, url, response=response, _pool=self)
            except MaxRetryError:
                if retries.raise_on_status:
                    response.release_conn()
                    raise
                return response

            retries.sleep()
            log.info('Forced retry: %s', url)
            return self.urlopen(method, url, body, headers, retries=retries, redirect=redirect, assert_same_host=assert_same_host, timeout=timeout, pool_timeout=pool_timeout, release_conn=release_conn, **response_kw)
        return response


class HTTPSConnectionPool(HTTPConnectionPool):
    scheme = 'https'
    ConnectionCls = HTTPSConnection

    def __init__(self, host, port = None, strict = False, timeout = Timeout.DEFAULT_TIMEOUT, maxsize = 1, block = False, headers = None, retries = None, _proxy = None, _proxy_headers = None, key_file = None, cert_file = None, cert_reqs = None, ca_certs = None, ssl_version = None, assert_hostname = None, assert_fingerprint = None, ca_cert_dir = None, **conn_kw):
        HTTPConnectionPool.__init__(self, host, port, strict, timeout, maxsize, block, headers, retries, _proxy, _proxy_headers, **conn_kw)
        if ca_certs and cert_reqs is None:
            cert_reqs = 'CERT_REQUIRED'
        self.key_file = key_file
        self.cert_file = cert_file
        self.cert_reqs = cert_reqs
        self.ca_certs = ca_certs
        self.ca_cert_dir = ca_cert_dir
        self.ssl_version = ssl_version
        self.assert_hostname = assert_hostname
        self.assert_fingerprint = assert_fingerprint

    def _prepare_conn(self, conn):
        if isinstance(conn, VerifiedHTTPSConnection):
            conn.set_cert(key_file=self.key_file, cert_file=self.cert_file, cert_reqs=self.cert_reqs, ca_certs=self.ca_certs, ca_cert_dir=self.ca_cert_dir, assert_hostname=self.assert_hostname, assert_fingerprint=self.assert_fingerprint)
            conn.ssl_version = self.ssl_version
        return conn

    def _prepare_proxy(self, conn):
        try:
            set_tunnel = conn.set_tunnel
        except AttributeError:
            set_tunnel = conn._set_tunnel

        if sys.version_info <= (2, 6, 4) and not self.proxy_headers:
            set_tunnel(self.host, self.port)
        else:
            set_tunnel(self.host, self.port, self.proxy_headers)
        conn.connect()

    def _new_conn(self):
        self.num_connections += 1
        log.info('Starting new HTTPS connection (%d): %s', self.num_connections, self.host)
        if not self.ConnectionCls or self.ConnectionCls is DummyConnection:
            raise SSLError("Can't connect to HTTPS URL because the SSL module is not available.")
        actual_host = self.host
        actual_port = self.port
        if self.proxy is not None:
            actual_host = self.proxy.host
            actual_port = self.proxy.port
        conn = self.ConnectionCls(host=actual_host, port=actual_port, timeout=self.timeout.connect_timeout, strict=self.strict, **self.conn_kw)
        return self._prepare_conn(conn)

    def _validate_conn(self, conn):
        super(HTTPSConnectionPool, self)._validate_conn(conn)
        if not getattr(conn, 'sock', None):
            conn.connect()
        if not conn.is_verified:
            warnings.warn('Unverified HTTPS request is being made. Adding certificate verification is strongly advised. See: https://urllib3.readthedocs.org/en/latest/security.html', InsecureRequestWarning)


def connection_from_url(url, **kw):
    scheme, host, port = get_host(url)
    port = port or port_by_scheme.get(scheme, 80)
    if scheme == 'https':
        return HTTPSConnectionPool(host, port=port, **kw)
    else:
        return HTTPConnectionPool(host, port=port, **kw)
