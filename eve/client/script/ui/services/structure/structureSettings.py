#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\services\structure\structureSettings.py
import service
import util

class StructureSettings(service.Service):
    __guid__ = 'svc.structureSettings'

    def Run(self, *args):
        pass

    @util.Memoized(2)
    def CharacterHasService(self, structureID, serviceID):
        return sm.RemoteSvc('structureSettings').CharacterHasService(structureID, serviceID)
