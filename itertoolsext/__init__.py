#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\itertoolsext\__init__.py
from brennivin.itertoolsext import *
_NOT_SUPPLIED = object()

def get_column(columnid, *rows):
    if not rows:
        return
    column_elements = zip(*rows)[columnid]
    return iter(column_elements)


def get_first_matching_index(iterable, predicate):
    for i, each in enumerate(iterable):
        if predicate(each):
            return i


def dump_dic(dic, indent = 0):
    buff = []
    ind = []
    for i in xrange(0, indent):
        ind.append('\t')

    ind = ''.join(ind)
    for k, v in dic.iteritems():
        if type(v) is dict:
            buff.append('%s%s = {\n' % (ind, k))
            buff.append(dump_dic(v, indent + 1))
            buff.append('%s}\n' % ind)
        else:
            buff.append('%s%s = %s %s\n' % (ind,
             k,
             v,
             type(v)))

    return ''.join(buff)


class IterTree(object):

    def __init__(self):
        self.nodes = {}

    def set(self, key_list, value):
        if isinstance(key_list, tuple):
            key_list = list(key_list)
        elif not isinstance(key_list, list):
            key_list = [key_list]
        key = key_list.pop(0)
        if key_list:
            if key not in self.nodes:
                self.nodes[key] = IterTree()
            self.nodes[key].set(key_list, value)
        else:
            self.nodes[key] = value

    def get(self, key_or_seq, default = _NOT_SUPPLIED):
        if isinstance(key_or_seq, tuple):
            key_or_seq = list(key_or_seq)
        elif not isinstance(key_or_seq, list):
            key_or_seq = [key_or_seq]
        key = key_or_seq.pop(0)
        if key not in self.nodes:
            if default == _NOT_SUPPLIED:
                raise KeyError(key)
            else:
                return default
        else:
            if key_or_seq:
                return self.nodes[key].get(key_or_seq, default)
            return self.nodes[key]

    def __setitem__(self, key_list, value):
        self.set(key_list, value)

    def __getitem__(self, key_list):
        return self.get(key_list)

    def __len__(self):
        leaf_len = 0
        for n in self.nodes.itervalues():
            if isinstance(n, IterTree):
                leaf_len += len(n)
            else:
                leaf_len += 1

        return leaf_len

    def __iter__(self):
        return self.iterkeys()

    def __delitem__(self, key_or_seq):
        if isinstance(key_or_seq, tuple):
            key_or_seq = list(key_or_seq)
        elif not isinstance(key_or_seq, list):
            key_or_seq = [key_or_seq]
        key = key_or_seq.pop(0)
        if key not in self.nodes:
            raise KeyError(key)
        elif key_or_seq:
            if isinstance(self.nodes[key], IterTree):
                self.nodes[key].__delitem__(key_or_seq)
                if len(self.nodes[key]) < 1:
                    del self.nodes[key]
            else:
                raise KeyError(key)
        else:
            del self.nodes[key]

    def popitem(self):
        for k in self.iterkeys():
            return (k, self.pop(k))

    def pop(self, key_or_seq, default = _NOT_SUPPLIED):
        if isinstance(key_or_seq, tuple):
            key_or_seq = list(key_or_seq)
        elif not isinstance(key_or_seq, list):
            key_or_seq = [key_or_seq]
        key = key_or_seq.pop(0)
        if key not in self.nodes:
            if default == _NOT_SUPPLIED:
                raise KeyError(key)
            else:
                return default
        else:
            if key_or_seq:
                val = self.nodes[key].pop(key_or_seq, default)
                if len(self.nodes[key]) < 1:
                    del self.nodes[key]
                return val
            return self.nodes.pop(key)

    def __contains__(self, key_or_seq):
        if isinstance(key_or_seq, tuple):
            key_or_seq = list(key_or_seq)
        elif not isinstance(key_or_seq, list):
            key_or_seq = [key_or_seq]
        key = key_or_seq.pop(0)
        if key not in self.nodes:
            return False
        if key_or_seq:
            if isinstance(self.nodes[key], IterTree):
                return key_or_seq in self.nodes[key]
            else:
                return False
        else:
            return True

    def keys(self):
        key_list = list()
        for k, n in self.nodes.iteritems():
            if isinstance(n, IterTree):
                for c in n.iterkeys():
                    new_key = [k]
                    new_key.extend(c)
                    key_list.append(new_key)

            else:
                key_list.append([k])

        return [ tuple(k) for k in key_list ]

    def iterkeys(self):
        for k, n in self.nodes.iteritems():
            if isinstance(n, IterTree):
                for c in n.iterkeys():
                    next_key = [k]
                    next_key.extend(c)
                    yield tuple(next_key)

            else:
                yield (k,)

    def values(self):
        value_list = list()
        for k, n in self.nodes.iteritems():
            if isinstance(n, IterTree):
                for v in n.values():
                    value_list.append(v)

            else:
                value_list.append(n)

        return value_list

    def itervalues(self):
        for k, n in self.nodes.iteritems():
            if isinstance(n, IterTree):
                for v in n.itervalues():
                    yield v

            else:
                yield n

    def items(self):
        item_list = list()
        for k, n in self.nodes.iteritems():
            if isinstance(n, IterTree):
                for nk, nv in n.items():
                    new_key = [k]
                    new_key.extend(nk)
                    item_list.append((new_key, nv))

            else:
                item_list.append(([k], n))

        return [ (tuple(ik), iv) for ik, iv in item_list ]

    def iteritems(self):
        for k, n in self.nodes.iteritems():
            if isinstance(n, IterTree):
                for nk, nv in n.iteritems():
                    next_key = [k]
                    next_key.extend(nk)
                    yield (tuple(next_key), nv)

            else:
                yield ((k,), n)

    def __repr__(self):
        buff = []
        for k, n in self.nodes.iteritems():
            buff.append('%s: %r' % (k, n))

        return '<IterTree [%s]>' % ', '.join(buff)

    def print_tree(self, _indent = 0):
        buff = []
        for k, n in self.nodes.iteritems():
            if isinstance(n, IterTree):
                buff.append('%s%s: {' % (' ' * (_indent * 4), k))
                buff.append(n.print_tree(_indent + 1))
                buff.append('%s}' % (' ' * (_indent * 4)))
            else:
                buff.append('%s%s: %r' % (' ' * (_indent * 4), k, n))

        return '\n'.join(buff)
