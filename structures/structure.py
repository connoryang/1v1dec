#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\structures\structure.py
import signals
import datetime
import structures

class Structure(object):

    def __init__(self):
        self.state = structures.STATE_UNKNOWN
        self.damage = (None, None, None)
        self.vulnerable = None
        self.timerStart = None
        self.timerEnd = None
        self.timerPaused = None
        self.firstAggressed = None
        self.lastAggressed = None
        self.repairing = None
        self.unanchoring = None
        self.schedule = structures.Schedule(required=self.GetRequiredHours(), timeZoneOffset=8 if boot.region == 'optic' else 0)
        self.OnStateChanged = signals.Signal()
        self.OnDamageChanged = signals.Signal()
        self.OnVulnerabilityChanged = signals.Signal()
        self.OnScheduleChanged = signals.Signal()
        self.OnTimerChanged = signals.Signal()
        self.OnRepairingChanged = signals.Signal()
        self.OnAggressionChanged = signals.Signal()
        self.OnUnanchoringChanged = signals.Signal()
        self.OnFirstAggressed = signals.Signal()
        self.schedule.OnChange.connect(self.HandleScheduleChanged)

    def Update(self):
        self.UpdateVulnerability()
        self.UpdateState()
        self.UpdateTimers()
        self.UpdateRepair()
        self.UpdateUnanchoring()

    def SaveState(self, state):
        pass

    def SaveDamage(self, damage):
        pass

    def SaveVulnerable(self, vulnerable):
        pass

    def SaveSchedule(self, schedule):
        pass

    def SaveTimer(self, start, end, paused):
        pass

    def SaveRepairing(self, repairing):
        pass

    def SaveUnanchoring(self, unanchoring):
        pass

    def GetRepairTime(self):
        return structures.REPAIR_TIMER

    def GetReinforceTimeShield(self):
        return structures.REINFORCE_TIME_SHIELD

    def GetReinforceTimeArmor(self):
        return structures.REINFORCE_TIME_ARMOR

    def GetAnchoringTime(self):
        return structures.ANCHORING_TIME

    def GetUnanchoringTime(self):
        return structures.UNANCHORING_TIME

    def GetRequiredHours(self):
        return 0

    def HandleStateChanged(self):
        self.SetTimer(None)
        self.SetRepairing(None)
        self.UpdateVulnerability()
        self.UpdateTimers()
        self.SetAggression(None)
        self.UpdateShieldArmorHull()
        self.UpdateRepair()
        self.UpdateUnanchoring()

    def HandleDamageChanged(self):
        self.UpdateAggression()
        self.Update()

    def HandleScheduleChanged(self, *args):
        if self.state in (structures.STATE_ONLINE, structures.STATE_SHIELD_VULNERABLE):
            self.Update()
        self.SaveSchedule(self.GetSchedule())
        self.OnScheduleChanged(self)

    def UpdateShieldArmorHull(self, *args):
        if self.state in structures.STATE_SHIELD_ARMOR_HULL:
            self.SetDamage(*structures.STATE_SHIELD_ARMOR_HULL[self.state])

    def UpdateVulnerability(self, *args):
        if self.state in structures.STATE_VULNERABILITY:
            self.SetVulnerable(structures.STATE_VULNERABILITY[self.state])

    def UpdateState(self, *args):
        vulnerable = self.schedule.IsVulnerableNow()
        if self.state == structures.STATE_ONLINE:
            if vulnerable:
                self.SetState(structures.STATE_SHIELD_VULNERABLE)
        elif self.state == structures.STATE_SHIELD_VULNERABLE:
            if not vulnerable and not self.IsDamaged():
                self.SetState(structures.STATE_ONLINE)
            elif self.IsArmorDamaged():
                self.SetState(structures.STATE_SHIELD_REINFORCE)
        elif self.state == structures.STATE_SHIELD_REINFORCE:
            if self.HasTimerExpired():
                self.SetState(structures.STATE_ARMOR_VULNERABLE)
        elif self.state == structures.STATE_ARMOR_VULNERABLE:
            if not self.IsDamaged():
                if vulnerable:
                    self.SetState(structures.STATE_SHIELD_VULNERABLE)
                else:
                    self.SetState(structures.STATE_ONLINE)
            elif self.IsHullDamaged():
                self.SetState(structures.STATE_ARMOR_REINFORCE)
        elif self.state == structures.STATE_ARMOR_REINFORCE:
            if self.HasTimerExpired():
                self.SetState(structures.STATE_HULL_VULNERABLE)
        elif self.state == structures.STATE_HULL_VULNERABLE:
            if not self.IsDamaged():
                if vulnerable:
                    self.SetState(structures.STATE_SHIELD_VULNERABLE)
                else:
                    self.SetState(structures.STATE_ONLINE)
        elif self.state == structures.STATE_ANCHORING:
            if self.HasTimerExpired():
                self.SetState(structures.STATE_HULL_VULNERABLE)

    def UpdateAggression(self, *args):
        if self.IsAggressed():
            aggressed = self.GetFirstAggressed()
            if not aggressed:
                self.SetAggression(self.GetTimeNow(), self.GetTimeNow())
            else:
                self.SetAggression(aggressed, self.GetTimeNow())
        else:
            self.SetAggression(None)

    def UpdateRepair(self, *args):
        if self.ShouldRepair():
            if self.GetRepairing() is None:
                self.SetTimer(self.GetTimeNow() + datetime.timedelta(seconds=self.GetRepairTime()), self.GetTimeNow())
                self.SetRepairing(True)
            elif self.ShouldRepairPause():
                self.SetTimerPaused(True)
                self.SetRepairing(False)
            else:
                self.SetTimerPaused(False)
                self.SetRepairing(True)
            if self.IsRepairing() and self.HasTimerExpired():
                self.SetDamage(1.0, 1.0, 1.0)
        else:
            self.SetRepairing(None)

    def UpdateTimers(self, *args):
        if self.ShouldRepair():
            return
        if self.state == structures.STATE_ONLINE:
            self.SetTimer(self.schedule.GetNextVulnerable(), self.schedule.GetPreviousVulnerable())
        elif self.state == structures.STATE_SHIELD_VULNERABLE:
            self.SetTimer(self.schedule.GetNextInvulnerable(), self.schedule.GetPreviousInvulnerable())
        elif self.state == structures.STATE_SHIELD_REINFORCE:
            if not self.GetTimerEnd():
                start = self.GetFirstAggressed() or self.GetTimeNow()
                self.SetTimer(start + datetime.timedelta(seconds=self.GetReinforceTimeShield()))
        elif self.state == structures.STATE_ARMOR_VULNERABLE:
            self.SetTimer(None)
        elif self.state == structures.STATE_ARMOR_REINFORCE:
            if not self.GetTimerEnd():
                start = self.GetFirstAggressed() or self.GetTimeNow()
                self.SetTimer(start + datetime.timedelta(seconds=self.GetReinforceTimeArmor()))
        elif self.state == structures.STATE_HULL_VULNERABLE:
            self.SetTimer(None)
        elif self.state == structures.STATE_ANCHORING:
            if not self.GetTimerEnd():
                self.SetTimer(self.GetTimeNow() + datetime.timedelta(seconds=self.GetAnchoringTime()))

    def UpdateUnanchoring(self):
        if structures.STATE_CANCELS_UNANCHOR.get(self.state) is True:
            self.SetUnanchoring(None)
        if self.HasUnanchoringExpired():
            self.SetState(structures.STATE_UNANCHORED)

    def GetState(self):
        return self.state

    def SetState(self, state):
        if state not in structures.STATES:
            raise structures.InvalidStructureState(state)
        current = self.GetState()
        if state != current:
            self.state = state
            self.SaveState(state)
            self.HandleStateChanged()
            self.OnStateChanged(self, current, state)

    def IsOnline(self):
        return self.GetState() not in structures.OFFLINE_STATES

    def IsOffline(self):
        return self.GetState() in structures.OFFLINE_STATES

    def IsDisabled(self):
        return self.GetState() in structures.DISABLED_STATES

    def GetUnanchoring(self):
        return self.unanchoring

    def SetUnanchoring(self, unanchoring):
        if unanchoring is not None and not isinstance(unanchoring, datetime.datetime):
            raise TypeError('Unanchoring time must be a datetime object or None')
        if unanchoring != self.GetUnanchoring():
            self.unanchoring = unanchoring
            self.SaveUnanchoring(unanchoring)
            self.OnUnanchoringChanged(self, unanchoring)

    def SetUnanchoringRemaining(self, seconds):
        self.SetUnanchoring(self.GetTimeNow() + datetime.timedelta(seconds=int(seconds)))

    def GetUnanchoringRemaining(self):
        unanchoring = self.GetUnanchoring()
        if unanchoring is not None:
            return int((unanchoring - self.GetTimeNow()).total_seconds())

    def StartUnanchoring(self):
        if self.GetUnanchoring() is None:
            self.SetUnanchoring(self.GetTimeNow() + datetime.timedelta(seconds=self.GetUnanchoringTime()))

    def StopUnanchoring(self):
        if self.GetUnanchoring():
            self.SetUnanchoring(None)

    def IsUnanchoring(self):
        return self.unanchoring is not None

    def GetUnanchorTime(self):
        return self.unanchoring

    def HasUnanchoringExpired(self):
        unanchoring = self.GetUnanchoring()
        return unanchoring is not None and unanchoring <= self.GetTimeNow()

    def IsShieldDamaged(self):
        return self.GetShield() < 1

    def IsArmorDamaged(self):
        return self.GetArmor() < 1

    def IsHullDamaged(self):
        return self.GetHull() < 1

    def IsDamaged(self):
        if self.GetDamage() == (None, None, None):
            return False
        return self.IsShieldDamaged() or self.IsArmorDamaged() or self.IsHullDamaged()

    def SetDamage(self, shield, armor, hull):
        damage = (max(min(float(shield), 1.0), 0.0), max(min(float(armor), 1.0), 0.0), max(min(float(hull), 1.0), 0.0))
        if damage != self.GetDamage():
            self.damage = damage
            self.SaveDamage(damage)
            self.HandleDamageChanged()
            self.OnDamageChanged(self, damage)

    def GetDamage(self):
        return self.damage

    def ShouldRepair(self):
        return self.IsDamaged() and self.IsVulnerable()

    def ShouldRepairPause(self):
        return self.GetLastAggressed()

    def IsRepairing(self):
        return bool(self.repairing)

    def GetRepairing(self):
        return self.repairing

    def SetRepairing(self, repairing):
        if repairing is not None and not isinstance(repairing, bool):
            raise TypeError('Repairing must be a bool or None')
        if repairing != self.repairing:
            self.repairing = repairing
            self.SaveRepairing(repairing)
            self.OnRepairingChanged(self, repairing)

    def IsAggressed(self):
        if self.state == structures.STATE_SHIELD_VULNERABLE:
            return self.IsShieldDamaged()
        if self.state == structures.STATE_ARMOR_VULNERABLE:
            return self.IsArmorDamaged()
        if self.state == structures.STATE_HULL_VULNERABLE:
            return self.IsHullDamaged()

    def GetFirstAggressed(self):
        return self.firstAggressed

    def GetLastAggressed(self):
        return self.lastAggressed

    def SetAggression(self, aggressed, latest = None):
        if aggressed is not None and not isinstance(aggressed, datetime.datetime):
            raise TypeError('Aggression time must be a datetime object or None')
        if latest is not None and not isinstance(aggressed, datetime.datetime):
            raise TypeError('Latest aggression time must be a datetime object or None')
        firstAggressed = self.GetFirstAggressed()
        if aggressed != firstAggressed or latest != self.GetLastAggressed():
            self.firstAggressed = aggressed
            self.lastAggressed = latest
            self.OnAggressionChanged(self, self.firstAggressed, self.lastAggressed)
            if firstAggressed is None and self.firstAggressed is not None:
                self.OnFirstAggressed(self, self.firstAggressed)

    def GetShield(self):
        return self.GetDamage()[0]

    def GetArmor(self):
        return self.GetDamage()[1]

    def GetHull(self):
        return self.GetDamage()[2]

    def GetVulnerable(self):
        return self.vulnerable

    def IsVulnerable(self):
        return bool(self.GetVulnerable())

    def SetVulnerable(self, vulnerable):
        vulnerable = bool(int(vulnerable))
        existing = self.GetVulnerable()
        if vulnerable != existing:
            self.vulnerable = vulnerable
            self.SaveVulnerable(vulnerable)
            self.OnVulnerabilityChanged(self, existing, vulnerable)

    def GetSchedule(self):
        return self.schedule

    def SetSchedule(self, schedule):
        schedule = int(schedule)
        if schedule != int(self.GetSchedule()):
            self.schedule.SetVulnerableHours(schedule)

    def SetVulnerableHour(self, day, hour):
        self.schedule.SetVulnerable(day, hour)

    def SetInvulnerableHour(self, day, hour):
        self.schedule.SetInvulnerable(day, hour)

    def SetVulnerableHourNow(self):
        self.schedule.SetVulnerableNow()

    def SetInvulnerableHourNow(self):
        self.schedule.SetInvulnerableNow()

    def SetTimer(self, timer, start = None, paused = None):
        if timer is not None and not isinstance(timer, datetime.datetime):
            raise TypeError('Timer must be a datetime object or None')
        if isinstance(paused, bool):
            paused = self.GetTimeNow() if paused else None
        elif paused is not None and not isinstance(paused, datetime.datetime):
            raise TypeError('Paused must be a datetime object, a bool or None')
        if timer != self.GetTimerEnd() or start != self.GetTimerStart() or paused != self.GetTimerPaused():
            self.timerStart = start or self.GetTimeNow()
            self.timerEnd = timer
            self.timerPaused = paused
            self.SaveTimer(self.timerStart, self.timerEnd, self.timerPaused)
            self.OnTimerChanged(self, self.timerStart, self.timerEnd, self.timerPaused)

    def GetTimerEnd(self):
        return self.timerEnd

    def GetTimerStart(self):
        return self.timerStart

    def GetTimerPaused(self):
        return self.timerPaused

    def SetTimerPaused(self, pausing):
        if self.IsTimerRunning():
            pausing = bool(int(pausing))
            paused = self.GetTimerPaused()
            if not paused and pausing:
                self.SetTimer(self.timerEnd, self.timerStart, self.GetTimeNow())
            elif paused and not pausing:
                elapsed = self.GetTimeNow() - paused
                start = self.timerStart + elapsed
                end = self.timerEnd + elapsed
                self.SetTimer(end, start, None)

    def IsTimerRunning(self):
        return self.timerStart and self.timerEnd

    def IsTimerPaused(self):
        return self.timerPaused is not None

    def SetTimerRemaining(self, seconds):
        self.SetTimer(self.GetTimeNow() + datetime.timedelta(seconds=int(seconds)))
        self.Update()

    def GetTimerRemaining(self):
        timer = self.GetTimerEnd()
        if timer is not None:
            return int((timer - self.GetTimeNow()).total_seconds())

    def GetTimerLength(self):
        start = self.GetTimerStart()
        end = self.GetTimerEnd()
        if start and end:
            return int((end - start).total_seconds())

    def HasTimerExpired(self):
        timer = self.GetTimerEnd()
        return timer is None or timer <= self.GetTimeNow()

    def GetTimeNow(self):
        now = datetime.datetime.utcnow()
        return now.replace(microsecond=0)


def LookupState(state):
    if state:
        state = str(state).lower()
        for value, name in structures.STATES.iteritems():
            if str(value) == state:
                return value
            if name.startswith(state):
                return value
