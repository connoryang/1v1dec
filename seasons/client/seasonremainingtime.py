#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\seasons\client\seasonremainingtime.py
import carbonui.const as uiconst
from carbonui.primitives.container import Container
import datetime
import datetimeutils
from eve.client.script.ui.control.eveLabel import EveLabelSmall
from gametime import GetWallclockTime, GetSecondsSinceWallclockTime
from seasons.client.const import get_time_remaining_string
from seasons.client.uiutils import SEASON_THEME_TEXT_COLOR_REGULAR
from seasons.common.exceptions import SeasonHasAlreadyEndedError
import uthread2
from carbonui.util import color
TIME_REMAINING_UPDATE_SLEEP_TIME_SECONDS = 5

class SeasonRemainingTime(Container):

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.season_service = attributes.season_service
        time_label_align = attributes.Get('time_label_align', uiconst.CENTERLEFT)
        self.time_remaining_label = EveLabelSmall(parent=self, align=time_label_align)
        try:
            self.seconds_remaining_at_start = self.season_service.get_season_remaining_seconds()
        except SeasonHasAlreadyEndedError:
            self.seconds_remaining_at_start = 0
        else:
            self.start_time = GetWallclockTime()
            self.start_update_thread()

    def update_color(self, days, hours, minutes, seconds):
        if days:
            self.time_remaining_label.color = SEASON_THEME_TEXT_COLOR_REGULAR
        elif hours >= 12:
            self.time_remaining_label.color = color.Color.YELLOW
        else:
            self.time_remaining_label.color = color.Color.RED

    def update_remaining_time(self):
        seconds_remaining = self.seconds_remaining_at_start - GetSecondsSinceWallclockTime(self.start_time)
        seconds_remaining = max(seconds_remaining, 0)
        time_remaining = datetime.timedelta(seconds=seconds_remaining)
        split_delta = datetimeutils.split_delta(time_remaining, include_weeks=False, include_months=False, include_years=False)
        d, h, m, s = (split_delta['days'],
         split_delta['hours'],
         split_delta['minutes'],
         split_delta['seconds'])
        self.time_remaining_label.text = get_time_remaining_string(d, h, m, s)
        self.update_color(d, h, m, s)
        return bool(time_remaining)

    def start_update_thread(self):
        self.update_thread = uthread2.start_tasklet(self._update_remaining_time_tasklet)

    def _update_remaining_time_tasklet(self):
        while not self.destroyed and self.update_remaining_time():
            uthread2.sleep(TIME_REMAINING_UPDATE_SLEEP_TIME_SECONDS)
