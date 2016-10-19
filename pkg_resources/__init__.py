#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\stdlib\pkg_resources\__init__.py
from __future__ import absolute_import
import sys
import os
import io
import time
import re
import types
import zipfile
import zipimport
import warnings
import stat
import functools
import pkgutil
import operator
import platform
import collections
import plistlib
import email.parser
import tempfile
import textwrap
from pkgutil import get_importer
try:
    import _imp
except ImportError:
    import imp as _imp

from pkg_resources.extern import six
from pkg_resources.extern.six.moves import urllib, map, filter
from os import utime
try:
    from os import mkdir, rename, unlink
    WRITE_SUPPORT = True
except ImportError:
    WRITE_SUPPORT = False

from os import open as os_open
from os.path import isdir, split
try:
    import importlib.machinery as importlib_machinery
    importlib_machinery.__name__
except ImportError:
    importlib_machinery = None

from pkg_resources.extern import packaging
__import__('pkg_resources.extern.packaging.version')
__import__('pkg_resources.extern.packaging.specifiers')
__import__('pkg_resources.extern.packaging.requirements')
__import__('pkg_resources.extern.packaging.markers')
if (3, 0) < sys.version_info < (3, 3):
    msg = 'Support for Python 3.0-3.2 has been dropped. Future versions will fail here.'
    warnings.warn(msg)
require = None
working_set = None

class PEP440Warning(RuntimeWarning):
    pass


class _SetuptoolsVersionMixin(object):

    def __hash__(self):
        return super(_SetuptoolsVersionMixin, self).__hash__()

    def __lt__(self, other):
        if isinstance(other, tuple):
            return tuple(self) < other
        else:
            return super(_SetuptoolsVersionMixin, self).__lt__(other)

    def __le__(self, other):
        if isinstance(other, tuple):
            return tuple(self) <= other
        else:
            return super(_SetuptoolsVersionMixin, self).__le__(other)

    def __eq__(self, other):
        if isinstance(other, tuple):
            return tuple(self) == other
        else:
            return super(_SetuptoolsVersionMixin, self).__eq__(other)

    def __ge__(self, other):
        if isinstance(other, tuple):
            return tuple(self) >= other
        else:
            return super(_SetuptoolsVersionMixin, self).__ge__(other)

    def __gt__(self, other):
        if isinstance(other, tuple):
            return tuple(self) > other
        else:
            return super(_SetuptoolsVersionMixin, self).__gt__(other)

    def __ne__(self, other):
        if isinstance(other, tuple):
            return tuple(self) != other
        else:
            return super(_SetuptoolsVersionMixin, self).__ne__(other)

    def __getitem__(self, key):
        return tuple(self)[key]

    def __iter__(self):
        component_re = re.compile('(\\d+ | [a-z]+ | \\.| -)', re.VERBOSE)
        replace = {'pre': 'c',
         'preview': 'c',
         '-': 'final-',
         'rc': 'c',
         'dev': '@'}.get

        def _parse_version_parts(s):
            for part in component_re.split(s):
                part = replace(part, part)
                if not part or part == '.':
                    continue
                if part[:1] in '0123456789':
                    yield part.zfill(8)
                else:
                    yield '*' + part

            yield '*final'

        def old_parse_version(s):
            parts = []
            for part in _parse_version_parts(s.lower()):
                if part.startswith('*'):
                    if part < '*final':
                        while parts and parts[-1] == '*final-':
                            parts.pop()

                    while parts and parts[-1] == '00000000':
                        parts.pop()

                parts.append(part)

            return tuple(parts)

        warnings.warn('You have iterated over the result of pkg_resources.parse_version. This is a legacy behavior which is inconsistent with the new version class introduced in setuptools 8.0. In most cases, conversion to a tuple is unnecessary. For comparison of versions, sort the Version instances directly. If you have another use case requiring the tuple, please file a bug with the setuptools project describing that need.', RuntimeWarning, stacklevel=1)
        for part in old_parse_version(str(self)):
            yield part


class SetuptoolsVersion(_SetuptoolsVersionMixin, packaging.version.Version):
    pass


class SetuptoolsLegacyVersion(_SetuptoolsVersionMixin, packaging.version.LegacyVersion):
    pass


def parse_version(v):
    try:
        return SetuptoolsVersion(v)
    except packaging.version.InvalidVersion:
        return SetuptoolsLegacyVersion(v)


_state_vars = {}

def _declare_state(vartype, **kw):
    globals().update(kw)
    _state_vars.update(dict.fromkeys(kw, vartype))


def __getstate__():
    state = {}
    g = globals()
    for k, v in _state_vars.items():
        state[k] = g['_sget_' + v](g[k])

    return state


def __setstate__(state):
    g = globals()
    for k, v in state.items():
        g['_sset_' + _state_vars[k]](k, g[k], v)

    return state


def _sget_dict(val):
    return val.copy()


def _sset_dict(key, ob, state):
    ob.clear()
    ob.update(state)


def _sget_object(val):
    return val.__getstate__()


def _sset_object(key, ob, state):
    ob.__setstate__(state)


_sget_none = _sset_none = lambda *args: None

def get_supported_platform():
    plat = get_build_platform()
    m = macosVersionString.match(plat)
    if m is not None and sys.platform == 'darwin':
        try:
            plat = 'macosx-%s-%s' % ('.'.join(_macosx_vers()[:2]), m.group(3))
        except ValueError:
            pass

    return plat


__all__ = ['require',
 'run_script',
 'get_provider',
 'get_distribution',
 'load_entry_point',
 'get_entry_map',
 'get_entry_info',
 'iter_entry_points',
 'resource_string',
 'resource_stream',
 'resource_filename',
 'resource_listdir',
 'resource_exists',
 'resource_isdir',
 'declare_namespace',
 'working_set',
 'add_activation_listener',
 'find_distributions',
 'set_extraction_path',
 'cleanup_resources',
 'get_default_cache',
 'Environment',
 'WorkingSet',
 'ResourceManager',
 'Distribution',
 'Requirement',
 'EntryPoint',
 'ResolutionError',
 'VersionConflict',
 'DistributionNotFound',
 'UnknownExtra',
 'ExtractionError',
 'PEP440Warning',
 'parse_requirements',
 'parse_version',
 'safe_name',
 'safe_version',
 'get_platform',
 'compatible_platforms',
 'yield_lines',
 'split_sections',
 'safe_extra',
 'to_filename',
 'invalid_marker',
 'evaluate_marker',
 'ensure_directory',
 'normalize_path',
 'EGG_DIST',
 'BINARY_DIST',
 'SOURCE_DIST',
 'CHECKOUT_DIST',
 'DEVELOP_DIST',
 'IMetadataProvider',
 'IResourceProvider',
 'FileMetadata',
 'PathMetadata',
 'EggMetadata',
 'EmptyProvider',
 'empty_provider',
 'NullProvider',
 'EggProvider',
 'DefaultProvider',
 'ZipProvider',
 'register_finder',
 'register_namespace_handler',
 'register_loader_type',
 'fixup_namespace_packages',
 'get_importer',
 'run_main',
 'AvailableDistributions']

class ResolutionError(Exception):

    def __repr__(self):
        return self.__class__.__name__ + repr(self.args)


class VersionConflict(ResolutionError):
    _template = '{self.dist} is installed but {self.req} is required'

    @property
    def dist(self):
        return self.args[0]

    @property
    def req(self):
        return self.args[1]

    def report(self):
        return self._template.format(**locals())

    def with_context(self, required_by):
        if not required_by:
            return self
        args = self.args + (required_by,)
        return ContextualVersionConflict(*args)


class ContextualVersionConflict(VersionConflict):
    _template = VersionConflict._template + ' by {self.required_by}'

    @property
    def required_by(self):
        return self.args[2]


class DistributionNotFound(ResolutionError):
    _template = "The '{self.req}' distribution was not found and is required by {self.requirers_str}"

    @property
    def req(self):
        return self.args[0]

    @property
    def requirers(self):
        return self.args[1]

    @property
    def requirers_str(self):
        if not self.requirers:
            return 'the application'
        return ', '.join(self.requirers)

    def report(self):
        return self._template.format(**locals())

    def __str__(self):
        return self.report()


class UnknownExtra(ResolutionError):
    pass


_provider_factories = {}
PY_MAJOR = sys.version[:3]
EGG_DIST = 3
BINARY_DIST = 2
SOURCE_DIST = 1
CHECKOUT_DIST = 0
DEVELOP_DIST = -1

def register_loader_type(loader_type, provider_factory):
    _provider_factories[loader_type] = provider_factory


def get_provider(moduleOrReq):
    if isinstance(moduleOrReq, Requirement):
        return working_set.find(moduleOrReq) or require(str(moduleOrReq))[0]
    try:
        module = sys.modules[moduleOrReq]
    except KeyError:
        __import__(moduleOrReq)
        module = sys.modules[moduleOrReq]

    loader = getattr(module, '__loader__', None)
    return _find_adapter(_provider_factories, loader)(module)


def _macosx_vers(_cache = []):
    if not _cache:
        version = platform.mac_ver()[0]
        if version == '':
            plist = '/System/Library/CoreServices/SystemVersion.plist'
            if os.path.exists(plist):
                if hasattr(plistlib, 'readPlist'):
                    plist_content = plistlib.readPlist(plist)
                    if 'ProductVersion' in plist_content:
                        version = plist_content['ProductVersion']
        _cache.append(version.split('.'))
    return _cache[0]


def _macosx_arch(machine):
    return {'PowerPC': 'ppc',
     'Power_Macintosh': 'ppc'}.get(machine, machine)


def get_build_platform():
    try:
        from sysconfig import get_platform
    except ImportError:
        from distutils.util import get_platform

    plat = get_platform()
    if sys.platform == 'darwin' and not plat.startswith('macosx-'):
        try:
            version = _macosx_vers()
            machine = os.uname()[4].replace(' ', '_')
            return 'macosx-%d.%d-%s' % (int(version[0]), int(version[1]), _macosx_arch(machine))
        except ValueError:
            pass

    return plat


macosVersionString = re.compile('macosx-(\\d+)\\.(\\d+)-(.*)')
darwinVersionString = re.compile('darwin-(\\d+)\\.(\\d+)\\.(\\d+)-(.*)')
get_platform = get_build_platform

def compatible_platforms(provided, required):
    if provided is None or required is None or provided == required:
        return True
    reqMac = macosVersionString.match(required)
    if reqMac:
        provMac = macosVersionString.match(provided)
        if not provMac:
            provDarwin = darwinVersionString.match(provided)
            if provDarwin:
                dversion = int(provDarwin.group(1))
                macosversion = '%s.%s' % (reqMac.group(1), reqMac.group(2))
                if dversion == 7 and macosversion >= '10.3' or dversion == 8 and macosversion >= '10.4':
                    return True
            return False
        if provMac.group(1) != reqMac.group(1) or provMac.group(3) != reqMac.group(3):
            return False
        if int(provMac.group(2)) > int(reqMac.group(2)):
            return False
        return True
    return False


def run_script(dist_spec, script_name):
    ns = sys._getframe(1).f_globals
    name = ns['__name__']
    ns.clear()
    ns['__name__'] = name
    require(dist_spec)[0].run_script(script_name, ns)


run_main = run_script

def get_distribution(dist):
    if isinstance(dist, six.string_types):
        dist = Requirement.parse(dist)
    if isinstance(dist, Requirement):
        dist = get_provider(dist)
    if not isinstance(dist, Distribution):
        raise TypeError('Expected string, Requirement, or Distribution', dist)
    return dist


def load_entry_point(dist, group, name):
    return get_distribution(dist).load_entry_point(group, name)


def get_entry_map(dist, group = None):
    return get_distribution(dist).get_entry_map(group)


def get_entry_info(dist, group, name):
    return get_distribution(dist).get_entry_info(group, name)


class IMetadataProvider():

    def has_metadata(name):
        pass

    def get_metadata(name):
        pass

    def get_metadata_lines(name):
        pass

    def metadata_isdir(name):
        pass

    def metadata_listdir(name):
        pass

    def run_script(script_name, namespace):
        pass


class IResourceProvider(IMetadataProvider):

    def get_resource_filename(manager, resource_name):
        pass

    def get_resource_stream(manager, resource_name):
        pass

    def get_resource_string(manager, resource_name):
        pass

    def has_resource(resource_name):
        pass

    def resource_isdir(resource_name):
        pass

    def resource_listdir(resource_name):
        pass


class WorkingSet(object):

    def __init__(self, entries = None):
        self.entries = []
        self.entry_keys = {}
        self.by_key = {}
        self.callbacks = []
        if entries is None:
            entries = sys.path
        for entry in entries:
            self.add_entry(entry)

    @classmethod
    def _build_master(cls):
        ws = cls()
        try:
            from __main__ import __requires__
        except ImportError:
            return ws

        try:
            ws.require(__requires__)
        except VersionConflict:
            return cls._build_from_requirements(__requires__)

        return ws

    @classmethod
    def _build_from_requirements(cls, req_spec):
        ws = cls([])
        reqs = parse_requirements(req_spec)
        dists = ws.resolve(reqs, Environment())
        for dist in dists:
            ws.add(dist)

        for entry in sys.path:
            if entry not in ws.entries:
                ws.add_entry(entry)

        sys.path[:] = ws.entries
        return ws

    def add_entry(self, entry):
        self.entry_keys.setdefault(entry, [])
        self.entries.append(entry)
        for dist in find_distributions(entry, True):
            self.add(dist, entry, False)

    def __contains__(self, dist):
        return self.by_key.get(dist.key) == dist

    def find(self, req):
        dist = self.by_key.get(req.key)
        if dist is not None and dist not in req:
            raise VersionConflict(dist, req)
        return dist

    def iter_entry_points(self, group, name = None):
        for dist in self:
            entries = dist.get_entry_map(group)
            if name is None:
                for ep in entries.values():
                    yield ep

            elif name in entries:
                yield entries[name]

    def run_script(self, requires, script_name):
        ns = sys._getframe(1).f_globals
        name = ns['__name__']
        ns.clear()
        ns['__name__'] = name
        self.require(requires)[0].run_script(script_name, ns)

    def __iter__(self):
        seen = {}
        for item in self.entries:
            if item not in self.entry_keys:
                continue
            for key in self.entry_keys[item]:
                if key not in seen:
                    seen[key] = 1
                    yield self.by_key[key]

    def add(self, dist, entry = None, insert = True, replace = False):
        if insert:
            dist.insert_on(self.entries, entry, replace=replace)
        if entry is None:
            entry = dist.location
        keys = self.entry_keys.setdefault(entry, [])
        keys2 = self.entry_keys.setdefault(dist.location, [])
        if not replace and dist.key in self.by_key:
            return
        self.by_key[dist.key] = dist
        if dist.key not in keys:
            keys.append(dist.key)
        if dist.key not in keys2:
            keys2.append(dist.key)
        self._added_new(dist)

    def resolve(self, requirements, env = None, installer = None, replace_conflicting = False):
        requirements = list(requirements)[::-1]
        processed = {}
        best = {}
        to_activate = []
        req_extras = _ReqExtras()
        required_by = collections.defaultdict(set)
        while requirements:
            req = requirements.pop(0)
            if req in processed:
                continue
            if not req_extras.markers_pass(req):
                continue
            dist = best.get(req.key)
            if dist is None:
                dist = self.by_key.get(req.key)
                if dist is None or dist not in req and replace_conflicting:
                    ws = self
                    if env is None:
                        if dist is None:
                            env = Environment(self.entries)
                        else:
                            env = Environment([])
                            ws = WorkingSet([])
                    dist = best[req.key] = env.best_match(req, ws, installer)
                    if dist is None:
                        requirers = required_by.get(req, None)
                        raise DistributionNotFound(req, requirers)
                to_activate.append(dist)
            if dist not in req:
                dependent_req = required_by[req]
                raise VersionConflict(dist, req).with_context(dependent_req)
            new_requirements = dist.requires(req.extras)[::-1]
            requirements.extend(new_requirements)
            for new_requirement in new_requirements:
                required_by[new_requirement].add(req.project_name)
                req_extras[new_requirement] = req.extras

            processed[req] = True

        return to_activate

    def find_plugins(self, plugin_env, full_env = None, installer = None, fallback = True):
        plugin_projects = list(plugin_env)
        plugin_projects.sort()
        error_info = {}
        distributions = {}
        if full_env is None:
            env = Environment(self.entries)
            env += plugin_env
        else:
            env = full_env + plugin_env
        shadow_set = self.__class__([])
        list(map(shadow_set.add, self))
        for project_name in plugin_projects:
            for dist in plugin_env[project_name]:
                req = [dist.as_requirement()]
                try:
                    resolvees = shadow_set.resolve(req, env, installer)
                except ResolutionError as v:
                    error_info[dist] = v
                    if fallback:
                        continue
                    else:
                        break
                else:
                    list(map(shadow_set.add, resolvees))
                    distributions.update(dict.fromkeys(resolvees))
                    break

        distributions = list(distributions)
        distributions.sort()
        return (distributions, error_info)

    def require(self, *requirements):
        needed = self.resolve(parse_requirements(requirements))
        for dist in needed:
            self.add(dist)

        return needed

    def subscribe(self, callback):
        if callback in self.callbacks:
            return
        self.callbacks.append(callback)
        for dist in self:
            callback(dist)

    def _added_new(self, dist):
        for callback in self.callbacks:
            callback(dist)

    def __getstate__(self):
        return (self.entries[:],
         self.entry_keys.copy(),
         self.by_key.copy(),
         self.callbacks[:])

    def __setstate__(self, e_k_b_c):
        entries, keys, by_key, callbacks = e_k_b_c
        self.entries = entries[:]
        self.entry_keys = keys.copy()
        self.by_key = by_key.copy()
        self.callbacks = callbacks[:]


class _ReqExtras(dict):

    def markers_pass(self, req):
        extra_evals = (req.marker.evaluate({'extra': extra}) for extra in self.get(req, ()))
        return not req.marker or any(extra_evals) or req.marker.evaluate()


class Environment(object):

    def __init__(self, search_path = None, platform = get_supported_platform(), python = PY_MAJOR):
        self._distmap = {}
        self.platform = platform
        self.python = python
        self.scan(search_path)

    def can_add(self, dist):
        return (self.python is None or dist.py_version is None or dist.py_version == self.python) and compatible_platforms(dist.platform, self.platform)

    def remove(self, dist):
        self._distmap[dist.key].remove(dist)

    def scan(self, search_path = None):
        if search_path is None:
            search_path = sys.path
        for item in search_path:
            for dist in find_distributions(item):
                self.add(dist)

    def __getitem__(self, project_name):
        distribution_key = project_name.lower()
        return self._distmap.get(distribution_key, [])

    def add(self, dist):
        if self.can_add(dist) and dist.has_version():
            dists = self._distmap.setdefault(dist.key, [])
            if dist not in dists:
                dists.append(dist)
                dists.sort(key=operator.attrgetter('hashcmp'), reverse=True)

    def best_match(self, req, working_set, installer = None):
        dist = working_set.find(req)
        if dist is not None:
            return dist
        for dist in self[req.key]:
            if dist in req:
                return dist

        return self.obtain(req, installer)

    def obtain(self, requirement, installer = None):
        if installer is not None:
            return installer(requirement)

    def __iter__(self):
        for key in self._distmap.keys():
            if self[key]:
                yield key

    def __iadd__(self, other):
        if isinstance(other, Distribution):
            self.add(other)
        elif isinstance(other, Environment):
            for project in other:
                for dist in other[project]:
                    self.add(dist)

        else:
            raise TypeError("Can't add %r to environment" % (other,))
        return self

    def __add__(self, other):
        new = self.__class__([], platform=None, python=None)
        for env in (self, other):
            new += env

        return new


AvailableDistributions = Environment

class ExtractionError(RuntimeError):
    pass


class ResourceManager():
    extraction_path = None

    def __init__(self):
        self.cached_files = {}

    def resource_exists(self, package_or_requirement, resource_name):
        return get_provider(package_or_requirement).has_resource(resource_name)

    def resource_isdir(self, package_or_requirement, resource_name):
        return get_provider(package_or_requirement).resource_isdir(resource_name)

    def resource_filename(self, package_or_requirement, resource_name):
        return get_provider(package_or_requirement).get_resource_filename(self, resource_name)

    def resource_stream(self, package_or_requirement, resource_name):
        return get_provider(package_or_requirement).get_resource_stream(self, resource_name)

    def resource_string(self, package_or_requirement, resource_name):
        return get_provider(package_or_requirement).get_resource_string(self, resource_name)

    def resource_listdir(self, package_or_requirement, resource_name):
        return get_provider(package_or_requirement).resource_listdir(resource_name)

    def extraction_error(self):
        old_exc = sys.exc_info()[1]
        cache_path = self.extraction_path or get_default_cache()
        tmpl = textwrap.dedent("\n            Can't extract file(s) to egg cache\n\n            The following error occurred while trying to extract file(s) to the Python egg\n            cache:\n\n              {old_exc}\n\n            The Python egg cache directory is currently set to:\n\n              {cache_path}\n\n            Perhaps your account does not have write access to this directory?  You can\n            change the cache directory by setting the PYTHON_EGG_CACHE environment\n            variable to point to an accessible directory.\n            ").lstrip()
        err = ExtractionError(tmpl.format(**locals()))
        err.manager = self
        err.cache_path = cache_path
        err.original_error = old_exc
        raise err

    def get_cache_path(self, archive_name, names = ()):
        extract_path = self.extraction_path or get_default_cache()
        target_path = os.path.join(extract_path, (archive_name + '-tmp'), *names)
        try:
            _bypass_ensure_directory(target_path)
        except:
            self.extraction_error()

        self._warn_unsafe_extraction_path(extract_path)
        self.cached_files[target_path] = 1
        return target_path

    @staticmethod
    def _warn_unsafe_extraction_path(path):
        if os.name == 'nt' and not path.startswith(os.environ['windir']):
            return
        mode = os.stat(path).st_mode
        if mode & stat.S_IWOTH or mode & stat.S_IWGRP:
            msg = '%s is writable by group/others and vulnerable to attack when used with get_resource_filename. Consider a more secure location (set with .set_extraction_path or the PYTHON_EGG_CACHE environment variable).' % path
            warnings.warn(msg, UserWarning)

    def postprocess(self, tempname, filename):
        if os.name == 'posix':
            mode = (os.stat(tempname).st_mode | 365) & 4095
            os.chmod(tempname, mode)

    def set_extraction_path(self, path):
        if self.cached_files:
            raise ValueError("Can't change extraction path, files already extracted")
        self.extraction_path = path

    def cleanup_resources(self, force = False):
        pass


def get_default_cache():
    try:
        return os.environ['PYTHON_EGG_CACHE']
    except KeyError:
        pass

    if os.name != 'nt':
        return os.path.expanduser('~/.python-eggs')
    app_data = 'Application Data'
    app_homes = [(('APPDATA',), None),
     (('USERPROFILE',), app_data),
     (('HOMEDRIVE', 'HOMEPATH'), app_data),
     (('HOMEPATH',), app_data),
     (('HOME',), None),
     (('WINDIR',), app_data)]
    for keys, subdir in app_homes:
        dirname = ''
        for key in keys:
            if key in os.environ:
                dirname = os.path.join(dirname, os.environ[key])
            else:
                break
        else:
            if subdir:
                dirname = os.path.join(dirname, subdir)
            return os.path.join(dirname, 'Python-Eggs')

    else:
        raise RuntimeError('Please set the PYTHON_EGG_CACHE enviroment variable')


def safe_name(name):
    return re.sub('[^A-Za-z0-9.]+', '-', name)


def safe_version(version):
    try:
        return str(packaging.version.Version(version))
    except packaging.version.InvalidVersion:
        version = version.replace(' ', '.')
        return re.sub('[^A-Za-z0-9.]+', '-', version)


def safe_extra(extra):
    return re.sub('[^A-Za-z0-9.]+', '_', extra).lower()


def to_filename(name):
    return name.replace('-', '_')


def invalid_marker(text):
    try:
        evaluate_marker(text)
    except SyntaxError as e:
        e.filename = None
        e.lineno = None
        return e

    return False


def evaluate_marker(text, extra = None):
    try:
        marker = packaging.markers.Marker(text)
        return marker.evaluate()
    except packaging.markers.InvalidMarker as e:
        raise SyntaxError(e)


class NullProvider():
    egg_name = None
    egg_info = None
    loader = None

    def __init__(self, module):
        self.loader = getattr(module, '__loader__', None)
        self.module_path = os.path.dirname(getattr(module, '__file__', ''))

    def get_resource_filename(self, manager, resource_name):
        return self._fn(self.module_path, resource_name)

    def get_resource_stream(self, manager, resource_name):
        return io.BytesIO(self.get_resource_string(manager, resource_name))

    def get_resource_string(self, manager, resource_name):
        return self._get(self._fn(self.module_path, resource_name))

    def has_resource(self, resource_name):
        return self._has(self._fn(self.module_path, resource_name))

    def has_metadata(self, name):
        return self.egg_info and self._has(self._fn(self.egg_info, name))

    if sys.version_info <= (3,):

        def get_metadata(self, name):
            if not self.egg_info:
                return ''
            return self._get(self._fn(self.egg_info, name))

    else:

        def get_metadata(self, name):
            if not self.egg_info:
                return ''
            return self._get(self._fn(self.egg_info, name)).decode('utf-8')

    def get_metadata_lines(self, name):
        return yield_lines(self.get_metadata(name))

    def resource_isdir(self, resource_name):
        return self._isdir(self._fn(self.module_path, resource_name))

    def metadata_isdir(self, name):
        return self.egg_info and self._isdir(self._fn(self.egg_info, name))

    def resource_listdir(self, resource_name):
        return self._listdir(self._fn(self.module_path, resource_name))

    def metadata_listdir(self, name):
        if self.egg_info:
            return self._listdir(self._fn(self.egg_info, name))
        return []

    def run_script(self, script_name, namespace):
        script = 'scripts/' + script_name
        if not self.has_metadata(script):
            raise ResolutionError('No script named %r' % script_name)
        script_text = self.get_metadata(script).replace('\r\n', '\n')
        script_text = script_text.replace('\r', '\n')
        script_filename = self._fn(self.egg_info, script)
        namespace['__file__'] = script_filename
        if os.path.exists(script_filename):
            source = open(script_filename).read()
            code = compile(source, script_filename, 'exec')
            exec (code, namespace, namespace)
        else:
            from linecache import cache
            cache[script_filename] = (len(script_text),
             0,
             script_text.split('\n'),
             script_filename)
            script_code = compile(script_text, script_filename, 'exec')
            exec (script_code, namespace, namespace)

    def _has(self, path):
        raise NotImplementedError("Can't perform this operation for unregistered loader type")

    def _isdir(self, path):
        raise NotImplementedError("Can't perform this operation for unregistered loader type")

    def _listdir(self, path):
        raise NotImplementedError("Can't perform this operation for unregistered loader type")

    def _fn(self, base, resource_name):
        if resource_name:
            return os.path.join(base, *resource_name.split('/'))
        return base

    def _get(self, path):
        if hasattr(self.loader, 'get_data'):
            return self.loader.get_data(path)
        raise NotImplementedError("Can't perform this operation for loaders without 'get_data()'")


register_loader_type(object, NullProvider)

class EggProvider(NullProvider):

    def __init__(self, module):
        NullProvider.__init__(self, module)
        self._setup_prefix()

    def _setup_prefix(self):
        path = self.module_path
        old = None
        while path != old:
            if _is_unpacked_egg(path):
                self.egg_name = os.path.basename(path)
                self.egg_info = os.path.join(path, 'EGG-INFO')
                self.egg_root = path
                break
            old = path
            path, base = os.path.split(path)


class DefaultProvider(EggProvider):

    def _has(self, path):
        return os.path.exists(path)

    def _isdir(self, path):
        return os.path.isdir(path)

    def _listdir(self, path):
        return os.listdir(path)

    def get_resource_stream(self, manager, resource_name):
        return open(self._fn(self.module_path, resource_name), 'rb')

    def _get(self, path):
        with open(path, 'rb') as stream:
            return stream.read()

    @classmethod
    def _register(cls):
        loader_cls = getattr(importlib_machinery, 'SourceFileLoader', type(None))
        register_loader_type(loader_cls, cls)


DefaultProvider._register()

class EmptyProvider(NullProvider):
    _isdir = _has = lambda self, path: False
    _get = lambda self, path: ''
    _listdir = lambda self, path: []
    module_path = None

    def __init__(self):
        pass


empty_provider = EmptyProvider()

class ZipManifests(dict):

    @classmethod
    def build(cls, path):
        with ContextualZipFile(path) as zfile:
            items = ((name.replace('/', os.sep), zfile.getinfo(name)) for name in zfile.namelist())
            return dict(items)

    load = build


class MemoizedZipManifests(ZipManifests):
    manifest_mod = collections.namedtuple('manifest_mod', 'manifest mtime')

    def load(self, path):
        path = os.path.normpath(path)
        mtime = os.stat(path).st_mtime
        if path not in self or self[path].mtime != mtime:
            manifest = self.build(path)
            self[path] = self.manifest_mod(manifest, mtime)
        return self[path].manifest


class ContextualZipFile(zipfile.ZipFile):

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def __new__(cls, *args, **kwargs):
        if hasattr(zipfile.ZipFile, '__exit__'):
            return zipfile.ZipFile(*args, **kwargs)
        return super(ContextualZipFile, cls).__new__(cls)


class ZipProvider(EggProvider):
    eagers = None
    _zip_manifests = MemoizedZipManifests()

    def __init__(self, module):
        EggProvider.__init__(self, module)
        self.zip_pre = self.loader.archive + os.sep

    def _zipinfo_name(self, fspath):
        if fspath.startswith(self.zip_pre):
            return fspath[len(self.zip_pre):]
        raise AssertionError('%s is not a subpath of %s' % (fspath, self.zip_pre))

    def _parts(self, zip_path):
        fspath = self.zip_pre + zip_path
        if fspath.startswith(self.egg_root + os.sep):
            return fspath[len(self.egg_root) + 1:].split(os.sep)
        raise AssertionError('%s is not a subpath of %s' % (fspath, self.egg_root))

    @property
    def zipinfo(self):
        return self._zip_manifests.load(self.loader.archive)

    def get_resource_filename(self, manager, resource_name):
        if not self.egg_name:
            raise NotImplementedError('resource_filename() only supported for .egg, not .zip')
        zip_path = self._resource_to_zip(resource_name)
        eagers = self._get_eager_resources()
        if '/'.join(self._parts(zip_path)) in eagers:
            for name in eagers:
                self._extract_resource(manager, self._eager_to_zip(name))

        return self._extract_resource(manager, zip_path)

    @staticmethod
    def _get_date_and_size(zip_stat):
        size = zip_stat.file_size
        date_time = zip_stat.date_time + (0, 0, -1)
        timestamp = time.mktime(date_time)
        return (timestamp, size)

    def _extract_resource(self, manager, zip_path):
        if zip_path in self._index():
            for name in self._index()[zip_path]:
                last = self._extract_resource(manager, os.path.join(zip_path, name))

            return os.path.dirname(last)
        timestamp, size = self._get_date_and_size(self.zipinfo[zip_path])
        if not WRITE_SUPPORT:
            raise IOError('"os.rename" and "os.unlink" are not supported on this platform')
        try:
            real_path = manager.get_cache_path(self.egg_name, self._parts(zip_path))
            if self._is_current(real_path, zip_path):
                return real_path
            outf, tmpnam = _mkstemp('.$extract', dir=os.path.dirname(real_path))
            os.write(outf, self.loader.get_data(zip_path))
            os.close(outf)
            utime(tmpnam, (timestamp, timestamp))
            manager.postprocess(tmpnam, real_path)
            try:
                rename(tmpnam, real_path)
            except os.error:
                if os.path.isfile(real_path):
                    if self._is_current(real_path, zip_path):
                        return real_path
                    if os.name == 'nt':
                        unlink(real_path)
                        rename(tmpnam, real_path)
                        return real_path
                raise

        except os.error:
            manager.extraction_error()

        return real_path

    def _is_current(self, file_path, zip_path):
        timestamp, size = self._get_date_and_size(self.zipinfo[zip_path])
        if not os.path.isfile(file_path):
            return False
        stat = os.stat(file_path)
        if stat.st_size != size or stat.st_mtime != timestamp:
            return False
        zip_contents = self.loader.get_data(zip_path)
        with open(file_path, 'rb') as f:
            file_contents = f.read()
        return zip_contents == file_contents

    def _get_eager_resources(self):
        if self.eagers is None:
            eagers = []
            for name in ('native_libs.txt', 'eager_resources.txt'):
                if self.has_metadata(name):
                    eagers.extend(self.get_metadata_lines(name))

            self.eagers = eagers
        return self.eagers

    def _index(self):
        try:
            return self._dirindex
        except AttributeError:
            ind = {}
            for path in self.zipinfo:
                parts = path.split(os.sep)
                while parts:
                    parent = os.sep.join(parts[:-1])
                    if parent in ind:
                        ind[parent].append(parts[-1])
                        break
                    else:
                        ind[parent] = [parts.pop()]

            self._dirindex = ind
            return ind

    def _has(self, fspath):
        zip_path = self._zipinfo_name(fspath)
        return zip_path in self.zipinfo or zip_path in self._index()

    def _isdir(self, fspath):
        return self._zipinfo_name(fspath) in self._index()

    def _listdir(self, fspath):
        return list(self._index().get(self._zipinfo_name(fspath), ()))

    def _eager_to_zip(self, resource_name):
        return self._zipinfo_name(self._fn(self.egg_root, resource_name))

    def _resource_to_zip(self, resource_name):
        return self._zipinfo_name(self._fn(self.module_path, resource_name))


register_loader_type(zipimport.zipimporter, ZipProvider)

class FileMetadata(EmptyProvider):

    def __init__(self, path):
        self.path = path

    def has_metadata(self, name):
        return name == 'PKG-INFO' and os.path.isfile(self.path)

    def get_metadata(self, name):
        if name == 'PKG-INFO':
            with io.open(self.path, encoding='utf-8') as f:
                try:
                    metadata = f.read()
                except UnicodeDecodeError as exc:
                    tmpl = ' in {self.path}'
                    exc.reason += tmpl.format(self=self)
                    raise

            return metadata
        raise KeyError('No metadata except PKG-INFO is available')

    def get_metadata_lines(self, name):
        return yield_lines(self.get_metadata(name))


class PathMetadata(DefaultProvider):

    def __init__(self, path, egg_info):
        self.module_path = path
        self.egg_info = egg_info


class EggMetadata(ZipProvider):

    def __init__(self, importer):
        self.zip_pre = importer.archive + os.sep
        self.loader = importer
        if importer.prefix:
            self.module_path = os.path.join(importer.archive, importer.prefix)
        else:
            self.module_path = importer.archive
        self._setup_prefix()


_declare_state('dict', _distribution_finders={})

def register_finder(importer_type, distribution_finder):
    _distribution_finders[importer_type] = distribution_finder


def find_distributions(path_item, only = False):
    importer = get_importer(path_item)
    finder = _find_adapter(_distribution_finders, importer)
    return finder(importer, path_item, only)


def find_eggs_in_zip(importer, path_item, only = False):
    if importer.archive.endswith('.whl'):
        return
    metadata = EggMetadata(importer)
    if metadata.has_metadata('PKG-INFO'):
        yield Distribution.from_filename(path_item, metadata=metadata)
    if only:
        return
    for subitem in metadata.resource_listdir('/'):
        if _is_unpacked_egg(subitem):
            subpath = os.path.join(path_item, subitem)
            for dist in find_eggs_in_zip(zipimport.zipimporter(subpath), subpath):
                yield dist


register_finder(zipimport.zipimporter, find_eggs_in_zip)

def find_nothing(importer, path_item, only = False):
    return ()


register_finder(object, find_nothing)

def find_on_path(importer, path_item, only = False):
    path_item = _normalize_cached(path_item)
    if os.path.isdir(path_item) and os.access(path_item, os.R_OK):
        if _is_unpacked_egg(path_item):
            yield Distribution.from_filename(path_item, metadata=PathMetadata(path_item, os.path.join(path_item, 'EGG-INFO')))
        else:
            for entry in os.listdir(path_item):
                lower = entry.lower()
                if lower.endswith('.egg-info') or lower.endswith('.dist-info'):
                    fullpath = os.path.join(path_item, entry)
                    if os.path.isdir(fullpath):
                        metadata = PathMetadata(path_item, fullpath)
                    else:
                        metadata = FileMetadata(fullpath)
                    yield Distribution.from_location(path_item, entry, metadata, precedence=DEVELOP_DIST)
                elif not only and _is_unpacked_egg(entry):
                    dists = find_distributions(os.path.join(path_item, entry))
                    for dist in dists:
                        yield dist

                elif not only and lower.endswith('.egg-link'):
                    with open(os.path.join(path_item, entry)) as entry_file:
                        entry_lines = entry_file.readlines()
                    for line in entry_lines:
                        if not line.strip():
                            continue
                        path = os.path.join(path_item, line.rstrip())
                        dists = find_distributions(path)
                        for item in dists:
                            yield item

                        break


register_finder(pkgutil.ImpImporter, find_on_path)
if hasattr(importlib_machinery, 'FileFinder'):
    register_finder(importlib_machinery.FileFinder, find_on_path)
_declare_state('dict', _namespace_handlers={})
_declare_state('dict', _namespace_packages={})

def register_namespace_handler(importer_type, namespace_handler):
    _namespace_handlers[importer_type] = namespace_handler


def _handle_ns(packageName, path_item):
    importer = get_importer(path_item)
    if importer is None:
        return
    loader = importer.find_module(packageName)
    if loader is None:
        return
    module = sys.modules.get(packageName)
    if module is None:
        module = sys.modules[packageName] = types.ModuleType(packageName)
        module.__path__ = []
        _set_parent_ns(packageName)
    elif not hasattr(module, '__path__'):
        raise TypeError('Not a package:', packageName)
    handler = _find_adapter(_namespace_handlers, importer)
    subpath = handler(importer, path_item, packageName, module)
    if subpath is not None:
        path = module.__path__
        path.append(subpath)
        loader.load_module(packageName)
        _rebuild_mod_path(path, packageName, module)
    return subpath


def _rebuild_mod_path(orig_path, package_name, module):
    sys_path = [ _normalize_cached(p) for p in sys.path ]

    def position_in_sys_path(path):
        path_parts = path.split(os.sep)
        module_parts = package_name.count('.') + 1
        parts = path_parts[:-module_parts]
        return sys_path.index(_normalize_cached(os.sep.join(parts)))

    orig_path.sort(key=position_in_sys_path)
    module.__path__[:] = [ _normalize_cached(p) for p in orig_path ]


def declare_namespace(packageName):
    _imp.acquire_lock()
    try:
        if packageName in _namespace_packages:
            return
        path, parent = sys.path, None
        if '.' in packageName:
            parent = '.'.join(packageName.split('.')[:-1])
            declare_namespace(parent)
            if parent not in _namespace_packages:
                __import__(parent)
            try:
                path = sys.modules[parent].__path__
            except AttributeError:
                raise TypeError('Not a package:', parent)

        _namespace_packages.setdefault(parent, []).append(packageName)
        _namespace_packages.setdefault(packageName, [])
        for path_item in path:
            _handle_ns(packageName, path_item)

    finally:
        _imp.release_lock()


def fixup_namespace_packages(path_item, parent = None):
    _imp.acquire_lock()
    try:
        for package in _namespace_packages.get(parent, ()):
            subpath = _handle_ns(package, path_item)
            if subpath:
                fixup_namespace_packages(subpath, package)

    finally:
        _imp.release_lock()


def file_ns_handler(importer, path_item, packageName, module):
    subpath = os.path.join(path_item, packageName.split('.')[-1])
    normalized = _normalize_cached(subpath)
    for item in module.__path__:
        if _normalize_cached(item) == normalized:
            break
    else:
        return subpath


register_namespace_handler(pkgutil.ImpImporter, file_ns_handler)
register_namespace_handler(zipimport.zipimporter, file_ns_handler)
if hasattr(importlib_machinery, 'FileFinder'):
    register_namespace_handler(importlib_machinery.FileFinder, file_ns_handler)

def null_ns_handler(importer, path_item, packageName, module):
    return None


register_namespace_handler(object, null_ns_handler)

def normalize_path(filename):
    return os.path.normcase(os.path.realpath(filename))


def _normalize_cached(filename, _cache = {}):
    try:
        return _cache[filename]
    except KeyError:
        _cache[filename] = result = normalize_path(filename)
        return result


def _is_unpacked_egg(path):
    return path.lower().endswith('.egg')


def _set_parent_ns(packageName):
    parts = packageName.split('.')
    name = parts.pop()
    if parts:
        parent = '.'.join(parts)
        setattr(sys.modules[parent], name, sys.modules[packageName])


def yield_lines(strs):
    if isinstance(strs, six.string_types):
        for s in strs.splitlines():
            s = s.strip()
            if s and not s.startswith('#'):
                yield s

    else:
        for ss in strs:
            for s in yield_lines(ss):
                yield s


MODULE = re.compile('\\w+(\\.\\w+)*$').match
EGG_NAME = re.compile('\n    (?P<name>[^-]+) (\n        -(?P<ver>[^-]+) (\n            -py(?P<pyver>[^-]+) (\n                -(?P<plat>.+)\n            )?\n        )?\n    )?\n    ', re.VERBOSE | re.IGNORECASE).match

class EntryPoint(object):

    def __init__(self, name, module_name, attrs = (), extras = (), dist = None):
        if not MODULE(module_name):
            raise ValueError('Invalid module name', module_name)
        self.name = name
        self.module_name = module_name
        self.attrs = tuple(attrs)
        self.extras = Requirement.parse('x[%s]' % ','.join(extras)).extras
        self.dist = dist

    def __str__(self):
        s = '%s = %s' % (self.name, self.module_name)
        if self.attrs:
            s += ':' + '.'.join(self.attrs)
        if self.extras:
            s += ' [%s]' % ','.join(self.extras)
        return s

    def __repr__(self):
        return 'EntryPoint.parse(%r)' % str(self)

    def load(self, require = True, *args, **kwargs):
        if not require or args or kwargs:
            warnings.warn('Parameters to load are deprecated.  Call .resolve and .require separately.', DeprecationWarning, stacklevel=2)
        if require:
            self.require(*args, **kwargs)
        return self.resolve()

    def resolve(self):
        module = __import__(self.module_name, fromlist=['__name__'], level=0)
        try:
            return functools.reduce(getattr, self.attrs, module)
        except AttributeError as exc:
            raise ImportError(str(exc))

    def require(self, env = None, installer = None):
        if self.extras and not self.dist:
            raise UnknownExtra("Can't require() without a distribution", self)
        reqs = self.dist.requires(self.extras)
        items = working_set.resolve(reqs, env, installer)
        list(map(working_set.add, items))

    pattern = re.compile('\\s*(?P<name>.+?)\\s*=\\s*(?P<module>[\\w.]+)\\s*(:\\s*(?P<attr>[\\w.]+))?\\s*(?P<extras>\\[.*\\])?\\s*$')

    @classmethod
    def parse(cls, src, dist = None):
        m = cls.pattern.match(src)
        if not m:
            msg = "EntryPoint must be in 'name=module:attrs [extras]' format"
            raise ValueError(msg, src)
        res = m.groupdict()
        extras = cls._parse_extras(res['extras'])
        attrs = res['attr'].split('.') if res['attr'] else ()
        return cls(res['name'], res['module'], attrs, extras, dist)

    @classmethod
    def _parse_extras(cls, extras_spec):
        if not extras_spec:
            return ()
        req = Requirement.parse('x' + extras_spec)
        if req.specs:
            raise ValueError()
        return req.extras

    @classmethod
    def parse_group(cls, group, lines, dist = None):
        if not MODULE(group):
            raise ValueError('Invalid group name', group)
        this = {}
        for line in yield_lines(lines):
            ep = cls.parse(line, dist)
            if ep.name in this:
                raise ValueError('Duplicate entry point', group, ep.name)
            this[ep.name] = ep

        return this

    @classmethod
    def parse_map(cls, data, dist = None):
        if isinstance(data, dict):
            data = data.items()
        else:
            data = split_sections(data)
        maps = {}
        for group, lines in data:
            if group is None:
                if not lines:
                    continue
                raise ValueError('Entry points must be listed in groups')
            group = group.strip()
            if group in maps:
                raise ValueError('Duplicate group name', group)
            maps[group] = cls.parse_group(group, lines, dist)

        return maps


def _remove_md5_fragment(location):
    if not location:
        return ''
    parsed = urllib.parse.urlparse(location)
    if parsed[-1].startswith('md5='):
        return urllib.parse.urlunparse(parsed[:-1] + ('',))
    return location


def _version_from_file(lines):
    is_version_line = lambda line: line.lower().startswith('version:')
    version_lines = filter(is_version_line, lines)
    line = next(iter(version_lines), '')
    _, _, value = line.partition(':')
    return safe_version(value.strip()) or None


class Distribution(object):
    PKG_INFO = 'PKG-INFO'

    def __init__(self, location = None, metadata = None, project_name = None, version = None, py_version = PY_MAJOR, platform = None, precedence = EGG_DIST):
        self.project_name = safe_name(project_name or 'Unknown')
        if version is not None:
            self._version = safe_version(version)
        self.py_version = py_version
        self.platform = platform
        self.location = location
        self.precedence = precedence
        self._provider = metadata or empty_provider

    @classmethod
    def from_location(cls, location, basename, metadata = None, **kw):
        project_name, version, py_version, platform = [None] * 4
        basename, ext = os.path.splitext(basename)
        if ext.lower() in _distributionImpl:
            cls = _distributionImpl[ext.lower()]
            match = EGG_NAME(basename)
            if match:
                project_name, version, py_version, platform = match.group('name', 'ver', 'pyver', 'plat')
        return cls(location, metadata, project_name=project_name, version=version, py_version=py_version, platform=platform, **kw)._reload_version()

    def _reload_version(self):
        return self

    @property
    def hashcmp(self):
        return (self.parsed_version,
         self.precedence,
         self.key,
         _remove_md5_fragment(self.location),
         self.py_version or '',
         self.platform or '')

    def __hash__(self):
        return hash(self.hashcmp)

    def __lt__(self, other):
        return self.hashcmp < other.hashcmp

    def __le__(self, other):
        return self.hashcmp <= other.hashcmp

    def __gt__(self, other):
        return self.hashcmp > other.hashcmp

    def __ge__(self, other):
        return self.hashcmp >= other.hashcmp

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.hashcmp == other.hashcmp

    def __ne__(self, other):
        return not self == other

    @property
    def key(self):
        try:
            return self._key
        except AttributeError:
            self._key = key = self.project_name.lower()
            return key

    @property
    def parsed_version(self):
        if not hasattr(self, '_parsed_version'):
            self._parsed_version = parse_version(self.version)
        return self._parsed_version

    def _warn_legacy_version(self):
        LV = packaging.version.LegacyVersion
        is_legacy = isinstance(self._parsed_version, LV)
        if not is_legacy:
            return
        if not self.version:
            return
        tmpl = textwrap.dedent("\n            '{project_name} ({version})' is being parsed as a legacy,\n            non PEP 440,\n            version. You may find odd behavior and sort order.\n            In particular it will be sorted as less than 0.0. It\n            is recommended to migrate to PEP 440 compatible\n            versions.\n            ").strip().replace('\n', ' ')
        warnings.warn(tmpl.format(**vars(self)), PEP440Warning)

    @property
    def version(self):
        try:
            return self._version
        except AttributeError:
            version = _version_from_file(self._get_metadata(self.PKG_INFO))
            if version is None:
                tmpl = "Missing 'Version:' header and/or %s file"
                raise ValueError(tmpl % self.PKG_INFO, self)
            return version

    @property
    def _dep_map(self):
        try:
            return self.__dep_map
        except AttributeError:
            dm = self.__dep_map = {None: []}
            for name in ('requires.txt', 'depends.txt'):
                for extra, reqs in split_sections(self._get_metadata(name)):
                    if extra:
                        if ':' in extra:
                            extra, marker = extra.split(':', 1)
                            if invalid_marker(marker):
                                reqs = []
                            elif not evaluate_marker(marker):
                                reqs = []
                        extra = safe_extra(extra) or None
                    dm.setdefault(extra, []).extend(parse_requirements(reqs))

            return dm

    def requires(self, extras = ()):
        dm = self._dep_map
        deps = []
        deps.extend(dm.get(None, ()))
        for ext in extras:
            try:
                deps.extend(dm[safe_extra(ext)])
            except KeyError:
                raise UnknownExtra('%s has no such extra feature %r' % (self, ext))

        return deps

    def _get_metadata(self, name):
        if self.has_metadata(name):
            for line in self.get_metadata_lines(name):
                yield line

    def activate(self, path = None):
        if path is None:
            path = sys.path
        self.insert_on(path, replace=True)
        if path is sys.path:
            fixup_namespace_packages(self.location)
            for pkg in self._get_metadata('namespace_packages.txt'):
                if pkg in sys.modules:
                    declare_namespace(pkg)

    def egg_name(self):
        filename = '%s-%s-py%s' % (to_filename(self.project_name), to_filename(self.version), self.py_version or PY_MAJOR)
        if self.platform:
            filename += '-' + self.platform
        return filename

    def __repr__(self):
        if self.location:
            return '%s (%s)' % (self, self.location)
        else:
            return str(self)

    def __str__(self):
        try:
            version = getattr(self, 'version', None)
        except ValueError:
            version = None

        version = version or '[unknown version]'
        return '%s %s' % (self.project_name, version)

    def __getattr__(self, attr):
        if attr.startswith('_'):
            raise AttributeError(attr)
        return getattr(self._provider, attr)

    @classmethod
    def from_filename(cls, filename, metadata = None, **kw):
        return cls.from_location(_normalize_cached(filename), os.path.basename(filename), metadata, **kw)

    def as_requirement(self):
        if isinstance(self.parsed_version, packaging.version.Version):
            spec = '%s==%s' % (self.project_name, self.parsed_version)
        else:
            spec = '%s===%s' % (self.project_name, self.parsed_version)
        return Requirement.parse(spec)

    def load_entry_point(self, group, name):
        ep = self.get_entry_info(group, name)
        if ep is None:
            raise ImportError('Entry point %r not found' % ((group, name),))
        return ep.load()

    def get_entry_map(self, group = None):
        try:
            ep_map = self._ep_map
        except AttributeError:
            ep_map = self._ep_map = EntryPoint.parse_map(self._get_metadata('entry_points.txt'), self)

        if group is not None:
            return ep_map.get(group, {})
        return ep_map

    def get_entry_info(self, group, name):
        return self.get_entry_map(group).get(name)

    def insert_on(self, path, loc = None, replace = False):
        loc = loc or self.location
        if not loc:
            return
        nloc = _normalize_cached(loc)
        bdir = os.path.dirname(nloc)
        npath = [ p and _normalize_cached(p) or p for p in path ]
        for p, item in enumerate(npath):
            if item == nloc:
                break
            elif item == bdir and self.precedence == EGG_DIST:
                if path is sys.path:
                    self.check_version_conflict()
                path.insert(p, loc)
                npath.insert(p, nloc)
                break
        else:
            if path is sys.path:
                self.check_version_conflict()
            if replace:
                path.insert(0, loc)
            else:
                path.append(loc)
            return

        while True:
            try:
                np = npath.index(nloc, p + 1)
            except ValueError:
                break
            else:
                del npath[np]
                del path[np]
                p = np

    def check_version_conflict(self):
        if self.key == 'setuptools':
            return
        nsp = dict.fromkeys(self._get_metadata('namespace_packages.txt'))
        loc = normalize_path(self.location)
        for modname in self._get_metadata('top_level.txt'):
            if modname not in sys.modules or modname in nsp or modname in _namespace_packages:
                continue
            if modname in ('pkg_resources', 'setuptools', 'site'):
                continue
            fn = getattr(sys.modules[modname], '__file__', None)
            if fn and (normalize_path(fn).startswith(loc) or fn.startswith(self.location)):
                continue
            issue_warning('Module %s was already imported from %s, but %s is being added to sys.path' % (modname, fn, self.location))

    def has_version(self):
        try:
            self.version
        except ValueError:
            issue_warning('Unbuilt egg for ' + repr(self))
            return False

        return True

    def clone(self, **kw):
        names = 'project_name version py_version platform location precedence'
        for attr in names.split():
            kw.setdefault(attr, getattr(self, attr, None))

        kw.setdefault('metadata', self._provider)
        return self.__class__(**kw)

    @property
    def extras(self):
        return [ dep for dep in self._dep_map if dep ]


class EggInfoDistribution(Distribution):

    def _reload_version(self):
        md_version = _version_from_file(self._get_metadata(self.PKG_INFO))
        if md_version:
            self._version = md_version
        return self


class DistInfoDistribution(Distribution):
    PKG_INFO = 'METADATA'
    EQEQ = re.compile('([\\(,])\\s*(\\d.*?)\\s*([,\\)])')

    @property
    def _parsed_pkg_info(self):
        try:
            return self._pkg_info
        except AttributeError:
            metadata = self.get_metadata(self.PKG_INFO)
            self._pkg_info = email.parser.Parser().parsestr(metadata)
            return self._pkg_info

    @property
    def _dep_map(self):
        try:
            return self.__dep_map
        except AttributeError:
            self.__dep_map = self._compute_dependencies()
            return self.__dep_map

    def _compute_dependencies(self):
        dm = self.__dep_map = {None: []}
        reqs = []
        for req in self._parsed_pkg_info.get_all('Requires-Dist') or []:
            reqs.extend(parse_requirements(req))

        def reqs_for_extra(extra):
            for req in reqs:
                if not req.marker or req.marker.evaluate({'extra': extra}):
                    yield req

        common = frozenset(reqs_for_extra(None))
        dm[None].extend(common)
        for extra in self._parsed_pkg_info.get_all('Provides-Extra') or []:
            extra = safe_extra(extra.strip())
            dm[extra] = list(frozenset(reqs_for_extra(extra)) - common)

        return dm


_distributionImpl = {'.egg': Distribution,
 '.egg-info': EggInfoDistribution,
 '.dist-info': DistInfoDistribution}

def issue_warning(*args, **kw):
    level = 1
    g = globals()
    try:
        while sys._getframe(level).f_globals is g:
            level += 1

    except ValueError:
        pass

    warnings.warn(stacklevel=(level + 1), *args, **kw)


class RequirementParseError(ValueError):

    def __str__(self):
        return ' '.join(self.args)


def parse_requirements(strs):
    lines = iter(yield_lines(strs))
    for line in lines:
        if ' #' in line:
            line = line[:line.find(' #')]
        if line.endswith('\\'):
            line = line[:-2].strip()
            line += next(lines)
        yield Requirement(line)


class Requirement(packaging.requirements.Requirement):

    def __init__(self, requirement_string):
        try:
            super(Requirement, self).__init__(requirement_string)
        except packaging.requirements.InvalidRequirement as e:
            raise RequirementParseError(str(e))

        self.unsafe_name = self.name
        project_name = safe_name(self.name)
        self.project_name, self.key = project_name, project_name.lower()
        self.specs = [ (spec.operator, spec.version) for spec in self.specifier ]
        self.extras = tuple(map(safe_extra, self.extras))
        self.hashCmp = (self.key,
         self.specifier,
         frozenset(self.extras),
         str(self.marker) if self.marker else None)
        self.__hash = hash(self.hashCmp)

    def __eq__(self, other):
        return isinstance(other, Requirement) and self.hashCmp == other.hashCmp

    def __ne__(self, other):
        return not self == other

    def __contains__(self, item):
        if isinstance(item, Distribution):
            if item.key != self.key:
                return False
            item = item.version
        return self.specifier.contains(item, prereleases=True)

    def __hash__(self):
        return self.__hash

    def __repr__(self):
        return 'Requirement.parse(%r)' % str(self)

    @staticmethod
    def parse(s):
        req, = parse_requirements(s)
        return req


def _get_mro(cls):
    if not isinstance(cls, type):

        class cls(cls, object):
            pass

        return cls.__mro__[1:]
    return cls.__mro__


def _find_adapter(registry, ob):
    for t in _get_mro(getattr(ob, '__class__', type(ob))):
        if t in registry:
            return registry[t]


def ensure_directory(path):
    dirname = os.path.dirname(path)
    if not os.path.isdir(dirname):
        os.makedirs(dirname)


def _bypass_ensure_directory(path):
    if not WRITE_SUPPORT:
        raise IOError('"os.mkdir" not supported on this platform.')
    dirname, filename = split(path)
    if dirname and filename and not isdir(dirname):
        _bypass_ensure_directory(dirname)
        mkdir(dirname, 493)


def split_sections(s):
    section = None
    content = []
    for line in yield_lines(s):
        if line.startswith('['):
            if line.endswith(']'):
                if section or content:
                    yield (section, content)
                section = line[1:-1].strip()
                content = []
            else:
                raise ValueError('Invalid section heading', line)
        else:
            content.append(line)

    yield (section, content)


def _mkstemp(*args, **kw):
    old_open = os.open
    try:
        os.open = os_open
        return tempfile.mkstemp(*args, **kw)
    finally:
        os.open = old_open


warnings.filterwarnings('ignore', category=PEP440Warning, append=True)

def _call_aside(f, *args, **kwargs):
    f(*args, **kwargs)
    return f


@_call_aside
def _initialize(g = globals()):
    manager = ResourceManager()
    g['_manager'] = manager
    for name in dir(manager):
        if not name.startswith('_'):
            g[name] = getattr(manager, name)


@_call_aside
def _initialize_master_working_set():
    working_set = WorkingSet._build_master()
    _declare_state('object', working_set=working_set)
    require = working_set.require
    iter_entry_points = working_set.iter_entry_points
    add_activation_listener = working_set.subscribe
    run_script = working_set.run_script
    run_main = run_script
    add_activation_listener(lambda dist: dist.activate())
    working_set.entries = []
    list(map(working_set.add_entry, sys.path))
    globals().update(locals())
