#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\raven\conf\__init__.py
from __future__ import absolute_import
import logging
__all__ = ['setup_logging']
EXCLUDE_LOGGER_DEFAULTS = ('raven', 'gunicorn', 'south', 'sentry.errors', 'django.request')

def setup_logging(handler, exclude = EXCLUDE_LOGGER_DEFAULTS):
    logger = logging.getLogger()
    if handler.__class__ in map(type, logger.handlers):
        return False
    logger.addHandler(handler)
    for logger_name in exclude:
        logger = logging.getLogger(logger_name)
        logger.propagate = False
        logger.addHandler(logging.StreamHandler())

    return True
