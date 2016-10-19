#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\raven\utils\wsgi.py
from __future__ import absolute_import
from raven._compat import iteritems
from raven.utils.compat import urllib_quote

def get_headers(environ):
    for key, value in iteritems(environ):
        key = str(key)
        if key.startswith('HTTP_') and key not in ('HTTP_CONTENT_TYPE', 'HTTP_CONTENT_LENGTH'):
            yield (key[5:].replace('_', '-').title(), value)
        elif key in ('CONTENT_TYPE', 'CONTENT_LENGTH'):
            yield (key.replace('_', '-').title(), value)


def get_environ(environ):
    for key in ('REMOTE_ADDR', 'SERVER_NAME', 'SERVER_PORT'):
        if key in environ:
            yield (key, environ[key])


def get_host(environ):
    scheme = environ.get('wsgi.url_scheme')
    if 'HTTP_X_FORWARDED_HOST' in environ:
        result = environ['HTTP_X_FORWARDED_HOST']
    elif 'HTTP_HOST' in environ:
        result = environ['HTTP_HOST']
    else:
        result = environ['SERVER_NAME']
        if (scheme, str(environ['SERVER_PORT'])) not in (('https', '443'), ('http', '80')):
            result += ':' + environ['SERVER_PORT']
    if result.endswith(':80') and scheme == 'http':
        result = result[:-3]
    elif result.endswith(':443') and scheme == 'https':
        result = result[:-4]
    return result


def get_current_url(environ, root_only = False, strip_querystring = False, host_only = False):
    tmp = [environ['wsgi.url_scheme'], '://', get_host(environ)]
    cat = tmp.append
    if host_only:
        return ''.join(tmp) + '/'
    cat(urllib_quote(environ.get('SCRIPT_NAME', '').rstrip('/')))
    if root_only:
        cat('/')
    else:
        cat(urllib_quote('/' + environ.get('PATH_INFO', '').lstrip('/')))
        if not strip_querystring:
            qs = environ.get('QUERY_STRING')
            if qs:
                cat('?' + qs)
    return ''.join(tmp)
