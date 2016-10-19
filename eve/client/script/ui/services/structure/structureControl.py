#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\services\structure\structureControl.py
import service
from eve.common.script.sys.eveCfg import IsControllingStructure

class StructureControl(service.Service):
    __guid__ = 'svc.structureControl'

    def Board(self, structureID):
        if session.structureid and session.solarsystemid and structureID == session.structureid and not IsControllingStructure():
            sm.RemoteSvc('structureControl').Board(session.structureid)

    def Alight(self, structureID):
        if session.shipid and session.solarsystemid and structureID == session.shipid:
            sm.RemoteSvc('structureControl').Alight(session.shipid)

    def CanBoard(self, structureID):
        if session.structureid and session.solarsystemid and structureID == session.structureid:
            return sm.RemoteSvc('structureControl').CanBoard(session.structureid)
