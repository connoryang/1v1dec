#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\services\structure\structureGuests.py
import uthread
import service

class StructureGuests(service.Service):
    __guid__ = 'svc.structureGuests'
    __notifyevents__ = ['DoSessionChanging', 'OnCharacterEnteredStructure', 'OnCharacterLeftStructure']

    def Run(self, *args):
        self.guests = None
        self.lock = uthread.Semaphore()

    def GetGuests(self):
        if self.guests is None:
            with self.lock:
                if self.guests is None:
                    self.guests = sm.RemoteSvc('structureGuests').GetGuests(session.structureid)
        return self.guests or {}

    def IsGuest(self, charID):
        return charID in self.GetGuests()

    def DoSessionChanging(self, isRemote, session, change):
        if 'structureid' in change:
            self.guests = None

    def OnCharacterEnteredStructure(self, characterID, corporationID, allianceID, factionID):
        self.GetGuests()[characterID] = (corporationID, allianceID, factionID)

    def OnCharacterLeftStructure(self, characterID):
        self.GetGuests().pop(characterID, None)
