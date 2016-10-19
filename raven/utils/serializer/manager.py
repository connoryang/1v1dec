#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\raven\utils\serializer\manager.py
from __future__ import absolute_import
import logging
from contextlib import closing
from raven._compat import text_type
__all__ = ('register', 'transform')
logger = logging.getLogger('sentry.errors.serializer')

class SerializationManager(object):
    logger = logger

    def __init__(self):
        self.__registry = []
        self.__serializers = {}

    @property
    def serializers(self):
        for serializer in self.__registry:
            yield serializer

    def register(self, serializer):
        if serializer not in self.__registry:
            self.__registry.append(serializer)
        return serializer


class Serializer(object):
    logger = logger

    def __init__(self, manager):
        self.manager = manager
        self.context = set()
        self.serializers = []
        for serializer in manager.serializers:
            self.serializers.append(serializer(self))

    def close(self):
        del self.serializers
        del self.context

    def transform(self, value, **kwargs):
        if value is None:
            return
        objid = id(value)
        if objid in self.context:
            return '<...>'
        self.context.add(objid)
        try:
            for serializer in self.serializers:
                if serializer.can(value):
                    try:
                        return serializer.serialize(value, **kwargs)
                    except Exception as e:
                        logger.exception(e)
                        return text_type(type(value))

            try:
                return repr(value)
            except Exception as e:
                logger.exception(e)
                return text_type(type(value))

        finally:
            self.context.remove(objid)


manager = SerializationManager()
register = manager.register

def transform(value, manager = manager, **kwargs):
    with closing(Serializer(manager)) as serializer:
        return serializer.transform(value, **kwargs)
