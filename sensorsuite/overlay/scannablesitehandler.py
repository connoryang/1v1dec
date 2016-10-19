#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\sensorsuite\overlay\scannablesitehandler.py
from sensorsuite.overlay.scannablesitedata import ScannableSiteData
from sensorsuite.overlay.sitehandler import SiteHandler

class ScannableSiteHandler(SiteHandler):

    def __init__(self):
        SiteHandler.__init__(self)

    def GetSiteData(self, siteID, position, targetID, difficulty, dungeonNameID, factionID, scanStrengthAttribute):
        return ScannableSiteData(siteID, position, targetID, difficulty, dungeonNameID, factionID, scanStrengthAttribute)

    def ProcessSiteUpdate(self, addedSites, removedSites):
        SiteHandler.ProcessSiteUpdate(self, addedSites, removedSites)
        sm.GetService('sensorSuite').InjectScannerResults(self.siteType)
