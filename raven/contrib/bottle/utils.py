#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\raven\contrib\bottle\utils.py
from __future__ import absolute_import
import logging
from raven.utils.compat import _urlparse
from raven.utils.wsgi import get_headers, get_environ
logger = logging.getLogger(__name__)

def get_data_from_request(request):
    urlparts = _urlparse.urlsplit(request.url)
    try:
        form_dict = request.forms.dict
        formdata = dict([ (k, form_dict[k][-1]) for k in form_dict ])
    except Exception:
        formdata = {}

    data = {'request': {'url': '%s://%s%s' % (urlparts.scheme, urlparts.netloc, urlparts.path),
                 'query_string': urlparts.query,
                 'method': request.method,
                 'data': formdata,
                 'headers': dict(get_headers(request.environ)),
                 'env': dict(get_environ(request.environ))}}
    return data
