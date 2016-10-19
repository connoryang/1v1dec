#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\structures\schedule.py
import struct
import signals
import datetime
import structures
import functools

@functools.total_ordering

class Schedule(object):
    HOURS = 168

    def __init__(self, value = None, required = None, timeZoneOffset = 0):
        self.required = required
        self.value = None
        self.OnChange = signals.Signal()
        self.SetVulnerableHours(value)
        self.timeZoneOffset = timeZoneOffset

    def __int__(self):
        total = 0
        for offset in [ offset for offset, vulnerable in enumerate(self.value) if vulnerable ]:
            total |= 1 << offset

        return total

    def __eq__(self, other):
        return self.value == other.value

    def __lt__(self, other):
        return self.value < other.value

    def __str__(self):
        data = [0] * 21
        for offset in [ offset for offset, vulnerable in enumerate(self.value) if vulnerable ]:
            index = int(offset / 8)
            data[index] = data[index] | 1 << offset % 8

        return struct.pack('!BBBBBBBBBBBBBBBBBBBBB', *data)

    def Copy(self):
        return Schedule(int(self), self.required)

    def Reset(self):
        self.SetVulnerableHours()

    def LogFormat(self):
        return ','.join([ '{}:{}'.format(day, hour) for day, hour in self.GetVulnerableHours() ])

    def SetRequiredHours(self, required):
        if required is None:
            self.required = None
        else:
            self.required = int(required)

    def GetRequiredHours(self):
        return self.required

    def SetVulnerableHours(self, value = None, notify = True):
        if value is None:
            value = 0
        if isinstance(value, (int, long)):
            value = int(value)
            hours = [ bool(value & 1 << offset) for offset in range(self.HOURS) ]
        elif isinstance(value, (tuple, list)):
            hours = [ bool(self.DayHour(offset) in value) for offset in range(self.HOURS) ]
        elif isinstance(value, basestring):
            hours = []
            for value in struct.unpack('!BBBBBBBBBBBBBBBBBBBBB', value):
                for offset in range(8):
                    hours.append(bool(value & 1 << offset))

        else:
            raise ValueError('Vulnerable hours must be an integer, string or list of tuples')
        if hours != self.value:
            self.value = hours
            if notify:
                self.OnChange(self)

    def GetVulnerableHours(self):
        return [ self.DayHour(offset) for offset, vulnerable in enumerate(self.value) if vulnerable ]

    def GetReinforcementHours(self):
        return [ self.DayHour(offset + structures.REINFORCE_TIME_SHIELD / 60 / 60) for offset, vulnerable in enumerate(self.value) if vulnerable ]

    def SetVulnerable(self, day, hour, vulnerable = True):
        offset = self.Offset(day, hour)
        self.value[offset] = bool(vulnerable)
        self.OnChange(self)

    def SetInvulnerable(self, day, hour):
        self.SetVulnerable(day, hour, False)

    def IsVulnerable(self, day, hour):
        offset = self.Offset(day, hour)
        return bool(self.value[offset])

    def IsVulnerableNow(self):
        now = GetCurrentTime() + datetime.timedelta(hours=self.timeZoneOffset)
        return self.IsVulnerable(now.weekday(), now.hour)

    def SetVulnerableNow(self):
        now = GetCurrentTime() + datetime.timedelta(hours=self.timeZoneOffset)
        self.SetVulnerable(now.weekday(), now.hour)

    def SetInvulnerableNow(self):
        now = GetCurrentTime()
        self.SetInvulnerable(now.weekday(), now.hour)

    def SearchVulnerability(self, vulnerable = True, reverse = False, start = None):
        start = start or GetCurrentTime()
        start += datetime.timedelta(hours=self.timeZoneOffset)
        offset = self.Offset(start.weekday(), start.hour)
        search = list(enumerate(self.value[offset:], start=offset)) + list(enumerate(self.value[:offset]))
        if reverse:
            search.reverse()
        for i, v in search:
            if v == vulnerable:
                result = self.DateTime(start=start, reverse=reverse, *self.DayHour(i))
                if reverse and start.replace(minute=0, second=0, microsecond=0) != result:
                    result += datetime.timedelta(hours=1)
                return result - datetime.timedelta(hours=self.timeZoneOffset)

    def GetNextVulnerable(self, start = None):
        return self.SearchVulnerability(vulnerable=True, reverse=False, start=start)

    def GetNextInvulnerable(self, start = None):
        return self.SearchVulnerability(vulnerable=False, reverse=False, start=start)

    def GetPreviousVulnerable(self, start = None):
        return self.SearchVulnerability(vulnerable=True, reverse=True, start=start)

    def GetPreviousInvulnerable(self, start = None):
        return self.SearchVulnerability(vulnerable=False, reverse=True, start=start)

    def IsAllocated(self):
        return self.Remaining() == 0

    def Remaining(self):
        if self.required is not None:
            return self.required - sum(self.value)
        else:
            return 0

    def Offset(self, day, hour):
        if day not in structures.DAYS:
            raise ValueError('Day must be an integer between 1 and 7 inclusive')
        if not isinstance(hour, (int, long)) or hour < 0 or hour > 23:
            raise ValueError('Hour must be an integer between 0 and 23 inclusive')
        return int(day * 24 + hour)

    def DayHour(self, offset):
        day = int(offset / 24)
        hour = offset - day * 24
        if day == 7:
            day = 0
        return (day, hour)

    def DateTime(self, day, hour, start = None, reverse = False):
        if day not in structures.DAYS:
            raise ValueError('Day must be an integer between 1 and 7 inclusive')
        if not isinstance(hour, (int, long)) or hour < 0 or hour > 23:
            raise ValueError('Hour must be an integer between 0 and 23 inclusive')
        dt = start or GetCurrentTime()
        while dt.hour != hour:
            dt += datetime.timedelta(hours=-1 if reverse else 1)

        while dt.weekday() != day:
            dt += datetime.timedelta(days=-1 if reverse else 1)

        return dt.replace(minute=0, second=0, microsecond=0)


def GetCurrentTime():
    return datetime.datetime.utcnow()
