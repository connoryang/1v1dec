#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\neocom\charactersheet.py
import service
import form
from eve.client.script.ui.shared.neocom.characterSheetWindow import CharacterSheetWindow

class CharacterSheet(service.Service):
    __exportedcalls__ = {'Show': []}
    __update_on_reload__ = 0
    __guid__ = 'svc.charactersheet'
    __notifyevents__ = ['ProcessSessionChange',
     'OnSkillsChanged',
     'OnSkillQueueChanged',
     'OnRankChange',
     'OnKillNotification',
     'OnUpdatedMedalsAvailable',
     'OnUIRefresh']
    __servicename__ = 'charactersheet'
    __displayname__ = 'Character Sheet Client Service'
    __dependencies__ = []
    __startupdependencies__ = ['settings', 'skills', 'neocom']

    def Run(self, memStream = None):
        self.LogInfo('Starting Character Sheet')
        self.Reset()
        if not sm.GetService('skillqueue').SkillInTraining():
            sm.GetService('neocom').Blink('charactersheet')

    def Stop(self, memStream = None):
        wnd = self.GetWnd()
        if wnd is not None and not wnd.destroyed:
            wnd.Close()

    def Reset(self):
        self.daysLeft = -1

    def OnUIRefresh(self, *args):
        wnd = form.CharacterSheet.GetIfOpen()
        if wnd:
            wnd.Close()
            self.Show()

    def ProcessSessionChange(self, isremote, session, change):
        if session.charid is None:
            self.Stop()
            self.Reset()

    def OnRankChange(self, oldrank, newrank):
        if not session.warfactionid:
            return
        rankLabel, _ = sm.GetService('facwar').GetRankLabel(session.warfactionid, newrank)
        if newrank > oldrank:
            blinkMsg = cfg.GetMessage('RankGained', {'rank': rankLabel}).text
        else:
            blinkMsg = cfg.GetMessage('RankLost', {'rank': rankLabel}).text
        sm.GetService('neocom').Blink('charactersheet', blinkMsg)

    def OnSkillsChanged(self, *args):
        sm.GetService('neocom').Blink('charactersheet')

    def OnSkillQueueChanged(self):
        self.OnSkillsChanged()

    def ForceShowSkillHistoryHighlighting(self, skillTypeIds):
        CharacterSheetWindow.OpenSkillHistoryHilightSkills(skillTypeIds)

    def OnKillNotification(self):
        sm.StartService('objectCaching').InvalidateCachedMethodCall('charMgr', 'GetRecentShipKillsAndLosses', 25, None)

    def OnUpdatedMedalsAvailable(self):
        sm.GetService('neocom').Blink('charactersheet')

    def Show(self):
        wnd = self.GetWnd(1)
        if wnd is not None and not wnd.destroyed:
            wnd.Maximize()
            return wnd

    def GetWnd(self, getnew = 0):
        if not getnew:
            return form.CharacterSheet.GetIfOpen()
        else:
            return form.CharacterSheet.ToggleOpenClose()

    def GetSubscriptionDays(self, force = False):
        if self.daysLeft == -1 or force:
            charDetails = sm.RemoteSvc('charUnboundMgr').GetCharacterToSelect(session.charid)
            self.daysLeft = getattr(charDetails[0], 'daysLeft', None) if len(charDetails) else None
        return self.daysLeft
