#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\raven\_compat.py
from __future__ import absolute_import
import operator
import sys
import types
__author__ = 'Benjamin Peterson <benjamin@python.org>'
__version__ = '1.3.0'
PY2 = sys.version_info[0] == 2
if not PY2:
    string_types = (str,)
    integer_types = (int,)
    class_types = (type,)
    text_type = str
    binary_type = bytes
    MAXSIZE = sys.maxsize
else:
    string_types = (basestring,)
    integer_types = (int, long)
    class_types = (type, types.ClassType)
    text_type = unicode
    binary_type = str
    if sys.platform.startswith('java'):
        MAXSIZE = int(2147483647L)
    else:

        class X(object):

            def __len__(self):
                return 2147483648L


        try:
            len(X())
        except OverflowError:
            MAXSIZE = int(2147483647L)
        else:
            MAXSIZE = int(9223372036854775807L)
            del X

def _import_module(name):
    __import__(name)
    return sys.modules[name]


if not PY2:
    _iterkeys = 'keys'
    _itervalues = 'values'
    _iteritems = 'items'
    _iterlists = 'lists'
else:
    _iterkeys = 'iterkeys'
    _itervalues = 'itervalues'
    _iteritems = 'iteritems'
    _iterlists = 'iterlists'
try:
    advance_iterator = next
except NameError:

    def advance_iterator(it):
        return it.next()


next = advance_iterator
try:
    callable = callable
except NameError:

    def callable(obj):
        return any(('__call__' in klass.__dict__ for klass in type(obj).__mro__))


def iterkeys(d, **kw):
    return iter(getattr(d, _iterkeys)(**kw))


def itervalues(d, **kw):
    return iter(getattr(d, _itervalues)(**kw))


def iteritems(d, **kw):
    return iter(getattr(d, _iteritems)(**kw))


def iterlists(d, **kw):
    return iter(getattr(d, _iterlists)(**kw))


if not PY2:

    def b(s):
        return s.encode('latin-1')


    def u(s):
        return s


    if sys.version_info[1] <= 1:

        def int2byte(i):
            return bytes((i,))


    else:
        int2byte = operator.methodcaller('to_bytes', 1, 'big')
    import io
    StringIO = io.StringIO
    BytesIO = io.BytesIO
else:

    def b(s):
        return s


    def u(s):
        return unicode(s, 'unicode_escape')


    int2byte = chr
    import StringIO
    StringIO = BytesIO = StringIO.StringIO
if not PY2:
    import builtins
    exec_ = getattr(builtins, 'exec')

    def reraise(tp, value, tb = None):
        if value.__traceback__ is not tb:
            raise value.with_traceback(tb)
        raise value


    del builtins
else:

    def exec_(_code_, _globs_ = None, _locs_ = None):
        if _globs_ is None:
            frame = sys._getframe(1)
            _globs_ = frame.f_globals
            if _locs_ is None:
                _locs_ = frame.f_locals
            del frame
        elif _locs_ is None:
            _locs_ = _globs_
        exec 'exec _code_ in _globs_, _locs_'


    exec_('def reraise(tp, value, tb=None):\n    raise tp, value, tb\n')

def with_metaclass(meta, base = object):
    return meta('NewBase', (base,), {})


def get_code(func):
    rv = getattr(func, '__code__', getattr(func, 'func_code', None))
    if rv is None:
        raise TypeError('Could not get code from %r' % type(func).__name__)
    return rv


try:
    advance_iterator = next
except NameError:

    def advance_iterator(it):
        return it.next()


    next = advance_iterator

try:
    callable = callable
except NameError:

    def callable(obj):
        return any(('__call__' in klass.__dict__ for klass in type(obj).__mro__))


if not PY2:

    def get_unbound_function(unbound):
        return unbound


    create_bound_method = types.MethodType

    def create_unbound_method(func, cls):
        return func


    Iterator = object
else:

    def get_unbound_function(unbound):
        return unbound.im_func


    def create_bound_method(func, obj):
        return types.MethodType(func, obj, obj.__class__)


    def create_unbound_method(func, cls):
        return types.MethodType(func, None, cls)


    class Iterator(object):

        def next(self):
            return type(self).__next__(self)

        callable = callable
