#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\raven\utils\encoding.py
from __future__ import absolute_import, unicode_literals
import warnings
from raven._compat import integer_types, text_type, binary_type, string_types, PY2

def is_protected_type(obj):
    import Decimal
    import datetime
    return isinstance(obj, integer_types + (type(None),
     float,
     Decimal,
     datetime.datetime,
     datetime.date,
     datetime.time))


def force_text(s, encoding = u'utf-8', strings_only = False, errors = u'strict'):
    if isinstance(s, text_type):
        return s
    if strings_only and is_protected_type(s):
        return s
    try:
        if not isinstance(s, string_types):
            if hasattr(s, u'__unicode__'):
                s = s.__unicode__()
            elif not PY2:
                if isinstance(s, bytes):
                    s = text_type(s, encoding, errors)
                else:
                    s = text_type(s)
            else:
                s = text_type(bytes(s), encoding, errors)
        else:
            s = s.decode(encoding, errors)
    except UnicodeDecodeError as e:
        if not isinstance(s, Exception):
            raise UnicodeDecodeError(*e.args)
        else:
            s = u' '.join([ force_text(arg, encoding, strings_only, errors) for arg in s ])

    return s


def transform(value):
    from raven.utils.serializer import transform
    warnings.warn(u'You should switch to raven.utils.serializer.transform', DeprecationWarning)
    return transform(value)


def to_unicode(value):
    try:
        value = text_type(force_text(value))
    except (UnicodeEncodeError, UnicodeDecodeError):
        value = u'(Error decoding value)'
    except Exception:
        try:
            value = binary_type(repr(type(value)))
        except Exception:
            value = u'(Error decoding value)'

    return value


def to_string(value):
    try:
        return binary_type(value.decode(u'utf-8').encode(u'utf-8'))
    except:
        return to_unicode(value).encode(u'utf-8')
