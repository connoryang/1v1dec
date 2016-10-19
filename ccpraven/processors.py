#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\ccpraven\processors.py
import __builtin__
from raven.processors import Processor

class EveSessionProcessor(Processor):

    def get_data(self, data, **kwargs):
        extra_session, user_info = self.get_eve_info()
        tasklet_info = self.get_tasklet_info()
        extra = data.get('extra', None)
        if extra is None:
            extra = {}
        if extra_session:
            extra.update(extra_session)
        if tasklet_info:
            extra.update(tasklet_info)
        extra = {'extra': extra}
        if user_info:
            extra.update(user_info)
        data.update(extra)
        return data

    def get_eve_info(self):
        session = getattr(__builtin__, 'session', None)
        if session:
            extra_session = {'session': session.__dict__.copy()}
            extra_session['session']['sessionhist'] = 'Omitted by Raven'
            user_info = {'user': {'id': getattr(session, 'userid'),
                      'charid': getattr(session, 'charid')}}
            return (extra_session, user_info)
        return (None, None)

    def get_tasklet_info(self):
        try:
            import stackless
            tasklet = stackless.getcurrent()
            origin_traceback = tasklet.origin_traceback
            tasklet_info = {'tasklet_origin': origin_traceback}
            return tasklet_info
        except Exception as e:
            pass
