#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\scriber\widgets\inputfields.py
import scriber
import datetime
import datetimeutils

class _AbstractInputField(object):
    template = 'widgets/test.html'

    def __init__(self, name, value = None, dom_id = None):
        self.dom_id = dom_id
        self.name = name
        self.value = value

    def _pre_render(self):
        pass

    def render(self):
        self._pre_render()
        return scriber.scribe(self.template, self.__dict__)

    def __str__(self):
        return self.render()


class DateInputField(_AbstractInputField):
    template = 'widgets/inputfields/date_input.html'

    def __init__(self, name, value = None, dom_id = None, end_date = None, start_date = None):
        super(DateInputField, self).__init__(name, value, dom_id)
        self.start_date = start_date
        self.end_date = end_date

    def _pre_render(self):
        self.dom_id = self.dom_id or self.name
        if self.value:
            if not isinstance(self.value, (datetime.date, datetime.datetime)):
                self.value = datetimeutils.any_to_datetime(self.value)

    @classmethod
    def get(cls, name, value = None, dom_id = None, end_date = None, start_date = None):
        return cls(name, value, dom_id, end_date, start_date)


class DateRangeInputField(_AbstractInputField):
    template = 'widgets/inputfields/date_range_input.html'

    def __init__(self, name, value = None, dom_id = None, end_date = None, start_date = None):
        super(DateRangeInputField, self).__init__(name, value, dom_id)
        self.start_date = start_date
        self.end_date = end_date
        self.value_from = None
        self.value_to = None

    def _pre_render(self):
        self.dom_id = self.dom_id or self.name
        if self.value:
            if isinstance(self.value, (list, tuple)):
                self.value_from = self.value[0]
                if len(self.value) > 1:
                    self.value_to = self.value[1]
            elif isinstance(self.value, (str, unicode)):
                self.value_from, self.value_to = DateRangeInputField.parse_value(self.value)
            if not isinstance(self.value_from, (datetime.date, datetime.datetime)):
                self.value_from = None
            if not isinstance(self.value_to, (datetime.date, datetime.datetime)):
                self.value_to = None

    @classmethod
    def get(cls, name, value = None, dom_id = None, end_date = None, start_date = None):
        return cls(name, value, dom_id, end_date, start_date)

    @staticmethod
    def parse_value(value, default_from = None, default_to = None):
        if value and isinstance(value, (str, unicode)) and len(value) > 19:
            return (datetimeutils.any_to_datetime(value[:10], default_from), datetimeutils.any_to_datetime(value[-10:], default_to))
        return (default_from, default_to)
