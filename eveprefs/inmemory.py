#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\eveprefs\inmemory.py
from . import BaseIniFile, strip_spaces

class InMemoryIniFile(BaseIniFile):

    def __init__(self, seq = (), **keyvals):
        totaldict = dict(seq, **keyvals)
        self.keyval = strip_spaces(totaldict)

    def _GetKeySet(self):
        return self.keyval

    def _GetValue(self, key):
        return self.keyval[key]

    def _SetValue(self, key, value, forcePickle):
        self.keyval[key] = value

    def _DeleteValue(self, key):
        del self.keyval[key]
