#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\inflight\bracketsAndTargets\structureBracket.py
import blue
import structures
import localization
from eve.client.script.ui.inflight.bracketsAndTargets.inSpaceBracket import InSpaceBracket
from eve.client.script.ui.control.countdownTimer import CountdownTimer, TIMER_RUNNING_OUT_NO_ANIMATION
from eve.client.script.ui.control.damageRing import DamageRing

class StructureBracket(InSpaceBracket):

    def ApplyAttributes(self, attributes):
        InSpaceBracket.ApplyAttributes(self, attributes)
        self.damage = DamageRing(name='DamageRing', parent=self)
        self.timer = CountdownTimer(name='StructureCounter', parent=self, countsDown=True, timerFunc=blue.os.GetWallclockTime, timerRunningOutAnimation=TIMER_RUNNING_OUT_NO_ANIMATION)
        self.timer.Hide()

    def Startup(self, slimItem, ball = None, transform = None):
        InSpaceBracket.Startup(self, slimItem, ball=ball, transform=transform)
        self.Update()

    def Showing(self):
        return self.sr.selection is not None and self.sr.selection.display

    def Select(self, status):
        if bool(status) != self.Showing():
            InSpaceBracket.Select(self, status)
            self.Update()

    def GetDocked(self):
        if self.IsVisible():
            return self.slimItem.docked

    def OnSlimItemChange(self, oldSlim, newSlim):
        self.slimItem = newSlim
        self.Update()

    def Update(self):
        self.SetSubLabelCallback(self.UpdateLabel)
        self.UpdateTimer()

    def UpdateLabel(self):
        if self.slimItem.timer and self.slimItem.state and self.IsVisible():
            start, end, paused = self.slimItem.timer
            remaining = max(end - (paused or blue.os.GetWallclockTime()), 0L)
            return u'{state}: {time} {paused} {unanchoring}'.format(state=self.GetStateLabel(), time=localization.formatters.FormatTimeIntervalShortWritten(remaining, showFrom='day', showTo='second'), paused=localization.GetByLabel('UI/Structures/States/Paused') if paused else '', unanchoring=localization.GetByLabel('UI/Structures/States/Unanchoring') if self.slimItem.unanchoring else '')

    def GetStateLabel(self):
        if self.slimItem.repairing is not None:
            return localization.GetByLabel('UI/Structures/States/Repairing')
        elif self.slimItem.state:
            return localization.GetByLabel(structures.STATE_LABELS[self.slimItem.state])
        else:
            return ''

    def UpdateTimer(self):
        visible = self.IsVisible()
        start, end, paused = self.slimItem.timer or (0, 0, None)
        validTime = start and end and bool(int(end - start))
        if validTime:
            self.timer.SetExpiryTime(end, end - start, paused)
        if self.slimItem.state:
            self.timer.SetTimerColor(structures.STATE_COLOR.get(self.slimItem.state, (1, 1, 1, 1)))
        if validTime and (self.IsSelectedOrHilted() or self.slimItem.damage) and visible:
            self.timer.Show()
        else:
            self.timer.Hide()
        if self.slimItem.damage and visible:
            self.damage.Show()
            self.damage.SetDamage(self.slimItem.damage)
        else:
            self.damage.Hide()

    def IsVisible(self):
        return sm.GetService('michelle').IsBallVisible(self.itemID)
