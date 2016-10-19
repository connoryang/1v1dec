#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\stdlib\pkg_resources\_vendor\packaging\version.py
from __future__ import absolute_import, division, print_function
import collections
import itertools
import re
from ._structures import Infinity
__all__ = ['parse',
 'Version',
 'LegacyVersion',
 'InvalidVersion',
 'VERSION_PATTERN']
_Version = collections.namedtuple('_Version', ['epoch',
 'release',
 'dev',
 'pre',
 'post',
 'local'])

def parse(version):
    try:
        return Version(version)
    except InvalidVersion:
        return LegacyVersion(version)


class InvalidVersion(ValueError):
    pass


class _BaseVersion(object):

    def __hash__(self):
        return hash(self._key)

    def __lt__(self, other):
        return self._compare(other, lambda s, o: s < o)

    def __le__(self, other):
        return self._compare(other, lambda s, o: s <= o)

    def __eq__(self, other):
        return self._compare(other, lambda s, o: s == o)

    def __ge__(self, other):
        return self._compare(other, lambda s, o: s >= o)

    def __gt__(self, other):
        return self._compare(other, lambda s, o: s > o)

    def __ne__(self, other):
        return self._compare(other, lambda s, o: s != o)

    def _compare(self, other, method):
        if not isinstance(other, _BaseVersion):
            return NotImplemented
        return method(self._key, other._key)


class LegacyVersion(_BaseVersion):

    def __init__(self, version):
        self._version = str(version)
        self._key = _legacy_cmpkey(self._version)

    def __str__(self):
        return self._version

    def __repr__(self):
        return '<LegacyVersion({0})>'.format(repr(str(self)))

    @property
    def public(self):
        return self._version

    @property
    def base_version(self):
        return self._version

    @property
    def local(self):
        return None

    @property
    def is_prerelease(self):
        return False

    @property
    def is_postrelease(self):
        return False


_legacy_version_component_re = re.compile('(\\d+ | [a-z]+ | \\.| -)', re.VERBOSE)
_legacy_version_replacement_map = {'pre': 'c',
 'preview': 'c',
 '-': 'final-',
 'rc': 'c',
 'dev': '@'}

def _parse_version_parts(s):
    for part in _legacy_version_component_re.split(s):
        part = _legacy_version_replacement_map.get(part, part)
        if not part or part == '.':
            continue
        if part[:1] in '0123456789':
            yield part.zfill(8)
        else:
            yield '*' + part

    yield '*final'


def _legacy_cmpkey(version):
    epoch = -1
    parts = []
    for part in _parse_version_parts(version.lower()):
        if part.startswith('*'):
            if part < '*final':
                while parts and parts[-1] == '*final-':
                    parts.pop()

            while parts and parts[-1] == '00000000':
                parts.pop()

        parts.append(part)

    parts = tuple(parts)
    return (epoch, parts)


VERSION_PATTERN = '\n    v?\n    (?:\n        (?:(?P<epoch>[0-9]+)!)?                           # epoch\n        (?P<release>[0-9]+(?:\\.[0-9]+)*)                  # release segment\n        (?P<pre>                                          # pre-release\n            [-_\\.]?\n            (?P<pre_l>(a|b|c|rc|alpha|beta|pre|preview))\n            [-_\\.]?\n            (?P<pre_n>[0-9]+)?\n        )?\n        (?P<post>                                         # post release\n            (?:-(?P<post_n1>[0-9]+))\n            |\n            (?:\n                [-_\\.]?\n                (?P<post_l>post|rev|r)\n                [-_\\.]?\n                (?P<post_n2>[0-9]+)?\n            )\n        )?\n        (?P<dev>                                          # dev release\n            [-_\\.]?\n            (?P<dev_l>dev)\n            [-_\\.]?\n            (?P<dev_n>[0-9]+)?\n        )?\n    )\n    (?:\\+(?P<local>[a-z0-9]+(?:[-_\\.][a-z0-9]+)*))?       # local version\n'

class Version(_BaseVersion):
    _regex = re.compile('^\\s*' + VERSION_PATTERN + '\\s*$', re.VERBOSE | re.IGNORECASE)

    def __init__(self, version):
        match = self._regex.search(version)
        if not match:
            raise InvalidVersion("Invalid version: '{0}'".format(version))
        self._version = _Version(epoch=int(match.group('epoch')) if match.group('epoch') else 0, release=tuple((int(i) for i in match.group('release').split('.'))), pre=_parse_letter_version(match.group('pre_l'), match.group('pre_n')), post=_parse_letter_version(match.group('post_l'), match.group('post_n1') or match.group('post_n2')), dev=_parse_letter_version(match.group('dev_l'), match.group('dev_n')), local=_parse_local_version(match.group('local')))
        self._key = _cmpkey(self._version.epoch, self._version.release, self._version.pre, self._version.post, self._version.dev, self._version.local)

    def __repr__(self):
        return '<Version({0})>'.format(repr(str(self)))

    def __str__(self):
        parts = []
        if self._version.epoch != 0:
            parts.append('{0}!'.format(self._version.epoch))
        parts.append('.'.join((str(x) for x in self._version.release)))
        if self._version.pre is not None:
            parts.append(''.join((str(x) for x in self._version.pre)))
        if self._version.post is not None:
            parts.append('.post{0}'.format(self._version.post[1]))
        if self._version.dev is not None:
            parts.append('.dev{0}'.format(self._version.dev[1]))
        if self._version.local is not None:
            parts.append('+{0}'.format('.'.join((str(x) for x in self._version.local))))
        return ''.join(parts)

    @property
    def public(self):
        return str(self).split('+', 1)[0]

    @property
    def base_version(self):
        parts = []
        if self._version.epoch != 0:
            parts.append('{0}!'.format(self._version.epoch))
        parts.append('.'.join((str(x) for x in self._version.release)))
        return ''.join(parts)

    @property
    def local(self):
        version_string = str(self)
        if '+' in version_string:
            return version_string.split('+', 1)[1]

    @property
    def is_prerelease(self):
        return bool(self._version.dev or self._version.pre)

    @property
    def is_postrelease(self):
        return bool(self._version.post)


def _parse_letter_version(letter, number):
    if letter:
        if number is None:
            number = 0
        letter = letter.lower()
        if letter == 'alpha':
            letter = 'a'
        elif letter == 'beta':
            letter = 'b'
        elif letter in ('c', 'pre', 'preview'):
            letter = 'rc'
        elif letter in ('rev', 'r'):
            letter = 'post'
        return (letter, int(number))
    if not letter and number:
        letter = 'post'
        return (letter, int(number))


_local_version_seperators = re.compile('[\\._-]')

def _parse_local_version(local):
    if local is not None:
        return tuple(((part.lower() if not part.isdigit() else int(part)) for part in _local_version_seperators.split(local)))


def _cmpkey(epoch, release, pre, post, dev, local):
    release = tuple(reversed(list(itertools.dropwhile(lambda x: x == 0, reversed(release)))))
    if pre is None and post is None and dev is not None:
        pre = -Infinity
    elif pre is None:
        pre = Infinity
    if post is None:
        post = -Infinity
    if dev is None:
        dev = Infinity
    if local is None:
        local = -Infinity
    else:
        local = tuple((((i, '') if isinstance(i, int) else (-Infinity, i)) for i in local))
    return (epoch,
     release,
     pre,
     post,
     dev,
     local)
