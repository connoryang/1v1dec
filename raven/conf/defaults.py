#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\raven\conf\defaults.py
from __future__ import absolute_import
import os
import os.path
import socket
ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), os.pardir))
TIMEOUT = 1
CLIENT = 'raven.contrib.django.DjangoClient'
NAME = socket.gethostname() if hasattr(socket, 'gethostname') else None
MAX_LENGTH_LIST = 50
MAX_LENGTH_STRING = 400
AUTO_LOG_STACKS = False
CAPTURE_LOCALS = True
PROCESSORS = ('raven.processors.SanitizePasswordsProcessor',)
try:
    import certifi
    CA_BUNDLE = certifi.where()
except ImportError:
    CA_BUNDLE = os.path.join(ROOT, 'data', 'cacert.pem')
