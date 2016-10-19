#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\stdlib\testfixtures\replace.py
from functools import partial
from testfixtures.compat import ClassType
from testfixtures.resolve import resolve, not_there
from testfixtures.utils import wrap
import warnings

def not_same_descriptor(x, y, descriptor):
    return isinstance(x, descriptor) and not isinstance(y, descriptor)


class Replacer:

    def __init__(self, replace_returns = False):
        self.originals = {}
        self.replace_returns = replace_returns

    def _replace(self, container, name, method, value, strict = True):
        if value is not_there:
            if method == 'a':
                delattr(container, name)
            if method == 'i':
                del container[name]
        else:
            if method == 'a':
                setattr(container, name, value)
            if method == 'i':
                container[name] = value

    def replace(self, target, replacement, strict = True):
        container, method, attribute, t_obj = resolve(target)
        if method is None:
            raise ValueError('target must contain at least one dot!')
        if t_obj is not_there and strict:
            raise AttributeError('Original %r not found' % attribute)
        if t_obj is not_there and replacement is not_there:
            return not_there
        replacement_to_use = replacement
        if isinstance(container, (type, ClassType)):
            if not_same_descriptor(t_obj, replacement, classmethod):
                replacement_to_use = classmethod(replacement)
            elif not_same_descriptor(t_obj, replacement, staticmethod):
                replacement_to_use = staticmethod(replacement)
        self._replace(container, attribute, method, replacement_to_use, strict)
        if target not in self.originals:
            self.originals[target] = t_obj
        if self.replace_returns:
            return replacement

    def restore(self):
        for target, original in tuple(self.originals.items()):
            container, method, attribute, found = resolve(target)
            self._replace(container, attribute, method, original, strict=False)
            del self.originals[target]

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.restore()

    def __del__(self):
        if self.originals:
            warnings.warn('Replacer deleted without being restored, originals left: %r' % self.originals)


def replace(target, replacement, strict = True):
    r = Replacer(replace_returns=True)
    return wrap(partial(r.replace, target, replacement, strict), r.restore)
