#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\raven\contrib\celery\__init__.py
from __future__ import absolute_import
import logging
from celery.exceptions import SoftTimeLimitExceeded
from celery.signals import after_setup_logger, task_failure
from raven.handlers.logging import SentryHandler

class CeleryFilter(logging.Filter):

    def filter(self, record):
        extra_data = getattr(record, 'data', {})
        if not isinstance(extra_data, dict):
            return record.funcName != '_log_error'
        return extra_data.get('internal', record.funcName != '_log_error')


def register_signal(client, ignore_expected = False):

    def process_failure_signal(sender, task_id, args, kwargs, einfo, **kw):
        if ignore_expected and isinstance(einfo.exception, sender.throws):
            return
        if isinstance(einfo.exception, SoftTimeLimitExceeded):
            fingerprint = ['celery', 'SoftTimeLimitExceeded', sender]
        else:
            fingerprint = None
        client.captureException(extra={'task_id': task_id,
         'task': sender,
         'args': args,
         'kwargs': kwargs}, fingerprint=fingerprint)

    task_failure.connect(process_failure_signal, weak=False)


def register_logger_signal(client, logger = None, loglevel = logging.ERROR):
    filter_ = CeleryFilter()
    handler = SentryHandler(client)
    handler.setLevel(loglevel)
    handler.addFilter(filter_)

    def process_logger_event(sender, logger, loglevel, logfile, format, colorize, **kw):
        for h in logger.handlers:
            if type(h) == SentryHandler:
                h.addFilter(filter_)
                return False

        logger.addHandler(handler)

    after_setup_logger.connect(process_logger_event, weak=False)
