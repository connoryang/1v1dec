#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\requests\packages\urllib3\_collections.py
from __future__ import absolute_import
from collections import Mapping, MutableMapping
try:
    from threading import RLock
except ImportError:

    class RLock:

        def __enter__(self):
            pass

        def __exit__(self, exc_type, exc_value, traceback):
            pass


try:
    from collections import OrderedDict
except ImportError:
    from .packages.ordered_dict import OrderedDict

from .packages.six import iterkeys, itervalues, PY3
__all__ = ['RecentlyUsedContainer', 'HTTPHeaderDict']
_Null = object()

class RecentlyUsedContainer(MutableMapping):
    ContainerCls = OrderedDict

    def __init__(self, maxsize = 10, dispose_func = None):
        self._maxsize = maxsize
        self.dispose_func = dispose_func
        self._container = self.ContainerCls()
        self.lock = RLock()

    def __getitem__(self, key):
        with self.lock:
            item = self._container.pop(key)
            self._container[key] = item
            return item

    def __setitem__(self, key, value):
        evicted_value = _Null
        with self.lock:
            evicted_value = self._container.get(key, _Null)
            self._container[key] = value
            if len(self._container) > self._maxsize:
                _key, evicted_value = self._container.popitem(last=False)
        if self.dispose_func and evicted_value is not _Null:
            self.dispose_func(evicted_value)

    def __delitem__(self, key):
        with self.lock:
            value = self._container.pop(key)
        if self.dispose_func:
            self.dispose_func(value)

    def __len__(self):
        with self.lock:
            return len(self._container)

    def __iter__(self):
        raise NotImplementedError('Iteration over this class is unlikely to be threadsafe.')

    def clear(self):
        with self.lock:
            values = list(itervalues(self._container))
            self._container.clear()
        if self.dispose_func:
            for value in values:
                self.dispose_func(value)

    def keys(self):
        with self.lock:
            return list(iterkeys(self._container))


class HTTPHeaderDict(MutableMapping):

    def __init__(self, headers = None, **kwargs):
        super(HTTPHeaderDict, self).__init__()
        self._container = OrderedDict()
        if headers is not None:
            if isinstance(headers, HTTPHeaderDict):
                self._copy_from(headers)
            else:
                self.extend(headers)
        if kwargs:
            self.extend(kwargs)

    def __setitem__(self, key, val):
        self._container[key.lower()] = (key, val)
        return self._container[key.lower()]

    def __getitem__(self, key):
        val = self._container[key.lower()]
        return ', '.join(val[1:])

    def __delitem__(self, key):
        del self._container[key.lower()]

    def __contains__(self, key):
        return key.lower() in self._container

    def __eq__(self, other):
        if not isinstance(other, Mapping) and not hasattr(other, 'keys'):
            return False
        if not isinstance(other, type(self)):
            other = type(self)(other)
        return dict(((k.lower(), v) for k, v in self.itermerged())) == dict(((k.lower(), v) for k, v in other.itermerged()))

    def __ne__(self, other):
        return not self.__eq__(other)

    if not PY3:
        iterkeys = MutableMapping.iterkeys
        itervalues = MutableMapping.itervalues
    __marker = object()

    def __len__(self):
        return len(self._container)

    def __iter__(self):
        for vals in self._container.values():
            yield vals[0]

    def pop(self, key, default = __marker):
        try:
            value = self[key]
        except KeyError:
            if default is self.__marker:
                raise
            return default

        del self[key]
        return value

    def discard(self, key):
        try:
            del self[key]
        except KeyError:
            pass

    def add(self, key, val):
        key_lower = key.lower()
        new_vals = (key, val)
        vals = self._container.setdefault(key_lower, new_vals)
        if new_vals is not vals:
            if isinstance(vals, list):
                vals.append(val)
            else:
                self._container[key_lower] = [vals[0], vals[1], val]

    def extend(self, *args, **kwargs):
        if len(args) > 1:
            raise TypeError('extend() takes at most 1 positional arguments ({0} given)'.format(len(args)))
        other = args[0] if len(args) >= 1 else ()
        if isinstance(other, HTTPHeaderDict):
            for key, val in other.iteritems():
                self.add(key, val)

        elif isinstance(other, Mapping):
            for key in other:
                self.add(key, other[key])

        elif hasattr(other, 'keys'):
            for key in other.keys():
                self.add(key, other[key])

        else:
            for key, value in other:
                self.add(key, value)

        for key, value in kwargs.items():
            self.add(key, value)

    def getlist(self, key):
        try:
            vals = self._container[key.lower()]
        except KeyError:
            return []

        if isinstance(vals, tuple):
            return [vals[1]]
        else:
            return vals[1:]

    getheaders = getlist
    getallmatchingheaders = getlist
    iget = getlist

    def __repr__(self):
        return '%s(%s)' % (type(self).__name__, dict(self.itermerged()))

    def _copy_from(self, other):
        for key in other:
            val = other.getlist(key)
            if isinstance(val, list):
                val = list(val)
            self._container[key.lower()] = [key] + val

    def copy(self):
        clone = type(self)()
        clone._copy_from(self)
        return clone

    def iteritems(self):
        for key in self:
            vals = self._container[key.lower()]
            for val in vals[1:]:
                yield (vals[0], val)

    def itermerged(self):
        for key in self:
            val = self._container[key.lower()]
            yield (val[0], ', '.join(val[1:]))

    def items(self):
        return list(self.iteritems())

    @classmethod
    def from_httplib(cls, message):
        headers = []
        for line in message.headers:
            if line.startswith((' ', '\t')):
                key, value = headers[-1]
                headers[-1] = (key, value + '\r\n' + line.rstrip())
                continue
            key, value = line.split(':', 1)
            headers.append((key, value.strip()))

        return cls(headers)
