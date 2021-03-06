#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\lib\urllib3\filepost.py
import codecs
import mimetypes
try:
    from mimetools import choose_boundary
except ImportError:
    from .packages.mimetools_choose_boundary import choose_boundary

from io import BytesIO
from .packages import six
from .packages.six import b
writer = codecs.lookup('utf-8')[3]

def get_content_type(filename):
    return mimetypes.guess_type(filename)[0] or 'application/octet-stream'


def iter_fields(fields):
    if isinstance(fields, dict):
        return ((k, v) for k, v in six.iteritems(fields))
    return ((k, v) for k, v in fields)


def encode_multipart_formdata(fields, boundary = None):
    body = BytesIO()
    if boundary is None:
        boundary = choose_boundary()
    for fieldname, value in iter_fields(fields):
        body.write(b('--%s\r\n' % boundary))
        if isinstance(value, tuple):
            filename, data = value
            writer(body).write('Content-Disposition: form-data; name="%s"; filename="%s"\r\n' % (fieldname, filename))
            body.write(b('Content-Type: %s\r\n\r\n' % get_content_type(filename)))
        else:
            data = value
            writer(body).write('Content-Disposition: form-data; name="%s"\r\n' % fieldname)
            body.write('Content-Type: text/plain\r\n\r\n')
        if isinstance(data, int):
            data = str(data)
        if isinstance(data, six.text_type):
            writer(body).write(data)
        else:
            body.write(data)
        body.write('\r\n')

    body.write(b('--%s--\r\n' % boundary))
    content_type = b('multipart/form-data; boundary=%s' % boundary)
    return (body.getvalue(), content_type)
