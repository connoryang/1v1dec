#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\raven\utils\imports.py
from __future__ import absolute_import
from raven._compat import PY2

def import_string(key):
    if PY2:
        key = str(key)
    if '.' not in key:
        return __import__(key)
    module_name, class_name = key.rsplit('.', 1)
    module = __import__(module_name, {}, {}, [class_name], 0)
    return getattr(module, class_name)
