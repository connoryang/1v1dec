#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\services\structure\structureDeployment.py
import evetypes
import service
import localization
import inventorycommon
import carbonui.const as uiconst
from eve.common.script.sys.eveCfg import InShipInSpace
from eve.client.script.ui.structure.deployment.deploymentCont import StructureDeploymentWnd
from eve.client.script.ui.structure.deployment.deploymentEntity import StructurePlacementEntity

class StructureDeployment(service.Service):
    __guid__ = 'svc.structureDeployment'
    __dependencies__ = ['machoNet', 'viewState', 'michelle']
    __notifyevents__ = ['OnSessionChanged',
     'OnViewStateChanged',
     'OnWarpStarted',
     'OnItemChange',
     'DoBallClear']

    def Run(self, *args):
        self.isDeploying = False
        self.isMovingStrucuture = False
        self.tacticalOverlayWasOpen = None
        self.invItem = None
        self.wnd = None
        self.entity = None
        self.blocked = self.GetBlockedSystems()

    def GetBlockedSystems(self):
        blocked = set()
        for _, row in cfg.mapSolarSystemContentCache.iteritems():
            if const.categoryStructure in getattr(row, 'disallowedAnchorCategories', []):
                blocked.add(row.solarSystemID)

        return blocked

    def Unanchor(self, structureID, typeID):
        if eve.Message('ConfirmDecommissionStructure', {'item': typeID}, uiconst.YESNO, suppress=uiconst.ID_YES) == uiconst.ID_YES:
            sm.RemoteSvc('structureDeployment').Unanchor(structureID)

    def CancelUnanchor(self, structureID, typeID):
        sm.RemoteSvc('structureDeployment').CancelUnanchor(structureID)

    def Deploy(self, invItem):
        if self.isDeploying:
            return
        if not self.viewState.IsViewActive('inflight'):
            return
        if not InShipInSpace():
            return
        if self.michelle.InWarp():
            raise UserError('ShipInWarp')
        if inventorycommon.util.IsNPC(session.corpid):
            raise UserError('DropNeedsPlayerCorp', {'item': invItem.typeID})
        if not session.corprole & const.corpRoleStationManager:
            raise UserError('CrpAccessDenied', {'reason': localization.GetByLabel('UI/Corporations/AccessRestrictions/InsufficientRoles')})
        if session.solarsystemid in self.blocked:
            raise UserError('CantDeployBlocked', {'typeID': invItem.typeID})
        try:
            self.invItem = invItem
            self.isDeploying = True
            self.entity = StructurePlacementEntity(invItem.typeID)
            self.wnd = StructureDeploymentWnd.Open(controller=self, useDefaultPos=True, typeID=invItem.typeID)
            tacticalOverlayOpen = sm.GetService('tactical').IsTacticalOverlayActive()
            self.tacticalOverlayWasOpen = tacticalOverlayOpen
            if not tacticalOverlayOpen:
                sm.GetService('tactical').ShowTacticalOverlay()
        except Exception:
            self._Cleanup()
            raise

    def IsDeploying(self):
        return self.isDeploying

    def _Cleanup(self):
        if self.wnd:
            self.wnd.Close()
            self.wnd = None
        if self.tacticalOverlayWasOpen is False:
            sm.GetService('tactical').HideTacticalOverlay()
            self.tacticalOverlayWasOpen = None
        self.isDeploying = False
        if self.entity:
            self.entity.Close()
            self.entity = None

    def ConfirmDeployment(self, schedule = None, profileID = None, structureName = ''):
        pos = self.entity.GetPosition()
        rotation = self.entity.GetRotation()
        schedulaInt = int(schedule)
        sm.RemoteSvc('structureDeployment').Anchor(self.invItem.itemID, pos[0], pos[2], rotation[0], schedulaInt, profileID, structureName)
        self._Cleanup()

    def CancelDeployment(self):
        self._Cleanup()

    def StartMovingStructure(self):
        self.isMovingStrucuture = True
        self.entity.StartMoving()

    def EndMovingStructure(self):
        self.isMovingStrucuture = False
        self.entity.EndMoving()

    def IsMovingStructure(self):
        return self.isMovingStrucuture

    def GetCaption(self):
        return evetypes.GetName(self.invItem.typeID)

    def GetSubCaption(self):
        return 'Drag structure gantry with left mouse button and rotate with right'

    def OnSessionChanged(self, *args):
        self.CancelDeployment()

    def OnItemChange(self, item, change):
        if self.invItem and self.invItem.itemID == item.itemID:
            self.CancelDeployment()

    def OnViewStateChanged(self, *args):
        self.CancelDeployment()

    def OnWarpStarted(self, *args):
        self.CancelDeployment()

    def DoBallClear(self, *args):
        self.CancelDeployment()

    def MoveDragObject(self):
        self.entity.MoveDragObject()

    def RotateDragObject(self):
        self.entity.RotateDragObject()

    def GetEntity(self):
        return self.entity
