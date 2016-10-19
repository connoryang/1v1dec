#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\raven\contrib\django\serializers.py
from __future__ import absolute_import
from __future__ import unicode_literals
from django.conf import settings
from django.http import HttpRequest
from django.utils.functional import Promise
from raven.utils.serializer import Serializer, register
from raven._compat import text_type
__all__ = (u'PromiseSerializer',)

class PromiseSerializer(Serializer):
    types = (Promise,)

    def can(self, value):
        if not super(PromiseSerializer, self).can(value):
            return False
        pre = value.__class__.__name__[1:]
        if not (hasattr(value, u'%s__func' % pre) or hasattr(value, u'%s__unicode_cast' % pre) or hasattr(value, u'%s__text_cast' % pre)):
            return False
        return True

    def serialize(self, value, **kwargs):
        pre = value.__class__.__name__[1:]
        if hasattr(value, u'%s__func' % pre):
            value = getattr(value, u'%s__func' % pre)(*getattr(value, u'%s__args' % pre), **getattr(value, u'%s__kw' % pre))
        else:
            return self.recurse(text_type(value))
        return self.recurse(value, **kwargs)


register(PromiseSerializer)

class HttpRequestSerializer(Serializer):
    types = (HttpRequest,)

    def serialize(self, value, **kwargs):
        return u'<%s at 0x%s>' % (type(value).__name__, id(value))


register(HttpRequestSerializer)
if getattr(settings, u'DATABASES', None):
    from django.db.models.query import QuerySet

    class QuerySetSerializer(Serializer):
        types = (QuerySet,)

        def serialize(self, value, **kwargs):
            qs_name = type(value).__name__
            if value.model:
                return u'<%s: model=%s>' % (qs_name, value.model.__name__)
            return u'<%s: (Unbound)>' % (qs_name,)


    register(QuerySetSerializer)
