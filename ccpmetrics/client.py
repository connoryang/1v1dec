#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\ccpmetrics\client.py
import json
import requests
import time
import random
from socket import gethostname

class Client(object):

    def __init__(self, host, env_tags = None, batch_size = 0, proxies = None):
        self.host = host
        self.env_tags = env_tags
        self.batch = []
        self.batch_size = batch_size
        self.session = requests.Session()
        if proxies:
            self.session.proxies.update(proxies)

    def gauge(self, metric, value, tags = None, secondary_values = None, sample_rate = 1, batch = False):
        if batch:
            self._add_to_batch(metric, value, 'gauge', tags=tags, secondary_values=secondary_values, sample_rate=sample_rate)
        else:
            self._write_metric(metric, value, 'gauge', tags=tags, secondary_values=secondary_values, sample_rate=sample_rate)

    def increment(self, metric, value = 1, tags = None, secondary_values = None, sample_rate = 1, batch = False):
        if batch:
            self._add_to_batch(metric, value, 'counter', tags, secondary_values, sample_rate)
        else:
            self._write_metric(metric, value, 'counter', tags, secondary_values, sample_rate)

    def decrement(self, metric, value = 1, tags = None, secondary_values = None, sample_rate = 1, batch = False):
        if batch:
            self._add_to_batch(metric, -value, 'counter', secondary_values, tags, sample_rate)
        else:
            self._write_metric(metric, -value, 'counter', secondary_values, tags, sample_rate)

    def histogram(self, metric, value, tags = None, secondary_values = None, sample_rate = 1, batch = False):
        if batch:
            self._add_to_batch(metric, value, 'histogram', secondary_values, tags, sample_rate)
        else:
            self._write_metric(metric, value, 'histogram', secondary_values, tags, sample_rate)

    def set(self, metric, value, tags = None, secondary_values = None, sample_rate = 1, batch = False):
        if batch:
            self._add_to_batch(metric, value, 'set', secondary_values, tags, sample_rate, batch=False)
        else:
            self._write_metric(metric, value, 'set', secondary_values, tags, sample_rate, batch=False)

    def event(self, title, text, alert_type = None, aggregation_key = None, source_type_name = None, priority = None, tags = None, hostname = None, date_happened = None):
        tags = self.add_app_tags(tags)
        output = json.dumps({'name': title,
         'text': text,
         'host': hostname,
         'alerttype': alert_type,
         'priority': priority,
         'timestamp': time.time(),
         'AggregationKey': aggregation_key,
         'SourceType': source_type_name,
         'tags': tags})
        resp = self.session.post('https://' + self.host + '/events', output)
        resp.raise_for_status()

    def _write_metric(self, metric, value, metric_type, tags = None, secondary_values = None, sample_rate = 1):
        if self._include_metric(sample_rate):
            secondary_values = self._remove_secondary_values_nones(secondary_values)
            tags = self._add_app_tags(self._remove_tags_nones(tags))
            output = self._metric_to_json(metric, value, metric_type, tags, secondary_values, sample_rate)
            resp = self.session.post('https://' + self.host + '/metrics', output)
            resp.raise_for_status()

    def _metric_to_json(self, metric, value, metric_type, tags = None, secondary_values = None, sample_rate = 1):
        return json.dumps({'name': metric,
         'host': gethostname(),
         'timestamp': time.time(),
         'type': metric_type,
         'value': value,
         'secondarydata': secondary_values,
         'sampling': sample_rate,
         'tags': tags})

    def _add_to_batch(self, metric, value, metric_type, tags = None, secondary_values = None, sample_rate = 1):
        if self._include_metric(sample_rate):
            secondary_values = self._remove_secondary_values_nones(secondary_values)
            tags = self._add_app_tags(self._remove_tags_nones(tags))
            self.batch.append({'name': metric,
             'host': gethostname(),
             'timestamp': time.time(),
             'type': metric_type,
             'value': value,
             'secondarydata': secondary_values,
             'sampling': sample_rate,
             'tags': tags})
            if len(self.batch) > self.batch_size:
                self._write_batch()

    def _remove_tags_nones(self, tags):
        if tags is not None:
            for key in tags:
                if tags[key] == None:
                    tags[key] = ''

        else:
            tags = {}
        return tags

    def _remove_secondary_values_nones(self, secondary_values):
        if secondary_values is not None:
            for key in secondary_values:
                if secondary_values[key] == None:
                    secondary_values[key] = 0

        else:
            secondary_values = {}
        return secondary_values

    def _include_metric(self, sample_rate):
        if sample_rate < 1:
            if random.random() < sample_rate:
                return True
            else:
                return False
        return True

    def _write_batch(self):
        output = json.dumps({'batch': self.batch,
         'size': len(self.batch)})
        self.batch = []
        resp = self.session.post('https://' + self.host + '/metrics_batch', output)
        resp.raise_for_status()

    def _add_app_tags(self, tags):
        if tags is None:
            return self.env_tags
        elif self.env_tags is not None:
            temp_tags = self.env_tags.copy()
            temp_tags.update(tags)
            return temp_tags
        else:
            return tags

    def flush(self):
        if len(self.batch) > 0:
            self._write_batch()
