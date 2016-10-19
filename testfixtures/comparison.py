#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\stdlib\testfixtures\comparison.py
from collections import Iterable
from difflib import unified_diff
from pprint import pformat
from re import compile, MULTILINE
from testfixtures import not_there
from testfixtures.compat import ClassType, Unicode, basestring, PY3, mock_call, unittest_mock_call
from testfixtures.resolve import resolve
from types import GeneratorType

def compare_simple(x, y, context):
    return context.label('x', repr(x)) + ' != ' + context.label('y', repr(y))


def compare_with_type(x, y, context):
    source = locals()
    to_render = {}
    for name in ('x', 'y'):
        obj = source[name]
        to_render[name] = context.label(name, '{0} ({1!r})'.format(_short_repr(obj), type(obj)))

    return '{x} != {y}'.format(**to_render)


def compare_sequence(x, y, context):
    l_x = len(x)
    l_y = len(y)
    i = 0
    while i < l_x and i < l_y:
        if context.different(x[i], y[i], '[%i]' % i):
            break
        i += 1

    if l_x == l_y and i == l_x:
        return
    return 'sequence not as expected:\n\nsame:\n%s\n\n%s:\n%s\n\n%s:\n%s' % (pformat(x[:i]),
     context.x_label or 'first',
     pformat(x[i:]),
     context.y_label or 'second',
     pformat(y[i:]))


def compare_generator(x, y, context):
    x = tuple(x)
    y = tuple(y)
    if x == y:
        return
    return compare_sequence(x, y, context)


def compare_tuple(x, y, context):
    x_fields = getattr(x, '_fields', None)
    y_fields = getattr(y, '_fields', None)
    if x_fields and y_fields:
        if x_fields == y_fields:
            return _compare_mapping(dict(zip(x_fields, x)), dict(zip(y_fields, y)), context, x)
        else:
            return compare_with_type(x, y, context)
    return compare_sequence(x, y, context)


def compare_dict(x, y, context):
    return _compare_mapping(x, y, context, x)


def sorted_by_repr(sequence):
    return sorted(sequence, key=lambda o: repr(o))


def _compare_mapping(x, y, context, obj_for_class):
    x_keys = set(x.keys())
    y_keys = set(y.keys())
    x_not_y = x_keys - y_keys
    y_not_x = y_keys - x_keys
    same = []
    diffs = []
    for key in sorted_by_repr(x_keys.intersection(y_keys)):
        if context.different(x[key], y[key], '[%r]' % (key,)):
            diffs.append('%r: %s != %s' % (key, context.label('x', pformat(x[key])), context.label('y', pformat(y[key]))))
        else:
            same.append(key)

    lines = ['%s not as expected:' % obj_for_class.__class__.__name__]
    if same:
        set_same = set(same)
        if set_same == x_keys == y_keys:
            return
        lines.extend(('', 'same:', repr(same)))
    x_label = context.x_label or 'first'
    y_label = context.y_label or 'second'
    if x_not_y:
        lines.extend(('', 'in %s but not %s:' % (x_label, y_label)))
        for key in sorted_by_repr(x_not_y):
            lines.append('%r: %s' % (key, pformat(x[key])))

    if y_not_x:
        lines.extend(('', 'in %s but not %s:' % (y_label, x_label)))
        for key in sorted_by_repr(y_not_x):
            lines.append('%r: %s' % (key, pformat(y[key])))

    if diffs:
        lines.extend(('', 'values differ:'))
        lines.extend(diffs)
    return '\n'.join(lines)


def compare_set(x, y, context):
    x_not_y = x - y
    y_not_x = y - x
    lines = ['%s not as expected:' % x.__class__.__name__, '']
    x_label = context.x_label or 'first'
    y_label = context.y_label or 'second'
    if x_not_y:
        lines.extend(('in %s but not %s:' % (x_label, y_label), pformat(sorted_by_repr(x_not_y)), ''))
    if y_not_x:
        lines.extend(('in %s but not %s:' % (y_label, x_label), pformat(sorted_by_repr(y_not_x)), ''))
    return '\n'.join(lines) + '\n'


trailing_whitespace_re = compile('\\s+$', MULTILINE)

def strip_blank_lines(text):
    result = []
    for line in text.split('\n'):
        if line and not line.isspace():
            result.append(line)

    return '\n'.join(result)


def split_repr(text):
    parts = text.split('\n')
    for i, part in enumerate(parts[:-1]):
        parts[i] = repr(part + '\n')

    parts[-1] = repr(parts[-1])
    return '\n'.join(parts)


def compare_text(x, y, context):
    blanklines = context.get_option('blanklines', True)
    trailing_whitespace = context.get_option('trailing_whitespace', True)
    show_whitespace = context.get_option('show_whitespace', False)
    if not trailing_whitespace:
        x = trailing_whitespace_re.sub('', x)
        y = trailing_whitespace_re.sub('', y)
    if not blanklines:
        x = strip_blank_lines(x)
        y = strip_blank_lines(y)
    if x == y:
        return
    labelled_x = context.label('x', repr(x))
    labelled_y = context.label('y', repr(y))
    if len(x) > 10 or len(y) > 10:
        if '\n' in x or '\n' in y:
            if show_whitespace:
                x = split_repr(x)
                y = split_repr(y)
            message = '\n' + diff(x, y, context.x_label, context.y_label)
        else:
            message = '\n%s\n!=\n%s' % (labelled_x, labelled_y)
    else:
        message = labelled_x + ' != ' + labelled_y
    return message


def _short_repr(obj):
    repr_ = repr(obj)
    if len(repr_) > 30:
        repr_ = repr_[:30] + '...'
    return repr_


_registry = {dict: compare_dict,
 set: compare_set,
 list: compare_sequence,
 tuple: compare_tuple,
 str: compare_text,
 Unicode: compare_text,
 GeneratorType: compare_generator,
 mock_call.__class__: compare_simple,
 unittest_mock_call.__class__: compare_simple}

def register(type, comparer):
    _registry[type] = comparer


def _mro(obj):
    class_ = getattr(obj, '__class__', None)
    if class_ is None:
        return (obj,)
    mro = getattr(class_, '__mro__', None)
    if mro is None:
        return (class_,)
    return mro


def _shared_mro(x, y):
    y_mro = set(_mro(y))
    for class_ in _mro(x):
        if class_ in y_mro:
            yield class_


_unsafe_iterables = (basestring, dict)

class CompareContext(object):
    x_label = y_label = None

    def __init__(self, options):
        comparers = options.pop('comparers', None)
        if comparers:
            self.registry = dict(_registry)
            self.registry.update(comparers)
        else:
            self.registry = _registry
        self.recursive = options.pop('recursive', True)
        self.strict = options.pop('strict', False)
        if 'expected' in options or 'actual' in options:
            self.x_label = 'expected'
            self.y_label = 'actual'
        self.x_label = options.pop('x_label', self.x_label)
        self.y_label = options.pop('y_label', self.y_label)
        self.options = options
        self.message = ''
        self.breadcrumbs = []

    def extract_args(self, args):
        possible = []
        expected = self.options.pop('expected', not_there)
        if expected is not not_there:
            possible.append(expected)
        possible.extend(args)
        actual = self.options.pop('actual', not_there)
        if actual is not not_there:
            possible.append(actual)
        if len(possible) != 2:
            raise TypeError('Exactly two objects needed, you supplied: ' + repr(possible))
        return possible

    def get_option(self, name, default = None):
        return self.options.get(name, default)

    def label(self, side, value):
        r = str(value)
        label = getattr(self, side + '_label')
        if label:
            r += ' (' + label + ')'
        return r

    def _lookup(self, x, y):
        if self.strict and type(x) is not type(y):
            return compare_with_type
        for class_ in _shared_mro(x, y):
            comparer = self.registry.get(class_)
            if comparer:
                return comparer

        if isinstance(x, Iterable) and isinstance(y, Iterable) and not (isinstance(x, _unsafe_iterables) or isinstance(y, _unsafe_iterables)):
            return compare_generator
        return compare_simple

    def _separator(self):
        return '\n\nWhile comparing %s: ' % ''.join(self.breadcrumbs[1:])

    def different(self, x, y, breadcrumb):
        recursed = bool(self.breadcrumbs)
        self.breadcrumbs.append(breadcrumb)
        existing_message = self.message
        self.message = ''
        current_message = ''
        try:
            if not self.strict and x == y:
                return False
            comparer = self._lookup(x, y)
            result = comparer(x, y, self)
            specific_comparer = comparer is not compare_simple
            if self.strict:
                if type(x) is type(x) and x == y and not specific_comparer:
                    return False
            if result:
                if specific_comparer and recursed:
                    current_message = self._separator()
                if specific_comparer or not recursed:
                    current_message += result
                    if self.recursive:
                        current_message += self.message
            return result
        finally:
            self.message = existing_message + current_message
            self.breadcrumbs.pop()


def compare(*args, **kw):
    prefix = kw.pop('prefix', None)
    raises = kw.pop('raises', True)
    context = CompareContext(kw)
    x, y = context.extract_args(args)
    if not context.different(x, y, not_there):
        return
    message = context.message
    if prefix:
        message = prefix + ': ' + message
    if raises:
        raise AssertionError(message)
    return message


class Comparison(object):
    failed = None

    def __init__(self, object_or_type, attribute_dict = None, strict = True, **attributes):
        if attributes:
            if attribute_dict is None:
                attribute_dict = attributes
            else:
                attribute_dict.update(attributes)
        if isinstance(object_or_type, basestring):
            container, method, name, c = resolve(object_or_type)
            if c is not_there:
                raise AttributeError('%r could not be resolved' % object_or_type)
        elif isinstance(object_or_type, (ClassType, type)):
            c = object_or_type
        elif isinstance(object_or_type, BaseException):
            c = object_or_type.__class__
            if attribute_dict is None:
                attribute_dict = vars(object_or_type)
                attribute_dict['args'] = object_or_type.args
        else:
            c = object_or_type.__class__
            if attribute_dict is None:
                attribute_dict = vars(object_or_type)
        self.c = c
        self.v = attribute_dict
        self.strict = strict

    def __eq__(self, other):
        if self.c is not other.__class__:
            self.failed = True
            return False
        if self.v is None:
            return True
        self.failed = {}
        if isinstance(other, BaseException):
            v = dict(vars(other))
            v['args'] = other.args
            if PY3 and '_not_found' in v:
                del v['_not_found']
        else:
            try:
                v = vars(other)
            except TypeError:
                if self.strict:
                    raise TypeError('%r does not support vars() so cannot do strict comparison' % other)
                v = {}
                for k in self.v.keys():
                    try:
                        v[k] = getattr(other, k)
                    except AttributeError:
                        pass

        e = set(self.v.keys())
        a = set(v.keys())
        for k in e.difference(a):
            try:
                v[k] = getattr(other, k)
            except AttributeError:
                self.failed[k] = '%s not in other' % repr(self.v[k])
            else:
                a.add(k)

        if self.strict:
            for k in a.difference(e):
                self.failed[k] = '%s not in Comparison' % repr(v[k])

        for k in e.intersection(a):
            ev = self.v[k]
            av = v[k]
            if ev != av:
                self.failed[k] = '%r != %r' % (ev, av)

        if self.failed:
            return False
        return True

    def __ne__(self, other):
        return not self == other

    def __repr__(self, indent = 2):
        full = False
        if self.failed is True:
            v = 'wrong type</C>'
        elif self.v is None:
            v = ''
        else:
            full = True
            v = '\n'
            if self.failed:
                vd = self.failed
                r = str
            else:
                vd = self.v
                r = repr
            for vk, vv in sorted(vd.items()):
                if isinstance(vv, Comparison):
                    vvr = vv.__repr__(indent + 2)
                else:
                    vvr = r(vv)
                v += ' ' * indent + '%s:%s\n' % (vk, vvr)

            v += ' ' * indent + '</C>'
        name = getattr(self.c, '__module__', '')
        if name:
            name += '.'
        name += getattr(self.c, '__name__', '')
        if not name:
            name = repr(self.c)
        r = '<C%s:%s>%s' % (self.failed and '(failed)' or '', name, v)
        if full:
            return '\n' + ' ' * indent + r
        else:
            return r


class StringComparison:

    def __init__(self, regex_source):
        self.re = compile(regex_source)

    def __eq__(self, other):
        if not isinstance(other, basestring):
            return
        if self.re.match(other):
            return True
        return False

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        return '<S:%s>' % self.re.pattern

    def __lt__(self, other):
        return self.re.pattern < other

    def __gt__(self, other):
        return self.re.pattern > other


class RoundComparison:

    def __init__(self, value, precision):
        self.rounded = round(value, precision)
        self.precision = precision

    def __eq__(self, other):
        other_rounded = round(other, self.precision)
        if type(self.rounded) is not type(other_rounded):
            raise TypeError('Cannot compare %r with %r' % (self, type(other)))
        return self.rounded == other_rounded

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        return '<R:%s to %i digits>' % (self.rounded, self.precision)


def diff(x, y, x_label = '', y_label = ''):
    return '\n'.join(unified_diff(x.split('\n'), y.split('\n'), x_label or 'first', y_label or 'second', lineterm=''))
