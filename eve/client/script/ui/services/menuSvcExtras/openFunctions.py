#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\services\menuSvcExtras\openFunctions.py
import util
import form
import invCtrl
import const

def OpenShipHangarCargo(itemIDs):
    usePrimary = len(itemIDs) == 1
    openFromWnd = uicore.registry.GetActive() if usePrimary else None
    for itemID in itemIDs:
        invID = ('ShipCargo', itemID)
        form.Inventory.OpenOrShow(invID=invID, usePrimary=usePrimary, openFromWnd=openFromWnd)


def OpenDroneBay(itemIDs):
    usePrimary = len(itemIDs) == 1
    openFromWnd = uicore.registry.GetActive() if usePrimary else None
    for itemID in itemIDs:
        invID = ('ShipDroneBay', itemID)
        invCtrl.ShipDroneBay(itemID).GetItems()
        form.Inventory.OpenOrShow(invID=invID, usePrimary=usePrimary, openFromWnd=openFromWnd)


def OpenFighterBay(itemIDs):
    usePrimary = len(itemIDs) == 1
    openFromWnd = uicore.registry.GetActive() if usePrimary else None
    for itemID in itemIDs:
        invID = ('ShipFighterBay', itemID)
        invCtrl.ShipFighterBay(itemID).GetItems()
        form.Inventory.OpenOrShow(invID=invID, usePrimary=usePrimary, openFromWnd=openFromWnd)


def OpenShipMaintenanceBayShip(itemID, name):
    invID = ('ShipMaintenanceBay', itemID)
    if itemID != util.GetActiveShip() and not session.stationid2:
        invCtrl.ShipMaintenanceBay(itemID).GetItems()
        sm.GetService('inv').AddTemporaryInvLocation(invID)
    form.Inventory.OpenOrShow(invID=invID)


def OpenFleetHangar(itemID):
    invID = ('ShipFleetHangar', itemID)
    if itemID != util.GetActiveShip() and not session.stationid2:
        invCtrl.ShipFleetHangar(itemID).GetItems()
        sm.GetService('inv').AddTemporaryInvLocation(invID)
    form.Inventory.OpenOrShow(invID=invID)


def OpenInfrastructureHubPanel(itemID):
    occupierID = sm.GetService('facwar').GetSystemOccupier(session.solarsystemid)
    if occupierID == session.warfactionid:
        bp = sm.GetService('michelle').GetBallpark()
        distance = bp.GetSurfaceDist(session.shipid, itemID)
        if distance < const.facwarIHubInteractDist:
            form.FWInfrastructureHub.Open(itemID=itemID)
        else:
            uicore.Message('InfrastructureHubCannotOpenDistance')
    else:
        uicore.Message('InfrastructureHubCannotOpenFaction', {'factionName': cfg.eveowners.Get(occupierID).name})


def OpenCargoContainer(invItems):
    usePrimary = len(invItems) == 1
    openFromWnd = uicore.registry.GetActive() if usePrimary else None
    for item in invItems:
        if item.ownerID not in (session.charid, session.corpid):
            eve.Message('CantDoThatWithSomeoneElsesStuff')
            return
        invID = ('StationContainer', item.itemID)
        form.Inventory.OpenOrShow(invID=invID, usePrimary=usePrimary, openFromWnd=openFromWnd)


def OpenBountyOffice(charID):
    wnd = form.BountyWindow.GetIfOpen()
    if not wnd:
        wnd = form.BountyWindow.Open()
    wnd.ownerID = charID
    wnd.ShowResult(charID)


def ViewAuditLogForALSC(itemID):
    form.AuditLogSecureContainerLogViewer.CloseIfOpen()
    form.AuditLogSecureContainerLogViewer.Open(itemID=itemID)


def RepairItems(items):
    if items is None or len(items) < 1:
        return
    wnd = form.RepairShopWindow.Open()
    if wnd and not wnd.destroyed:
        wnd.DisplayRepairQuote(items)


def OpenProfileSettingsForStructure(itemID):
    corpStructures = sm.GetService('structureDirectory').GetCorporationStructures()
    structureInfo = corpStructures.get(itemID, None)
    if not structureInfo:
        return
    profileID = structureInfo['profileID']
    browserController = sm.GetService('structureControllers').GetStructureBrowserController()
    browserController.SetProfileSettingsSelected()
    browserController.SelectProfile(profileID)
    from eve.client.script.ui.structure.structureBrowser.structureBrowserWnd import StructureBrowserWnd
    wnd = StructureBrowserWnd.GetIfOpen()
    if wnd:
        wnd.ForceProfileSettingsSelected()
    else:
        StructureBrowserWnd.Open()
