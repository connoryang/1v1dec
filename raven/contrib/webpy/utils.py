#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\raven\contrib\webpy\utils.py
from __future__ import absolute_import
import web
from raven.utils.wsgi import get_headers, get_environ

def get_data_from_request():
    return {'request': {'url': '%s://%s%s' % (web.ctx['protocol'], web.ctx['host'], web.ctx['path']),
                 'query_string': web.ctx.query,
                 'method': web.ctx.method,
                 'data': web.data(),
                 'headers': dict(get_headers(web.ctx.environ)),
                 'env': dict(get_environ(web.ctx.environ))}}
