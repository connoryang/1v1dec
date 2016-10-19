#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\sensorsuite\overlay\scannablesitedata.py
from carbonui.control.menuLabel import MenuLabel
from eve.client.script.ui.shared.radialMenu.radialMenuUtils import SimpleRadialMenuAction
from eve.client.script.ui.shared.radialMenu.spaceRadialMenuFunctions import bookMarkOption
from localization import GetByMessageID
from sensorsuite.overlay.sitedata import SiteData

class BaseScannableSiteData(SiteData):
    scanGroupID = None
    groupID = None

    def __init__(self, siteID, position, targetID):
        SiteData.__init__(self, siteID, position)
        self.targetID = targetID

    def GetMenu(self):
        scanSvc = sm.GetService('scanSvc')
        menu = [(MenuLabel(uicore.cmd.OpenScanner.nameLabelPath), uicore.cmd.OpenScanner, [])]
        menu.extend(scanSvc.GetScanResultMenuWithIgnore(self, self.scanGroupID))
        return menu

    def GetSiteActions(self):
        return [SimpleRadialMenuAction(option1=uicore.cmd.OpenScanner.nameLabelPath)]

    def GetSecondaryActions(self):
        return [bookMarkOption, SimpleRadialMenuAction(option1='UI/Inflight/Scanner/IngoreResult'), SimpleRadialMenuAction(option1='UI/Inflight/Scanner/IgnoreOtherResults')]

    def WarpToAction(self, _, distance, *args):
        return sm.GetService('menu').WarpToScanResult(self.targetID, minRange=distance)

    def GetScanName(self):
        return (None, '')


class ScannableSiteData(BaseScannableSiteData):
    scanGroupID = None
    groupID = None

    def __init__(self, siteID, position, targetID, difficulty, dungeonNameID, factionID, scanStrengthAttribute):
        BaseScannableSiteData.__init__(self, siteID, position, targetID)
        self.difficulty = difficulty
        self.dungeonNameID = dungeonNameID
        self.factionID = factionID
        self.scanStrengthAttribute = scanStrengthAttribute

    def GetName(self):
        return self.targetID

    def GetScanName(self):
        if self.dungeonNameID:
            dungeonName = GetByMessageID(self.dungeonNameID)
            return (self.dungeonNameID, dungeonName)
        return (None, '')
