#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\stdlib\pkg_resources\_vendor\pyparsing.py
"""
pyparsing module - Classes and methods to define and execute parsing grammars

The pyparsing module is an alternative approach to creating and executing simple grammars,
vs. the traditional lex/yacc approach, or the use of regular expressions.  With pyparsing, you
don't need to learn a new syntax for defining grammars or matching expressions - the parsing module
provides a library of classes that you use to construct the grammar directly in Python.

Here is a program to parse "Hello, World!" (or any greeting of the form C{"<salutation>, <addressee>!"})::

    from pyparsing import Word, alphas

    # define grammar of a greeting
    greet = Word( alphas ) + "," + Word( alphas ) + "!"

    hello = "Hello, World!"
    print (hello, "->", greet.parseString( hello ))

The program outputs the following::

    Hello, World! -> ['Hello', ',', 'World', '!']

The Python representation of the grammar is quite readable, owing to the self-explanatory
class names, and the use of '+', '|' and '^' operators.

The parsed results returned from C{parseString()} can be accessed as a nested list, a dictionary, or an
object with named attributes.

The pyparsing module handles some of the problems that are typically vexing when writing text parsers:
 - extra or missing whitespace (the above program will also handle "Hello,World!", "Hello  ,  World  !", etc.)
 - quoted strings
 - embedded comments
"""
__version__ = '2.0.6'
__versionTime__ = '9 Nov 2015 19:03'
__author__ = 'Paul McGuire <ptmcg@users.sourceforge.net>'
import string
from weakref import ref as wkref
import copy
import sys
import warnings
import re
import sre_constants
import collections
import pprint
import functools
import itertools
__all__ = ['And',
 'CaselessKeyword',
 'CaselessLiteral',
 'CharsNotIn',
 'Combine',
 'Dict',
 'Each',
 'Empty',
 'FollowedBy',
 'Forward',
 'GoToColumn',
 'Group',
 'Keyword',
 'LineEnd',
 'LineStart',
 'Literal',
 'MatchFirst',
 'NoMatch',
 'NotAny',
 'OneOrMore',
 'OnlyOnce',
 'Optional',
 'Or',
 'ParseBaseException',
 'ParseElementEnhance',
 'ParseException',
 'ParseExpression',
 'ParseFatalException',
 'ParseResults',
 'ParseSyntaxException',
 'ParserElement',
 'QuotedString',
 'RecursiveGrammarException',
 'Regex',
 'SkipTo',
 'StringEnd',
 'StringStart',
 'Suppress',
 'Token',
 'TokenConverter',
 'Upcase',
 'White',
 'Word',
 'WordEnd',
 'WordStart',
 'ZeroOrMore',
 'alphanums',
 'alphas',
 'alphas8bit',
 'anyCloseTag',
 'anyOpenTag',
 'cStyleComment',
 'col',
 'commaSeparatedList',
 'commonHTMLEntity',
 'countedArray',
 'cppStyleComment',
 'dblQuotedString',
 'dblSlashComment',
 'delimitedList',
 'dictOf',
 'downcaseTokens',
 'empty',
 'hexnums',
 'htmlComment',
 'javaStyleComment',
 'keepOriginalText',
 'line',
 'lineEnd',
 'lineStart',
 'lineno',
 'makeHTMLTags',
 'makeXMLTags',
 'matchOnlyAtCol',
 'matchPreviousExpr',
 'matchPreviousLiteral',
 'nestedExpr',
 'nullDebugAction',
 'nums',
 'oneOf',
 'opAssoc',
 'operatorPrecedence',
 'printables',
 'punc8bit',
 'pythonStyleComment',
 'quotedString',
 'removeQuotes',
 'replaceHTMLEntity',
 'replaceWith',
 'restOfLine',
 'sglQuotedString',
 'srange',
 'stringEnd',
 'stringStart',
 'traceParseAction',
 'unicodeString',
 'upcaseTokens',
 'withAttribute',
 'indentedBlock',
 'originalTextFor',
 'ungroup',
 'infixNotation',
 'locatedExpr',
 'withClass']
PY_3 = sys.version.startswith('3')
if PY_3:
    _MAX_INT = sys.maxsize
    basestring = str
    unichr = chr
    _ustr = str
    singleArgBuiltins = [sum,
     len,
     sorted,
     reversed,
     list,
     tuple,
     set,
     any,
     all,
     min,
     max]
else:
    _MAX_INT = sys.maxint
    range = xrange

    def _ustr(obj):
        if isinstance(obj, unicode):
            return obj
        try:
            return str(obj)
        except UnicodeEncodeError:
            return unicode(obj)


    singleArgBuiltins = []
    import __builtin__
    for fname in 'sum len sorted reversed list tuple set any all min max'.split():
        try:
            singleArgBuiltins.append(getattr(__builtin__, fname))
        except AttributeError:
            continue

_generatorType = type((y for y in range(1)))

def _xml_escape(data):
    from_symbols = '&><"\''
    to_symbols = ('&' + s + ';' for s in 'amp gt lt quot apos'.split())
    for from_, to_ in zip(from_symbols, to_symbols):
        data = data.replace(from_, to_)

    return data


class _Constants(object):
    pass


alphas = string.ascii_lowercase + string.ascii_uppercase
nums = '0123456789'
hexnums = nums + 'ABCDEFabcdef'
alphanums = alphas + nums
_bslash = chr(92)
printables = ''.join((c for c in string.printable if c not in string.whitespace))

class ParseBaseException(Exception):

    def __init__(self, pstr, loc = 0, msg = None, elem = None):
        self.loc = loc
        if msg is None:
            self.msg = pstr
            self.pstr = ''
        else:
            self.msg = msg
            self.pstr = pstr
        self.parserElement = elem

    def __getattr__(self, aname):
        if aname == 'lineno':
            return lineno(self.loc, self.pstr)
        if aname in ('col', 'column'):
            return col(self.loc, self.pstr)
        if aname == 'line':
            return line(self.loc, self.pstr)
        raise AttributeError(aname)

    def __str__(self):
        return '%s (at char %d), (line:%d, col:%d)' % (self.msg,
         self.loc,
         self.lineno,
         self.column)

    def __repr__(self):
        return _ustr(self)

    def markInputline(self, markerString = '>!<'):
        line_str = self.line
        line_column = self.column - 1
        if markerString:
            line_str = ''.join((line_str[:line_column], markerString, line_str[line_column:]))
        return line_str.strip()

    def __dir__(self):
        return 'loc msg pstr parserElement lineno col line markInputline __str__ __repr__'.split()


class ParseException(ParseBaseException):
    pass


class ParseFatalException(ParseBaseException):
    pass


class ParseSyntaxException(ParseFatalException):

    def __init__(self, pe):
        super(ParseSyntaxException, self).__init__(pe.pstr, pe.loc, pe.msg, pe.parserElement)


class RecursiveGrammarException(Exception):

    def __init__(self, parseElementList):
        self.parseElementTrace = parseElementList

    def __str__(self):
        return 'RecursiveGrammarException: %s' % self.parseElementTrace


class _ParseResultsWithOffset(object):

    def __init__(self, p1, p2):
        self.tup = (p1, p2)

    def __getitem__(self, i):
        return self.tup[i]

    def __repr__(self):
        return repr(self.tup)

    def setOffset(self, i):
        self.tup = (self.tup[0], i)


class ParseResults(object):

    def __new__(cls, toklist, name = None, asList = True, modal = True):
        if isinstance(toklist, cls):
            return toklist
        retobj = object.__new__(cls)
        retobj.__doinit = True
        return retobj

    def __init__(self, toklist, name = None, asList = True, modal = True, isinstance = isinstance):
        if self.__doinit:
            self.__doinit = False
            self.__name = None
            self.__parent = None
            self.__accumNames = {}
            if isinstance(toklist, list):
                self.__toklist = toklist[:]
            elif isinstance(toklist, _generatorType):
                self.__toklist = list(toklist)
            else:
                self.__toklist = [toklist]
            self.__tokdict = dict()
        if name is not None and name:
            if not modal:
                self.__accumNames[name] = 0
            if isinstance(name, int):
                name = _ustr(name)
            self.__name = name
            if not (isinstance(toklist, (type(None), basestring, list)) and toklist in (None, '', [])):
                if isinstance(toklist, basestring):
                    toklist = [toklist]
                if asList:
                    if isinstance(toklist, ParseResults):
                        self[name] = _ParseResultsWithOffset(toklist.copy(), 0)
                    else:
                        self[name] = _ParseResultsWithOffset(ParseResults(toklist[0]), 0)
                    self[name].__name = name
                else:
                    try:
                        self[name] = toklist[0]
                    except (KeyError, TypeError, IndexError):
                        self[name] = toklist

    def __getitem__(self, i):
        if isinstance(i, (int, slice)):
            return self.__toklist[i]
        elif i not in self.__accumNames:
            return self.__tokdict[i][-1][0]
        else:
            return ParseResults([ v[0] for v in self.__tokdict[i] ])

    def __setitem__(self, k, v, isinstance = isinstance):
        if isinstance(v, _ParseResultsWithOffset):
            self.__tokdict[k] = self.__tokdict.get(k, list()) + [v]
            sub = v[0]
        elif isinstance(k, int):
            self.__toklist[k] = v
            sub = v
        else:
            self.__tokdict[k] = self.__tokdict.get(k, list()) + [_ParseResultsWithOffset(v, 0)]
            sub = v
        if isinstance(sub, ParseResults):
            sub.__parent = wkref(self)

    def __delitem__(self, i):
        if isinstance(i, (int, slice)):
            mylen = len(self.__toklist)
            del self.__toklist[i]
            if isinstance(i, int):
                if i < 0:
                    i += mylen
                i = slice(i, i + 1)
            removed = list(range(*i.indices(mylen)))
            removed.reverse()
            for name, occurrences in self.__tokdict.items():
                for j in removed:
                    for k, (value, position) in enumerate(occurrences):
                        occurrences[k] = _ParseResultsWithOffset(value, position - (position > j))

        else:
            del self.__tokdict[i]

    def __contains__(self, k):
        return k in self.__tokdict

    def __len__(self):
        return len(self.__toklist)

    def __bool__(self):
        return len(self.__toklist) > 0

    __nonzero__ = __bool__

    def __iter__(self):
        return iter(self.__toklist)

    def __reversed__(self):
        return iter(self.__toklist[::-1])

    def iterkeys(self):
        if hasattr(self.__tokdict, 'iterkeys'):
            return self.__tokdict.iterkeys()
        else:
            return iter(self.__tokdict)

    def itervalues(self):
        return (self[k] for k in self.iterkeys())

    def iteritems(self):
        return ((k, self[k]) for k in self.iterkeys())

    if PY_3:
        keys = iterkeys
        values = itervalues
        items = iteritems
    else:

        def keys(self):
            return list(self.iterkeys())

        def values(self):
            return list(self.itervalues())

        def items(self):
            return list(self.iteritems())

    def haskeys(self):
        return bool(self.__tokdict)

    def pop(self, *args, **kwargs):
        if not args:
            args = [-1]
        for k, v in kwargs.items():
            if k == 'default':
                args = (args[0], v)
            else:
                raise TypeError("pop() got an unexpected keyword argument '%s'" % k)

        if isinstance(args[0], int) or len(args) == 1 or args[0] in self:
            index = args[0]
            ret = self[index]
            del self[index]
            return ret
        else:
            defaultvalue = args[1]
            return defaultvalue

    def get(self, key, defaultValue = None):
        if key in self:
            return self[key]
        else:
            return defaultValue

    def insert(self, index, insStr):
        self.__toklist.insert(index, insStr)
        for name, occurrences in self.__tokdict.items():
            for k, (value, position) in enumerate(occurrences):
                occurrences[k] = _ParseResultsWithOffset(value, position + (position > index))

    def append(self, item):
        self.__toklist.append(item)

    def extend(self, itemseq):
        if isinstance(itemseq, ParseResults):
            self += itemseq
        else:
            self.__toklist.extend(itemseq)

    def clear(self):
        del self.__toklist[:]
        self.__tokdict.clear()

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            return ''

        if name in self.__tokdict:
            if name not in self.__accumNames:
                return self.__tokdict[name][-1][0]
            else:
                return ParseResults([ v[0] for v in self.__tokdict[name] ])
        else:
            return ''

    def __add__(self, other):
        ret = self.copy()
        ret += other
        return ret

    def __iadd__(self, other):
        if other.__tokdict:
            offset = len(self.__toklist)
            addoffset = lambda a: (offset if a < 0 else a + offset)
            otheritems = other.__tokdict.items()
            otherdictitems = [ (k, _ParseResultsWithOffset(v[0], addoffset(v[1]))) for k, vlist in otheritems for v in vlist ]
            for k, v in otherdictitems:
                self[k] = v
                if isinstance(v[0], ParseResults):
                    v[0].__parent = wkref(self)

        self.__toklist += other.__toklist
        self.__accumNames.update(other.__accumNames)
        return self

    def __radd__(self, other):
        if isinstance(other, int) and other == 0:
            return self.copy()

    def __repr__(self):
        return '(%s, %s)' % (repr(self.__toklist), repr(self.__tokdict))

    def __str__(self):
        return '[' + ', '.join(((_ustr(i) if isinstance(i, ParseResults) else repr(i)) for i in self.__toklist)) + ']'

    def _asStringList(self, sep = ''):
        out = []
        for item in self.__toklist:
            if out and sep:
                out.append(sep)
            if isinstance(item, ParseResults):
                out += item._asStringList()
            else:
                out.append(_ustr(item))

        return out

    def asList(self):
        return [ (res.asList() if isinstance(res, ParseResults) else res) for res in self.__toklist ]

    def asDict(self):
        if PY_3:
            return dict(self.items())
        else:
            return dict(self.iteritems())

    def copy(self):
        ret = ParseResults(self.__toklist)
        ret.__tokdict = self.__tokdict.copy()
        ret.__parent = self.__parent
        ret.__accumNames.update(self.__accumNames)
        ret.__name = self.__name
        return ret

    def asXML(self, doctag = None, namedItemsOnly = False, indent = '', formatted = True):
        nl = '\n'
        out = []
        namedItems = dict(((v[1], k) for k, vlist in self.__tokdict.items() for v in vlist))
        nextLevelIndent = indent + '  '
        if not formatted:
            indent = ''
            nextLevelIndent = ''
            nl = ''
        selfTag = None
        if doctag is not None:
            selfTag = doctag
        elif self.__name:
            selfTag = self.__name
        if not selfTag:
            if namedItemsOnly:
                return ''
            selfTag = 'ITEM'
        out += [nl,
         indent,
         '<',
         selfTag,
         '>']
        for i, res in enumerate(self.__toklist):
            if isinstance(res, ParseResults):
                if i in namedItems:
                    out += [res.asXML(namedItems[i], namedItemsOnly and doctag is None, nextLevelIndent, formatted)]
                else:
                    out += [res.asXML(None, namedItemsOnly and doctag is None, nextLevelIndent, formatted)]
            else:
                resTag = None
                if i in namedItems:
                    resTag = namedItems[i]
                if not resTag:
                    if namedItemsOnly:
                        continue
                    else:
                        resTag = 'ITEM'
                xmlBodyText = _xml_escape(_ustr(res))
                out += [nl,
                 nextLevelIndent,
                 '<',
                 resTag,
                 '>',
                 xmlBodyText,
                 '</',
                 resTag,
                 '>']

        out += [nl,
         indent,
         '</',
         selfTag,
         '>']
        return ''.join(out)

    def __lookup(self, sub):
        for k, vlist in self.__tokdict.items():
            for v, loc in vlist:
                if sub is v:
                    return k

    def getName(self):
        if self.__name:
            return self.__name
        if self.__parent:
            par = self.__parent()
            if par:
                return par.__lookup(self)
            else:
                return None
        else:
            if len(self) == 1 and len(self.__tokdict) == 1 and self.__tokdict.values()[0][0][1] in (0, -1):
                return self.__tokdict.keys()[0]
            return None

    def dump(self, indent = '', depth = 0):
        out = []
        NL = '\n'
        out.append(indent + _ustr(self.asList()))
        if self.haskeys():
            items = sorted(self.items())
            for k, v in items:
                if out:
                    out.append(NL)
                out.append('%s%s- %s: ' % (indent, '  ' * depth, k))
                if isinstance(v, ParseResults):
                    if v:
                        out.append(v.dump(indent, depth + 1))
                    else:
                        out.append(_ustr(v))
                else:
                    out.append(_ustr(v))

        elif any((isinstance(vv, ParseResults) for vv in self)):
            v = self
            for i, vv in enumerate(v):
                if isinstance(vv, ParseResults):
                    out.append('\n%s%s[%d]:\n%s%s%s' % (indent,
                     '  ' * depth,
                     i,
                     indent,
                     '  ' * (depth + 1),
                     vv.dump(indent, depth + 1)))
                else:
                    out.append('\n%s%s[%d]:\n%s%s%s' % (indent,
                     '  ' * depth,
                     i,
                     indent,
                     '  ' * (depth + 1),
                     _ustr(vv)))

        return ''.join(out)

    def pprint(self, *args, **kwargs):
        pprint.pprint(self.asList(), *args, **kwargs)

    def __getstate__(self):
        return (self.__toklist, (self.__tokdict.copy(),
          self.__parent is not None and self.__parent() or None,
          self.__accumNames,
          self.__name))

    def __setstate__(self, state):
        self.__toklist = state[0]
        self.__tokdict, par, inAccumNames, self.__name = state[1]
        self.__accumNames = {}
        self.__accumNames.update(inAccumNames)
        if par is not None:
            self.__parent = wkref(par)
        else:
            self.__parent = None

    def __dir__(self):
        return dir(super(ParseResults, self)) + list(self.keys())


collections.MutableMapping.register(ParseResults)

def col(loc, strg):
    s = strg
    if loc < len(s) and s[loc] == '\n':
        return 1
    return loc - s.rfind('\n', 0, loc)


def lineno(loc, strg):
    return strg.count('\n', 0, loc) + 1


def line(loc, strg):
    lastCR = strg.rfind('\n', 0, loc)
    nextCR = strg.find('\n', loc)
    if nextCR >= 0:
        return strg[lastCR + 1:nextCR]
    else:
        return strg[lastCR + 1:]


def _defaultStartDebugAction(instring, loc, expr):
    print 'Match ' + _ustr(expr) + ' at loc ' + _ustr(loc) + '(%d,%d)' % (lineno(loc, instring), col(loc, instring))


def _defaultSuccessDebugAction(instring, startloc, endloc, expr, toks):
    print 'Matched ' + _ustr(expr) + ' -> ' + str(toks.asList())


def _defaultExceptionDebugAction(instring, loc, expr, exc):
    print 'Exception raised:' + _ustr(exc)


def nullDebugAction(*args):
    pass


def _trim_arity(func, maxargs = 2):
    if func in singleArgBuiltins:
        return lambda s, l, t: func(t)
    limit = [0]
    foundArity = [False]

    def wrapper(*args):
        while 1:
            try:
                ret = func(*args[limit[0]:])
                foundArity[0] = True
                return ret
            except TypeError:
                if limit[0] <= maxargs and not foundArity[0]:
                    limit[0] += 1
                    continue
                raise

    return wrapper


class ParserElement(object):
    DEFAULT_WHITE_CHARS = ' \n\t\r'
    verbose_stacktrace = False

    @staticmethod
    def setDefaultWhitespaceChars(chars):
        ParserElement.DEFAULT_WHITE_CHARS = chars

    @staticmethod
    def inlineLiteralsUsing(cls):
        ParserElement.literalStringClass = cls

    def __init__(self, savelist = False):
        self.parseAction = list()
        self.failAction = None
        self.strRepr = None
        self.resultsName = None
        self.saveAsList = savelist
        self.skipWhitespace = True
        self.whiteChars = ParserElement.DEFAULT_WHITE_CHARS
        self.copyDefaultWhiteChars = True
        self.mayReturnEmpty = False
        self.keepTabs = False
        self.ignoreExprs = list()
        self.debug = False
        self.streamlined = False
        self.mayIndexError = True
        self.errmsg = ''
        self.modalResults = True
        self.debugActions = (None, None, None)
        self.re = None
        self.callPreparse = True
        self.callDuringTry = False

    def copy(self):
        cpy = copy.copy(self)
        cpy.parseAction = self.parseAction[:]
        cpy.ignoreExprs = self.ignoreExprs[:]
        if self.copyDefaultWhiteChars:
            cpy.whiteChars = ParserElement.DEFAULT_WHITE_CHARS
        return cpy

    def setName(self, name):
        self.name = name
        self.errmsg = 'Expected ' + self.name
        if hasattr(self, 'exception'):
            self.exception.msg = self.errmsg
        return self

    def setResultsName(self, name, listAllMatches = False):
        newself = self.copy()
        if name.endswith('*'):
            name = name[:-1]
            listAllMatches = True
        newself.resultsName = name
        newself.modalResults = not listAllMatches
        return newself

    def setBreak(self, breakFlag = True):
        if breakFlag:
            _parseMethod = self._parse

            def breaker(instring, loc, doActions = True, callPreParse = True):
                import pdb
                pdb.set_trace()
                return _parseMethod(instring, loc, doActions, callPreParse)

            breaker._originalParseMethod = _parseMethod
            self._parse = breaker
        elif hasattr(self._parse, '_originalParseMethod'):
            self._parse = self._parse._originalParseMethod
        return self

    def setParseAction(self, *fns, **kwargs):
        self.parseAction = list(map(_trim_arity, list(fns)))
        self.callDuringTry = kwargs.get('callDuringTry', False)
        return self

    def addParseAction(self, *fns, **kwargs):
        self.parseAction += list(map(_trim_arity, list(fns)))
        self.callDuringTry = self.callDuringTry or kwargs.get('callDuringTry', False)
        return self

    def addCondition(self, *fns, **kwargs):
        msg = kwargs.get('message') or 'failed user-defined condition'
        for fn in fns:

            def pa(s, l, t):
                if not bool(_trim_arity(fn)(s, l, t)):
                    raise ParseException(s, l, msg)
                return t

            self.parseAction.append(pa)

        self.callDuringTry = self.callDuringTry or kwargs.get('callDuringTry', False)
        return self

    def setFailAction(self, fn):
        self.failAction = fn
        return self

    def _skipIgnorables(self, instring, loc):
        exprsFound = True
        while exprsFound:
            exprsFound = False
            for e in self.ignoreExprs:
                try:
                    while 1:
                        loc, dummy = e._parse(instring, loc)
                        exprsFound = True

                except ParseException:
                    pass

        return loc

    def preParse(self, instring, loc):
        if self.ignoreExprs:
            loc = self._skipIgnorables(instring, loc)
        if self.skipWhitespace:
            wt = self.whiteChars
            instrlen = len(instring)
            while loc < instrlen and instring[loc] in wt:
                loc += 1

        return loc

    def parseImpl(self, instring, loc, doActions = True):
        return (loc, [])

    def postParse(self, instring, loc, tokenlist):
        return tokenlist

    def _parseNoCache(self, instring, loc, doActions = True, callPreParse = True):
        debugging = self.debug
        if debugging or self.failAction:
            if self.debugActions[0]:
                self.debugActions[0](instring, loc, self)
            if callPreParse and self.callPreparse:
                preloc = self.preParse(instring, loc)
            else:
                preloc = loc
            tokensStart = preloc
            try:
                try:
                    loc, tokens = self.parseImpl(instring, preloc, doActions)
                except IndexError:
                    raise ParseException(instring, len(instring), self.errmsg, self)

            except ParseBaseException as err:
                if self.debugActions[2]:
                    self.debugActions[2](instring, tokensStart, self, err)
                if self.failAction:
                    self.failAction(instring, tokensStart, self, err)
                raise

        else:
            if callPreParse and self.callPreparse:
                preloc = self.preParse(instring, loc)
            else:
                preloc = loc
            tokensStart = preloc
            if self.mayIndexError or loc >= len(instring):
                try:
                    loc, tokens = self.parseImpl(instring, preloc, doActions)
                except IndexError:
                    raise ParseException(instring, len(instring), self.errmsg, self)

            else:
                loc, tokens = self.parseImpl(instring, preloc, doActions)
        tokens = self.postParse(instring, loc, tokens)
        retTokens = ParseResults(tokens, self.resultsName, asList=self.saveAsList, modal=self.modalResults)
        if self.parseAction and (doActions or self.callDuringTry):
            if debugging:
                try:
                    for fn in self.parseAction:
                        tokens = fn(instring, tokensStart, retTokens)
                        if tokens is not None:
                            retTokens = ParseResults(tokens, self.resultsName, asList=self.saveAsList and isinstance(tokens, (ParseResults, list)), modal=self.modalResults)

                except ParseBaseException as err:
                    if self.debugActions[2]:
                        self.debugActions[2](instring, tokensStart, self, err)
                    raise

            else:
                for fn in self.parseAction:
                    tokens = fn(instring, tokensStart, retTokens)
                    if tokens is not None:
                        retTokens = ParseResults(tokens, self.resultsName, asList=self.saveAsList and isinstance(tokens, (ParseResults, list)), modal=self.modalResults)

        if debugging:
            if self.debugActions[1]:
                self.debugActions[1](instring, tokensStart, loc, self, retTokens)
        return (loc, retTokens)

    def tryParse(self, instring, loc):
        try:
            return self._parse(instring, loc, doActions=False)[0]
        except ParseFatalException:
            raise ParseException(instring, loc, self.errmsg, self)

    def _parseCache(self, instring, loc, doActions = True, callPreParse = True):
        lookup = (self,
         instring,
         loc,
         callPreParse,
         doActions)
        if lookup in ParserElement._exprArgCache:
            value = ParserElement._exprArgCache[lookup]
            if isinstance(value, Exception):
                raise value
            return (value[0], value[1].copy())
        try:
            value = self._parseNoCache(instring, loc, doActions, callPreParse)
            ParserElement._exprArgCache[lookup] = (value[0], value[1].copy())
            return value
        except ParseBaseException as pe:
            pe.__traceback__ = None
            ParserElement._exprArgCache[lookup] = pe
            raise

    _parse = _parseNoCache
    _exprArgCache = {}

    @staticmethod
    def resetCache():
        ParserElement._exprArgCache.clear()

    _packratEnabled = False

    @staticmethod
    def enablePackrat():
        if not ParserElement._packratEnabled:
            ParserElement._packratEnabled = True
            ParserElement._parse = ParserElement._parseCache

    def parseString(self, instring, parseAll = False):
        ParserElement.resetCache()
        if not self.streamlined:
            self.streamline()
        for e in self.ignoreExprs:
            e.streamline()

        if not self.keepTabs:
            instring = instring.expandtabs()
        try:
            loc, tokens = self._parse(instring, 0)
            if parseAll:
                loc = self.preParse(instring, loc)
                se = Empty() + StringEnd()
                se._parse(instring, loc)
        except ParseBaseException as exc:
            if ParserElement.verbose_stacktrace:
                raise
            else:
                raise exc
        else:
            return tokens

    def scanString(self, instring, maxMatches = _MAX_INT, overlap = False):
        if not self.streamlined:
            self.streamline()
        for e in self.ignoreExprs:
            e.streamline()

        if not self.keepTabs:
            instring = _ustr(instring).expandtabs()
        instrlen = len(instring)
        loc = 0
        preparseFn = self.preParse
        parseFn = self._parse
        ParserElement.resetCache()
        matches = 0
        try:
            while loc <= instrlen and matches < maxMatches:
                try:
                    preloc = preparseFn(instring, loc)
                    nextLoc, tokens = parseFn(instring, preloc, callPreParse=False)
                except ParseException:
                    loc = preloc + 1
                else:
                    if nextLoc > loc:
                        matches += 1
                        yield (tokens, preloc, nextLoc)
                        if overlap:
                            nextloc = preparseFn(instring, loc)
                            if nextloc > loc:
                                loc = nextLoc
                            else:
                                loc += 1
                        else:
                            loc = nextLoc
                    else:
                        loc = preloc + 1

        except ParseBaseException as exc:
            if ParserElement.verbose_stacktrace:
                raise
            else:
                raise exc

    def transformString(self, instring):
        out = []
        lastE = 0
        self.keepTabs = True
        try:
            for t, s, e in self.scanString(instring):
                out.append(instring[lastE:s])
                if t:
                    if isinstance(t, ParseResults):
                        out += t.asList()
                    elif isinstance(t, list):
                        out += t
                    else:
                        out.append(t)
                lastE = e

            out.append(instring[lastE:])
            out = [ o for o in out if o ]
            return ''.join(map(_ustr, _flatten(out)))
        except ParseBaseException as exc:
            if ParserElement.verbose_stacktrace:
                raise
            else:
                raise exc

    def searchString(self, instring, maxMatches = _MAX_INT):
        try:
            return ParseResults([ t for t, s, e in self.scanString(instring, maxMatches) ])
        except ParseBaseException as exc:
            if ParserElement.verbose_stacktrace:
                raise
            else:
                raise exc

    def __add__(self, other):
        if isinstance(other, basestring):
            other = ParserElement.literalStringClass(other)
        if not isinstance(other, ParserElement):
            warnings.warn('Cannot combine element of type %s with ParserElement' % type(other), SyntaxWarning, stacklevel=2)
            return None
        return And([self, other])

    def __radd__(self, other):
        if isinstance(other, basestring):
            other = ParserElement.literalStringClass(other)
        if not isinstance(other, ParserElement):
            warnings.warn('Cannot combine element of type %s with ParserElement' % type(other), SyntaxWarning, stacklevel=2)
            return None
        return other + self

    def __sub__(self, other):
        if isinstance(other, basestring):
            other = ParserElement.literalStringClass(other)
        if not isinstance(other, ParserElement):
            warnings.warn('Cannot combine element of type %s with ParserElement' % type(other), SyntaxWarning, stacklevel=2)
            return None
        return And([self, And._ErrorStop(), other])

    def __rsub__(self, other):
        if isinstance(other, basestring):
            other = ParserElement.literalStringClass(other)
        if not isinstance(other, ParserElement):
            warnings.warn('Cannot combine element of type %s with ParserElement' % type(other), SyntaxWarning, stacklevel=2)
            return None
        return other - self

    def __mul__(self, other):
        if isinstance(other, int):
            minElements, optElements = other, 0
        elif isinstance(other, tuple):
            other = (other + (None, None))[:2]
            if other[0] is None:
                other = (0, other[1])
            if isinstance(other[0], int) and other[1] is None:
                if other[0] == 0:
                    return ZeroOrMore(self)
                elif other[0] == 1:
                    return OneOrMore(self)
                else:
                    return self * other[0] + ZeroOrMore(self)
            elif isinstance(other[0], int) and isinstance(other[1], int):
                minElements, optElements = other
                optElements -= minElements
            else:
                raise TypeError("cannot multiply 'ParserElement' and ('%s','%s') objects", type(other[0]), type(other[1]))
        else:
            raise TypeError("cannot multiply 'ParserElement' and '%s' objects", type(other))
        if minElements < 0:
            raise ValueError('cannot multiply ParserElement by negative value')
        if optElements < 0:
            raise ValueError('second tuple value must be greater or equal to first tuple value')
        if minElements == optElements == 0:
            raise ValueError('cannot multiply ParserElement by 0 or (0,0)')
        if optElements:

            def makeOptionalList(n):
                if n > 1:
                    return Optional(self + makeOptionalList(n - 1))
                else:
                    return Optional(self)

            if minElements:
                if minElements == 1:
                    ret = self + makeOptionalList(optElements)
                else:
                    ret = And([self] * minElements) + makeOptionalList(optElements)
            else:
                ret = makeOptionalList(optElements)
        elif minElements == 1:
            ret = self
        else:
            ret = And([self] * minElements)
        return ret

    def __rmul__(self, other):
        return self.__mul__(other)

    def __or__(self, other):
        if isinstance(other, basestring):
            other = ParserElement.literalStringClass(other)
        if not isinstance(other, ParserElement):
            warnings.warn('Cannot combine element of type %s with ParserElement' % type(other), SyntaxWarning, stacklevel=2)
            return None
        return MatchFirst([self, other])

    def __ror__(self, other):
        if isinstance(other, basestring):
            other = ParserElement.literalStringClass(other)
        if not isinstance(other, ParserElement):
            warnings.warn('Cannot combine element of type %s with ParserElement' % type(other), SyntaxWarning, stacklevel=2)
            return None
        return other | self

    def __xor__(self, other):
        if isinstance(other, basestring):
            other = ParserElement.literalStringClass(other)
        if not isinstance(other, ParserElement):
            warnings.warn('Cannot combine element of type %s with ParserElement' % type(other), SyntaxWarning, stacklevel=2)
            return None
        return Or([self, other])

    def __rxor__(self, other):
        if isinstance(other, basestring):
            other = ParserElement.literalStringClass(other)
        if not isinstance(other, ParserElement):
            warnings.warn('Cannot combine element of type %s with ParserElement' % type(other), SyntaxWarning, stacklevel=2)
            return None
        return other ^ self

    def __and__(self, other):
        if isinstance(other, basestring):
            other = ParserElement.literalStringClass(other)
        if not isinstance(other, ParserElement):
            warnings.warn('Cannot combine element of type %s with ParserElement' % type(other), SyntaxWarning, stacklevel=2)
            return None
        return Each([self, other])

    def __rand__(self, other):
        if isinstance(other, basestring):
            other = ParserElement.literalStringClass(other)
        if not isinstance(other, ParserElement):
            warnings.warn('Cannot combine element of type %s with ParserElement' % type(other), SyntaxWarning, stacklevel=2)
            return None
        return other & self

    def __invert__(self):
        return NotAny(self)

    def __call__(self, name = None):
        if name is not None:
            return self.setResultsName(name)
        else:
            return self.copy()

    def suppress(self):
        return Suppress(self)

    def leaveWhitespace(self):
        self.skipWhitespace = False
        return self

    def setWhitespaceChars(self, chars):
        self.skipWhitespace = True
        self.whiteChars = chars
        self.copyDefaultWhiteChars = False
        return self

    def parseWithTabs(self):
        self.keepTabs = True
        return self

    def ignore(self, other):
        if isinstance(other, Suppress):
            if other not in self.ignoreExprs:
                self.ignoreExprs.append(other.copy())
        else:
            self.ignoreExprs.append(Suppress(other.copy()))
        return self

    def setDebugActions(self, startAction, successAction, exceptionAction):
        self.debugActions = (startAction or _defaultStartDebugAction, successAction or _defaultSuccessDebugAction, exceptionAction or _defaultExceptionDebugAction)
        self.debug = True
        return self

    def setDebug(self, flag = True):
        if flag:
            self.setDebugActions(_defaultStartDebugAction, _defaultSuccessDebugAction, _defaultExceptionDebugAction)
        else:
            self.debug = False
        return self

    def __str__(self):
        return self.name

    def __repr__(self):
        return _ustr(self)

    def streamline(self):
        self.streamlined = True
        self.strRepr = None
        return self

    def checkRecursion(self, parseElementList):
        pass

    def validate(self, validateTrace = []):
        self.checkRecursion([])

    def parseFile(self, file_or_filename, parseAll = False):
        try:
            file_contents = file_or_filename.read()
        except AttributeError:
            f = open(file_or_filename, 'r')
            file_contents = f.read()
            f.close()

        try:
            return self.parseString(file_contents, parseAll)
        except ParseBaseException as exc:
            if ParserElement.verbose_stacktrace:
                raise
            else:
                raise exc

    def __eq__(self, other):
        if isinstance(other, ParserElement):
            return self is other or self.__dict__ == other.__dict__
        if isinstance(other, basestring):
            try:
                self.parseString(_ustr(other), parseAll=True)
                return True
            except ParseBaseException:
                return False

        else:
            return super(ParserElement, self) == other

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        return hash(id(self))

    def __req__(self, other):
        return self == other

    def __rne__(self, other):
        return not self == other

    def runTests(self, tests, parseAll = False):
        if isinstance(tests, basestring):
            tests = map(str.strip, tests.splitlines())
        for t in tests:
            out = [t]
            try:
                out.append(self.parseString(t, parseAll=parseAll).dump())
            except ParseException as pe:
                if '\n' in t:
                    out.append(line(pe.loc, t))
                    out.append(' ' * (col(pe.loc, t) - 1) + '^')
                else:
                    out.append(' ' * pe.loc + '^')
                out.append(str(pe))

            out.append('')
            print '\n'.join(out)


class Token(ParserElement):

    def __init__(self):
        super(Token, self).__init__(savelist=False)


class Empty(Token):

    def __init__(self):
        super(Empty, self).__init__()
        self.name = 'Empty'
        self.mayReturnEmpty = True
        self.mayIndexError = False


class NoMatch(Token):

    def __init__(self):
        super(NoMatch, self).__init__()
        self.name = 'NoMatch'
        self.mayReturnEmpty = True
        self.mayIndexError = False
        self.errmsg = 'Unmatchable token'

    def parseImpl(self, instring, loc, doActions = True):
        raise ParseException(instring, loc, self.errmsg, self)


class Literal(Token):

    def __init__(self, matchString):
        super(Literal, self).__init__()
        self.match = matchString
        self.matchLen = len(matchString)
        try:
            self.firstMatchChar = matchString[0]
        except IndexError:
            warnings.warn('null string passed to Literal; use Empty() instead', SyntaxWarning, stacklevel=2)
            self.__class__ = Empty

        self.name = '"%s"' % _ustr(self.match)
        self.errmsg = 'Expected ' + self.name
        self.mayReturnEmpty = False
        self.mayIndexError = False

    def parseImpl(self, instring, loc, doActions = True):
        if instring[loc] == self.firstMatchChar and (self.matchLen == 1 or instring.startswith(self.match, loc)):
            return (loc + self.matchLen, self.match)
        raise ParseException(instring, loc, self.errmsg, self)


_L = Literal
ParserElement.literalStringClass = Literal

class Keyword(Token):
    DEFAULT_KEYWORD_CHARS = alphanums + '_$'

    def __init__(self, matchString, identChars = DEFAULT_KEYWORD_CHARS, caseless = False):
        super(Keyword, self).__init__()
        self.match = matchString
        self.matchLen = len(matchString)
        try:
            self.firstMatchChar = matchString[0]
        except IndexError:
            warnings.warn('null string passed to Keyword; use Empty() instead', SyntaxWarning, stacklevel=2)

        self.name = '"%s"' % self.match
        self.errmsg = 'Expected ' + self.name
        self.mayReturnEmpty = False
        self.mayIndexError = False
        self.caseless = caseless
        if caseless:
            self.caselessmatch = matchString.upper()
            identChars = identChars.upper()
        self.identChars = set(identChars)

    def parseImpl(self, instring, loc, doActions = True):
        if self.caseless:
            if instring[loc:loc + self.matchLen].upper() == self.caselessmatch and (loc >= len(instring) - self.matchLen or instring[loc + self.matchLen].upper() not in self.identChars) and (loc == 0 or instring[loc - 1].upper() not in self.identChars):
                return (loc + self.matchLen, self.match)
        elif instring[loc] == self.firstMatchChar and (self.matchLen == 1 or instring.startswith(self.match, loc)) and (loc >= len(instring) - self.matchLen or instring[loc + self.matchLen] not in self.identChars) and (loc == 0 or instring[loc - 1] not in self.identChars):
            return (loc + self.matchLen, self.match)
        raise ParseException(instring, loc, self.errmsg, self)

    def copy(self):
        c = super(Keyword, self).copy()
        c.identChars = Keyword.DEFAULT_KEYWORD_CHARS
        return c

    @staticmethod
    def setDefaultKeywordChars(chars):
        Keyword.DEFAULT_KEYWORD_CHARS = chars


class CaselessLiteral(Literal):

    def __init__(self, matchString):
        super(CaselessLiteral, self).__init__(matchString.upper())
        self.returnString = matchString
        self.name = "'%s'" % self.returnString
        self.errmsg = 'Expected ' + self.name

    def parseImpl(self, instring, loc, doActions = True):
        if instring[loc:loc + self.matchLen].upper() == self.match:
            return (loc + self.matchLen, self.returnString)
        raise ParseException(instring, loc, self.errmsg, self)


class CaselessKeyword(Keyword):

    def __init__(self, matchString, identChars = Keyword.DEFAULT_KEYWORD_CHARS):
        super(CaselessKeyword, self).__init__(matchString, identChars, caseless=True)

    def parseImpl(self, instring, loc, doActions = True):
        if instring[loc:loc + self.matchLen].upper() == self.caselessmatch and (loc >= len(instring) - self.matchLen or instring[loc + self.matchLen].upper() not in self.identChars):
            return (loc + self.matchLen, self.match)
        raise ParseException(instring, loc, self.errmsg, self)


class Word(Token):

    def __init__(self, initChars, bodyChars = None, min = 1, max = 0, exact = 0, asKeyword = False, excludeChars = None):
        super(Word, self).__init__()
        if excludeChars:
            initChars = ''.join((c for c in initChars if c not in excludeChars))
            if bodyChars:
                bodyChars = ''.join((c for c in bodyChars if c not in excludeChars))
        self.initCharsOrig = initChars
        self.initChars = set(initChars)
        if bodyChars:
            self.bodyCharsOrig = bodyChars
            self.bodyChars = set(bodyChars)
        else:
            self.bodyCharsOrig = initChars
            self.bodyChars = set(initChars)
        self.maxSpecified = max > 0
        if min < 1:
            raise ValueError('cannot specify a minimum length < 1; use Optional(Word()) if zero-length word is permitted')
        self.minLen = min
        if max > 0:
            self.maxLen = max
        else:
            self.maxLen = _MAX_INT
        if exact > 0:
            self.maxLen = exact
            self.minLen = exact
        self.name = _ustr(self)
        self.errmsg = 'Expected ' + self.name
        self.mayIndexError = False
        self.asKeyword = asKeyword
        if ' ' not in self.initCharsOrig + self.bodyCharsOrig and min == 1 and max == 0 and exact == 0:
            if self.bodyCharsOrig == self.initCharsOrig:
                self.reString = '[%s]+' % _escapeRegexRangeChars(self.initCharsOrig)
            elif len(self.initCharsOrig) == 1:
                self.reString = '%s[%s]*' % (re.escape(self.initCharsOrig), _escapeRegexRangeChars(self.bodyCharsOrig))
            else:
                self.reString = '[%s][%s]*' % (_escapeRegexRangeChars(self.initCharsOrig), _escapeRegexRangeChars(self.bodyCharsOrig))
            if self.asKeyword:
                self.reString = '\\b' + self.reString + '\\b'
            try:
                self.re = re.compile(self.reString)
            except:
                self.re = None

    def parseImpl(self, instring, loc, doActions = True):
        if self.re:
            result = self.re.match(instring, loc)
            if not result:
                raise ParseException(instring, loc, self.errmsg, self)
            loc = result.end()
            return (loc, result.group())
        if instring[loc] not in self.initChars:
            raise ParseException(instring, loc, self.errmsg, self)
        start = loc
        loc += 1
        instrlen = len(instring)
        bodychars = self.bodyChars
        maxloc = start + self.maxLen
        maxloc = min(maxloc, instrlen)
        while loc < maxloc and instring[loc] in bodychars:
            loc += 1

        throwException = False
        if loc - start < self.minLen:
            throwException = True
        if self.maxSpecified and loc < instrlen and instring[loc] in bodychars:
            throwException = True
        if self.asKeyword:
            if start > 0 and instring[start - 1] in bodychars or loc < instrlen and instring[loc] in bodychars:
                throwException = True
        if throwException:
            raise ParseException(instring, loc, self.errmsg, self)
        return (loc, instring[start:loc])

    def __str__(self):
        try:
            return super(Word, self).__str__()
        except:
            pass

        if self.strRepr is None:

            def charsAsStr(s):
                if len(s) > 4:
                    return s[:4] + '...'
                else:
                    return s

            if self.initCharsOrig != self.bodyCharsOrig:
                self.strRepr = 'W:(%s,%s)' % (charsAsStr(self.initCharsOrig), charsAsStr(self.bodyCharsOrig))
            else:
                self.strRepr = 'W:(%s)' % charsAsStr(self.initCharsOrig)
        return self.strRepr


class Regex(Token):
    compiledREtype = type(re.compile('[A-Z]'))

    def __init__(self, pattern, flags = 0):
        super(Regex, self).__init__()
        if isinstance(pattern, basestring):
            if len(pattern) == 0:
                warnings.warn('null string passed to Regex; use Empty() instead', SyntaxWarning, stacklevel=2)
            self.pattern = pattern
            self.flags = flags
            try:
                self.re = re.compile(self.pattern, self.flags)
                self.reString = self.pattern
            except sre_constants.error:
                warnings.warn('invalid pattern (%s) passed to Regex' % pattern, SyntaxWarning, stacklevel=2)
                raise

        elif isinstance(pattern, Regex.compiledREtype):
            self.re = pattern
            self.pattern = self.reString = str(pattern)
            self.flags = flags
        else:
            raise ValueError('Regex may only be constructed with a string or a compiled RE object')
        self.name = _ustr(self)
        self.errmsg = 'Expected ' + self.name
        self.mayIndexError = False
        self.mayReturnEmpty = True

    def parseImpl(self, instring, loc, doActions = True):
        result = self.re.match(instring, loc)
        if not result:
            raise ParseException(instring, loc, self.errmsg, self)
        loc = result.end()
        d = result.groupdict()
        ret = ParseResults(result.group())
        if d:
            for k in d:
                ret[k] = d[k]

        return (loc, ret)

    def __str__(self):
        try:
            return super(Regex, self).__str__()
        except:
            pass

        if self.strRepr is None:
            self.strRepr = 'Re:(%s)' % repr(self.pattern)
        return self.strRepr


class QuotedString(Token):

    def __init__(self, quoteChar, escChar = None, escQuote = None, multiline = False, unquoteResults = True, endQuoteChar = None):
        super(QuotedString, self).__init__()
        quoteChar = quoteChar.strip()
        if len(quoteChar) == 0:
            warnings.warn('quoteChar cannot be the empty string', SyntaxWarning, stacklevel=2)
            raise SyntaxError()
        if endQuoteChar is None:
            endQuoteChar = quoteChar
        else:
            endQuoteChar = endQuoteChar.strip()
            if len(endQuoteChar) == 0:
                warnings.warn('endQuoteChar cannot be the empty string', SyntaxWarning, stacklevel=2)
                raise SyntaxError()
        self.quoteChar = quoteChar
        self.quoteCharLen = len(quoteChar)
        self.firstQuoteChar = quoteChar[0]
        self.endQuoteChar = endQuoteChar
        self.endQuoteCharLen = len(endQuoteChar)
        self.escChar = escChar
        self.escQuote = escQuote
        self.unquoteResults = unquoteResults
        if multiline:
            self.flags = re.MULTILINE | re.DOTALL
            self.pattern = '%s(?:[^%s%s]' % (re.escape(self.quoteChar), _escapeRegexRangeChars(self.endQuoteChar[0]), escChar is not None and _escapeRegexRangeChars(escChar) or '')
        else:
            self.flags = 0
            self.pattern = '%s(?:[^%s\\n\\r%s]' % (re.escape(self.quoteChar), _escapeRegexRangeChars(self.endQuoteChar[0]), escChar is not None and _escapeRegexRangeChars(escChar) or '')
        if len(self.endQuoteChar) > 1:
            self.pattern += '|(?:' + ')|(?:'.join(('%s[^%s]' % (re.escape(self.endQuoteChar[:i]), _escapeRegexRangeChars(self.endQuoteChar[i])) for i in range(len(self.endQuoteChar) - 1, 0, -1))) + ')'
        if escQuote:
            self.pattern += '|(?:%s)' % re.escape(escQuote)
        if escChar:
            self.pattern += '|(?:%s.)' % re.escape(escChar)
            self.escCharReplacePattern = re.escape(self.escChar) + '(.)'
        self.pattern += ')*%s' % re.escape(self.endQuoteChar)
        try:
            self.re = re.compile(self.pattern, self.flags)
            self.reString = self.pattern
        except sre_constants.error:
            warnings.warn('invalid pattern (%s) passed to Regex' % self.pattern, SyntaxWarning, stacklevel=2)
            raise

        self.name = _ustr(self)
        self.errmsg = 'Expected ' + self.name
        self.mayIndexError = False
        self.mayReturnEmpty = True

    def parseImpl(self, instring, loc, doActions = True):
        result = instring[loc] == self.firstQuoteChar and self.re.match(instring, loc) or None
        if not result:
            raise ParseException(instring, loc, self.errmsg, self)
        loc = result.end()
        ret = result.group()
        if self.unquoteResults:
            ret = ret[self.quoteCharLen:-self.endQuoteCharLen]
            if isinstance(ret, basestring):
                if self.escChar:
                    ret = re.sub(self.escCharReplacePattern, '\\g<1>', ret)
                if self.escQuote:
                    ret = ret.replace(self.escQuote, self.endQuoteChar)
        return (loc, ret)

    def __str__(self):
        try:
            return super(QuotedString, self).__str__()
        except:
            pass

        if self.strRepr is None:
            self.strRepr = 'quoted string, starting with %s ending with %s' % (self.quoteChar, self.endQuoteChar)
        return self.strRepr


class CharsNotIn(Token):

    def __init__(self, notChars, min = 1, max = 0, exact = 0):
        super(CharsNotIn, self).__init__()
        self.skipWhitespace = False
        self.notChars = notChars
        if min < 1:
            raise ValueError('cannot specify a minimum length < 1; use Optional(CharsNotIn()) if zero-length char group is permitted')
        self.minLen = min
        if max > 0:
            self.maxLen = max
        else:
            self.maxLen = _MAX_INT
        if exact > 0:
            self.maxLen = exact
            self.minLen = exact
        self.name = _ustr(self)
        self.errmsg = 'Expected ' + self.name
        self.mayReturnEmpty = self.minLen == 0
        self.mayIndexError = False

    def parseImpl(self, instring, loc, doActions = True):
        if instring[loc] in self.notChars:
            raise ParseException(instring, loc, self.errmsg, self)
        start = loc
        loc += 1
        notchars = self.notChars
        maxlen = min(start + self.maxLen, len(instring))
        while loc < maxlen and instring[loc] not in notchars:
            loc += 1

        if loc - start < self.minLen:
            raise ParseException(instring, loc, self.errmsg, self)
        return (loc, instring[start:loc])

    def __str__(self):
        try:
            return super(CharsNotIn, self).__str__()
        except:
            pass

        if self.strRepr is None:
            if len(self.notChars) > 4:
                self.strRepr = '!W:(%s...)' % self.notChars[:4]
            else:
                self.strRepr = '!W:(%s)' % self.notChars
        return self.strRepr


class White(Token):
    whiteStrs = {' ': '<SPC>',
     '\t': '<TAB>',
     '\n': '<LF>',
     '\r': '<CR>',
     '\x0c': '<FF>'}

    def __init__(self, ws = ' \t\r\n', min = 1, max = 0, exact = 0):
        super(White, self).__init__()
        self.matchWhite = ws
        self.setWhitespaceChars(''.join((c for c in self.whiteChars if c not in self.matchWhite)))
        self.name = ''.join((White.whiteStrs[c] for c in self.matchWhite))
        self.mayReturnEmpty = True
        self.errmsg = 'Expected ' + self.name
        self.minLen = min
        if max > 0:
            self.maxLen = max
        else:
            self.maxLen = _MAX_INT
        if exact > 0:
            self.maxLen = exact
            self.minLen = exact

    def parseImpl(self, instring, loc, doActions = True):
        if instring[loc] not in self.matchWhite:
            raise ParseException(instring, loc, self.errmsg, self)
        start = loc
        loc += 1
        maxloc = start + self.maxLen
        maxloc = min(maxloc, len(instring))
        while loc < maxloc and instring[loc] in self.matchWhite:
            loc += 1

        if loc - start < self.minLen:
            raise ParseException(instring, loc, self.errmsg, self)
        return (loc, instring[start:loc])


class _PositionToken(Token):

    def __init__(self):
        super(_PositionToken, self).__init__()
        self.name = self.__class__.__name__
        self.mayReturnEmpty = True
        self.mayIndexError = False


class GoToColumn(_PositionToken):

    def __init__(self, colno):
        super(GoToColumn, self).__init__()
        self.col = colno

    def preParse(self, instring, loc):
        if col(loc, instring) != self.col:
            instrlen = len(instring)
            if self.ignoreExprs:
                loc = self._skipIgnorables(instring, loc)
            while loc < instrlen and instring[loc].isspace() and col(loc, instring) != self.col:
                loc += 1

        return loc

    def parseImpl(self, instring, loc, doActions = True):
        thiscol = col(loc, instring)
        if thiscol > self.col:
            raise ParseException(instring, loc, 'Text not in expected column', self)
        newloc = loc + self.col - thiscol
        ret = instring[loc:newloc]
        return (newloc, ret)


class LineStart(_PositionToken):

    def __init__(self):
        super(LineStart, self).__init__()
        self.setWhitespaceChars(ParserElement.DEFAULT_WHITE_CHARS.replace('\n', ''))
        self.errmsg = 'Expected start of line'

    def preParse(self, instring, loc):
        preloc = super(LineStart, self).preParse(instring, loc)
        if instring[preloc] == '\n':
            loc += 1
        return loc

    def parseImpl(self, instring, loc, doActions = True):
        if not (loc == 0 or loc == self.preParse(instring, 0) or instring[loc - 1] == '\n'):
            raise ParseException(instring, loc, self.errmsg, self)
        return (loc, [])


class LineEnd(_PositionToken):

    def __init__(self):
        super(LineEnd, self).__init__()
        self.setWhitespaceChars(ParserElement.DEFAULT_WHITE_CHARS.replace('\n', ''))
        self.errmsg = 'Expected end of line'

    def parseImpl(self, instring, loc, doActions = True):
        if loc < len(instring):
            if instring[loc] == '\n':
                return (loc + 1, '\n')
            raise ParseException(instring, loc, self.errmsg, self)
        else:
            if loc == len(instring):
                return (loc + 1, [])
            raise ParseException(instring, loc, self.errmsg, self)


class StringStart(_PositionToken):

    def __init__(self):
        super(StringStart, self).__init__()
        self.errmsg = 'Expected start of text'

    def parseImpl(self, instring, loc, doActions = True):
        if loc != 0:
            if loc != self.preParse(instring, 0):
                raise ParseException(instring, loc, self.errmsg, self)
        return (loc, [])


class StringEnd(_PositionToken):

    def __init__(self):
        super(StringEnd, self).__init__()
        self.errmsg = 'Expected end of text'

    def parseImpl(self, instring, loc, doActions = True):
        if loc < len(instring):
            raise ParseException(instring, loc, self.errmsg, self)
        else:
            if loc == len(instring):
                return (loc + 1, [])
            if loc > len(instring):
                return (loc, [])
            raise ParseException(instring, loc, self.errmsg, self)


class WordStart(_PositionToken):

    def __init__(self, wordChars = printables):
        super(WordStart, self).__init__()
        self.wordChars = set(wordChars)
        self.errmsg = 'Not at the start of a word'

    def parseImpl(self, instring, loc, doActions = True):
        if loc != 0:
            if instring[loc - 1] in self.wordChars or instring[loc] not in self.wordChars:
                raise ParseException(instring, loc, self.errmsg, self)
        return (loc, [])


class WordEnd(_PositionToken):

    def __init__(self, wordChars = printables):
        super(WordEnd, self).__init__()
        self.wordChars = set(wordChars)
        self.skipWhitespace = False
        self.errmsg = 'Not at the end of a word'

    def parseImpl(self, instring, loc, doActions = True):
        instrlen = len(instring)
        if instrlen > 0 and loc < instrlen:
            if instring[loc] in self.wordChars or instring[loc - 1] not in self.wordChars:
                raise ParseException(instring, loc, self.errmsg, self)
        return (loc, [])


class ParseExpression(ParserElement):

    def __init__(self, exprs, savelist = False):
        super(ParseExpression, self).__init__(savelist)
        if isinstance(exprs, _generatorType):
            exprs = list(exprs)
        if isinstance(exprs, basestring):
            self.exprs = [Literal(exprs)]
        elif isinstance(exprs, collections.Sequence):
            if all((isinstance(expr, basestring) for expr in exprs)):
                exprs = map(Literal, exprs)
            self.exprs = list(exprs)
        else:
            try:
                self.exprs = list(exprs)
            except TypeError:
                self.exprs = [exprs]

        self.callPreparse = False

    def __getitem__(self, i):
        return self.exprs[i]

    def append(self, other):
        self.exprs.append(other)
        self.strRepr = None
        return self

    def leaveWhitespace(self):
        self.skipWhitespace = False
        self.exprs = [ e.copy() for e in self.exprs ]
        for e in self.exprs:
            e.leaveWhitespace()

        return self

    def ignore(self, other):
        if isinstance(other, Suppress):
            if other not in self.ignoreExprs:
                super(ParseExpression, self).ignore(other)
                for e in self.exprs:
                    e.ignore(self.ignoreExprs[-1])

        else:
            super(ParseExpression, self).ignore(other)
            for e in self.exprs:
                e.ignore(self.ignoreExprs[-1])

        return self

    def __str__(self):
        try:
            return super(ParseExpression, self).__str__()
        except:
            pass

        if self.strRepr is None:
            self.strRepr = '%s:(%s)' % (self.__class__.__name__, _ustr(self.exprs))
        return self.strRepr

    def streamline(self):
        super(ParseExpression, self).streamline()
        for e in self.exprs:
            e.streamline()

        if len(self.exprs) == 2:
            other = self.exprs[0]
            if isinstance(other, self.__class__) and not other.parseAction and other.resultsName is None and not other.debug:
                self.exprs = other.exprs[:] + [self.exprs[1]]
                self.strRepr = None
                self.mayReturnEmpty |= other.mayReturnEmpty
                self.mayIndexError |= other.mayIndexError
            other = self.exprs[-1]
            if isinstance(other, self.__class__) and not other.parseAction and other.resultsName is None and not other.debug:
                self.exprs = self.exprs[:-1] + other.exprs[:]
                self.strRepr = None
                self.mayReturnEmpty |= other.mayReturnEmpty
                self.mayIndexError |= other.mayIndexError
        self.errmsg = 'Expected ' + str(self)
        return self

    def setResultsName(self, name, listAllMatches = False):
        ret = super(ParseExpression, self).setResultsName(name, listAllMatches)
        return ret

    def validate(self, validateTrace = []):
        tmp = validateTrace[:] + [self]
        for e in self.exprs:
            e.validate(tmp)

        self.checkRecursion([])

    def copy(self):
        ret = super(ParseExpression, self).copy()
        ret.exprs = [ e.copy() for e in self.exprs ]
        return ret


class And(ParseExpression):

    class _ErrorStop(Empty):

        def __init__(self, *args, **kwargs):
            super(And._ErrorStop, self).__init__(*args, **kwargs)
            self.name = '-'
            self.leaveWhitespace()

    def __init__(self, exprs, savelist = True):
        super(And, self).__init__(exprs, savelist)
        self.mayReturnEmpty = all((e.mayReturnEmpty for e in self.exprs))
        self.setWhitespaceChars(self.exprs[0].whiteChars)
        self.skipWhitespace = self.exprs[0].skipWhitespace
        self.callPreparse = True

    def parseImpl(self, instring, loc, doActions = True):
        loc, resultlist = self.exprs[0]._parse(instring, loc, doActions, callPreParse=False)
        errorStop = False
        for e in self.exprs[1:]:
            if isinstance(e, And._ErrorStop):
                errorStop = True
                continue
            if errorStop:
                try:
                    loc, exprtokens = e._parse(instring, loc, doActions)
                except ParseSyntaxException:
                    raise
                except ParseBaseException as pe:
                    pe.__traceback__ = None
                    raise ParseSyntaxException(pe)
                except IndexError:
                    raise ParseSyntaxException(ParseException(instring, len(instring), self.errmsg, self))

            else:
                loc, exprtokens = e._parse(instring, loc, doActions)
            if exprtokens or exprtokens.haskeys():
                resultlist += exprtokens

        return (loc, resultlist)

    def __iadd__(self, other):
        if isinstance(other, basestring):
            other = Literal(other)
        return self.append(other)

    def checkRecursion(self, parseElementList):
        subRecCheckList = parseElementList[:] + [self]
        for e in self.exprs:
            e.checkRecursion(subRecCheckList)
            if not e.mayReturnEmpty:
                break

    def __str__(self):
        if hasattr(self, 'name'):
            return self.name
        if self.strRepr is None:
            self.strRepr = '{' + ' '.join((_ustr(e) for e in self.exprs)) + '}'
        return self.strRepr


class Or(ParseExpression):

    def __init__(self, exprs, savelist = False):
        super(Or, self).__init__(exprs, savelist)
        if self.exprs:
            self.mayReturnEmpty = any((e.mayReturnEmpty for e in self.exprs))
        else:
            self.mayReturnEmpty = True

    def parseImpl(self, instring, loc, doActions = True):
        maxExcLoc = -1
        maxException = None
        matches = []
        for e in self.exprs:
            try:
                loc2 = e.tryParse(instring, loc)
            except ParseException as err:
                err.__traceback__ = None
                if err.loc > maxExcLoc:
                    maxException = err
                    maxExcLoc = err.loc
            except IndexError:
                if len(instring) > maxExcLoc:
                    maxException = ParseException(instring, len(instring), e.errmsg, self)
                    maxExcLoc = len(instring)
            else:
                matches.append((loc2, e))

        if matches:
            matches.sort(key=lambda x: -x[0])
            for _, e in matches:
                try:
                    return e._parse(instring, loc, doActions)
                except ParseException as err:
                    err.__traceback__ = None
                    if err.loc > maxExcLoc:
                        maxException = err
                        maxExcLoc = err.loc

        if maxException is not None:
            maxException.msg = self.errmsg
            raise maxException
        else:
            raise ParseException(instring, loc, 'no defined alternatives to match', self)

    def __ixor__(self, other):
        if isinstance(other, basestring):
            other = ParserElement.literalStringClass(other)
        return self.append(other)

    def __str__(self):
        if hasattr(self, 'name'):
            return self.name
        if self.strRepr is None:
            self.strRepr = '{' + ' ^ '.join((_ustr(e) for e in self.exprs)) + '}'
        return self.strRepr

    def checkRecursion(self, parseElementList):
        subRecCheckList = parseElementList[:] + [self]
        for e in self.exprs:
            e.checkRecursion(subRecCheckList)


class MatchFirst(ParseExpression):

    def __init__(self, exprs, savelist = False):
        super(MatchFirst, self).__init__(exprs, savelist)
        if self.exprs:
            self.mayReturnEmpty = any((e.mayReturnEmpty for e in self.exprs))
        else:
            self.mayReturnEmpty = True

    def parseImpl(self, instring, loc, doActions = True):
        maxExcLoc = -1
        maxException = None
        for e in self.exprs:
            try:
                ret = e._parse(instring, loc, doActions)
                return ret
            except ParseException as err:
                if err.loc > maxExcLoc:
                    maxException = err
                    maxExcLoc = err.loc
            except IndexError:
                if len(instring) > maxExcLoc:
                    maxException = ParseException(instring, len(instring), e.errmsg, self)
                    maxExcLoc = len(instring)

        else:
            if maxException is not None:
                maxException.msg = self.errmsg
                raise maxException
            else:
                raise ParseException(instring, loc, 'no defined alternatives to match', self)

    def __ior__(self, other):
        if isinstance(other, basestring):
            other = ParserElement.literalStringClass(other)
        return self.append(other)

    def __str__(self):
        if hasattr(self, 'name'):
            return self.name
        if self.strRepr is None:
            self.strRepr = '{' + ' | '.join((_ustr(e) for e in self.exprs)) + '}'
        return self.strRepr

    def checkRecursion(self, parseElementList):
        subRecCheckList = parseElementList[:] + [self]
        for e in self.exprs:
            e.checkRecursion(subRecCheckList)


class Each(ParseExpression):

    def __init__(self, exprs, savelist = True):
        super(Each, self).__init__(exprs, savelist)
        self.mayReturnEmpty = all((e.mayReturnEmpty for e in self.exprs))
        self.skipWhitespace = True
        self.initExprGroups = True

    def parseImpl(self, instring, loc, doActions = True):
        if self.initExprGroups:
            self.opt1map = dict(((id(e.expr), e) for e in self.exprs if isinstance(e, Optional)))
            opt1 = [ e.expr for e in self.exprs if isinstance(e, Optional) ]
            opt2 = [ e for e in self.exprs if e.mayReturnEmpty and not isinstance(e, Optional) ]
            self.optionals = opt1 + opt2
            self.multioptionals = [ e.expr for e in self.exprs if isinstance(e, ZeroOrMore) ]
            self.multirequired = [ e.expr for e in self.exprs if isinstance(e, OneOrMore) ]
            self.required = [ e for e in self.exprs if not isinstance(e, (Optional, ZeroOrMore, OneOrMore)) ]
            self.required += self.multirequired
            self.initExprGroups = False
        tmpLoc = loc
        tmpReqd = self.required[:]
        tmpOpt = self.optionals[:]
        matchOrder = []
        keepMatching = True
        while keepMatching:
            tmpExprs = tmpReqd + tmpOpt + self.multioptionals + self.multirequired
            failed = []
            for e in tmpExprs:
                try:
                    tmpLoc = e.tryParse(instring, tmpLoc)
                except ParseException:
                    failed.append(e)
                else:
                    matchOrder.append(self.opt1map.get(id(e), e))
                    if e in tmpReqd:
                        tmpReqd.remove(e)
                    elif e in tmpOpt:
                        tmpOpt.remove(e)

            if len(failed) == len(tmpExprs):
                keepMatching = False

        if tmpReqd:
            missing = ', '.join((_ustr(e) for e in tmpReqd))
            raise ParseException(instring, loc, 'Missing one or more required elements (%s)' % missing)
        matchOrder += [ e for e in self.exprs if isinstance(e, Optional) and e.expr in tmpOpt ]
        resultlist = []
        for e in matchOrder:
            loc, results = e._parse(instring, loc, doActions)
            resultlist.append(results)

        finalResults = ParseResults([])
        for r in resultlist:
            dups = {}
            for k in r.keys():
                if k in finalResults:
                    tmp = ParseResults(finalResults[k])
                    tmp += ParseResults(r[k])
                    dups[k] = tmp

            finalResults += ParseResults(r)
            for k, v in dups.items():
                finalResults[k] = v

        return (loc, finalResults)

    def __str__(self):
        if hasattr(self, 'name'):
            return self.name
        if self.strRepr is None:
            self.strRepr = '{' + ' & '.join((_ustr(e) for e in self.exprs)) + '}'
        return self.strRepr

    def checkRecursion(self, parseElementList):
        subRecCheckList = parseElementList[:] + [self]
        for e in self.exprs:
            e.checkRecursion(subRecCheckList)


class ParseElementEnhance(ParserElement):

    def __init__(self, expr, savelist = False):
        super(ParseElementEnhance, self).__init__(savelist)
        if isinstance(expr, basestring):
            expr = Literal(expr)
        self.expr = expr
        self.strRepr = None
        if expr is not None:
            self.mayIndexError = expr.mayIndexError
            self.mayReturnEmpty = expr.mayReturnEmpty
            self.setWhitespaceChars(expr.whiteChars)
            self.skipWhitespace = expr.skipWhitespace
            self.saveAsList = expr.saveAsList
            self.callPreparse = expr.callPreparse
            self.ignoreExprs.extend(expr.ignoreExprs)

    def parseImpl(self, instring, loc, doActions = True):
        if self.expr is not None:
            return self.expr._parse(instring, loc, doActions, callPreParse=False)
        raise ParseException('', loc, self.errmsg, self)

    def leaveWhitespace(self):
        self.skipWhitespace = False
        self.expr = self.expr.copy()
        if self.expr is not None:
            self.expr.leaveWhitespace()
        return self

    def ignore(self, other):
        if isinstance(other, Suppress):
            if other not in self.ignoreExprs:
                super(ParseElementEnhance, self).ignore(other)
                if self.expr is not None:
                    self.expr.ignore(self.ignoreExprs[-1])
        else:
            super(ParseElementEnhance, self).ignore(other)
            if self.expr is not None:
                self.expr.ignore(self.ignoreExprs[-1])
        return self

    def streamline(self):
        super(ParseElementEnhance, self).streamline()
        if self.expr is not None:
            self.expr.streamline()
        return self

    def checkRecursion(self, parseElementList):
        if self in parseElementList:
            raise RecursiveGrammarException(parseElementList + [self])
        subRecCheckList = parseElementList[:] + [self]
        if self.expr is not None:
            self.expr.checkRecursion(subRecCheckList)

    def validate(self, validateTrace = []):
        tmp = validateTrace[:] + [self]
        if self.expr is not None:
            self.expr.validate(tmp)
        self.checkRecursion([])

    def __str__(self):
        try:
            return super(ParseElementEnhance, self).__str__()
        except:
            pass

        if self.strRepr is None and self.expr is not None:
            self.strRepr = '%s:(%s)' % (self.__class__.__name__, _ustr(self.expr))
        return self.strRepr


class FollowedBy(ParseElementEnhance):

    def __init__(self, expr):
        super(FollowedBy, self).__init__(expr)
        self.mayReturnEmpty = True

    def parseImpl(self, instring, loc, doActions = True):
        self.expr.tryParse(instring, loc)
        return (loc, [])


class NotAny(ParseElementEnhance):

    def __init__(self, expr):
        super(NotAny, self).__init__(expr)
        self.skipWhitespace = False
        self.mayReturnEmpty = True
        self.errmsg = 'Found unwanted token, ' + _ustr(self.expr)

    def parseImpl(self, instring, loc, doActions = True):
        try:
            self.expr.tryParse(instring, loc)
        except (ParseException, IndexError):
            pass
        else:
            raise ParseException(instring, loc, self.errmsg, self)

        return (loc, [])

    def __str__(self):
        if hasattr(self, 'name'):
            return self.name
        if self.strRepr is None:
            self.strRepr = '~{' + _ustr(self.expr) + '}'
        return self.strRepr


class ZeroOrMore(ParseElementEnhance):

    def __init__(self, expr):
        super(ZeroOrMore, self).__init__(expr)
        self.mayReturnEmpty = True

    def parseImpl(self, instring, loc, doActions = True):
        tokens = []
        try:
            loc, tokens = self.expr._parse(instring, loc, doActions, callPreParse=False)
            hasIgnoreExprs = len(self.ignoreExprs) > 0
            while 1:
                if hasIgnoreExprs:
                    preloc = self._skipIgnorables(instring, loc)
                else:
                    preloc = loc
                loc, tmptokens = self.expr._parse(instring, preloc, doActions)
                if tmptokens or tmptokens.haskeys():
                    tokens += tmptokens

        except (ParseException, IndexError):
            pass

        return (loc, tokens)

    def __str__(self):
        if hasattr(self, 'name'):
            return self.name
        if self.strRepr is None:
            self.strRepr = '[' + _ustr(self.expr) + ']...'
        return self.strRepr

    def setResultsName(self, name, listAllMatches = False):
        ret = super(ZeroOrMore, self).setResultsName(name, listAllMatches)
        ret.saveAsList = True
        return ret


class OneOrMore(ParseElementEnhance):

    def parseImpl(self, instring, loc, doActions = True):
        loc, tokens = self.expr._parse(instring, loc, doActions, callPreParse=False)
        try:
            hasIgnoreExprs = len(self.ignoreExprs) > 0
            while 1:
                if hasIgnoreExprs:
                    preloc = self._skipIgnorables(instring, loc)
                else:
                    preloc = loc
                loc, tmptokens = self.expr._parse(instring, preloc, doActions)
                if tmptokens or tmptokens.haskeys():
                    tokens += tmptokens

        except (ParseException, IndexError):
            pass

        return (loc, tokens)

    def __str__(self):
        if hasattr(self, 'name'):
            return self.name
        if self.strRepr is None:
            self.strRepr = '{' + _ustr(self.expr) + '}...'
        return self.strRepr

    def setResultsName(self, name, listAllMatches = False):
        ret = super(OneOrMore, self).setResultsName(name, listAllMatches)
        ret.saveAsList = True
        return ret


class _NullToken(object):

    def __bool__(self):
        return False

    __nonzero__ = __bool__

    def __str__(self):
        return ''


_optionalNotMatched = _NullToken()

class Optional(ParseElementEnhance):

    def __init__(self, expr, default = _optionalNotMatched):
        super(Optional, self).__init__(expr, savelist=False)
        self.defaultValue = default
        self.mayReturnEmpty = True

    def parseImpl(self, instring, loc, doActions = True):
        try:
            loc, tokens = self.expr._parse(instring, loc, doActions, callPreParse=False)
        except (ParseException, IndexError):
            if self.defaultValue is not _optionalNotMatched:
                if self.expr.resultsName:
                    tokens = ParseResults([self.defaultValue])
                    tokens[self.expr.resultsName] = self.defaultValue
                else:
                    tokens = [self.defaultValue]
            else:
                tokens = []

        return (loc, tokens)

    def __str__(self):
        if hasattr(self, 'name'):
            return self.name
        if self.strRepr is None:
            self.strRepr = '[' + _ustr(self.expr) + ']'
        return self.strRepr


class SkipTo(ParseElementEnhance):

    def __init__(self, other, include = False, ignore = None, failOn = None):
        super(SkipTo, self).__init__(other)
        self.ignoreExpr = ignore
        self.mayReturnEmpty = True
        self.mayIndexError = False
        self.includeMatch = include
        self.asList = False
        if failOn is not None and isinstance(failOn, basestring):
            self.failOn = Literal(failOn)
        else:
            self.failOn = failOn
        self.errmsg = 'No match found for ' + _ustr(self.expr)

    def parseImpl(self, instring, loc, doActions = True):
        startLoc = loc
        instrlen = len(instring)
        expr = self.expr
        failParse = False
        while loc <= instrlen:
            try:
                if self.failOn:
                    try:
                        self.failOn.tryParse(instring, loc)
                    except ParseBaseException:
                        pass
                    else:
                        failParse = True
                        raise ParseException(instring, loc, 'Found expression ' + str(self.failOn))

                    failParse = False
                if self.ignoreExpr is not None:
                    while 1:
                        try:
                            loc = self.ignoreExpr.tryParse(instring, loc)
                        except ParseBaseException:
                            break

                expr._parse(instring, loc, doActions=False, callPreParse=False)
                skipText = instring[startLoc:loc]
                if self.includeMatch:
                    loc, mat = expr._parse(instring, loc, doActions, callPreParse=False)
                    if mat:
                        skipRes = ParseResults(skipText)
                        skipRes += mat
                        return (loc, [skipRes])
                    else:
                        return (loc, [skipText])
                else:
                    return (loc, [skipText])
            except (ParseException, IndexError):
                if failParse:
                    raise
                else:
                    loc += 1

        raise ParseException(instring, loc, self.errmsg, self)


class Forward(ParseElementEnhance):

    def __init__(self, other = None):
        super(Forward, self).__init__(other, savelist=False)

    def __lshift__(self, other):
        if isinstance(other, basestring):
            other = ParserElement.literalStringClass(other)
        self.expr = other
        self.mayReturnEmpty = other.mayReturnEmpty
        self.strRepr = None
        self.mayIndexError = self.expr.mayIndexError
        self.mayReturnEmpty = self.expr.mayReturnEmpty
        self.setWhitespaceChars(self.expr.whiteChars)
        self.skipWhitespace = self.expr.skipWhitespace
        self.saveAsList = self.expr.saveAsList
        self.ignoreExprs.extend(self.expr.ignoreExprs)
        return self

    def __ilshift__(self, other):
        return self << other

    def leaveWhitespace(self):
        self.skipWhitespace = False
        return self

    def streamline(self):
        if not self.streamlined:
            self.streamlined = True
            if self.expr is not None:
                self.expr.streamline()
        return self

    def validate(self, validateTrace = []):
        if self not in validateTrace:
            tmp = validateTrace[:] + [self]
            if self.expr is not None:
                self.expr.validate(tmp)
        self.checkRecursion([])

    def __str__(self):
        if hasattr(self, 'name'):
            return self.name
        self._revertClass = self.__class__
        self.__class__ = _ForwardNoRecurse
        try:
            if self.expr is not None:
                retString = _ustr(self.expr)
            else:
                retString = 'None'
        finally:
            self.__class__ = self._revertClass

        return self.__class__.__name__ + ': ' + retString

    def copy(self):
        if self.expr is not None:
            return super(Forward, self).copy()
        else:
            ret = Forward()
            ret <<= self
            return ret


class _ForwardNoRecurse(Forward):

    def __str__(self):
        return '...'


class TokenConverter(ParseElementEnhance):

    def __init__(self, expr, savelist = False):
        super(TokenConverter, self).__init__(expr)
        self.saveAsList = False


class Upcase(TokenConverter):

    def __init__(self, *args):
        super(Upcase, self).__init__(*args)
        warnings.warn('Upcase class is deprecated, use upcaseTokens parse action instead', DeprecationWarning, stacklevel=2)

    def postParse(self, instring, loc, tokenlist):
        return list(map(str.upper, tokenlist))


class Combine(TokenConverter):

    def __init__(self, expr, joinString = '', adjacent = True):
        super(Combine, self).__init__(expr)
        if adjacent:
            self.leaveWhitespace()
        self.adjacent = adjacent
        self.skipWhitespace = True
        self.joinString = joinString
        self.callPreparse = True

    def ignore(self, other):
        if self.adjacent:
            ParserElement.ignore(self, other)
        else:
            super(Combine, self).ignore(other)
        return self

    def postParse(self, instring, loc, tokenlist):
        retToks = tokenlist.copy()
        del retToks[:]
        retToks += ParseResults([''.join(tokenlist._asStringList(self.joinString))], modal=self.modalResults)
        if self.resultsName and retToks.haskeys():
            return [retToks]
        else:
            return retToks


class Group(TokenConverter):

    def __init__(self, expr):
        super(Group, self).__init__(expr)
        self.saveAsList = True

    def postParse(self, instring, loc, tokenlist):
        return [tokenlist]


class Dict(TokenConverter):

    def __init__(self, expr):
        super(Dict, self).__init__(expr)
        self.saveAsList = True

    def postParse(self, instring, loc, tokenlist):
        for i, tok in enumerate(tokenlist):
            if len(tok) == 0:
                continue
            ikey = tok[0]
            if isinstance(ikey, int):
                ikey = _ustr(tok[0]).strip()
            if len(tok) == 1:
                tokenlist[ikey] = _ParseResultsWithOffset('', i)
            elif len(tok) == 2 and not isinstance(tok[1], ParseResults):
                tokenlist[ikey] = _ParseResultsWithOffset(tok[1], i)
            else:
                dictvalue = tok.copy()
                del dictvalue[0]
                if len(dictvalue) != 1 or isinstance(dictvalue, ParseResults) and dictvalue.haskeys():
                    tokenlist[ikey] = _ParseResultsWithOffset(dictvalue, i)
                else:
                    tokenlist[ikey] = _ParseResultsWithOffset(dictvalue[0], i)

        if self.resultsName:
            return [tokenlist]
        else:
            return tokenlist


class Suppress(TokenConverter):

    def postParse(self, instring, loc, tokenlist):
        return []

    def suppress(self):
        return self


class OnlyOnce(object):

    def __init__(self, methodCall):
        self.callable = _trim_arity(methodCall)
        self.called = False

    def __call__(self, s, l, t):
        if not self.called:
            results = self.callable(s, l, t)
            self.called = True
            return results
        raise ParseException(s, l, '')

    def reset(self):
        self.called = False


def traceParseAction(f):
    f = _trim_arity(f)

    def z(*paArgs):
        thisFunc = f.func_name
        s, l, t = paArgs[-3:]
        if len(paArgs) > 3:
            thisFunc = paArgs[0].__class__.__name__ + '.' + thisFunc
        sys.stderr.write(">>entering %s(line: '%s', %d, %s)\n" % (thisFunc,
         line(l, s),
         l,
         t))
        try:
            ret = f(*paArgs)
        except Exception as exc:
            sys.stderr.write('<<leaving %s (exception: %s)\n' % (thisFunc, exc))
            raise

        sys.stderr.write('<<leaving %s (ret: %s)\n' % (thisFunc, ret))
        return ret

    try:
        z.__name__ = f.__name__
    except AttributeError:
        pass

    return z


def delimitedList(expr, delim = ',', combine = False):
    dlName = _ustr(expr) + ' [' + _ustr(delim) + ' ' + _ustr(expr) + ']...'
    if combine:
        return Combine(expr + ZeroOrMore(delim + expr)).setName(dlName)
    else:
        return (expr + ZeroOrMore(Suppress(delim) + expr)).setName(dlName)


def countedArray(expr, intExpr = None):
    arrayExpr = Forward()

    def countFieldParseAction(s, l, t):
        n = t[0]
        arrayExpr << (n and Group(And([expr] * n)) or Group(empty))
        return []

    if intExpr is None:
        intExpr = Word(nums).setParseAction(lambda t: int(t[0]))
    else:
        intExpr = intExpr.copy()
    intExpr.setName('arrayLen')
    intExpr.addParseAction(countFieldParseAction, callDuringTry=True)
    return intExpr + arrayExpr


def _flatten(L):
    ret = []
    for i in L:
        if isinstance(i, list):
            ret.extend(_flatten(i))
        else:
            ret.append(i)

    return ret


def matchPreviousLiteral(expr):
    rep = Forward()

    def copyTokenToRepeater(s, l, t):
        if t:
            if len(t) == 1:
                rep << t[0]
            else:
                tflat = _flatten(t.asList())
                rep << And([ Literal(tt) for tt in tflat ])
        else:
            rep << Empty()

    expr.addParseAction(copyTokenToRepeater, callDuringTry=True)
    return rep


def matchPreviousExpr(expr):
    rep = Forward()
    e2 = expr.copy()
    rep <<= e2

    def copyTokenToRepeater(s, l, t):
        matchTokens = _flatten(t.asList())

        def mustMatchTheseTokens(s, l, t):
            theseTokens = _flatten(t.asList())
            if theseTokens != matchTokens:
                raise ParseException('', 0, '')

        rep.setParseAction(mustMatchTheseTokens, callDuringTry=True)

    expr.addParseAction(copyTokenToRepeater, callDuringTry=True)
    return rep


def _escapeRegexRangeChars(s):
    for c in '\\^-]':
        s = s.replace(c, _bslash + c)

    s = s.replace('\n', '\\n')
    s = s.replace('\t', '\\t')
    return _ustr(s)


def oneOf(strs, caseless = False, useRegex = True):
    if caseless:
        isequal = lambda a, b: a.upper() == b.upper()
        masks = lambda a, b: b.upper().startswith(a.upper())
        parseElementClass = CaselessLiteral
    else:
        isequal = lambda a, b: a == b
        masks = lambda a, b: b.startswith(a)
        parseElementClass = Literal
    symbols = []
    if isinstance(strs, basestring):
        symbols = strs.split()
    elif isinstance(strs, collections.Sequence):
        symbols = list(strs[:])
    elif isinstance(strs, _generatorType):
        symbols = list(strs)
    else:
        warnings.warn('Invalid argument to oneOf, expected string or list', SyntaxWarning, stacklevel=2)
    if not symbols:
        return NoMatch()
    i = 0
    while i < len(symbols) - 1:
        cur = symbols[i]
        for j, other in enumerate(symbols[i + 1:]):
            if isequal(other, cur):
                del symbols[i + j + 1]
                break
            elif masks(cur, other):
                del symbols[i + j + 1]
                symbols.insert(i, other)
                cur = other
                break
        else:
            i += 1

    if not caseless and useRegex:
        try:
            if len(symbols) == len(''.join(symbols)):
                return Regex('[%s]' % ''.join((_escapeRegexRangeChars(sym) for sym in symbols)))
            return Regex('|'.join((re.escape(sym) for sym in symbols)))
        except:
            warnings.warn('Exception creating Regex for oneOf, building MatchFirst', SyntaxWarning, stacklevel=2)

    return MatchFirst([ parseElementClass(sym) for sym in symbols ])


def dictOf(key, value):
    return Dict(ZeroOrMore(Group(key + value)))


def originalTextFor(expr, asString = True):
    locMarker = Empty().setParseAction(lambda s, loc, t: loc)
    endlocMarker = locMarker.copy()
    endlocMarker.callPreparse = False
    matchExpr = locMarker('_original_start') + expr + endlocMarker('_original_end')
    if asString:
        extractText = lambda s, l, t: s[t._original_start:t._original_end]
    else:

        def extractText(s, l, t):
            del t[:]
            t.insert(0, s[t._original_start:t._original_end])
            del t['_original_start']
            del t['_original_end']

    matchExpr.setParseAction(extractText)
    return matchExpr


def ungroup(expr):
    return TokenConverter(expr).setParseAction(lambda t: t[0])


def locatedExpr(expr):
    locator = Empty().setParseAction(lambda s, l, t: l)
    return Group(locator('locn_start') + expr('value') + locator.copy().leaveWhitespace()('locn_end'))


empty = Empty().setName('empty')
lineStart = LineStart().setName('lineStart')
lineEnd = LineEnd().setName('lineEnd')
stringStart = StringStart().setName('stringStart')
stringEnd = StringEnd().setName('stringEnd')
_escapedPunc = Word(_bslash, '\\[]-*.$+^?()~ ', exact=2).setParseAction(lambda s, l, t: t[0][1])
_escapedHexChar = Regex('\\\\0?[xX][0-9a-fA-F]+').setParseAction(lambda s, l, t: unichr(int(t[0].lstrip('\\0x'), 16)))
_escapedOctChar = Regex('\\\\0[0-7]+').setParseAction(lambda s, l, t: unichr(int(t[0][1:], 8)))
_singleChar = _escapedPunc | _escapedHexChar | _escapedOctChar | Word(printables, excludeChars='\\]', exact=1) | Regex('\\w', re.UNICODE)
_charRange = Group(_singleChar + Suppress('-') + _singleChar)
_reBracketExpr = Literal('[') + Optional('^').setResultsName('negate') + Group(OneOrMore(_charRange | _singleChar)).setResultsName('body') + ']'

def srange(s):
    _expanded = lambda p:     if not isinstance(p, ParseResults):
p''.join((unichr(c) for c in range(ord(p[0]), ord(p[1]) + 1)))
    try:
        return ''.join((_expanded(part) for part in _reBracketExpr.parseString(s).body))
    except:
        return ''


def matchOnlyAtCol(n):

    def verifyCol(strg, locn, toks):
        if col(locn, strg) != n:
            raise ParseException(strg, locn, 'matched token not at column %d' % n)

    return verifyCol


def replaceWith(replStr):
    return functools.partial(next, itertools.repeat([replStr]))


def removeQuotes(s, l, t):
    return t[0][1:-1]


def upcaseTokens(s, l, t):
    return [ tt.upper() for tt in map(_ustr, t) ]


def downcaseTokens(s, l, t):
    return [ tt.lower() for tt in map(_ustr, t) ]


def keepOriginalText(s, startLoc, t):
    try:
        endloc = getTokensEndLoc()
    except ParseException:
        raise ParseFatalException('incorrect usage of keepOriginalText - may only be called as a parse action')

    del t[:]
    t += ParseResults(s[startLoc:endloc])
    return t


def getTokensEndLoc():
    import inspect
    fstack = inspect.stack()
    try:
        for f in fstack[2:]:
            if f[3] == '_parseNoCache':
                endloc = f[0].f_locals['loc']
                return endloc
        else:
            raise ParseFatalException('incorrect usage of getTokensEndLoc - may only be called from within a parse action')

    finally:
        del fstack


def _makeTags(tagStr, xml):
    if isinstance(tagStr, basestring):
        resname = tagStr
        tagStr = Keyword(tagStr, caseless=not xml)
    else:
        resname = tagStr.name
    tagAttrName = Word(alphas, alphanums + '_-:')
    if xml:
        tagAttrValue = dblQuotedString.copy().setParseAction(removeQuotes)
        openTag = Suppress('<') + tagStr('tag') + Dict(ZeroOrMore(Group(tagAttrName + Suppress('=') + tagAttrValue))) + Optional('/', default=[False]).setResultsName('empty').setParseAction(lambda s, l, t: t[0] == '/') + Suppress('>')
    else:
        printablesLessRAbrack = ''.join((c for c in printables if c not in '>'))
        tagAttrValue = quotedString.copy().setParseAction(removeQuotes) | Word(printablesLessRAbrack)
        openTag = Suppress('<') + tagStr('tag') + Dict(ZeroOrMore(Group(tagAttrName.setParseAction(downcaseTokens) + Optional(Suppress('=') + tagAttrValue)))) + Optional('/', default=[False]).setResultsName('empty').setParseAction(lambda s, l, t: t[0] == '/') + Suppress('>')
    closeTag = Combine(_L('</') + tagStr + '>')
    openTag = openTag.setResultsName('start' + ''.join(resname.replace(':', ' ').title().split())).setName('<%s>' % tagStr)
    closeTag = closeTag.setResultsName('end' + ''.join(resname.replace(':', ' ').title().split())).setName('</%s>' % tagStr)
    openTag.tag = resname
    closeTag.tag = resname
    return (openTag, closeTag)


def makeHTMLTags(tagStr):
    return _makeTags(tagStr, False)


def makeXMLTags(tagStr):
    return _makeTags(tagStr, True)


def withAttribute(*args, **attrDict):
    if args:
        attrs = args[:]
    else:
        attrs = attrDict.items()
    attrs = [ (k, v) for k, v in attrs ]

    def pa(s, l, tokens):
        for attrName, attrValue in attrs:
            if attrName not in tokens:
                raise ParseException(s, l, 'no matching attribute ' + attrName)
            if attrValue != withAttribute.ANY_VALUE and tokens[attrName] != attrValue:
                raise ParseException(s, l, "attribute '%s' has value '%s', must be '%s'" % (attrName, tokens[attrName], attrValue))

    return pa


withAttribute.ANY_VALUE = object()

def withClass(classname, namespace = ''):
    classattr = '%s:class' % namespace if namespace else 'class'
    return withAttribute(**{classattr: classname})


opAssoc = _Constants()
opAssoc.LEFT = object()
opAssoc.RIGHT = object()

def infixNotation(baseExpr, opList, lpar = Suppress('('), rpar = Suppress(')')):
    ret = Forward()
    lastExpr = baseExpr | lpar + ret + rpar
    for i, operDef in enumerate(opList):
        opExpr, arity, rightLeftAssoc, pa = (operDef + (None,))[:4]
        if arity == 3:
            if opExpr is None or len(opExpr) != 2:
                raise ValueError('if numterms=3, opExpr must be a tuple or list of two expressions')
            opExpr1, opExpr2 = opExpr
        thisExpr = Forward()
        if rightLeftAssoc == opAssoc.LEFT:
            if arity == 1:
                matchExpr = FollowedBy(lastExpr + opExpr) + Group(lastExpr + OneOrMore(opExpr))
            elif arity == 2:
                if opExpr is not None:
                    matchExpr = FollowedBy(lastExpr + opExpr + lastExpr) + Group(lastExpr + OneOrMore(opExpr + lastExpr))
                else:
                    matchExpr = FollowedBy(lastExpr + lastExpr) + Group(lastExpr + OneOrMore(lastExpr))
            elif arity == 3:
                matchExpr = FollowedBy(lastExpr + opExpr1 + lastExpr + opExpr2 + lastExpr) + Group(lastExpr + opExpr1 + lastExpr + opExpr2 + lastExpr)
            else:
                raise ValueError('operator must be unary (1), binary (2), or ternary (3)')
        elif rightLeftAssoc == opAssoc.RIGHT:
            if arity == 1:
                if not isinstance(opExpr, Optional):
                    opExpr = Optional(opExpr)
                matchExpr = FollowedBy(opExpr.expr + thisExpr) + Group(opExpr + thisExpr)
            elif arity == 2:
                if opExpr is not None:
                    matchExpr = FollowedBy(lastExpr + opExpr + thisExpr) + Group(lastExpr + OneOrMore(opExpr + thisExpr))
                else:
                    matchExpr = FollowedBy(lastExpr + thisExpr) + Group(lastExpr + OneOrMore(thisExpr))
            elif arity == 3:
                matchExpr = FollowedBy(lastExpr + opExpr1 + thisExpr + opExpr2 + thisExpr) + Group(lastExpr + opExpr1 + thisExpr + opExpr2 + thisExpr)
            else:
                raise ValueError('operator must be unary (1), binary (2), or ternary (3)')
        else:
            raise ValueError('operator must indicate right or left associativity')
        if pa:
            matchExpr.setParseAction(pa)
        thisExpr <<= matchExpr | lastExpr
        lastExpr = thisExpr

    ret <<= lastExpr
    return ret


operatorPrecedence = infixNotation
dblQuotedString = Regex('"(?:[^"\\n\\r\\\\]|(?:"")|(?:\\\\x[0-9a-fA-F]+)|(?:\\\\.))*"').setName('string enclosed in double quotes')
sglQuotedString = Regex("'(?:[^'\\n\\r\\\\]|(?:'')|(?:\\\\x[0-9a-fA-F]+)|(?:\\\\.))*'").setName('string enclosed in single quotes')
quotedString = Regex('(?:"(?:[^"\\n\\r\\\\]|(?:"")|(?:\\\\x[0-9a-fA-F]+)|(?:\\\\.))*")|(?:\'(?:[^\'\\n\\r\\\\]|(?:\'\')|(?:\\\\x[0-9a-fA-F]+)|(?:\\\\.))*\')').setName('quotedString using single or double quotes')
unicodeString = Combine(_L('u') + quotedString.copy())

def nestedExpr(opener = '(', closer = ')', content = None, ignoreExpr = quotedString.copy()):
    if opener == closer:
        raise ValueError('opening and closing strings cannot be the same')
    if content is None:
        if isinstance(opener, basestring) and isinstance(closer, basestring):
            if len(opener) == 1 and len(closer) == 1:
                if ignoreExpr is not None:
                    content = Combine(OneOrMore(~ignoreExpr + CharsNotIn(opener + closer + ParserElement.DEFAULT_WHITE_CHARS, exact=1))).setParseAction(lambda t: t[0].strip())
                else:
                    content = empty.copy() + CharsNotIn(opener + closer + ParserElement.DEFAULT_WHITE_CHARS).setParseAction(lambda t: t[0].strip())
            elif ignoreExpr is not None:
                content = Combine(OneOrMore(~ignoreExpr + ~Literal(opener) + ~Literal(closer) + CharsNotIn(ParserElement.DEFAULT_WHITE_CHARS, exact=1))).setParseAction(lambda t: t[0].strip())
            else:
                content = Combine(OneOrMore(~Literal(opener) + ~Literal(closer) + CharsNotIn(ParserElement.DEFAULT_WHITE_CHARS, exact=1))).setParseAction(lambda t: t[0].strip())
        else:
            raise ValueError('opening and closing arguments must be strings if no content expression is given')
    ret = Forward()
    if ignoreExpr is not None:
        ret <<= Group(Suppress(opener) + ZeroOrMore(ignoreExpr | ret | content) + Suppress(closer))
    else:
        ret <<= Group(Suppress(opener) + ZeroOrMore(ret | content) + Suppress(closer))
    return ret


def indentedBlock(blockStatementExpr, indentStack, indent = True):

    def checkPeerIndent(s, l, t):
        if l >= len(s):
            return
        curCol = col(l, s)
        if curCol != indentStack[-1]:
            if curCol > indentStack[-1]:
                raise ParseFatalException(s, l, 'illegal nesting')
            raise ParseException(s, l, 'not a peer entry')

    def checkSubIndent(s, l, t):
        curCol = col(l, s)
        if curCol > indentStack[-1]:
            indentStack.append(curCol)
        else:
            raise ParseException(s, l, 'not a subentry')

    def checkUnindent(s, l, t):
        if l >= len(s):
            return
        curCol = col(l, s)
        if not (indentStack and curCol < indentStack[-1] and curCol <= indentStack[-2]):
            raise ParseException(s, l, 'not an unindent')
        indentStack.pop()

    NL = OneOrMore(LineEnd().setWhitespaceChars('\t ').suppress())
    INDENT = Empty() + Empty().setParseAction(checkSubIndent)
    PEER = Empty().setParseAction(checkPeerIndent)
    UNDENT = Empty().setParseAction(checkUnindent)
    if indent:
        smExpr = Group(Optional(NL) + INDENT + OneOrMore(PEER + Group(blockStatementExpr) + Optional(NL)) + UNDENT)
    else:
        smExpr = Group(Optional(NL) + OneOrMore(PEER + Group(blockStatementExpr) + Optional(NL)))
    blockStatementExpr.ignore(_bslash + LineEnd())
    return smExpr


alphas8bit = srange('[\\0xc0-\\0xd6\\0xd8-\\0xf6\\0xf8-\\0xff]')
punc8bit = srange('[\\0xa1-\\0xbf\\0xd7\\0xf7]')
anyOpenTag, anyCloseTag = makeHTMLTags(Word(alphas, alphanums + '_:'))
commonHTMLEntity = Combine(_L('&') + oneOf('gt lt amp nbsp quot').setResultsName('entity') + ';').streamline()
_htmlEntityMap = dict(zip('gt lt amp nbsp quot'.split(), '><& "'))
replaceHTMLEntity = lambda t: t.entity in _htmlEntityMap and _htmlEntityMap[t.entity] or None
cStyleComment = Regex('/\\*(?:[^*]*\\*+)+?/').setName('C style comment')
htmlComment = Regex('<!--[\\s\\S]*?-->')
restOfLine = Regex('.*').leaveWhitespace()
dblSlashComment = Regex('\\/\\/(\\\\\\n|.)*').setName('// comment')
cppStyleComment = Regex('/(?:\\*(?:[^*]*\\*+)+?/|/[^\\n]*(?:\\n[^\\n]*)*?(?:(?<!\\\\)|\\Z))').setName('C++ style comment')
javaStyleComment = cppStyleComment
pythonStyleComment = Regex('#.*').setName('Python style comment')
_commasepitem = Combine(OneOrMore(Word(printables, excludeChars=',') + Optional(Word(' \t') + ~Literal(',') + ~LineEnd()))).streamline().setName('commaItem')
commaSeparatedList = delimitedList(Optional(quotedString.copy() | _commasepitem, default='')).setName('commaSeparatedList')
if __name__ == '__main__':
    selectToken = CaselessLiteral('select')
    fromToken = CaselessLiteral('from')
    ident = Word(alphas, alphanums + '_$')
    columnName = delimitedList(ident, '.', combine=True).setParseAction(upcaseTokens)
    columnNameList = Group(delimitedList(columnName)).setName('columns')
    tableName = delimitedList(ident, '.', combine=True).setParseAction(upcaseTokens)
    tableNameList = Group(delimitedList(tableName)).setName('tables')
    simpleSQL = selectToken + ('*' | columnNameList).setResultsName('columns') + fromToken + tableNameList.setResultsName('tables')
    simpleSQL.runTests('          SELECT * from XYZZY, ABC\n          select * from SYS.XYZZY\n          Select A from Sys.dual\n          Select AA,BB,CC from Sys.dual\n          Select A, B, C from Sys.dual\n          Select A, B, C from Sys.dual\n          Xelect A, B, C from Sys.dual\n          Select A, B, C frox Sys.dual\n          Select\n          Select ^^^ frox Sys.dual\n          Select A, B, C from Sys.dual, Table2')
