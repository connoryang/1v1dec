#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\requests\packages\urllib3\util\response.py
from __future__ import absolute_import
from ..packages.six.moves import http_client as httplib
from ..exceptions import HeaderParsingError

def is_fp_closed(obj):
    try:
        return obj.closed
    except AttributeError:
        pass

    try:
        return obj.fp is None
    except AttributeError:
        pass

    raise ValueError('Unable to determine whether fp is closed.')


def assert_header_parsing(headers):
    if not isinstance(headers, httplib.HTTPMessage):
        raise TypeError('expected httplib.Message, got {0}.'.format(type(headers)))
    defects = getattr(headers, 'defects', None)
    get_payload = getattr(headers, 'get_payload', None)
    unparsed_data = None
    if get_payload:
        unparsed_data = get_payload()
    if defects or unparsed_data:
        raise HeaderParsingError(defects=defects, unparsed_data=unparsed_data)


def is_response_to_head(response):
    method = response._method
    if isinstance(method, int):
        return method == 3
    return method.upper() == 'HEAD'
