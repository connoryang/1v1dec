#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\services\structure\structureOffices.py
import uthread
import service

class StructureOffices(service.Service):
    __guid__ = 'svc.structureOffices'
    __dependencies__ = ['corp']
    __notifyevents__ = ['DoSessionChanging', 'OnOfficeRentalChanged']

    def Run(self, *args):
        sm.FavourMe(self.OnOfficeRentalChanged)
        self.lock = uthread.Semaphore()
        self.offices = None

    def DoSessionChanging(self, isRemote, session, change):
        if 'structureid' in change:
            self.offices = None

    def OnOfficeRentalChanged(self, corporationID, officeID, folderID):
        self.offices = None

    def GetOffices(self):
        if self.offices is None:
            with self.lock:
                if self.offices is None:
                    self.offices = sm.RemoteSvc('structureOffices').GetCorporations(session.structureid)
        return self.offices or []

    def GetCorporations(self):
        return self.corp.GetCorporations(self.GetOffices())

    def HasOffice(self):
        return session.corpid in self.GetOffices()

    def GetCost(self, structureID = None):
        if structureID or session.structureid:
            return sm.RemoteSvc('structureOffices').OfficeCost(structureID or session.structureid, session.corpid)

    def RentOffice(self, cost, structureID = None):
        if structureID or session.structureid:
            return sm.RemoteSvc('structureOffices').RentOffice(structureID or session.structureid, session.corpid, cost)

    def UnrentOffice(self, structureID = None):
        if structureID or session.structureid:
            return sm.RemoteSvc('structureOffices').UnrentOffice(structureID or session.structureid, session.corpid)
