#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\requests\models.py
import collections
import datetime
from io import BytesIO, UnsupportedOperation
from .hooks import default_hooks
from .structures import CaseInsensitiveDict
from .auth import HTTPBasicAuth
from .cookies import cookiejar_from_dict, get_cookie_header, _copy_cookie_jar
from .packages.urllib3.fields import RequestField
from .packages.urllib3.filepost import encode_multipart_formdata
from .packages.urllib3.util import parse_url
from .packages.urllib3.exceptions import DecodeError, ReadTimeoutError, ProtocolError, LocationParseError
from .exceptions import HTTPError, MissingSchema, InvalidURL, ChunkedEncodingError, ContentDecodingError, ConnectionError, StreamConsumedError
from .utils import guess_filename, get_auth_from_url, requote_uri, stream_decode_response_unicode, to_key_val_list, parse_header_links, iter_slices, guess_json_utf, super_len, to_native_string
from .compat import cookielib, urlunparse, urlsplit, urlencode, str, bytes, StringIO, is_py2, chardet, builtin_str, basestring
from .compat import json as complexjson
from .status_codes import codes
REDIRECT_STATI = (codes.moved,
 codes.found,
 codes.other,
 codes.temporary_redirect,
 codes.permanent_redirect)
DEFAULT_REDIRECT_LIMIT = 30
CONTENT_CHUNK_SIZE = 10 * 1024
ITER_CHUNK_SIZE = 512

class RequestEncodingMixin(object):

    @property
    def path_url(self):
        url = []
        p = urlsplit(self.url)
        path = p.path
        if not path:
            path = '/'
        url.append(path)
        query = p.query
        if query:
            url.append('?')
            url.append(query)
        return ''.join(url)

    @staticmethod
    def _encode_params(data):
        if isinstance(data, (str, bytes)):
            return data
        elif hasattr(data, 'read'):
            return data
        elif hasattr(data, '__iter__'):
            result = []
            for k, vs in to_key_val_list(data):
                if isinstance(vs, basestring) or not hasattr(vs, '__iter__'):
                    vs = [vs]
                for v in vs:
                    if v is not None:
                        result.append((k.encode('utf-8') if isinstance(k, str) else k, v.encode('utf-8') if isinstance(v, str) else v))

            return urlencode(result, doseq=True)
        else:
            return data

    @staticmethod
    def _encode_files(files, data):
        if not files:
            raise ValueError('Files must be provided.')
        elif isinstance(data, basestring):
            raise ValueError('Data must not be a string.')
        new_fields = []
        fields = to_key_val_list(data or {})
        files = to_key_val_list(files or {})
        for field, val in fields:
            if isinstance(val, basestring) or not hasattr(val, '__iter__'):
                val = [val]
            for v in val:
                if v is not None:
                    if not isinstance(v, bytes):
                        v = str(v)
                    new_fields.append((field.decode('utf-8') if isinstance(field, bytes) else field, v.encode('utf-8') if isinstance(v, str) else v))

        for k, v in files:
            ft = None
            fh = None
            if isinstance(v, (tuple, list)):
                if len(v) == 2:
                    fn, fp = v
                elif len(v) == 3:
                    fn, fp, ft = v
                else:
                    fn, fp, ft, fh = v
            else:
                fn = guess_filename(v) or k
                fp = v
            if isinstance(fp, (str, bytes, bytearray)):
                fdata = fp
            else:
                fdata = fp.read()
            rf = RequestField(name=k, data=fdata, filename=fn, headers=fh)
            rf.make_multipart(content_type=ft)
            new_fields.append(rf)

        body, content_type = encode_multipart_formdata(new_fields)
        return (body, content_type)


class RequestHooksMixin(object):

    def register_hook(self, event, hook):
        if event not in self.hooks:
            raise ValueError('Unsupported event specified, with event name "%s"' % event)
        if isinstance(hook, collections.Callable):
            self.hooks[event].append(hook)
        elif hasattr(hook, '__iter__'):
            self.hooks[event].extend((h for h in hook if isinstance(h, collections.Callable)))

    def deregister_hook(self, event, hook):
        try:
            self.hooks[event].remove(hook)
            return True
        except ValueError:
            return False


class Request(RequestHooksMixin):

    def __init__(self, method = None, url = None, headers = None, files = None, data = None, params = None, auth = None, cookies = None, hooks = None, json = None):
        data = [] if data is None else data
        files = [] if files is None else files
        headers = {} if headers is None else headers
        params = {} if params is None else params
        hooks = {} if hooks is None else hooks
        self.hooks = default_hooks()
        for k, v in list(hooks.items()):
            self.register_hook(event=k, hook=v)

        self.method = method
        self.url = url
        self.headers = headers
        self.files = files
        self.data = data
        self.json = json
        self.params = params
        self.auth = auth
        self.cookies = cookies

    def __repr__(self):
        return '<Request [%s]>' % self.method

    def prepare(self):
        p = PreparedRequest()
        p.prepare(method=self.method, url=self.url, headers=self.headers, files=self.files, data=self.data, json=self.json, params=self.params, auth=self.auth, cookies=self.cookies, hooks=self.hooks)
        return p


class PreparedRequest(RequestEncodingMixin, RequestHooksMixin):

    def __init__(self):
        self.method = None
        self.url = None
        self.headers = None
        self._cookies = None
        self.body = None
        self.hooks = default_hooks()

    def prepare(self, method = None, url = None, headers = None, files = None, data = None, params = None, auth = None, cookies = None, hooks = None, json = None):
        self.prepare_method(method)
        self.prepare_url(url, params)
        self.prepare_headers(headers)
        self.prepare_cookies(cookies)
        self.prepare_body(data, files, json)
        self.prepare_auth(auth, url)
        self.prepare_hooks(hooks)

    def __repr__(self):
        return '<PreparedRequest [%s]>' % self.method

    def copy(self):
        p = PreparedRequest()
        p.method = self.method
        p.url = self.url
        p.headers = self.headers.copy() if self.headers is not None else None
        p._cookies = _copy_cookie_jar(self._cookies)
        p.body = self.body
        p.hooks = self.hooks
        return p

    def prepare_method(self, method):
        self.method = method
        if self.method is not None:
            self.method = to_native_string(self.method.upper())

    def prepare_url(self, url, params):
        if isinstance(url, bytes):
            url = url.decode('utf8')
        else:
            url = unicode(url) if is_py2 else str(url)
        if ':' in url and not url.lower().startswith('http'):
            self.url = url
            return
        try:
            scheme, auth, host, port, path, query, fragment = parse_url(url)
        except LocationParseError as e:
            raise InvalidURL(*e.args)

        if not scheme:
            error = 'Invalid URL {0!r}: No schema supplied. Perhaps you meant http://{0}?'
            error = error.format(to_native_string(url, 'utf8'))
            raise MissingSchema(error)
        if not host:
            raise InvalidURL('Invalid URL %r: No host supplied' % url)
        try:
            host = host.encode('idna').decode('utf-8')
        except UnicodeError:
            raise InvalidURL('URL has an invalid label.')

        netloc = auth or ''
        if netloc:
            netloc += '@'
        netloc += host
        if port:
            netloc += ':' + str(port)
        if not path:
            path = '/'
        if is_py2:
            if isinstance(scheme, str):
                scheme = scheme.encode('utf-8')
            if isinstance(netloc, str):
                netloc = netloc.encode('utf-8')
            if isinstance(path, str):
                path = path.encode('utf-8')
            if isinstance(query, str):
                query = query.encode('utf-8')
            if isinstance(fragment, str):
                fragment = fragment.encode('utf-8')
        if isinstance(params, (str, bytes)):
            params = to_native_string(params)
        enc_params = self._encode_params(params)
        if enc_params:
            if query:
                query = '%s&%s' % (query, enc_params)
            else:
                query = enc_params
        url = requote_uri(urlunparse([scheme,
         netloc,
         path,
         None,
         query,
         fragment]))
        self.url = url

    def prepare_headers(self, headers):
        if headers:
            self.headers = CaseInsensitiveDict(((to_native_string(name), value) for name, value in headers.items()))
        else:
            self.headers = CaseInsensitiveDict()

    def prepare_body(self, data, files, json = None):
        body = None
        content_type = None
        length = None
        if not data and json is not None:
            content_type = 'application/json'
            body = complexjson.dumps(json)
        is_stream = all([hasattr(data, '__iter__'), not isinstance(data, (basestring,
          list,
          tuple,
          dict))])
        try:
            length = super_len(data)
        except (TypeError, AttributeError, UnsupportedOperation):
            length = None

        if is_stream:
            body = data
            if files:
                raise NotImplementedError('Streamed bodies and files are mutually exclusive.')
            if length:
                self.headers['Content-Length'] = builtin_str(length)
            else:
                self.headers['Transfer-Encoding'] = 'chunked'
        else:
            if files:
                body, content_type = self._encode_files(files, data)
            elif data:
                body = self._encode_params(data)
                if isinstance(data, basestring) or hasattr(data, 'read'):
                    content_type = None
                else:
                    content_type = 'application/x-www-form-urlencoded'
            self.prepare_content_length(body)
            if content_type and 'content-type' not in self.headers:
                self.headers['Content-Type'] = content_type
        self.body = body

    def prepare_content_length(self, body):
        if hasattr(body, 'seek') and hasattr(body, 'tell'):
            curr_pos = body.tell()
            body.seek(0, 2)
            end_pos = body.tell()
            self.headers['Content-Length'] = builtin_str(max(0, end_pos - curr_pos))
            body.seek(curr_pos, 0)
        elif body is not None:
            l = super_len(body)
            if l:
                self.headers['Content-Length'] = builtin_str(l)
        elif self.method not in ('GET', 'HEAD') and self.headers.get('Content-Length') is None:
            self.headers['Content-Length'] = '0'

    def prepare_auth(self, auth, url = ''):
        if auth is None:
            url_auth = get_auth_from_url(self.url)
            auth = url_auth if any(url_auth) else None
        if auth:
            if isinstance(auth, tuple) and len(auth) == 2:
                auth = HTTPBasicAuth(*auth)
            r = auth(self)
            self.__dict__.update(r.__dict__)
            self.prepare_content_length(self.body)

    def prepare_cookies(self, cookies):
        if isinstance(cookies, cookielib.CookieJar):
            self._cookies = cookies
        else:
            self._cookies = cookiejar_from_dict(cookies)
        cookie_header = get_cookie_header(self._cookies, self)
        if cookie_header is not None:
            self.headers['Cookie'] = cookie_header

    def prepare_hooks(self, hooks):
        hooks = hooks or []
        for event in hooks:
            self.register_hook(event, hooks[event])


class Response(object):
    __attrs__ = ['_content',
     'status_code',
     'headers',
     'url',
     'history',
     'encoding',
     'reason',
     'cookies',
     'elapsed',
     'request']

    def __init__(self):
        super(Response, self).__init__()
        self._content = False
        self._content_consumed = False
        self.status_code = None
        self.headers = CaseInsensitiveDict()
        self.raw = None
        self.url = None
        self.encoding = None
        self.history = []
        self.reason = None
        self.cookies = cookiejar_from_dict({})
        self.elapsed = datetime.timedelta(0)
        self.request = None

    def __getstate__(self):
        if not self._content_consumed:
            self.content
        return dict(((attr, getattr(self, attr, None)) for attr in self.__attrs__))

    def __setstate__(self, state):
        for name, value in state.items():
            setattr(self, name, value)

        setattr(self, '_content_consumed', True)
        setattr(self, 'raw', None)

    def __repr__(self):
        return '<Response [%s]>' % self.status_code

    def __bool__(self):
        return self.ok

    def __nonzero__(self):
        return self.ok

    def __iter__(self):
        return self.iter_content(128)

    @property
    def ok(self):
        try:
            self.raise_for_status()
        except HTTPError:
            return False

        return True

    @property
    def is_redirect(self):
        return 'location' in self.headers and self.status_code in REDIRECT_STATI

    @property
    def is_permanent_redirect(self):
        return 'location' in self.headers and self.status_code in (codes.moved_permanently, codes.permanent_redirect)

    @property
    def apparent_encoding(self):
        return chardet.detect(self.content)['encoding']

    def iter_content(self, chunk_size = 1, decode_unicode = False):

        def generate():
            if hasattr(self.raw, 'stream'):
                try:
                    for chunk in self.raw.stream(chunk_size, decode_content=True):
                        yield chunk

                except ProtocolError as e:
                    raise ChunkedEncodingError(e)
                except DecodeError as e:
                    raise ContentDecodingError(e)
                except ReadTimeoutError as e:
                    raise ConnectionError(e)

            else:
                while True:
                    chunk = self.raw.read(chunk_size)
                    if not chunk:
                        break
                    yield chunk

            self._content_consumed = True

        if self._content_consumed and isinstance(self._content, bool):
            raise StreamConsumedError()
        reused_chunks = iter_slices(self._content, chunk_size)
        stream_chunks = generate()
        chunks = reused_chunks if self._content_consumed else stream_chunks
        if decode_unicode:
            chunks = stream_decode_response_unicode(chunks, self)
        return chunks

    def iter_lines(self, chunk_size = ITER_CHUNK_SIZE, decode_unicode = None, delimiter = None):
        pending = None
        for chunk in self.iter_content(chunk_size=chunk_size, decode_unicode=decode_unicode):
            if pending is not None:
                chunk = pending + chunk
            if delimiter:
                lines = chunk.split(delimiter)
            else:
                lines = chunk.splitlines()
            if lines and lines[-1] and chunk and lines[-1][-1] == chunk[-1]:
                pending = lines.pop()
            else:
                pending = None
            for line in lines:
                yield line

        if pending is not None:
            yield pending

    @property
    def content(self):
        if self._content is False:
            try:
                if self._content_consumed:
                    raise RuntimeError('The content for this response was already consumed')
                if self.status_code == 0:
                    self._content = None
                else:
                    self._content = bytes().join(self.iter_content(CONTENT_CHUNK_SIZE)) or bytes()
            except AttributeError:
                self._content = None

        self._content_consumed = True
        return self._content

    @property
    def text(self):
        content = None
        encoding = self.encoding
        if not self.content:
            return str('')
        if self.encoding is None:
            encoding = self.apparent_encoding
        try:
            content = str(self.content, encoding, errors='replace')
        except (LookupError, TypeError):
            content = str(self.content, errors='replace')

        return content

    def json(self, **kwargs):
        if not self.encoding and len(self.content) > 3:
            encoding = guess_json_utf(self.content)
            if encoding is not None:
                try:
                    return complexjson.loads(self.content.decode(encoding), **kwargs)
                except UnicodeDecodeError:
                    pass

        return complexjson.loads(self.text, **kwargs)

    @property
    def links(self):
        header = self.headers.get('link')
        l = {}
        if header:
            links = parse_header_links(header)
            for link in links:
                key = link.get('rel') or link.get('url')
                l[key] = link

        return l

    def raise_for_status(self):
        http_error_msg = ''
        if 400 <= self.status_code < 500:
            http_error_msg = '%s Client Error: %s for url: %s' % (self.status_code, self.reason, self.url)
        elif 500 <= self.status_code < 600:
            http_error_msg = '%s Server Error: %s for url: %s' % (self.status_code, self.reason, self.url)
        if http_error_msg:
            raise HTTPError(http_error_msg, response=self)

    def close(self):
        if not self._content_consumed:
            return self.raw.close()
        return self.raw.release_conn()
