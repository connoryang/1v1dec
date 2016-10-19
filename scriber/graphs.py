#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\scriber\graphs.py
import json
import random
import scriber
import datetime
import datetimeutils
import typeutils

class LinesOptions(object):

    def __init__(self):
        self.show = False
        self.line_width = 2
        self.fill = False
        self.fill_color = None
        self.zero = False
        self.steps = False

    def to_dict(self):
        if self.show:
            return {'show': self.show,
             'lineWidth': self.line_width,
             'fill': self.fill,
             'fillColor': self.fill_color,
             'zero': self.zero,
             'steps': self.steps}
        else:
            return {}


class PointsOptions(object):

    def __init__(self):
        self.show = False
        self.line_width = 1
        self.fill = False
        self.fill_color = None
        self.radius = 3
        self.symbol = 'circle'

    def to_dict(self):
        if self.show:
            return {'show': self.show,
             'lineWidth': self.line_width,
             'fill': self.fill,
             'fillColor': self.fill_color,
             'radius': self.radius,
             'symbol': self.symbol}
        else:
            return {}


class BarsOptions(object):

    def __init__(self):
        self.show = False
        self.line_width = 10
        self.fill = True
        self.fill_color = None
        self.zero = False
        self.bar_width = 0
        self.align = 'center'
        self.horizontal = False

    def to_dict(self):
        if self.show:
            return {'show': self.show,
             'lineWidth': self.line_width,
             'fill': self.fill,
             'fillColor': self.fill_color,
             'zero': self.zero,
             'barWidth': self.bar_width,
             'align': self.align,
             'horizontal': self.horizontal}
        else:
            return {}


class LegendOptions(object):

    def __init__(self):
        self.show = True
        self.labelFormatter = None
        self.labelBoxBorderColor = ''
        self.noColumns = 2
        self.position = 'nw'
        self.margin = 2
        self.backgroundColor = None
        self.backgroundOpacity = 0.0
        self.container = None
        self.sorted = None

    def to_dict(self):
        if self.show:
            return {'foo': 'bar'}
        else:
            return {}


class GridOptions(object):

    def __init__(self):
        self.show = True
        self.margin = 1
        self.border_width = 1
        self.border_color = '#aaaaaa'
        self.aboveData = False
        self.color = ''
        self.backgroundColor = None
        self.labelMargin = 1
        self.axisMargin = 1
        self.markings = []
        self.minBorderMargin = 1
        self.clickable = False
        self.hoverable = False
        self.autoHighlight = False
        self.mouseActiveRadius = 1

    def to_dict(self):
        if self.show:
            return {'show': self.show,
             'margin': self.margin,
             'borderWidth': self.border_width,
             'borderColor': self.border_color}
        else:
            return {}


class AxisOptions(object):

    def __init__(self):
        self.show = True
        self.mode = None
        self.ticks = None
        self.tick_size = None
        self.tick_length = None
        self.align_ticks_with_axis = 1
        self.tick_decimals = 0
        self.minTickSize = None
        self.position = None
        self.timezone = None
        self.color = None
        self.tickColor = None
        self.font = None
        self.min = None
        self.max = None
        self.autoscaleMargin = None
        self.transform = None
        self.inverseTransform = None
        self.tickFormatter = None
        self.labelWidth = None
        self.labelHeight = None
        self.reserveSpace = None

    def to_dict(self):
        if self.show:
            return {'show': self.show,
             'mode': self.mode,
             'ticks': self.ticks,
             'tickSize': self.tick_size,
             'tickLength': self.tick_length,
             'alignTicksWithAxis': self.align_ticks_with_axis,
             'tickDecimals': self.tick_decimals}
        else:
            return {}


class DataSeries(object):
    SERIES_TYPE_AUTO_DETECT = 0
    SERIES_TYPE_INT = 1
    SERIES_TYPE_FLOAT = 2
    SERIES_TYPE_STR = 3
    SERIES_TYPE_DATE = 4
    SERIES_TYPE_TIME = 5
    SERIES_TYPE_DATETIME = 6

    def __init__(self, label = '', data = None, color = ''):
        self.data = data or []
        self.series_type_x = DataSeries.SERIES_TYPE_AUTO_DETECT
        self.label = label
        self.lines = LinesOptions()
        self.bars = BarsOptions()
        self.points = PointsOptions()
        self.xaxis = 1
        self.yaxis = 1
        self.clickable = False
        self.hoverable = False
        self.color = color
        self.shadow_size = 0
        self.highlightColor = ''

    def add_point(self, x, y):
        self.data.append([x, y])

    def _detect_type(self):
        if self.data:
            sample = self.data[0]
            if sample:
                data_sample = sample[0]
                if isinstance(data_sample, datetime.time):
                    self.series_type_x = DataSeries.SERIES_TYPE_TIME
                elif isinstance(data_sample, datetime.date):
                    self.series_type_x = DataSeries.SERIES_TYPE_DATE
                elif isinstance(data_sample, datetime.datetime):
                    self.series_type_x = DataSeries.SERIES_TYPE_DATETIME
                elif isinstance(data_sample, float):
                    self.series_type_x = DataSeries.SERIES_TYPE_FLOAT
                elif isinstance(data_sample, (int, long)):
                    self.series_type_x = DataSeries.SERIES_TYPE_INT
                else:
                    self.series_type_x = DataSeries.SERIES_TYPE_STR
            else:
                self.series_type_x = DataSeries.SERIES_TYPE_STR
        else:
            self.series_type_x = DataSeries.SERIES_TYPE_STR

    def _get_data_as_datetime(self):
        return [ [datetimeutils.datetime_to_timestamp(datetimeutils.any_to_datetime(x)) * 1000, y] for x, y in self.data ]

    def _get_data_as_int(self):
        return [ [typeutils.int_eval(x), y] for x, y in self.data ]

    def _get_data_as_float(self):
        return [ [typeutils.float_eval(x), y] for x, y in self.data ]

    def _get_data_as_str(self):
        return [ [str(x), y] for x, y in self.data ]

    def _get_formatted_data(self):
        if self.series_type_x == DataSeries.SERIES_TYPE_AUTO_DETECT:
            self._detect_type()
        if self.series_type_x in (DataSeries.SERIES_TYPE_DATE, DataSeries.SERIES_TYPE_DATETIME, DataSeries.SERIES_TYPE_TIME):
            return self._get_data_as_datetime()
        elif self.series_type_x == DataSeries.SERIES_TYPE_INT:
            return self._get_data_as_int()
        elif self.series_type_x == DataSeries.SERIES_TYPE_FLOAT:
            return self._get_data_as_float()
        else:
            return self._get_data_as_str()

    def to_dict(self):
        d = {'data': self._get_formatted_data(),
         'label': self.label,
         'shadowSize': self.shadow_size,
         'color': self.color}
        l = self.lines.to_dict()
        if l:
            d['lines'] = l
        b = self.bars.to_dict()
        if b:
            d['bars'] = b
        p = self.points.to_dict()
        if p:
            d['points'] = p
        return d


class LinesSeries(DataSeries):

    def __init__(self, label = '', data = None, color = ''):
        super(LinesSeries, self).__init__(label, data, color)
        self.lines.show = True
        self.bars.show = False
        self.points.show = False


class FilledLinesSeries(DataSeries):

    def __init__(self, label = '', data = None, color = ''):
        super(FilledLinesSeries, self).__init__(label, data, color)
        self.lines.show = True
        self.lines.fill = True
        self.bars.show = False
        self.points.show = False


class StepsSeries(DataSeries):

    def __init__(self, label = '', data = None, color = ''):
        super(StepsSeries, self).__init__(label, data, color)
        self.lines.show = True
        self.lines.steps = True
        self.bars.show = False
        self.points.show = False


class FilledStepsSeries(DataSeries):

    def __init__(self, label = '', data = None, color = ''):
        super(FilledStepsSeries, self).__init__(label, data, color)
        self.lines.show = True
        self.lines.steps = True
        self.lines.fill = True
        self.bars.show = False
        self.points.show = False


class BarsSeries(DataSeries):

    def __init__(self, label = '', data = None, color = ''):
        super(BarsSeries, self).__init__(label, data, color)
        self.lines.show = False
        self.bars.show = True
        self.points.show = False


class PointsSeries(DataSeries):

    def __init__(self, label = '', data = None, color = ''):
        super(PointsSeries, self).__init__(label, data, color)
        self.lines.show = False
        self.bars.show = False
        self.points.show = True


class Graph(object):
    template = 'widgets/graph.html'

    def __init__(self, data_series_list = None, element_id = None):
        self.element_id = element_id or 'randomGraphId%04d' % random.randrange(0, 9999)
        self.data_series_list = data_series_list or []
        if not isinstance(self.data_series_list, (list, tuple)):
            self.data_series_list = [self.data_series_list]
        if isinstance(self.data_series_list, tuple):
            self.data_series_list = list(self.data_series_list)
        self.legend = LegendOptions()
        self.x_axis = AxisOptions()
        self.y_axis = AxisOptions()
        self.grid = GridOptions()
        self.height = 200

    def add_series(self, series):
        self.data_series_list.append(series)

    def render_data(self):
        max_ticks = 0
        data_buffer = []
        if self.y_axis.tick_size is None:
            self.y_axis.tick_size = 1
        for ds in self.data_series_list:
            data_buffer.append(ds.to_dict())
            if ds.series_type_x in (DataSeries.SERIES_TYPE_DATE, DataSeries.SERIES_TYPE_DATETIME, DataSeries.SERIES_TYPE_TIME):
                self.x_axis.mode = 'time'
            max_ticks = max(len(ds.data), max_ticks)

        if self.x_axis.ticks is None and max_ticks < 100:
            self.x_axis.ticks = max_ticks
        return json.dumps(data_buffer, separators=(',', ':'))

    def render_options(self):
        d = {}
        x = self.x_axis.to_dict()
        if x:
            d['xaxis'] = x
        y = self.y_axis.to_dict()
        if y:
            d['yaxis'] = y
        grid = self.grid.to_dict()
        if grid:
            d['grid'] = grid
        return json.dumps(d, separators=(',', ':'))

    def render(self):
        data = self.render_data()
        options = self.render_options()
        return scriber.scribe(Graph.template, element_id=self.element_id, data=data, options=options, height=self.height)

    def __str__(self):
        return self.render()
