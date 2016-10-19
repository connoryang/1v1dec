#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\requests\sessions.py
import os
from collections import Mapping
from datetime import datetime
from .auth import _basic_auth_str
from .compat import cookielib, OrderedDict, urljoin, urlparse
from .cookies import cookiejar_from_dict, extract_cookies_to_jar, RequestsCookieJar, merge_cookies
from .models import Request, PreparedRequest, DEFAULT_REDIRECT_LIMIT
from .hooks import default_hooks, dispatch_hook
from .utils import to_key_val_list, default_headers, to_native_string
from .exceptions import TooManyRedirects, InvalidSchema, ChunkedEncodingError, ContentDecodingError
from .packages.urllib3._collections import RecentlyUsedContainer
from .structures import CaseInsensitiveDict
from .adapters import HTTPAdapter
from .utils import requote_uri, get_environ_proxies, get_netrc_auth, should_bypass_proxies, get_auth_from_url
from .status_codes import codes
from .models import REDIRECT_STATI
REDIRECT_CACHE_SIZE = 1000

def merge_setting(request_setting, session_setting, dict_class = OrderedDict):
    if session_setting is None:
        return request_setting
    if request_setting is None:
        return session_setting
    if not (isinstance(session_setting, Mapping) and isinstance(request_setting, Mapping)):
        return request_setting
    merged_setting = dict_class(to_key_val_list(session_setting))
    merged_setting.update(to_key_val_list(request_setting))
    none_keys = [ k for k, v in merged_setting.items() if v is None ]
    for key in none_keys:
        del merged_setting[key]

    return merged_setting


def merge_hooks(request_hooks, session_hooks, dict_class = OrderedDict):
    if session_hooks is None or session_hooks.get('response') == []:
        return request_hooks
    if request_hooks is None or request_hooks.get('response') == []:
        return session_hooks
    return merge_setting(request_hooks, session_hooks, dict_class)


class SessionRedirectMixin(object):

    def resolve_redirects(self, resp, req, stream = False, timeout = None, verify = True, cert = None, proxies = None, **adapter_kwargs):
        i = 0
        hist = []
        while resp.is_redirect:
            prepared_request = req.copy()
            if i > 0:
                hist.append(resp)
                new_hist = list(hist)
                resp.history = new_hist
            try:
                resp.content
            except (ChunkedEncodingError, ContentDecodingError, RuntimeError):
                resp.raw.read(decode_content=False)

            if i >= self.max_redirects:
                raise TooManyRedirects('Exceeded %s redirects.' % self.max_redirects, response=resp)
            resp.close()
            url = resp.headers['location']
            if url.startswith('//'):
                parsed_rurl = urlparse(resp.url)
                url = '%s:%s' % (parsed_rurl.scheme, url)
            parsed = urlparse(url)
            url = parsed.geturl()
            if not parsed.netloc:
                url = urljoin(resp.url, requote_uri(url))
            else:
                url = requote_uri(url)
            prepared_request.url = to_native_string(url)
            if resp.is_permanent_redirect and req.url != prepared_request.url:
                self.redirect_cache[req.url] = prepared_request.url
            self.rebuild_method(prepared_request, resp)
            if resp.status_code not in (codes.temporary_redirect, codes.permanent_redirect):
                if 'Content-Length' in prepared_request.headers:
                    del prepared_request.headers['Content-Length']
                prepared_request.body = None
            headers = prepared_request.headers
            try:
                del headers['Cookie']
            except KeyError:
                pass

            extract_cookies_to_jar(prepared_request._cookies, req, resp.raw)
            prepared_request._cookies.update(self.cookies)
            prepared_request.prepare_cookies(prepared_request._cookies)
            proxies = self.rebuild_proxies(prepared_request, proxies)
            self.rebuild_auth(prepared_request, resp)
            req = prepared_request
            resp = self.send(req, stream=stream, timeout=timeout, verify=verify, cert=cert, proxies=proxies, allow_redirects=False, **adapter_kwargs)
            extract_cookies_to_jar(self.cookies, prepared_request, resp.raw)
            i += 1
            yield resp

    def rebuild_auth(self, prepared_request, response):
        headers = prepared_request.headers
        url = prepared_request.url
        if 'Authorization' in headers:
            original_parsed = urlparse(response.request.url)
            redirect_parsed = urlparse(url)
            if original_parsed.hostname != redirect_parsed.hostname:
                del headers['Authorization']
        new_auth = get_netrc_auth(url) if self.trust_env else None
        if new_auth is not None:
            prepared_request.prepare_auth(new_auth)

    def rebuild_proxies(self, prepared_request, proxies):
        headers = prepared_request.headers
        url = prepared_request.url
        scheme = urlparse(url).scheme
        new_proxies = proxies.copy() if proxies is not None else {}
        if self.trust_env and not should_bypass_proxies(url):
            environ_proxies = get_environ_proxies(url)
            proxy = environ_proxies.get(scheme)
            if proxy:
                new_proxies.setdefault(scheme, environ_proxies[scheme])
        if 'Proxy-Authorization' in headers:
            del headers['Proxy-Authorization']
        try:
            username, password = get_auth_from_url(new_proxies[scheme])
        except KeyError:
            username, password = (None, None)

        if username and password:
            headers['Proxy-Authorization'] = _basic_auth_str(username, password)
        return new_proxies

    def rebuild_method(self, prepared_request, response):
        method = prepared_request.method
        if response.status_code == codes.see_other and method != 'HEAD':
            method = 'GET'
        if response.status_code == codes.found and method != 'HEAD':
            method = 'GET'
        if response.status_code == codes.moved and method == 'POST':
            method = 'GET'
        prepared_request.method = method


class Session(SessionRedirectMixin):
    __attrs__ = ['headers',
     'cookies',
     'auth',
     'proxies',
     'hooks',
     'params',
     'verify',
     'cert',
     'prefetch',
     'adapters',
     'stream',
     'trust_env',
     'max_redirects']

    def __init__(self):
        self.headers = default_headers()
        self.auth = None
        self.proxies = {}
        self.hooks = default_hooks()
        self.params = {}
        self.stream = False
        self.verify = True
        self.cert = None
        self.max_redirects = DEFAULT_REDIRECT_LIMIT
        self.trust_env = True
        self.cookies = cookiejar_from_dict({})
        self.adapters = OrderedDict()
        self.mount('https://', HTTPAdapter())
        self.mount('http://', HTTPAdapter())
        self.redirect_cache = RecentlyUsedContainer(REDIRECT_CACHE_SIZE)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def prepare_request(self, request):
        cookies = request.cookies or {}
        if not isinstance(cookies, cookielib.CookieJar):
            cookies = cookiejar_from_dict(cookies)
        merged_cookies = merge_cookies(merge_cookies(RequestsCookieJar(), self.cookies), cookies)
        auth = request.auth
        if self.trust_env and not auth and not self.auth:
            auth = get_netrc_auth(request.url)
        p = PreparedRequest()
        p.prepare(method=request.method.upper(), url=request.url, files=request.files, data=request.data, json=request.json, headers=merge_setting(request.headers, self.headers, dict_class=CaseInsensitiveDict), params=merge_setting(request.params, self.params), auth=merge_setting(auth, self.auth), cookies=merged_cookies, hooks=merge_hooks(request.hooks, self.hooks))
        return p

    def request(self, method, url, params = None, data = None, headers = None, cookies = None, files = None, auth = None, timeout = None, allow_redirects = True, proxies = None, hooks = None, stream = None, verify = None, cert = None, json = None):
        req = Request(method=method.upper(), url=url, headers=headers, files=files, data=data or {}, json=json, params=params or {}, auth=auth, cookies=cookies, hooks=hooks)
        prep = self.prepare_request(req)
        proxies = proxies or {}
        settings = self.merge_environment_settings(prep.url, proxies, stream, verify, cert)
        send_kwargs = {'timeout': timeout,
         'allow_redirects': allow_redirects}
        send_kwargs.update(settings)
        resp = self.send(prep, **send_kwargs)
        return resp

    def get(self, url, **kwargs):
        kwargs.setdefault('allow_redirects', True)
        return self.request('GET', url, **kwargs)

    def options(self, url, **kwargs):
        kwargs.setdefault('allow_redirects', True)
        return self.request('OPTIONS', url, **kwargs)

    def head(self, url, **kwargs):
        kwargs.setdefault('allow_redirects', False)
        return self.request('HEAD', url, **kwargs)

    def post(self, url, data = None, json = None, **kwargs):
        return self.request('POST', url, data=data, json=json, **kwargs)

    def put(self, url, data = None, **kwargs):
        return self.request('PUT', url, data=data, **kwargs)

    def patch(self, url, data = None, **kwargs):
        return self.request('PATCH', url, data=data, **kwargs)

    def delete(self, url, **kwargs):
        return self.request('DELETE', url, **kwargs)

    def send(self, request, **kwargs):
        kwargs.setdefault('stream', self.stream)
        kwargs.setdefault('verify', self.verify)
        kwargs.setdefault('cert', self.cert)
        kwargs.setdefault('proxies', self.proxies)
        if isinstance(request, Request):
            raise ValueError('You can only send PreparedRequests.')
        allow_redirects = kwargs.pop('allow_redirects', True)
        stream = kwargs.get('stream')
        hooks = request.hooks
        if allow_redirects:
            checked_urls = set()
            while request.url in self.redirect_cache:
                checked_urls.add(request.url)
                new_url = self.redirect_cache.get(request.url)
                if new_url in checked_urls:
                    break
                request.url = new_url

        adapter = self.get_adapter(url=request.url)
        start = datetime.utcnow()
        r = adapter.send(request, **kwargs)
        r.elapsed = datetime.utcnow() - start
        r = dispatch_hook('response', hooks, r, **kwargs)
        if r.history:
            for resp in r.history:
                extract_cookies_to_jar(self.cookies, resp.request, resp.raw)

        extract_cookies_to_jar(self.cookies, request, r.raw)
        gen = self.resolve_redirects(r, request, **kwargs)
        history = [ resp for resp in gen ] if allow_redirects else []
        if history:
            history.insert(0, r)
            r = history.pop()
            r.history = history
        if not stream:
            r.content
        return r

    def merge_environment_settings(self, url, proxies, stream, verify, cert):
        if self.trust_env:
            env_proxies = get_environ_proxies(url) or {}
            for k, v in env_proxies.items():
                proxies.setdefault(k, v)

            if verify is True or verify is None:
                verify = os.environ.get('REQUESTS_CA_BUNDLE') or os.environ.get('CURL_CA_BUNDLE')
        proxies = merge_setting(proxies, self.proxies)
        stream = merge_setting(stream, self.stream)
        verify = merge_setting(verify, self.verify)
        cert = merge_setting(cert, self.cert)
        return {'verify': verify,
         'proxies': proxies,
         'stream': stream,
         'cert': cert}

    def get_adapter(self, url):
        for prefix, adapter in self.adapters.items():
            if url.lower().startswith(prefix):
                return adapter

        raise InvalidSchema("No connection adapters were found for '%s'" % url)

    def close(self):
        for v in self.adapters.values():
            v.close()

    def mount(self, prefix, adapter):
        self.adapters[prefix] = adapter
        keys_to_move = [ k for k in self.adapters if len(k) < len(prefix) ]
        for key in keys_to_move:
            self.adapters[key] = self.adapters.pop(key)

    def __getstate__(self):
        state = dict(((attr, getattr(self, attr, None)) for attr in self.__attrs__))
        state['redirect_cache'] = dict(self.redirect_cache)
        return state

    def __setstate__(self, state):
        redirect_cache = state.pop('redirect_cache', {})
        for attr, value in state.items():
            setattr(self, attr, value)

        self.redirect_cache = RecentlyUsedContainer(REDIRECT_CACHE_SIZE)
        for redirect, to in redirect_cache.items():
            self.redirect_cache[redirect] = to


def session():
    return Session()
