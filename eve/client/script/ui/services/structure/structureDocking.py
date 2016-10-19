#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\services\structure\structureDocking.py
from contextlib import contextmanager
import service
import carbonui.const as uiconst
from eve.client.script.ui.station.undockQuestions import IsOkToUndock

class StructureDocking(service.Service):
    __guid__ = 'svc.structureDocking'
    __dependencies__ = ['autoPilot', 'clientDogmaIM', 'gameui']

    @property
    def dogmaLocation(self):
        return self.clientDogmaIM.GetDogmaLocation()

    def Undock(self, structureID):
        if not self._InStateToUndock(structureID):
            return
        if session.shipid == session.structureid:
            shipID = None
        else:
            shipID = session.shipid
        if not IsOkToUndock():
            return

        def TryUndockOnServer(doIgnoreContraband):
            sm.RemoteSvc('structureDocking').Undock(session.structureid, shipID, ignoreContraband=doIgnoreContraband)

        try:
            ignoreContraband = settings.user.suppress.Get('suppress.ShipContrabandWarningUndock', None) == uiconst.ID_OK
            TryUndockOnServer(doIgnoreContraband=ignoreContraband)
        except UserError as e:
            if e.msg == 'ShipContrabandWarningUndock':
                if eve.Message(e.msg, e.dict, uiconst.OKCANCEL, suppress=uiconst.ID_OK) == uiconst.ID_OK:
                    TryUndockOnServer(doIgnoreContraband=True)
            else:
                raise

        self.CloseStationWindows()

    def _InStateToUndock(self, structureID):
        if not session.structureid:
            return False
        if not session.solarsystemid:
            return False
        if structureID != session.structureid:
            return False
        return True

    def Dock(self, structureID):

        def RequestDocking():
            if session.shipid and session.solarsystemid:
                sm.RemoteSvc('structureDocking').Dock(structureID, session.shipid)

        self.autoPilot.NavigateSystemTo(structureID, 2500, RequestDocking)

    def ActivateShip(self, shipID):
        if session.structureid:
            typeID = sm.GetService('invCache').GetInventoryFromId(shipID).GetTypeID()
            self.dogmaLocation.CheckSkillRequirementsForType(None, typeID, 'ShipHasSkillPrerequisites')
            self.dogmaLocation.MakeShipActive(shipID)

    def LeaveShip(self, shipID):
        if session.structureid:
            capsuleID = self.gameui.GetShipAccess().LeaveShip(shipID)
            self.dogmaLocation.MakeShipActive(capsuleID)

    def CloseStationWindows(self):
        from reprocessing.ui.reprocessingWnd import ReprocessingWnd
        ReprocessingWnd.CloseIfOpen()
