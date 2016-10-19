#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\gametime\ingameclock.py
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from eve.client.script.ui.control.eveLabel import Label
from carbon.common.lib.const import HOUR
import carbonui.const as uiconst
import blue
import uthread
CLOCK_UPDATE_SLEEP_TIME_MS = 5000
CLOCK_LABEL_TEXT = '<b>%2.2i:%2.2i</b>'
CHINA_TIME_OFFSET = 8 * HOUR

class InGameClock(Container):

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self._construct_clock_label(attributes.label_font_size)
        self.update_clock_thread = None

    def _construct_clock_label(self, label_font_size):
        self.clock_label = Label(parent=self, name='clock_label', align=uiconst.CENTER, fontsize=label_font_size)

    def update_clock(self):
        if self.update_clock_thread:
            self.update_clock_thread.kill()
        self.update_clock_thread = uthread.new(self._update_clock)

    def _update_clock(self):
        time_offset = 0
        if boot.region == 'optic':
            time_offset = CHINA_TIME_OFFSET
        while not self.destroyed:
            _, _, _, _, hour, minute, _, _ = blue.os.GetTimeParts(blue.os.GetTime() + time_offset)
            self.clock_label.text = CLOCK_LABEL_TEXT % (hour, minute)
            blue.synchro.SleepWallclock(CLOCK_UPDATE_SLEEP_TIME_MS)
