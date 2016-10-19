#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\requests\adapters.py
import os.path
import socket
from .models import Response
from .packages.urllib3.poolmanager import PoolManager, proxy_from_url
from .packages.urllib3.response import HTTPResponse
from .packages.urllib3.util import Timeout as TimeoutSauce
from .packages.urllib3.util.retry import Retry
from .compat import urlparse, basestring
from .utils import DEFAULT_CA_BUNDLE_PATH, get_encoding_from_headers, prepend_scheme_if_needed, get_auth_from_url, urldefragauth, select_proxy, to_native_string
from .structures import CaseInsensitiveDict
from .packages.urllib3.exceptions import ClosedPoolError
from .packages.urllib3.exceptions import ConnectTimeoutError
from .packages.urllib3.exceptions import HTTPError as _HTTPError
from .packages.urllib3.exceptions import MaxRetryError
from .packages.urllib3.exceptions import NewConnectionError
from .packages.urllib3.exceptions import ProxyError as _ProxyError
from .packages.urllib3.exceptions import ProtocolError
from .packages.urllib3.exceptions import ReadTimeoutError
from .packages.urllib3.exceptions import SSLError as _SSLError
from .packages.urllib3.exceptions import ResponseError
from .cookies import extract_cookies_to_jar
from .exceptions import ConnectionError, ConnectTimeout, ReadTimeout, SSLError, ProxyError, RetryError, InvalidSchema
from .auth import _basic_auth_str
try:
    from .packages.urllib3.contrib.socks import SOCKSProxyManager
except ImportError:

    def SOCKSProxyManager(*args, **kwargs):
        raise InvalidSchema('Missing dependencies for SOCKS support.')


DEFAULT_POOLBLOCK = False
DEFAULT_POOLSIZE = 10
DEFAULT_RETRIES = 0
DEFAULT_POOL_TIMEOUT = None

class BaseAdapter(object):

    def __init__(self):
        super(BaseAdapter, self).__init__()

    def send(self):
        raise NotImplementedError

    def close(self):
        raise NotImplementedError


class HTTPAdapter(BaseAdapter):
    __attrs__ = ['max_retries',
     'config',
     '_pool_connections',
     '_pool_maxsize',
     '_pool_block']

    def __init__(self, pool_connections = DEFAULT_POOLSIZE, pool_maxsize = DEFAULT_POOLSIZE, max_retries = DEFAULT_RETRIES, pool_block = DEFAULT_POOLBLOCK):
        if max_retries == DEFAULT_RETRIES:
            self.max_retries = Retry(0, read=False)
        else:
            self.max_retries = Retry.from_int(max_retries)
        self.config = {}
        self.proxy_manager = {}
        super(HTTPAdapter, self).__init__()
        self._pool_connections = pool_connections
        self._pool_maxsize = pool_maxsize
        self._pool_block = pool_block
        self.init_poolmanager(pool_connections, pool_maxsize, block=pool_block)

    def __getstate__(self):
        return dict(((attr, getattr(self, attr, None)) for attr in self.__attrs__))

    def __setstate__(self, state):
        self.proxy_manager = {}
        self.config = {}
        for attr, value in state.items():
            setattr(self, attr, value)

        self.init_poolmanager(self._pool_connections, self._pool_maxsize, block=self._pool_block)

    def init_poolmanager(self, connections, maxsize, block = DEFAULT_POOLBLOCK, **pool_kwargs):
        self._pool_connections = connections
        self._pool_maxsize = maxsize
        self._pool_block = block
        self.poolmanager = PoolManager(num_pools=connections, maxsize=maxsize, block=block, strict=True, **pool_kwargs)

    def proxy_manager_for(self, proxy, **proxy_kwargs):
        if proxy in self.proxy_manager:
            manager = self.proxy_manager[proxy]
        elif proxy.lower().startswith('socks'):
            username, password = get_auth_from_url(proxy)
            manager = self.proxy_manager[proxy] = SOCKSProxyManager(proxy, username=username, password=password, num_pools=self._pool_connections, maxsize=self._pool_maxsize, block=self._pool_block, **proxy_kwargs)
        else:
            proxy_headers = self.proxy_headers(proxy)
            manager = self.proxy_manager[proxy] = proxy_from_url(proxy, proxy_headers=proxy_headers, num_pools=self._pool_connections, maxsize=self._pool_maxsize, block=self._pool_block, **proxy_kwargs)
        return manager

    def cert_verify(self, conn, url, verify, cert):
        if url.lower().startswith('https') and verify:
            cert_loc = None
            if verify is not True:
                cert_loc = verify
            if not cert_loc:
                cert_loc = DEFAULT_CA_BUNDLE_PATH
            if not cert_loc:
                raise Exception('Could not find a suitable SSL CA certificate bundle.')
            conn.cert_reqs = 'CERT_REQUIRED'
            if not os.path.isdir(cert_loc):
                conn.ca_certs = cert_loc
            else:
                conn.ca_cert_dir = cert_loc
        else:
            conn.cert_reqs = 'CERT_NONE'
            conn.ca_certs = None
            conn.ca_cert_dir = None
        if cert:
            if not isinstance(cert, basestring):
                conn.cert_file = cert[0]
                conn.key_file = cert[1]
            else:
                conn.cert_file = cert

    def build_response(self, req, resp):
        response = Response()
        response.status_code = getattr(resp, 'status', None)
        response.headers = CaseInsensitiveDict(getattr(resp, 'headers', {}))
        response.encoding = get_encoding_from_headers(response.headers)
        response.raw = resp
        response.reason = response.raw.reason
        if isinstance(req.url, bytes):
            response.url = req.url.decode('utf-8')
        else:
            response.url = req.url
        extract_cookies_to_jar(response.cookies, req, resp)
        response.request = req
        response.connection = self
        return response

    def get_connection(self, url, proxies = None):
        proxy = select_proxy(url, proxies)
        if proxy:
            proxy = prepend_scheme_if_needed(proxy, 'http')
            proxy_manager = self.proxy_manager_for(proxy)
            conn = proxy_manager.connection_from_url(url)
        else:
            parsed = urlparse(url)
            url = parsed.geturl()
            conn = self.poolmanager.connection_from_url(url)
        return conn

    def close(self):
        self.poolmanager.clear()
        for proxy in self.proxy_manager.values():
            proxy.clear()

    def request_url(self, request, proxies):
        proxy = select_proxy(request.url, proxies)
        scheme = urlparse(request.url).scheme
        is_proxied_http_request = proxy and scheme != 'https'
        using_socks_proxy = False
        if proxy:
            proxy_scheme = urlparse(proxy).scheme.lower()
            using_socks_proxy = proxy_scheme.startswith('socks')
        url = request.path_url
        if is_proxied_http_request and not using_socks_proxy:
            url = urldefragauth(request.url)
        return url

    def add_headers(self, request, **kwargs):
        pass

    def proxy_headers(self, proxy):
        headers = {}
        username, password = get_auth_from_url(proxy)
        if username and password:
            headers['Proxy-Authorization'] = _basic_auth_str(username, password)
        return headers

    def send(self, request, stream = False, timeout = None, verify = True, cert = None, proxies = None):
        conn = self.get_connection(request.url, proxies)
        self.cert_verify(conn, request.url, verify, cert)
        url = self.request_url(request, proxies)
        self.add_headers(request)
        chunked = not (request.body is None or 'Content-Length' in request.headers)
        if isinstance(timeout, tuple):
            try:
                connect, read = timeout
                timeout = TimeoutSauce(connect=connect, read=read)
            except ValueError as e:
                err = 'Invalid timeout {0}. Pass a (connect, read) timeout tuple, or a single float to set both timeouts to the same value'.format(timeout)
                raise ValueError(err)

        else:
            timeout = TimeoutSauce(connect=timeout, read=timeout)
        try:
            if not chunked:
                resp = conn.urlopen(method=request.method, url=url, body=request.body, headers=request.headers, redirect=False, assert_same_host=False, preload_content=False, decode_content=False, retries=self.max_retries, timeout=timeout)
            else:
                if hasattr(conn, 'proxy_pool'):
                    conn = conn.proxy_pool
                low_conn = conn._get_conn(timeout=DEFAULT_POOL_TIMEOUT)
                try:
                    low_conn.putrequest(request.method, url, skip_accept_encoding=True)
                    for header, value in request.headers.items():
                        low_conn.putheader(header, value)

                    low_conn.endheaders()
                    for i in request.body:
                        low_conn.send(hex(len(i))[2:].encode('utf-8'))
                        low_conn.send('\r\n')
                        low_conn.send(i)
                        low_conn.send('\r\n')

                    low_conn.send('0\r\n\r\n')
                    try:
                        r = low_conn.getresponse(buffering=True)
                    except TypeError:
                        r = low_conn.getresponse()

                    resp = HTTPResponse.from_httplib(r, pool=conn, connection=low_conn, preload_content=False, decode_content=False)
                except:
                    low_conn.close()
                    raise

        except (ProtocolError, socket.error) as err:
            raise ConnectionError(err, request=request)
        except MaxRetryError as e:
            if isinstance(e.reason, ConnectTimeoutError):
                if not isinstance(e.reason, NewConnectionError):
                    raise ConnectTimeout(e, request=request)
            if isinstance(e.reason, ResponseError):
                raise RetryError(e, request=request)
            if isinstance(e.reason, _ProxyError):
                raise ProxyError(e, request=request)
            raise ConnectionError(e, request=request)
        except ClosedPoolError as e:
            raise ConnectionError(e, request=request)
        except _ProxyError as e:
            raise ProxyError(e)
        except (_SSLError, _HTTPError) as e:
            if isinstance(e, _SSLError):
                raise SSLError(e, request=request)
            elif isinstance(e, ReadTimeoutError):
                raise ReadTimeout(e, request=request)
            else:
                raise

        return self.build_response(request, resp)
