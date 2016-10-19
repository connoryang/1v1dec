#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\requests\packages\urllib3\util\timeout.py
from __future__ import absolute_import
from socket import _GLOBAL_DEFAULT_TIMEOUT
import time
from ..exceptions import TimeoutStateError
_Default = object()

def current_time():
    return time.time()


class Timeout(object):
    DEFAULT_TIMEOUT = _GLOBAL_DEFAULT_TIMEOUT

    def __init__(self, total = None, connect = _Default, read = _Default):
        self._connect = self._validate_timeout(connect, 'connect')
        self._read = self._validate_timeout(read, 'read')
        self.total = self._validate_timeout(total, 'total')
        self._start_connect = None

    def __str__(self):
        return '%s(connect=%r, read=%r, total=%r)' % (type(self).__name__,
         self._connect,
         self._read,
         self.total)

    @classmethod
    def _validate_timeout(cls, value, name):
        if value is _Default:
            return cls.DEFAULT_TIMEOUT
        if value is None or value is cls.DEFAULT_TIMEOUT:
            return value
        try:
            float(value)
        except (TypeError, ValueError):
            raise ValueError('Timeout value %s was %s, but it must be an int or float.' % (name, value))

        try:
            if value < 0:
                raise ValueError('Attempted to set %s timeout to %s, but the timeout cannot be set to a value less than 0.' % (name, value))
        except TypeError:
            raise ValueError('Timeout value %s was %s, but it must be an int or float.' % (name, value))

        return value

    @classmethod
    def from_float(cls, timeout):
        return Timeout(read=timeout, connect=timeout)

    def clone(self):
        return Timeout(connect=self._connect, read=self._read, total=self.total)

    def start_connect(self):
        if self._start_connect is not None:
            raise TimeoutStateError('Timeout timer has already been started.')
        self._start_connect = current_time()
        return self._start_connect

    def get_connect_duration(self):
        if self._start_connect is None:
            raise TimeoutStateError("Can't get connect duration for timer that has not started.")
        return current_time() - self._start_connect

    @property
    def connect_timeout(self):
        if self.total is None:
            return self._connect
        if self._connect is None or self._connect is self.DEFAULT_TIMEOUT:
            return self.total
        return min(self._connect, self.total)

    @property
    def read_timeout(self):
        if self.total is not None and self.total is not self.DEFAULT_TIMEOUT and self._read is not None and self._read is not self.DEFAULT_TIMEOUT:
            if self._start_connect is None:
                return self._read
            return max(0, min(self.total - self.get_connect_duration(), self._read))
        elif self.total is not None and self.total is not self.DEFAULT_TIMEOUT:
            return max(0, self.total - self.get_connect_duration())
        else:
            return self._read
