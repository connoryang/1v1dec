#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\requests\utils.py
import cgi
import codecs
import collections
import io
import os
import re
import socket
import struct
import warnings
from . import __version__
from . import certs
from .compat import parse_http_list as _parse_list_header
from .compat import quote, urlparse, bytes, str, OrderedDict, unquote, is_py2, builtin_str, getproxies, proxy_bypass, urlunparse, basestring
from .cookies import RequestsCookieJar, cookiejar_from_dict
from .structures import CaseInsensitiveDict
from .exceptions import InvalidURL, FileModeWarning
_hush_pyflakes = (RequestsCookieJar,)
NETRC_FILES = ('.netrc', '_netrc')
DEFAULT_CA_BUNDLE_PATH = certs.where()

def dict_to_sequence(d):
    if hasattr(d, 'items'):
        d = d.items()
    return d


def super_len(o):
    total_length = 0
    current_position = 0
    if hasattr(o, '__len__'):
        total_length = len(o)
    elif hasattr(o, 'len'):
        total_length = o.len
    elif hasattr(o, 'getvalue'):
        total_length = len(o.getvalue())
    elif hasattr(o, 'fileno'):
        try:
            fileno = o.fileno()
        except io.UnsupportedOperation:
            pass
        else:
            total_length = os.fstat(fileno).st_size
            if 'b' not in o.mode:
                warnings.warn("Requests has determined the content-length for this request using the binary size of the file: however, the file has been opened in text mode (i.e. without the 'b' flag in the mode). This may lead to an incorrect content-length. In Requests 3.0, support will be removed for files in text mode.", FileModeWarning)
    if hasattr(o, 'tell'):
        try:
            current_position = o.tell()
        except (OSError, IOError):
            current_position = total_length

    return max(0, total_length - current_position)


def get_netrc_auth(url, raise_errors = False):
    try:
        from netrc import netrc, NetrcParseError
        netrc_path = None
        for f in NETRC_FILES:
            try:
                loc = os.path.expanduser('~/{0}'.format(f))
            except KeyError:
                return

            if os.path.exists(loc):
                netrc_path = loc
                break

        if netrc_path is None:
            return
        ri = urlparse(url)
        splitstr = ':'
        if isinstance(url, str):
            splitstr = splitstr.decode('ascii')
        host = ri.netloc.split(splitstr)[0]
        try:
            _netrc = netrc(netrc_path).authenticators(host)
            if _netrc:
                login_i = 0 if _netrc[0] else 1
                return (_netrc[login_i], _netrc[2])
        except (NetrcParseError, IOError):
            if raise_errors:
                raise

    except (ImportError, AttributeError):
        pass


def guess_filename(obj):
    name = getattr(obj, 'name', None)
    if name and isinstance(name, basestring) and name[0] != '<' and name[-1] != '>':
        return os.path.basename(name)


def from_key_val_list(value):
    if value is None:
        return
    if isinstance(value, (str,
     bytes,
     bool,
     int)):
        raise ValueError('cannot encode objects that are not 2-tuples')
    return OrderedDict(value)


def to_key_val_list(value):
    if value is None:
        return
    if isinstance(value, (str,
     bytes,
     bool,
     int)):
        raise ValueError('cannot encode objects that are not 2-tuples')
    if isinstance(value, collections.Mapping):
        value = value.items()
    return list(value)


def parse_list_header(value):
    result = []
    for item in _parse_list_header(value):
        if item[:1] == item[-1:] == '"':
            item = unquote_header_value(item[1:-1])
        result.append(item)

    return result


def parse_dict_header(value):
    result = {}
    for item in _parse_list_header(value):
        if '=' not in item:
            result[item] = None
            continue
        name, value = item.split('=', 1)
        if value[:1] == value[-1:] == '"':
            value = unquote_header_value(value[1:-1])
        result[name] = value

    return result


def unquote_header_value(value, is_filename = False):
    if value and value[0] == value[-1] == '"':
        value = value[1:-1]
        if not is_filename or value[:2] != '\\\\':
            return value.replace('\\\\', '\\').replace('\\"', '"')
    return value


def dict_from_cookiejar(cj):
    cookie_dict = {}
    for cookie in cj:
        cookie_dict[cookie.name] = cookie.value

    return cookie_dict


def add_dict_to_cookiejar(cj, cookie_dict):
    cj2 = cookiejar_from_dict(cookie_dict)
    cj.update(cj2)
    return cj


def get_encodings_from_content(content):
    warnings.warn('In requests 3.0, get_encodings_from_content will be removed. For more information, please see the discussion on issue #2266. (This warning should only appear once.)', DeprecationWarning)
    charset_re = re.compile('<meta.*?charset=["\\\']*(.+?)["\\\'>]', flags=re.I)
    pragma_re = re.compile('<meta.*?content=["\\\']*;?charset=(.+?)["\\\'>]', flags=re.I)
    xml_re = re.compile('^<\\?xml.*?encoding=["\\\']*(.+?)["\\\'>]')
    return charset_re.findall(content) + pragma_re.findall(content) + xml_re.findall(content)


def get_encoding_from_headers(headers):
    content_type = headers.get('content-type')
    if not content_type:
        return None
    content_type, params = cgi.parse_header(content_type)
    if 'charset' in params:
        return params['charset'].strip('\'"')
    if 'text' in content_type:
        return 'ISO-8859-1'


def stream_decode_response_unicode(iterator, r):
    if r.encoding is None:
        for item in iterator:
            yield item

        return
    decoder = codecs.getincrementaldecoder(r.encoding)(errors='replace')
    for chunk in iterator:
        rv = decoder.decode(chunk)
        if rv:
            yield rv

    rv = decoder.decode('', final=True)
    if rv:
        yield rv


def iter_slices(string, slice_length):
    pos = 0
    while pos < len(string):
        yield string[pos:pos + slice_length]
        pos += slice_length


def get_unicode_from_response(r):
    warnings.warn('In requests 3.0, get_unicode_from_response will be removed. For more information, please see the discussion on issue #2266. (This warning should only appear once.)', DeprecationWarning)
    tried_encodings = []
    encoding = get_encoding_from_headers(r.headers)
    if encoding:
        try:
            return str(r.content, encoding)
        except UnicodeError:
            tried_encodings.append(encoding)

    try:
        return str(r.content, encoding, errors='replace')
    except TypeError:
        return r.content


UNRESERVED_SET = frozenset('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz' + '0123456789-._~')

def unquote_unreserved(uri):
    parts = uri.split('%')
    for i in range(1, len(parts)):
        h = parts[i][0:2]
        if len(h) == 2 and h.isalnum():
            try:
                c = chr(int(h, 16))
            except ValueError:
                raise InvalidURL("Invalid percent-escape sequence: '%s'" % h)

            if c in UNRESERVED_SET:
                parts[i] = c + parts[i][2:]
            else:
                parts[i] = '%' + parts[i]
        else:
            parts[i] = '%' + parts[i]

    return ''.join(parts)


def requote_uri(uri):
    safe_with_percent = "!#$%&'()*+,/:;=?@[]~"
    safe_without_percent = "!#$&'()*+,/:;=?@[]~"
    try:
        return quote(unquote_unreserved(uri), safe=safe_with_percent)
    except InvalidURL:
        return quote(uri, safe=safe_without_percent)


def address_in_network(ip, net):
    ipaddr = struct.unpack('=L', socket.inet_aton(ip))[0]
    netaddr, bits = net.split('/')
    netmask = struct.unpack('=L', socket.inet_aton(dotted_netmask(int(bits))))[0]
    network = struct.unpack('=L', socket.inet_aton(netaddr))[0] & netmask
    return ipaddr & netmask == network & netmask


def dotted_netmask(mask):
    bits = 4294967295L ^ (1 << 32 - mask) - 1
    return socket.inet_ntoa(struct.pack('>I', bits))


def is_ipv4_address(string_ip):
    try:
        socket.inet_aton(string_ip)
    except socket.error:
        return False

    return True


def is_valid_cidr(string_network):
    if string_network.count('/') == 1:
        try:
            mask = int(string_network.split('/')[1])
        except ValueError:
            return False

        if mask < 1 or mask > 32:
            return False
        try:
            socket.inet_aton(string_network.split('/')[0])
        except socket.error:
            return False

    else:
        return False
    return True


def should_bypass_proxies(url):
    get_proxy = lambda k: os.environ.get(k) or os.environ.get(k.upper())
    no_proxy = get_proxy('no_proxy')
    netloc = urlparse(url).netloc
    if no_proxy:
        no_proxy = (host for host in no_proxy.replace(' ', '').split(',') if host)
        ip = netloc.split(':')[0]
        if is_ipv4_address(ip):
            for proxy_ip in no_proxy:
                if is_valid_cidr(proxy_ip):
                    if address_in_network(ip, proxy_ip):
                        return True

        else:
            for host in no_proxy:
                if netloc.endswith(host) or netloc.split(':')[0].endswith(host):
                    return True

    try:
        bypass = proxy_bypass(netloc)
    except (TypeError, socket.gaierror):
        bypass = False

    if bypass:
        return True
    return False


def get_environ_proxies(url):
    if should_bypass_proxies(url):
        return {}
    else:
        return getproxies()


def select_proxy(url, proxies):
    proxies = proxies or {}
    urlparts = urlparse(url)
    if urlparts.hostname is None:
        proxy = None
    else:
        proxy = proxies.get(urlparts.scheme + '://' + urlparts.hostname)
    if proxy is None:
        proxy = proxies.get(urlparts.scheme)
    return proxy


def default_user_agent(name = 'python-requests'):
    return '%s/%s' % (name, __version__)


def default_headers():
    return CaseInsensitiveDict({'User-Agent': default_user_agent(),
     'Accept-Encoding': ', '.join(('gzip', 'deflate')),
     'Accept': '*/*',
     'Connection': 'keep-alive'})


def parse_header_links(value):
    links = []
    replace_chars = ' \'"'
    for val in re.split(', *<', value):
        try:
            url, params = val.split(';', 1)
        except ValueError:
            url, params = val, ''

        link = {'url': url.strip('<> \'"')}
        for param in params.split(';'):
            try:
                key, value = param.split('=')
            except ValueError:
                break

            link[key.strip(replace_chars)] = value.strip(replace_chars)

        links.append(link)

    return links


_null = '\x00'.encode('ascii')
_null2 = _null * 2
_null3 = _null * 3

def guess_json_utf(data):
    sample = data[:4]
    if sample in (codecs.BOM_UTF32_LE, codecs.BOM32_BE):
        return 'utf-32'
    if sample[:3] == codecs.BOM_UTF8:
        return 'utf-8-sig'
    if sample[:2] in (codecs.BOM_UTF16_LE, codecs.BOM_UTF16_BE):
        return 'utf-16'
    nullcount = sample.count(_null)
    if nullcount == 0:
        return 'utf-8'
    if nullcount == 2:
        if sample[::2] == _null2:
            return 'utf-16-be'
        if sample[1::2] == _null2:
            return 'utf-16-le'
    if nullcount == 3:
        if sample[:3] == _null3:
            return 'utf-32-be'
        if sample[1:] == _null3:
            return 'utf-32-le'


def prepend_scheme_if_needed(url, new_scheme):
    scheme, netloc, path, params, query, fragment = urlparse(url, new_scheme)
    if not netloc:
        netloc, path = path, netloc
    return urlunparse((scheme,
     netloc,
     path,
     params,
     query,
     fragment))


def get_auth_from_url(url):
    parsed = urlparse(url)
    try:
        auth = (unquote(parsed.username), unquote(parsed.password))
    except (AttributeError, TypeError):
        auth = ('', '')

    return auth


def to_native_string(string, encoding = 'ascii'):
    if isinstance(string, builtin_str):
        out = string
    elif is_py2:
        out = string.encode(encoding)
    else:
        out = string.decode(encoding)
    return out


def urldefragauth(url):
    scheme, netloc, path, params, query, fragment = urlparse(url)
    if not netloc:
        netloc, path = path, netloc
    netloc = netloc.rsplit('@', 1)[-1]
    return urlunparse((scheme,
     netloc,
     path,
     params,
     query,
     ''))
