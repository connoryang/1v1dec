#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\neocom\charsheet\killRightsPanel.py
from carbonui.primitives.container import Container
from eve.client.script.ui.control import entries
from eve.client.script.ui.control.eveScroll import Scroll
import blue
from localization import GetByLabel

class KillRightsPanel(Container):
    default_name = 'KillRightsPanel'
    __notifyevents__ = ['OnKillRightSold',
     'OnKillRightExpired',
     'OnKillRightSellCancel',
     'OnKillRightCreated',
     'OnKillRightUsed']

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        sm.RegisterNotify(self)
        self.scroll = Scroll(parent=self, padding=(0, 4, 0, 4))

    def LoadPanel(self, *args):
        scrolllist = []
        killRights = sm.GetService('bountySvc').GetMyKillRights()
        currentTime = blue.os.GetWallclockTime()
        myKillRights = filter(lambda x: x.fromID == session.charid and currentTime < x.expiryTime, killRights)
        otherKillRights = filter(lambda x: x.toID == session.charid and currentTime < x.expiryTime, killRights)
        charIDsToPrime = set()
        for eachKR in myKillRights:
            charIDsToPrime.add(eachKR.toID)

        for eachKR in otherKillRights:
            charIDsToPrime.add(eachKR.fromID)

        cfg.eveowners.Prime(charIDsToPrime)
        if myKillRights:
            scrolllist.append(entries.Get('Header', {'label': GetByLabel('UI/InfoWindow/CanKill'),
             'hideLines': True}))
            for killRight in myKillRights:
                scrolllist.append(entries.Get('KillRightsEntry', {'charID': killRight.toID,
                 'expiryTime': killRight.expiryTime,
                 'killRight': killRight,
                 'isMine': True}))

        if otherKillRights:
            scrolllist.append(entries.Get('Header', {'label': GetByLabel('UI/InfoWindow/CanBeKilledBy'),
             'hideLines': True}))
            for killRight in otherKillRights:
                scrolllist.append(entries.Get('KillRightsEntry', {'charID': killRight.fromID,
                 'expiryTime': killRight.expiryTime,
                 'killRight': killRight,
                 'isMine': False}))

        self.scroll.sr.id = 'charsheet_killrights'
        self.scroll.Load(contentList=scrolllist, noContentHint=GetByLabel('UI/CharacterSheet/CharacterSheetWindow/KillsTabs/NoKillRightsFound'))

    def OnKillRightSold(self, killRightID):
        if self.display:
            self.LoadKillRightsPanel()

    def OnKillRightExpired(self, killRightID):
        if self.display:
            self.LoadKillRightsPanel()

    def OnKillRightSellCancel(self, killRightID):
        if self.display:
            self.LoadKillRightsPanel()

    def OnKillRightCreated(self, killRightID, fromID, toID, expiryTime):
        if self.display:
            self.LoadKillRightsPanel()

    def OnKillRightUsed(self, killRightID, toID):
        if self.display:
            self.LoadKillRightsPanel()
