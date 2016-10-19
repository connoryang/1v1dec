#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\raven\contrib\zerorpc\__init__.py
from __future__ import absolute_import
import inspect
from raven.base import Client

class SentryMiddleware(object):

    def __init__(self, hide_zerorpc_frames = True, client = None, **kwargs):
        self._sentry_client = client or Client(**kwargs)
        self._hide_zerorpc_frames = hide_zerorpc_frames

    def server_inspect_exception(self, req_event, rep_event, task_ctx, exc_info):
        if self._hide_zerorpc_frames:
            traceback = exc_info[2]
            while traceback:
                zerorpc_frame = traceback.tb_frame
                zerorpc_frame.f_locals['__traceback_hide__'] = True
                frame_info = inspect.getframeinfo(zerorpc_frame)
                if frame_info.function == '__call__' or frame_info.function == '_receiver':
                    break
                traceback = traceback.tb_next

        self._sentry_client.captureException(exc_info, extra=task_ctx)
