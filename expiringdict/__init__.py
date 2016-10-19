#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\expiringdict\__init__.py
from time import time
from threading import RLock
try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict

class ExpiringDict(OrderedDict):

    def __init__(self, max_len, max_age_seconds):
        OrderedDict.__init__(self)
        self.max_len = max_len
        self.max_age = max_age_seconds
        self.lock = RLock()

    def __contains__(self, key):
        try:
            with self.lock:
                item = OrderedDict.__getitem__(self, key)
                if time() - item[1] < self.max_age:
                    return True
                del self[key]
        except KeyError:
            pass

        return False

    def __getitem__(self, key, with_age = False):
        with self.lock:
            item = OrderedDict.__getitem__(self, key)
            item_age = time() - item[1]
            if item_age < self.max_age:
                if with_age:
                    return (item[0], item_age)
                else:
                    return item[0]
            else:
                del self[key]
                raise KeyError(key)

    def __setitem__(self, key, value):
        with self.lock:
            if len(self) >= self.max_len:
                self.popitem(last=False)
            OrderedDict.__setitem__(self, key, (value, time()))

    def grow(self, new_size):
        if new_size > self.max_len:
            self.max_len = new_size

    def size(self):
        return self.max_len

    def ttl(self, key):
        key_value, key_age = self.get(key, with_age=True)
        if key_age:
            key_ttl = self.max_age - key_age
            if key_ttl > 0:
                return key_ttl

    def pop(self, key, default = None):
        with self.lock:
            try:
                item = OrderedDict.__getitem__(self, key)
                del self[key]
                return item[0]
            except KeyError:
                return default

    def get(self, key, default = None, with_age = False):
        try:
            return self.__getitem__(key, with_age)
        except KeyError:
            if with_age:
                return (default, None)
            else:
                return default

    def items(self):
        r = []
        for key in self:
            try:
                r.append((key, self[key]))
            except KeyError:
                pass

        return r

    def values(self):
        r = []
        for key in self:
            try:
                r.append(self[key])
            except KeyError:
                pass

        return r

    def fromkeys(self):
        raise NotImplementedError()

    def iteritems(self):
        raise NotImplementedError()

    def itervalues(self):
        raise NotImplementedError()

    def viewitems(self):
        raise NotImplementedError()

    def viewkeys(self):
        raise NotImplementedError()

    def viewvalues(self):
        raise NotImplementedError()
