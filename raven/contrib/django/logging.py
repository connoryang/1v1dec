#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\raven\contrib\django\logging.py
from __future__ import absolute_import
import warnings
warnings.warn('raven.contrib.django.logging is deprecated. Use raven.contrib.django.handlers instead.', DeprecationWarning)
from raven.contrib.django.handlers import SentryHandler
__all__ = ('SentryHandler',)
