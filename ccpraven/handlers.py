#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\ccpraven\handlers.py
from raven.handlers.logging import SentryHandler

class CcpHandler(SentryHandler):

    def __init__(self, *args, **kwargs):
        self.ignore_exceptions = kwargs.get('ignore_exceptions', [])
        super(CcpHandler, self).__init__(*args, **kwargs)

    def can_record(self, record):
        exc_info = record.exc_info
        if exc_info is not None and self.ignore_exceptions:
            exc_type = exc_info[0]
            exc_name = '%s.%s' % (exc_type.__module__, exc_type.__name__)
            exclusions = self.ignore_exceptions
            if exc_type.__name__ in exclusions:
                return False
            if exc_name in exclusions:
                return False
            if any((exc_name.startswith(e[:-1]) for e in exclusions if e.endswith('*'))):
                return False
        return super(CcpHandler, self).can_record(record)
