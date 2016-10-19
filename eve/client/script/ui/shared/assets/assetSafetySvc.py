#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\assets\assetSafetySvc.py
import util
import service
import carbonui.const as uiconst
from eve.common.script.sys.eveCfg import IsControllingStructure

class AssetSafetySvc(service.Service):
    __guid__ = 'svc.assetSafety'
    __servicename__ = 'assetSafety'
    __notifyevents__ = ['OnAssetSafetyCreated', 'OnAssetSafetyDelivered']
    __dependencies__ = ['objectCaching']

    def GetItemsInSafetyForCharacter(self):
        return sm.RemoteSvc('structureAssetSafety').GetItemsInSafetyForCharacter()

    def GetItemsInSafetyForCorp(self):
        return sm.RemoteSvc('structureAssetSafety').GetItemsInSafetyForCorp()

    def MoveItemsInStructureToAssetSafetyForCharacter(self, solarSystemID, structureID):
        if IsControllingStructure() and session.shipid == structureID:
            raise UserError('CannotPutItemsInSafetyWhileControllingStructure')
        itemsAtStructureExceptCurrentShip = [ item for item in sm.GetService('invCache').GetInventory(const.containerGlobal).ListStationItems(structureID) if item.itemID != session.shipid ]
        if 0 < len(itemsAtStructureExceptCurrentShip):
            if util.IsWormholeSystem(solarSystemID):
                label = 'ConfirmAssetEjectionCharacter'
            else:
                label = 'ConfirmAssetSafetyCharacter'
            if eve.Message(label, {'structureID': structureID,
             'solarsystemID': solarSystemID}, uiconst.YESNO) == uiconst.ID_YES:
                sm.RemoteSvc('structureAssetSafety').MovePersonalAssetsToSafety(solarSystemID, structureID)
        else:
            raise UserError('NoItemsToPutInAssetSafety')

    def MoveItemsInStructureToAssetSafetyForCorp(self, solarSystemID, structureID):
        if util.IsWormholeSystem(solarSystemID):
            label = 'ConfirmAssetEjectionCorp'
        else:
            label = 'ConfirmAssetSafetyCorp'
        if eve.Message(label, {'corpName': cfg.eveowners.Get(session.corpid).name,
         'structureID': structureID,
         'solarsystemID': solarSystemID}, uiconst.YESNO) == uiconst.ID_YES:
            sm.RemoteSvc('structureAssetSafety').MoveCorpAssetsToSafety(solarSystemID, structureID)

    def OnAssetSafetyCreated(self, ownerID, solarSystemID, locationID):
        if ownerID == session.corpid:
            self.objectCaching.InvalidateCachedMethodCall('corpmgr', 'GetAssetInventoryForLocation', session.corpid, locationID, 'offices')
            self.objectCaching.InvalidateCachedMethodCall('structureAssetSafety', 'GetItemsInSafetyForCorp')
            sm.ScatterEvent('OnReloadCorpAssets')

    def OnAssetSafetyDelivered(self, ownerID, solarSystemID, locationID, assetWrapID):
        if ownerID == session.corpid:
            self.objectCaching.InvalidateCachedMethodCall('structureAssetSafety', 'GetItemsInSafetyForCorp')
            sm.ScatterEvent('OnReloadCorpAssets')
