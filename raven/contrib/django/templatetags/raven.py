#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\raven\contrib\django\templatetags\raven.py
from __future__ import absolute_import
from django import template
register = template.Library()

@register.simple_tag
def sentry_public_dsn(scheme = None):
    from raven.contrib.django.models import client
    return client.get_public_dsn(scheme) or ''
