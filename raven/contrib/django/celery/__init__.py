#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\raven\contrib\django\celery\__init__.py
from __future__ import absolute_import
from raven.contrib.django.client import DjangoClient
try:
    from celery.task import task
except ImportError:
    from celery.decorators import task

class CeleryClient(DjangoClient):

    def send_integrated(self, kwargs):
        return send_raw_integrated.delay(kwargs)

    def send_encoded(self, *args, **kwargs):
        return send_raw.delay(*args, **kwargs)


@task(routing_key='sentry')
def send_raw_integrated(kwargs):
    from raven.contrib.django.models import get_client
    super(DjangoClient, get_client()).send_integrated(kwargs)


@task(routing_key='sentry')
def send_raw(*args, **kwargs):
    from raven.contrib.django.models import get_client
    super(DjangoClient, get_client()).send_encoded(*args, **kwargs)
