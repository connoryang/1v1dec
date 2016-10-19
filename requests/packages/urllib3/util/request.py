#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\requests\packages\urllib3\util\request.py
from __future__ import absolute_import
from base64 import b64encode
from ..packages.six import b
ACCEPT_ENCODING = 'gzip,deflate'

def make_headers(keep_alive = None, accept_encoding = None, user_agent = None, basic_auth = None, proxy_basic_auth = None, disable_cache = None):
    headers = {}
    if accept_encoding:
        if isinstance(accept_encoding, str):
            pass
        elif isinstance(accept_encoding, list):
            accept_encoding = ','.join(accept_encoding)
        else:
            accept_encoding = ACCEPT_ENCODING
        headers['accept-encoding'] = accept_encoding
    if user_agent:
        headers['user-agent'] = user_agent
    if keep_alive:
        headers['connection'] = 'keep-alive'
    if basic_auth:
        headers['authorization'] = 'Basic ' + b64encode(b(basic_auth)).decode('utf-8')
    if proxy_basic_auth:
        headers['proxy-authorization'] = 'Basic ' + b64encode(b(proxy_basic_auth)).decode('utf-8')
    if disable_cache:
        headers['cache-control'] = 'no-cache'
    return headers
