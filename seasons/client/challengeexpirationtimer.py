#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\seasons\client\challengeexpirationtimer.py
import carbonui.const as uiconst
import gametime
import uthread2
from carbon.common.lib.const import DAY, SEC
from carbon.common.script.util.format import GetTimeParts
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from localization import GetByLabel
CHALLENGE_EXPIRATION_CLOCK_SIZE = 16
CHALLENGE_CLOCK_TEXTURE_PATH = 'res:/UI/Texture/Classes/Seasons/clockIcon.png'
CHALLENGE_EXPIRATION_CLOCK_COLOR = (1.0, 0.8, 0.224, 1.0)
CHALLENGE_EXPIRATION_TIMER_LABEL_PATH = 'UI/Seasons/ChallengeExpiryHint'

class ChallengeExpirationTimer(Container):

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.Hide()
        self.expiration_date = attributes.expiration_date
        self.expiration_timer_thread = None
        self._construct_expiration_timer()
        self._show_expiration_timer()

    def _construct_expiration_timer(self):
        self.expiration_sprite = Sprite(name='expiration_timer_sprite', parent=self, texturePath=CHALLENGE_CLOCK_TEXTURE_PATH, align=uiconst.TOALL, color=CHALLENGE_EXPIRATION_CLOCK_COLOR)
        self.expiration_sprite.OnMouseEnter = self._set_timer_hint

    def _show_expiration_timer(self):
        time_until_expiration = self._get_time_until_expiration()
        sleep_time = time_until_expiration - DAY
        if sleep_time > DAY:
            return
        if sleep_time > 0:
            self.expiration_timer_thread = uthread2.start_tasklet(self._show_expiration_timer_thread, sleep_time)
        else:
            self.Show()

    def _show_expiration_timer_thread(self, sleep_time):
        uthread2.sleep(sleep_time / SEC)
        self.Show()

    def _get_time_until_expiration(self):
        return self.expiration_date - gametime.GetWallclockTime()

    def _set_timer_hint(self):
        self.expiration_sprite.SetHint(self._get_timer_hint())

    def _get_timer_hint(self, *args):
        if self.IsHidden():
            return
        time_until_expiration = self._get_time_until_expiration()
        if time_until_expiration > 0:
            _, _, _, _, hours, minutes, _, _ = GetTimeParts(time_until_expiration)
            return GetByLabel(CHALLENGE_EXPIRATION_TIMER_LABEL_PATH, hours=hours, minutes=minutes)
        return GetByLabel(CHALLENGE_EXPIRATION_TIMER_LABEL_PATH, hours=0, minutes=0)

    def Close(self):
        Container.Close(self)
        if self.expiration_timer_thread is not None:
            self.expiration_timer_thread.kill()
