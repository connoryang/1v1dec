#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\stdlib\coverage\control.py
import atexit, os, random, socket, sys
from coverage.annotate import AnnotateReporter
from coverage.backward import string_class, iitems, sorted
from coverage.codeunit import code_unit_factory, CodeUnit
from coverage.collector import Collector
from coverage.config import CoverageConfig
from coverage.data import CoverageData
from coverage.debug import DebugControl
from coverage.files import FileLocator, TreeMatcher, FnmatchMatcher
from coverage.files import PathAliases, find_python_files, prep_patterns
from coverage.html import HtmlReporter
from coverage.misc import CoverageException, bool_or_none, join_regex
from coverage.misc import file_be_gone
from coverage.results import Analysis, Numbers
from coverage.summary import SummaryReporter
from coverage.xmlreport import XmlReporter
try:
    import _structseq
except ImportError:
    _structseq = None

class coverage(object):

    def __init__(self, data_file = None, data_suffix = None, cover_pylib = None, auto_data = False, timid = None, branch = None, config_file = True, source = None, omit = None, include = None, debug = None, debug_file = None):
        from coverage import __version__
        self._warnings = []
        self.config = CoverageConfig()
        if config_file:
            if config_file is True:
                config_file = '.coveragerc'
            try:
                self.config.from_file(config_file)
            except ValueError:
                _, err, _ = sys.exc_info()
                raise CoverageException("Couldn't read config file %s: %s" % (config_file, err))

        self.config.from_environment('COVERAGE_OPTIONS')
        env_data_file = os.environ.get('COVERAGE_FILE')
        if env_data_file:
            self.config.data_file = env_data_file
        self.config.from_args(data_file=data_file, cover_pylib=cover_pylib, timid=timid, branch=branch, parallel=bool_or_none(data_suffix), source=source, omit=omit, include=include, debug=debug)
        self.debug = DebugControl(self.config.debug, debug_file or sys.stderr)
        self.auto_data = auto_data
        self._exclude_re = {}
        self._exclude_regex_stale()
        self.file_locator = FileLocator()
        self.source = []
        self.source_pkgs = []
        for src in self.config.source or []:
            if os.path.exists(src):
                self.source.append(self.file_locator.canonical_filename(src))
            else:
                self.source_pkgs.append(src)

        self.omit = prep_patterns(self.config.omit)
        self.include = prep_patterns(self.config.include)
        self.collector = Collector(self._should_trace, timid=self.config.timid, branch=self.config.branch, warn=self._warn)
        if data_suffix or self.config.parallel:
            if not isinstance(data_suffix, string_class):
                data_suffix = True
        else:
            data_suffix = None
        self.data_suffix = None
        self.run_suffix = data_suffix
        self.data = CoverageData(basename=self.config.data_file, collector='coverage v%s' % __version__, debug=self.debug)
        self.pylib_dirs = []
        if not self.config.cover_pylib:
            for m in (atexit,
             os,
             random,
             socket,
             _structseq):
                if m is not None and hasattr(m, '__file__'):
                    m_dir = self._canonical_dir(m)
                    if m_dir not in self.pylib_dirs:
                        self.pylib_dirs.append(m_dir)

        self.cover_dir = self._canonical_dir(__file__)
        self.source_match = None
        self.pylib_match = self.cover_match = None
        self.include_match = self.omit_match = None
        Numbers.set_precision(self.config.precision)
        self._warn_no_data = True
        self._warn_unimported_source = True
        self._started = False
        self._measured = False
        atexit.register(self._atexit)

    def _canonical_dir(self, morf):
        return os.path.split(CodeUnit(morf, self.file_locator).filename)[0]

    def _source_for_file(self, filename):
        if not filename.endswith('.py'):
            if filename[-4:-1] == '.py':
                filename = filename[:-1]
            elif filename.endswith('$py.class'):
                filename = filename[:-9] + '.py'
        return filename

    def _should_trace_with_reason(self, filename, frame):
        if not filename:
            return (None, "empty string isn't a filename")
        if filename.startswith('<'):
            return (None, 'not a real filename')
        self._check_for_packages()
        dunder_file = frame.f_globals.get('__file__')
        if dunder_file:
            filename = self._source_for_file(dunder_file)
        if filename.endswith('$py.class'):
            filename = filename[:-9] + '.py'
        canonical = self.file_locator.canonical_filename(filename)
        if self.source_match:
            if not self.source_match.match(canonical):
                return (None, 'falls outside the --source trees')
        elif self.include_match:
            if not self.include_match.match(canonical):
                return (None, 'falls outside the --include trees')
        else:
            if self.pylib_match and self.pylib_match.match(canonical):
                return (None, 'is in the stdlib')
            if self.cover_match and self.cover_match.match(canonical):
                return (None, 'is part of coverage.py')
        if self.omit_match and self.omit_match.match(canonical):
            return (None, 'is inside an --omit pattern')
        return (canonical, 'because we love you')

    def _should_trace(self, filename, frame):
        canonical, reason = self._should_trace_with_reason(filename, frame)
        if self.debug.should('trace'):
            if not canonical:
                msg = 'Not tracing %r: %s' % (filename, reason)
            else:
                msg = 'Tracing %r' % (filename,)
            self.debug.write(msg)
        return canonical

    def _warn(self, msg):
        self._warnings.append(msg)
        sys.stderr.write('Coverage.py warning: %s\n' % msg)

    def _check_for_packages(self):
        if self.source_pkgs:
            found = []
            for pkg in self.source_pkgs:
                try:
                    mod = sys.modules[pkg]
                except KeyError:
                    continue

                found.append(pkg)
                try:
                    pkg_file = mod.__file__
                except AttributeError:
                    pkg_file = None
                else:
                    d, f = os.path.split(pkg_file)
                    if f.startswith('__init__'):
                        pkg_file = d
                    else:
                        pkg_file = self._source_for_file(pkg_file)
                    pkg_file = self.file_locator.canonical_filename(pkg_file)
                    if not os.path.exists(pkg_file):
                        pkg_file = None

                if pkg_file:
                    self.source.append(pkg_file)
                    self.source_match.add(pkg_file)
                else:
                    self._warn('Module %s has no Python source.' % pkg)

            for pkg in found:
                self.source_pkgs.remove(pkg)

    def use_cache(self, usecache):
        self.data.usefile(usecache)

    def load(self):
        self.collector.reset()
        self.data.read()

    def start(self):
        if self.run_suffix:
            self.data_suffix = self.run_suffix
        if self.auto_data:
            self.load()
        if self.source or self.source_pkgs:
            self.source_match = TreeMatcher(self.source)
        else:
            if self.cover_dir:
                self.cover_match = TreeMatcher([self.cover_dir])
            if self.pylib_dirs:
                self.pylib_match = TreeMatcher(self.pylib_dirs)
        if self.include:
            self.include_match = FnmatchMatcher(self.include)
        if self.omit:
            self.omit_match = FnmatchMatcher(self.omit)
        if self.debug.should('config'):
            self.debug.write('Configuration values:')
            config_info = sorted(self.config.__dict__.items())
            self.debug.write_formatted_info(config_info)
        if self.debug.should('sys'):
            self.debug.write('Debugging info:')
            self.debug.write_formatted_info(self.sysinfo())
        self.collector.start()
        self._started = True
        self._measured = True

    def stop(self):
        self._started = False
        self.collector.stop()

    def _atexit(self):
        if self._started:
            self.stop()
        if self.auto_data:
            self.save()

    def erase(self):
        self.collector.reset()
        self.data.erase()

    def clear_exclude(self, which = 'exclude'):
        setattr(self.config, which + '_list', [])
        self._exclude_regex_stale()

    def exclude(self, regex, which = 'exclude'):
        excl_list = getattr(self.config, which + '_list')
        excl_list.append(regex)
        self._exclude_regex_stale()

    def _exclude_regex_stale(self):
        self._exclude_re.clear()

    def _exclude_regex(self, which):
        if which not in self._exclude_re:
            excl_list = getattr(self.config, which + '_list')
            self._exclude_re[which] = join_regex(excl_list)
        return self._exclude_re[which]

    def get_exclude_list(self, which = 'exclude'):
        return getattr(self.config, which + '_list')

    def save(self):
        data_suffix = self.data_suffix
        if data_suffix is True:
            extra = ''
            if _TEST_NAME_FILE:
                f = open(_TEST_NAME_FILE)
                test_name = f.read()
                f.close()
                extra = '.' + test_name
            data_suffix = '%s%s.%s.%06d' % (socket.gethostname(),
             extra,
             os.getpid(),
             random.randint(0, 999999))
        self._harvest_data()
        self.data.write(suffix=data_suffix)

    def combine(self):
        aliases = None
        if self.config.paths:
            aliases = PathAliases(self.file_locator)
            for paths in self.config.paths.values():
                result = paths[0]
                for pattern in paths[1:]:
                    aliases.add(pattern, result)

        self.data.combine_parallel_data(aliases=aliases)

    def _harvest_data(self):
        if not self._measured:
            return
        self.data.add_line_data(self.collector.get_line_data())
        self.data.add_arc_data(self.collector.get_arc_data())
        self.collector.reset()
        if self._warn_unimported_source:
            for pkg in self.source_pkgs:
                self._warn('Module %s was never imported.' % pkg)

        summary = self.data.summary()
        if not summary and self._warn_no_data:
            self._warn('No data was collected.')
        for src in self.source:
            for py_file in find_python_files(src):
                py_file = self.file_locator.canonical_filename(py_file)
                if self.omit_match and self.omit_match.match(py_file):
                    continue
                self.data.touch_file(py_file)

        self._measured = False

    def analysis(self, morf):
        f, s, _, m, mf = self.analysis2(morf)
        return (f,
         s,
         m,
         mf)

    def analysis2(self, morf):
        analysis = self._analyze(morf)
        return (analysis.filename,
         analysis.statements,
         analysis.excluded,
         analysis.missing,
         analysis.missing_formatted())

    def _analyze(self, it):
        self._harvest_data()
        if not isinstance(it, CodeUnit):
            it = code_unit_factory(it, self.file_locator)[0]
        return Analysis(self, it)

    def report(self, morfs = None, show_missing = True, ignore_errors = None, file = None, omit = None, include = None):
        self._harvest_data()
        self.config.from_args(ignore_errors=ignore_errors, omit=omit, include=include, show_missing=show_missing)
        reporter = SummaryReporter(self, self.config)
        return reporter.report(morfs, outfile=file)

    def annotate(self, morfs = None, directory = None, ignore_errors = None, omit = None, include = None):
        self._harvest_data()
        self.config.from_args(ignore_errors=ignore_errors, omit=omit, include=include)
        reporter = AnnotateReporter(self, self.config)
        reporter.report(morfs, directory=directory)

    def html_report(self, morfs = None, directory = None, ignore_errors = None, omit = None, include = None, extra_css = None, title = None):
        self._harvest_data()
        self.config.from_args(ignore_errors=ignore_errors, omit=omit, include=include, html_dir=directory, extra_css=extra_css, html_title=title)
        reporter = HtmlReporter(self, self.config)
        return reporter.report(morfs)

    def xml_report(self, morfs = None, outfile = None, ignore_errors = None, omit = None, include = None):
        self._harvest_data()
        self.config.from_args(ignore_errors=ignore_errors, omit=omit, include=include, xml_output=outfile)
        file_to_close = None
        delete_file = False
        if self.config.xml_output:
            if self.config.xml_output == '-':
                outfile = sys.stdout
            else:
                outfile = open(self.config.xml_output, 'w')
                file_to_close = outfile
        try:
            reporter = XmlReporter(self, self.config)
            return reporter.report(morfs, outfile=outfile)
        except CoverageException:
            delete_file = True
            raise
        finally:
            if file_to_close:
                file_to_close.close()
                if delete_file:
                    file_be_gone(self.config.xml_output)

    def sysinfo(self):
        import coverage as covmod
        import platform, re
        try:
            implementation = platform.python_implementation()
        except AttributeError:
            implementation = 'unknown'

        info = [('version', covmod.__version__),
         ('coverage', covmod.__file__),
         ('cover_dir', self.cover_dir),
         ('pylib_dirs', self.pylib_dirs),
         ('tracer', self.collector.tracer_name()),
         ('config_files', self.config.attempted_config_files),
         ('configs_read', self.config.config_files),
         ('data_path', self.data.filename),
         ('python', sys.version.replace('\n', '')),
         ('platform', platform.platform()),
         ('implementation', implementation),
         ('executable', sys.executable),
         ('cwd', os.getcwd()),
         ('path', sys.path),
         ('environment', sorted([ '%s = %s' % (k, v) for k, v in iitems(os.environ) if re.search('^COV|^PY', k) ])),
         ('command_line', ' '.join(getattr(sys, 'argv', ['???'])))]
        if self.source_match:
            info.append(('source_match', self.source_match.info()))
        if self.include_match:
            info.append(('include_match', self.include_match.info()))
        if self.omit_match:
            info.append(('omit_match', self.omit_match.info()))
        if self.cover_match:
            info.append(('cover_match', self.cover_match.info()))
        if self.pylib_match:
            info.append(('pylib_match', self.pylib_match.info()))
        return info


def process_startup():
    cps = os.environ.get('COVERAGE_PROCESS_START')
    if cps:
        cov = coverage(config_file=cps, auto_data=True)
        cov.start()
        cov._warn_no_data = False
        cov._warn_unimported_source = False


_TEST_NAME_FILE = ''
