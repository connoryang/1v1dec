#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\stdlib\yaml\emitter.py
__all__ = ['Emitter', 'EmitterError']
from error import YAMLError
from events import *

class EmitterError(YAMLError):
    pass


class ScalarAnalysis(object):

    def __init__(self, scalar, empty, multiline, allow_flow_plain, allow_block_plain, allow_single_quoted, allow_double_quoted, allow_block):
        self.scalar = scalar
        self.empty = empty
        self.multiline = multiline
        self.allow_flow_plain = allow_flow_plain
        self.allow_block_plain = allow_block_plain
        self.allow_single_quoted = allow_single_quoted
        self.allow_double_quoted = allow_double_quoted
        self.allow_block = allow_block


class Emitter(object):
    DEFAULT_TAG_PREFIXES = {u'!': u'!',
     u'tag:yaml.org,2002:': u'!!'}

    def __init__(self, stream, canonical = None, indent = None, width = None, allow_unicode = None, line_break = None):
        self.stream = stream
        self.encoding = None
        self.states = []
        self.state = self.expect_stream_start
        self.events = []
        self.event = None
        self.indents = []
        self.indent = None
        self.flow_level = 0
        self.root_context = False
        self.sequence_context = False
        self.mapping_context = False
        self.simple_key_context = False
        self.line = 0
        self.column = 0
        self.whitespace = True
        self.indention = True
        self.open_ended = False
        self.canonical = canonical
        self.allow_unicode = allow_unicode
        self.best_indent = 2
        if indent and 1 < indent < 10:
            self.best_indent = indent
        self.best_width = 80
        if width and width > self.best_indent * 2:
            self.best_width = width
        self.best_line_break = u'\n'
        if line_break in (u'\r', u'\n', u'\r\n'):
            self.best_line_break = line_break
        self.tag_prefixes = None
        self.prepared_anchor = None
        self.prepared_tag = None
        self.analysis = None
        self.style = None

    def emit(self, event):
        self.events.append(event)
        while not self.need_more_events():
            self.event = self.events.pop(0)
            self.state()
            self.event = None

    def need_more_events(self):
        if not self.events:
            return True
        event = self.events[0]
        if isinstance(event, DocumentStartEvent):
            return self.need_events(1)
        elif isinstance(event, SequenceStartEvent):
            return self.need_events(2)
        elif isinstance(event, MappingStartEvent):
            return self.need_events(3)
        else:
            return False

    def need_events(self, count):
        level = 0
        for event in self.events[1:]:
            if isinstance(event, (DocumentStartEvent, CollectionStartEvent)):
                level += 1
            elif isinstance(event, (DocumentEndEvent, CollectionEndEvent)):
                level -= 1
            elif isinstance(event, StreamEndEvent):
                level = -1
            if level < 0:
                return False

        return len(self.events) < count + 1

    def increase_indent(self, flow = False, indentless = False):
        self.indents.append(self.indent)
        if self.indent is None:
            if flow:
                self.indent = self.best_indent
            else:
                self.indent = 0
        elif not indentless:
            self.indent += self.best_indent

    def expect_stream_start(self):
        if isinstance(self.event, StreamStartEvent):
            if self.event.encoding and not getattr(self.stream, 'encoding', None):
                self.encoding = self.event.encoding
            self.write_stream_start()
            self.state = self.expect_first_document_start
        else:
            raise EmitterError('expected StreamStartEvent, but got %s' % self.event)

    def expect_nothing(self):
        raise EmitterError('expected nothing, but got %s' % self.event)

    def expect_first_document_start(self):
        return self.expect_document_start(first=True)

    def expect_document_start(self, first = False):
        if isinstance(self.event, DocumentStartEvent):
            if (self.event.version or self.event.tags) and self.open_ended:
                self.write_indicator(u'...', True)
                self.write_indent()
            if self.event.version:
                version_text = self.prepare_version(self.event.version)
                self.write_version_directive(version_text)
            self.tag_prefixes = self.DEFAULT_TAG_PREFIXES.copy()
            if self.event.tags:
                handles = self.event.tags.keys()
                handles.sort()
                for handle in handles:
                    prefix = self.event.tags[handle]
                    self.tag_prefixes[prefix] = handle
                    handle_text = self.prepare_tag_handle(handle)
                    prefix_text = self.prepare_tag_prefix(prefix)
                    self.write_tag_directive(handle_text, prefix_text)

            implicit = first and not self.event.explicit and not self.canonical and not self.event.version and not self.event.tags and not self.check_empty_document()
            if not implicit:
                self.write_indent()
                self.write_indicator(u'---', True)
                if self.canonical:
                    self.write_indent()
            self.state = self.expect_document_root
        elif isinstance(self.event, StreamEndEvent):
            if self.open_ended:
                self.write_indicator(u'...', True)
                self.write_indent()
            self.write_stream_end()
            self.state = self.expect_nothing
        else:
            raise EmitterError('expected DocumentStartEvent, but got %s' % self.event)

    def expect_document_end(self):
        if isinstance(self.event, DocumentEndEvent):
            self.write_indent()
            if self.event.explicit:
                self.write_indicator(u'...', True)
                self.write_indent()
            self.flush_stream()
            self.state = self.expect_document_start
        else:
            raise EmitterError('expected DocumentEndEvent, but got %s' % self.event)

    def expect_document_root(self):
        self.states.append(self.expect_document_end)
        self.expect_node(root=True)

    def expect_node(self, root = False, sequence = False, mapping = False, simple_key = False):
        self.root_context = root
        self.sequence_context = sequence
        self.mapping_context = mapping
        self.simple_key_context = simple_key
        if isinstance(self.event, AliasEvent):
            self.expect_alias()
        elif isinstance(self.event, (ScalarEvent, CollectionStartEvent)):
            self.process_anchor(u'&')
            self.process_tag()
            if isinstance(self.event, ScalarEvent):
                self.expect_scalar()
            elif isinstance(self.event, SequenceStartEvent):
                if self.flow_level or self.canonical or self.event.flow_style or self.check_empty_sequence():
                    self.expect_flow_sequence()
                else:
                    self.expect_block_sequence()
            elif isinstance(self.event, MappingStartEvent):
                if self.flow_level or self.canonical or self.event.flow_style or self.check_empty_mapping():
                    self.expect_flow_mapping()
                else:
                    self.expect_block_mapping()
        else:
            raise EmitterError('expected NodeEvent, but got %s' % self.event)

    def expect_alias(self):
        if self.event.anchor is None:
            raise EmitterError('anchor is not specified for alias')
        self.process_anchor(u'*')
        self.state = self.states.pop()

    def expect_scalar(self):
        self.increase_indent(flow=True)
        self.process_scalar()
        self.indent = self.indents.pop()
        self.state = self.states.pop()

    def expect_flow_sequence(self):
        self.write_indicator(u'[', True, whitespace=True)
        self.flow_level += 1
        self.increase_indent(flow=True)
        self.state = self.expect_first_flow_sequence_item

    def expect_first_flow_sequence_item(self):
        if isinstance(self.event, SequenceEndEvent):
            self.indent = self.indents.pop()
            self.flow_level -= 1
            self.write_indicator(u']', False)
            self.state = self.states.pop()
        else:
            if self.canonical or self.column > self.best_width:
                self.write_indent()
            self.states.append(self.expect_flow_sequence_item)
            self.expect_node(sequence=True)

    def expect_flow_sequence_item(self):
        if isinstance(self.event, SequenceEndEvent):
            self.indent = self.indents.pop()
            self.flow_level -= 1
            if self.canonical:
                self.write_indicator(u',', False)
                self.write_indent()
            self.write_indicator(u']', False)
            self.state = self.states.pop()
        else:
            self.write_indicator(u',', False)
            if self.canonical or self.column > self.best_width:
                self.write_indent()
            self.states.append(self.expect_flow_sequence_item)
            self.expect_node(sequence=True)

    def expect_flow_mapping(self):
        self.write_indicator(u'{', True, whitespace=True)
        self.flow_level += 1
        self.increase_indent(flow=True)
        self.state = self.expect_first_flow_mapping_key

    def expect_first_flow_mapping_key(self):
        if isinstance(self.event, MappingEndEvent):
            self.indent = self.indents.pop()
            self.flow_level -= 1
            self.write_indicator(u'}', False)
            self.state = self.states.pop()
        else:
            if self.canonical or self.column > self.best_width:
                self.write_indent()
            if not self.canonical and self.check_simple_key():
                self.states.append(self.expect_flow_mapping_simple_value)
                self.expect_node(mapping=True, simple_key=True)
            else:
                self.write_indicator(u'?', True)
                self.states.append(self.expect_flow_mapping_value)
                self.expect_node(mapping=True)

    def expect_flow_mapping_key(self):
        if isinstance(self.event, MappingEndEvent):
            self.indent = self.indents.pop()
            self.flow_level -= 1
            if self.canonical:
                self.write_indicator(u',', False)
                self.write_indent()
            self.write_indicator(u'}', False)
            self.state = self.states.pop()
        else:
            self.write_indicator(u',', False)
            if self.canonical or self.column > self.best_width:
                self.write_indent()
            if not self.canonical and self.check_simple_key():
                self.states.append(self.expect_flow_mapping_simple_value)
                self.expect_node(mapping=True, simple_key=True)
            else:
                self.write_indicator(u'?', True)
                self.states.append(self.expect_flow_mapping_value)
                self.expect_node(mapping=True)

    def expect_flow_mapping_simple_value(self):
        self.write_indicator(u':', False)
        self.states.append(self.expect_flow_mapping_key)
        self.expect_node(mapping=True)

    def expect_flow_mapping_value(self):
        if self.canonical or self.column > self.best_width:
            self.write_indent()
        self.write_indicator(u':', True)
        self.states.append(self.expect_flow_mapping_key)
        self.expect_node(mapping=True)

    def expect_block_sequence(self):
        indentless = self.mapping_context and not self.indention
        self.increase_indent(flow=False, indentless=indentless)
        self.state = self.expect_first_block_sequence_item

    def expect_first_block_sequence_item(self):
        return self.expect_block_sequence_item(first=True)

    def expect_block_sequence_item(self, first = False):
        if not first and isinstance(self.event, SequenceEndEvent):
            self.indent = self.indents.pop()
            self.state = self.states.pop()
        else:
            self.write_indent()
            self.write_indicator(u'-', True, indention=True)
            self.states.append(self.expect_block_sequence_item)
            self.expect_node(sequence=True)

    def expect_block_mapping(self):
        self.increase_indent(flow=False)
        self.state = self.expect_first_block_mapping_key

    def expect_first_block_mapping_key(self):
        return self.expect_block_mapping_key(first=True)

    def expect_block_mapping_key(self, first = False):
        if not first and isinstance(self.event, MappingEndEvent):
            self.indent = self.indents.pop()
            self.state = self.states.pop()
        else:
            self.write_indent()
            if self.check_simple_key():
                self.states.append(self.expect_block_mapping_simple_value)
                self.expect_node(mapping=True, simple_key=True)
            else:
                self.write_indicator(u'?', True, indention=True)
                self.states.append(self.expect_block_mapping_value)
                self.expect_node(mapping=True)

    def expect_block_mapping_simple_value(self):
        self.write_indicator(u':', False)
        self.states.append(self.expect_block_mapping_key)
        self.expect_node(mapping=True)

    def expect_block_mapping_value(self):
        self.write_indent()
        self.write_indicator(u':', True, indention=True)
        self.states.append(self.expect_block_mapping_key)
        self.expect_node(mapping=True)

    def check_empty_sequence(self):
        return isinstance(self.event, SequenceStartEvent) and self.events and isinstance(self.events[0], SequenceEndEvent)

    def check_empty_mapping(self):
        return isinstance(self.event, MappingStartEvent) and self.events and isinstance(self.events[0], MappingEndEvent)

    def check_empty_document(self):
        if not isinstance(self.event, DocumentStartEvent) or not self.events:
            return False
        event = self.events[0]
        return isinstance(event, ScalarEvent) and event.anchor is None and event.tag is None and event.implicit and event.value == u''

    def check_simple_key(self):
        length = 0
        if isinstance(self.event, NodeEvent) and self.event.anchor is not None:
            if self.prepared_anchor is None:
                self.prepared_anchor = self.prepare_anchor(self.event.anchor)
            length += len(self.prepared_anchor)
        if isinstance(self.event, (ScalarEvent, CollectionStartEvent)) and self.event.tag is not None:
            if self.prepared_tag is None:
                self.prepared_tag = self.prepare_tag(self.event.tag)
            length += len(self.prepared_tag)
        if isinstance(self.event, ScalarEvent):
            if self.analysis is None:
                self.analysis = self.analyze_scalar(self.event.value)
            length += len(self.analysis.scalar)
        return length < 128 and (isinstance(self.event, AliasEvent) or isinstance(self.event, ScalarEvent) and not self.analysis.empty and not self.analysis.multiline or self.check_empty_sequence() or self.check_empty_mapping())

    def process_anchor(self, indicator):
        if self.event.anchor is None:
            self.prepared_anchor = None
            return
        if self.prepared_anchor is None:
            self.prepared_anchor = self.prepare_anchor(self.event.anchor)
        if self.prepared_anchor:
            self.write_indicator(indicator + self.prepared_anchor, True)
        self.prepared_anchor = None

    def process_tag(self):
        tag = self.event.tag
        if isinstance(self.event, ScalarEvent):
            if self.style is None:
                self.style = self.choose_scalar_style()
            if (not self.canonical or tag is None) and (self.style == '' and self.event.implicit[0] or self.style != '' and self.event.implicit[1]):
                self.prepared_tag = None
                return
            if self.event.implicit[0] and tag is None:
                tag = u'!'
                self.prepared_tag = None
        elif (not self.canonical or tag is None) and self.event.implicit:
            self.prepared_tag = None
            return
        if tag is None:
            raise EmitterError('tag is not specified')
        if self.prepared_tag is None:
            self.prepared_tag = self.prepare_tag(tag)
        if self.prepared_tag:
            self.write_indicator(self.prepared_tag, True)
        self.prepared_tag = None

    def choose_scalar_style(self):
        if self.analysis is None:
            self.analysis = self.analyze_scalar(self.event.value)
        if self.event.style == '"' or self.canonical:
            return '"'
        if not self.event.style and self.event.implicit[0] and not (self.simple_key_context and (self.analysis.empty or self.analysis.multiline)):
            if self.flow_level and self.analysis.allow_flow_plain or not self.flow_level and self.analysis.allow_block_plain:
                return ''
        if self.event.style and self.event.style in '|>' and not self.flow_level and not self.simple_key_context:
            if self.analysis.allow_block:
                return self.event.style
        if (not self.event.style or self.event.style == "'") and self.analysis.allow_single_quoted:
            if not (self.simple_key_context and self.analysis.multiline):
                return "'"
        return '"'

    def process_scalar(self):
        if self.analysis is None:
            self.analysis = self.analyze_scalar(self.event.value)
        if self.style is None:
            self.style = self.choose_scalar_style()
        split = not self.simple_key_context
        if self.style == '"':
            self.write_double_quoted(self.analysis.scalar, split)
        elif self.style == "'":
            self.write_single_quoted(self.analysis.scalar, split)
        elif self.style == '>':
            self.write_folded(self.analysis.scalar)
        elif self.style == '|':
            self.write_literal(self.analysis.scalar)
        else:
            self.write_plain(self.analysis.scalar, split)
        self.analysis = None
        self.style = None

    def prepare_version(self, version):
        major, minor = version
        if major != 1:
            raise EmitterError('unsupported YAML version: %d.%d' % (major, minor))
        return u'%d.%d' % (major, minor)

    def prepare_tag_handle(self, handle):
        if not handle:
            raise EmitterError('tag handle must not be empty')
        if handle[0] != u'!' or handle[-1] != u'!':
            raise EmitterError("tag handle must start and end with '!': %r" % handle.encode('utf-8'))
        for ch in handle[1:-1]:
            if not (u'0' <= ch <= u'9' or u'A' <= ch <= u'Z' or u'a' <= ch <= u'z' or ch in u'-_'):
                raise EmitterError('invalid character %r in the tag handle: %r' % (ch.encode('utf-8'), handle.encode('utf-8')))

        return handle

    def prepare_tag_prefix(self, prefix):
        if not prefix:
            raise EmitterError('tag prefix must not be empty')
        chunks = []
        start = end = 0
        if prefix[0] == u'!':
            end = 1
        while end < len(prefix):
            ch = prefix[end]
            if u'0' <= ch <= u'9' or u'A' <= ch <= u'Z' or u'a' <= ch <= u'z' or ch in u"-;/?!:@&=+$,_.~*'()[]":
                end += 1
            else:
                if start < end:
                    chunks.append(prefix[start:end])
                start = end = end + 1
                data = ch.encode('utf-8')
                for ch in data:
                    chunks.append(u'%%%02X' % ord(ch))

        if start < end:
            chunks.append(prefix[start:end])
        return u''.join(chunks)

    def prepare_tag(self, tag):
        if not tag:
            raise EmitterError('tag must not be empty')
        if tag == u'!':
            return tag
        handle = None
        suffix = tag
        prefixes = self.tag_prefixes.keys()
        prefixes.sort()
        for prefix in prefixes:
            if tag.startswith(prefix) and (prefix == u'!' or len(prefix) < len(tag)):
                handle = self.tag_prefixes[prefix]
                suffix = tag[len(prefix):]

        chunks = []
        start = end = 0
        while end < len(suffix):
            ch = suffix[end]
            if u'0' <= ch <= u'9' or u'A' <= ch <= u'Z' or u'a' <= ch <= u'z' or ch in u"-;/?:@&=+$,_.~*'()[]" or ch == u'!' and handle != u'!':
                end += 1
            else:
                if start < end:
                    chunks.append(suffix[start:end])
                start = end = end + 1
                data = ch.encode('utf-8')
                for ch in data:
                    chunks.append(u'%%%02X' % ord(ch))

        if start < end:
            chunks.append(suffix[start:end])
        suffix_text = u''.join(chunks)
        if handle:
            return u'%s%s' % (handle, suffix_text)
        else:
            return u'!<%s>' % suffix_text

    def prepare_anchor(self, anchor):
        if not anchor:
            raise EmitterError('anchor must not be empty')
        for ch in anchor:
            if not (u'0' <= ch <= u'9' or u'A' <= ch <= u'Z' or u'a' <= ch <= u'z' or ch in u'-_'):
                raise EmitterError('invalid character %r in the anchor: %r' % (ch.encode('utf-8'), anchor.encode('utf-8')))

        return anchor

    def analyze_scalar(self, scalar):
        if not scalar:
            return ScalarAnalysis(scalar=scalar, empty=True, multiline=False, allow_flow_plain=False, allow_block_plain=True, allow_single_quoted=True, allow_double_quoted=True, allow_block=False)
        block_indicators = False
        flow_indicators = False
        line_breaks = False
        special_characters = False
        leading_space = False
        leading_break = False
        trailing_space = False
        trailing_break = False
        break_space = False
        space_break = False
        if scalar.startswith(u'---') or scalar.startswith(u'...'):
            block_indicators = True
            flow_indicators = True
        preceeded_by_whitespace = True
        followed_by_whitespace = len(scalar) == 1 or scalar[1] in u'\x00 \t\r\n\x85\u2028\u2029'
        previous_space = False
        previous_break = False
        index = 0
        while index < len(scalar):
            ch = scalar[index]
            if index == 0:
                if ch in u'#,[]{}&*!|>\'"%@`':
                    flow_indicators = True
                    block_indicators = True
                if ch in u'?:':
                    flow_indicators = True
                    if followed_by_whitespace:
                        block_indicators = True
                if ch == u'-' and followed_by_whitespace:
                    flow_indicators = True
                    block_indicators = True
            else:
                if ch in u',?[]{}':
                    flow_indicators = True
                if ch == u':':
                    flow_indicators = True
                    if followed_by_whitespace:
                        block_indicators = True
                if ch == u'#' and preceeded_by_whitespace:
                    flow_indicators = True
                    block_indicators = True
            if ch in u'\n\x85\u2028\u2029':
                line_breaks = True
            if not (ch == u'\n' or u' ' <= ch <= u'~'):
                if (ch == u'\x85' or u'\xa0' <= ch <= u'\ud7ff' or u'\ue000' <= ch <= u'\ufffd') and ch != u'\ufeff':
                    unicode_characters = True
                    if not self.allow_unicode:
                        special_characters = True
                else:
                    special_characters = True
            if ch == u' ':
                if index == 0:
                    leading_space = True
                if index == len(scalar) - 1:
                    trailing_space = True
                if previous_break:
                    break_space = True
                previous_space = True
                previous_break = False
            elif ch in u'\n\x85\u2028\u2029':
                if index == 0:
                    leading_break = True
                if index == len(scalar) - 1:
                    trailing_break = True
                if previous_space:
                    space_break = True
                previous_space = False
                previous_break = True
            else:
                previous_space = False
                previous_break = False
            index += 1
            preceeded_by_whitespace = ch in u'\x00 \t\r\n\x85\u2028\u2029'
            followed_by_whitespace = index + 1 >= len(scalar) or scalar[index + 1] in u'\x00 \t\r\n\x85\u2028\u2029'

        allow_flow_plain = True
        allow_block_plain = True
        allow_single_quoted = True
        allow_double_quoted = True
        allow_block = True
        if leading_space or leading_break or trailing_space or trailing_break:
            allow_flow_plain = allow_block_plain = False
        if trailing_space:
            allow_block = False
        if break_space:
            allow_flow_plain = allow_block_plain = allow_single_quoted = False
        if space_break or special_characters:
            allow_flow_plain = allow_block_plain = allow_single_quoted = allow_block = False
        if line_breaks:
            allow_flow_plain = allow_block_plain = False
        if flow_indicators:
            allow_flow_plain = False
        if block_indicators:
            allow_block_plain = False
        return ScalarAnalysis(scalar=scalar, empty=False, multiline=line_breaks, allow_flow_plain=allow_flow_plain, allow_block_plain=allow_block_plain, allow_single_quoted=allow_single_quoted, allow_double_quoted=allow_double_quoted, allow_block=allow_block)

    def flush_stream(self):
        if hasattr(self.stream, 'flush'):
            self.stream.flush()

    def write_stream_start(self):
        if self.encoding and self.encoding.startswith('utf-16'):
            self.stream.write(u'\ufeff'.encode(self.encoding))

    def write_stream_end(self):
        self.flush_stream()

    def write_indicator(self, indicator, need_whitespace, whitespace = False, indention = False):
        if self.whitespace or not need_whitespace:
            data = indicator
        else:
            data = u' ' + indicator
        self.whitespace = whitespace
        self.indention = self.indention and indention
        self.column += len(data)
        self.open_ended = False
        if self.encoding:
            data = data.encode(self.encoding)
        self.stream.write(data)

    def write_indent(self):
        indent = self.indent or 0
        if not self.indention or self.column > indent or self.column == indent and not self.whitespace:
            self.write_line_break()
        if self.column < indent:
            self.whitespace = True
            data = u' ' * (indent - self.column)
            self.column = indent
            if self.encoding:
                data = data.encode(self.encoding)
            self.stream.write(data)

    def write_line_break(self, data = None):
        if data is None:
            data = self.best_line_break
        self.whitespace = True
        self.indention = True
        self.line += 1
        self.column = 0
        if self.encoding:
            data = data.encode(self.encoding)
        self.stream.write(data)

    def write_version_directive(self, version_text):
        data = u'%%YAML %s' % version_text
        if self.encoding:
            data = data.encode(self.encoding)
        self.stream.write(data)
        self.write_line_break()

    def write_tag_directive(self, handle_text, prefix_text):
        data = u'%%TAG %s %s' % (handle_text, prefix_text)
        if self.encoding:
            data = data.encode(self.encoding)
        self.stream.write(data)
        self.write_line_break()

    def write_single_quoted(self, text, split = True):
        self.write_indicator(u"'", True)
        spaces = False
        breaks = False
        start = end = 0
        while end <= len(text):
            ch = None
            if end < len(text):
                ch = text[end]
            if spaces:
                if ch is None or ch != u' ':
                    if start + 1 == end and self.column > self.best_width and split and start != 0 and end != len(text):
                        self.write_indent()
                    else:
                        data = text[start:end]
                        self.column += len(data)
                        if self.encoding:
                            data = data.encode(self.encoding)
                        self.stream.write(data)
                    start = end
            elif breaks:
                if ch is None or ch not in u'\n\x85\u2028\u2029':
                    if text[start] == u'\n':
                        self.write_line_break()
                    for br in text[start:end]:
                        if br == u'\n':
                            self.write_line_break()
                        else:
                            self.write_line_break(br)

                    self.write_indent()
                    start = end
            elif ch is None or ch in u' \n\x85\u2028\u2029' or ch == u"'":
                if start < end:
                    data = text[start:end]
                    self.column += len(data)
                    if self.encoding:
                        data = data.encode(self.encoding)
                    self.stream.write(data)
                    start = end
            if ch == u"'":
                data = u"''"
                self.column += 2
                if self.encoding:
                    data = data.encode(self.encoding)
                self.stream.write(data)
                start = end + 1
            if ch is not None:
                spaces = ch == u' '
                breaks = ch in u'\n\x85\u2028\u2029'
            end += 1

        self.write_indicator(u"'", False)

    ESCAPE_REPLACEMENTS = {u'\x00': u'0',
     u'\x07': u'a',
     u'\x08': u'b',
     u'\t': u't',
     u'\n': u'n',
     u'\x0b': u'v',
     u'\x0c': u'f',
     u'\r': u'r',
     u'\x1b': u'e',
     u'"': u'"',
     u'\\': u'\\',
     u'\x85': u'N',
     u'\xa0': u'_',
     u'\u2028': u'L',
     u'\u2029': u'P'}

    def write_double_quoted(self, text, split = True):
        self.write_indicator(u'"', True)
        start = end = 0
        while end <= len(text):
            ch = None
            if end < len(text):
                ch = text[end]
            if ch is None or ch in u'"\\\x85\u2028\u2029\ufeff' or not (u' ' <= ch <= u'~' or self.allow_unicode and (u'\xa0' <= ch <= u'\ud7ff' or u'\ue000' <= ch <= u'\ufffd')):
                if start < end:
                    data = text[start:end]
                    self.column += len(data)
                    if self.encoding:
                        data = data.encode(self.encoding)
                    self.stream.write(data)
                    start = end
                if ch is not None:
                    if ch in self.ESCAPE_REPLACEMENTS:
                        data = u'\\' + self.ESCAPE_REPLACEMENTS[ch]
                    elif ch <= u'\xff':
                        data = u'\\x%02X' % ord(ch)
                    elif ch <= u'\uffff':
                        data = u'\\u%04X' % ord(ch)
                    else:
                        data = u'\\U%08X' % ord(ch)
                    self.column += len(data)
                    if self.encoding:
                        data = data.encode(self.encoding)
                    self.stream.write(data)
                    start = end + 1
            if 0 < end < len(text) - 1 and (ch == u' ' or start >= end) and self.column + (end - start) > self.best_width and split:
                data = text[start:end] + u'\\'
                if start < end:
                    start = end
                self.column += len(data)
                if self.encoding:
                    data = data.encode(self.encoding)
                self.stream.write(data)
                self.write_indent()
                self.whitespace = False
                self.indention = False
                if text[start] == u' ':
                    data = u'\\'
                    self.column += len(data)
                    if self.encoding:
                        data = data.encode(self.encoding)
                    self.stream.write(data)
            end += 1

        self.write_indicator(u'"', False)

    def determine_block_hints(self, text):
        hints = u''
        if text:
            if text[0] in u' \n\x85\u2028\u2029':
                hints += unicode(self.best_indent)
            if text[-1] not in u'\n\x85\u2028\u2029':
                hints += u'-'
            elif len(text) == 1 or text[-2] in u'\n\x85\u2028\u2029':
                hints += u'+'
        return hints

    def write_folded(self, text):
        hints = self.determine_block_hints(text)
        self.write_indicator(u'>' + hints, True)
        if hints[-1:] == u'+':
            self.open_ended = True
        self.write_line_break()
        leading_space = True
        spaces = False
        breaks = True
        start = end = 0
        while end <= len(text):
            ch = None
            if end < len(text):
                ch = text[end]
            if breaks:
                if ch is None or ch not in u'\n\x85\u2028\u2029':
                    if not leading_space and ch is not None and ch != u' ' and text[start] == u'\n':
                        self.write_line_break()
                    leading_space = ch == u' '
                    for br in text[start:end]:
                        if br == u'\n':
                            self.write_line_break()
                        else:
                            self.write_line_break(br)

                    if ch is not None:
                        self.write_indent()
                    start = end
            elif spaces:
                if ch != u' ':
                    if start + 1 == end and self.column > self.best_width:
                        self.write_indent()
                    else:
                        data = text[start:end]
                        self.column += len(data)
                        if self.encoding:
                            data = data.encode(self.encoding)
                        self.stream.write(data)
                    start = end
            elif ch is None or ch in u' \n\x85\u2028\u2029':
                data = text[start:end]
                self.column += len(data)
                if self.encoding:
                    data = data.encode(self.encoding)
                self.stream.write(data)
                if ch is None:
                    self.write_line_break()
                start = end
            if ch is not None:
                breaks = ch in u'\n\x85\u2028\u2029'
                spaces = ch == u' '
            end += 1

    def write_literal(self, text):
        hints = self.determine_block_hints(text)
        self.write_indicator(u'|' + hints, True)
        if hints[-1:] == u'+':
            self.open_ended = True
        self.write_line_break()
        breaks = True
        start = end = 0
        while end <= len(text):
            ch = None
            if end < len(text):
                ch = text[end]
            if breaks:
                if ch is None or ch not in u'\n\x85\u2028\u2029':
                    for br in text[start:end]:
                        if br == u'\n':
                            self.write_line_break()
                        else:
                            self.write_line_break(br)

                    if ch is not None:
                        self.write_indent()
                    start = end
            elif ch is None or ch in u'\n\x85\u2028\u2029':
                data = text[start:end]
                if self.encoding:
                    data = data.encode(self.encoding)
                self.stream.write(data)
                if ch is None:
                    self.write_line_break()
                start = end
            if ch is not None:
                breaks = ch in u'\n\x85\u2028\u2029'
            end += 1

    def write_plain(self, text, split = True):
        if self.root_context:
            self.open_ended = True
        if not text:
            return
        if not self.whitespace:
            data = u' '
            self.column += len(data)
            if self.encoding:
                data = data.encode(self.encoding)
            self.stream.write(data)
        self.whitespace = False
        self.indention = False
        spaces = False
        breaks = False
        start = end = 0
        while end <= len(text):
            ch = None
            if end < len(text):
                ch = text[end]
            if spaces:
                if ch != u' ':
                    if start + 1 == end and self.column > self.best_width and split:
                        self.write_indent()
                        self.whitespace = False
                        self.indention = False
                    else:
                        data = text[start:end]
                        self.column += len(data)
                        if self.encoding:
                            data = data.encode(self.encoding)
                        self.stream.write(data)
                    start = end
            elif breaks:
                if ch not in u'\n\x85\u2028\u2029':
                    if text[start] == u'\n':
                        self.write_line_break()
                    for br in text[start:end]:
                        if br == u'\n':
                            self.write_line_break()
                        else:
                            self.write_line_break(br)

                    self.write_indent()
                    self.whitespace = False
                    self.indention = False
                    start = end
            elif ch is None or ch in u' \n\x85\u2028\u2029':
                data = text[start:end]
                self.column += len(data)
                if self.encoding:
                    data = data.encode(self.encoding)
                self.stream.write(data)
                start = end
            if ch is not None:
                spaces = ch == u' '
                breaks = ch in u'\n\x85\u2028\u2029'
            end += 1
