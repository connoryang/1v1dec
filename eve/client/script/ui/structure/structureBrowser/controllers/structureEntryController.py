#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\structure\structureBrowser\controllers\structureEntryController.py
import random
from carbon.common.script.util.format import StrFromColor
from carbon.common.script.util.linkUtil import GetShowInfoLink
from eve.client.script.ui.structure.structureBrowser.tempUtils import GetStuctureServices
from eve.common.script.util.eveFormat import FmtSystemSecStatus
import evetypes
from localization import GetByLabel
from signals import Signal
import structures
from utillib import KeyVal

class StructureEntryController(object):

    def __init__(self, itemID, solarsystemID, typeID, ownerID, structureServices = None, profileID = None, currentSchedule = 0, nextSchedule = 0, state = None, unanchoring = None, fuelExpires = None):
        self.structureInfo = KeyVal(itemID=itemID, solarsystemID=solarsystemID, typeID=typeID, ownerID=ownerID, structureServices=structureServices, profileID=profileID, currentSchedule=currentSchedule, nextSchedule=nextSchedule, state=state, unanchoring=unanchoring, fuelExpires=fuelExpires)
        self.systemAndStructureName = None
        self.requiredHours = None
        self.on_structure_state_changed = Signal()

    def GetNumJumps(self):
        jumps = sm.GetService('clientPathfinderService').GetJumpCountFromCurrent(self.GetSolarSystemID())
        return jumps

    def GetSecurity(self):
        return sm.GetService('map').GetSecurityStatus(self.GetSolarSystemID())

    def GetSolarSystemID(self):
        return self.structureInfo.solarsystemID

    def GetSecurityWithColor(self):
        sec, col = FmtSystemSecStatus(self.GetSecurity(), 1)
        col.a = 1.0
        color = StrFromColor(col)
        return '<color=%s>%s</color>' % (color, sec)

    def GetName(self):
        if self.systemAndStructureName:
            return self.systemAndStructureName
        locationName = cfg.evelocations.Get(self.GetSolarSystemID()).name
        structureName = cfg.evelocations.Get(self.GetItemID()).name
        if evetypes.GetCategoryID(self.GetTypeID()) == const.categoryStation:
            stationInfo = cfg.stations.GetIfExists(self.GetItemID())
            if stationInfo:
                locationName = cfg.evelocations.Get(stationInfo.orbitID).name
                structureName = structureName.replace(locationName, '')
                structureName = structureName.replace(' - ', '', 1)
        if not structureName:
            structureName = evetypes.GetName(self.GetTypeID())
        solarsystemName = cfg.evelocations.Get(self.GetSolarSystemID()).name
        solarsystemLink = GetShowInfoLink(const.typeSolarSystem, solarsystemName, self.GetSolarSystemID())
        locationName = locationName.replace(solarsystemName, solarsystemLink)
        systemAndStructureName = '<br>'.join([locationName, structureName])
        self.systemAndStructureName = systemAndStructureName
        return self.systemAndStructureName

    def GetSystemName(self):
        return cfg.evelocations.Get(self.structureInfo.solarsystemID).name

    def GetTax(self):
        return random.randint(0, 10)

    def GetOwnerID(self):
        return self.structureInfo.ownerID

    def GetOwnerName(self):
        return cfg.eveowners.Get(self.GetOwnerID()).name

    def GetTypeID(self):
        return self.structureInfo.typeID

    def GetItemID(self):
        return self.structureInfo.itemID

    def GetProfileID(self):
        return self.structureInfo.profileID

    def GetServices(self):
        structureServices = GetStuctureServices(self.structureInfo.structureServices)
        return structureServices

    def HasService(self, serviceID):
        for eachService in self.GetServices():
            if eachService.name == serviceID:
                return True

        return False

    def GetStateLabel(self):
        return GetByLabel(structures.STATE_LABELS.get(self.GetState(), '.unknown)'))

    def GetInfoForExtraColumns(self, serviceID, settingData):
        if serviceID in self.structureInfo.structureServices:
            info = self.structureInfo.structureServices.get(serviceID)
            return info

    def GetCurrentSchedule(self):
        return self.structureInfo.currentSchedule

    def GetNextWeekSchedule(self):
        return self.structureInfo.nextSchedule

    def GetFuelExpiry(self):
        return self.structureInfo.fuelExpires

    def GetState(self):
        return self.structureInfo.state

    def GetRequiredHours(self):
        if self.requiredHours is None:
            self.requiredHours = int(sm.GetService('clientDogmaIM').GetDogmaLocation().GetModifiedTypeAttribute(self.GetTypeID(), const.attributeVulnerabilityRequired))
        return self.requiredHours

    def CanUnanchor(self):
        if session.corprole & const.corpRoleDirector:
            if self.structureInfo.unanchoring is None:
                return True
        return False

    def CanCancelUnanchor(self):
        if session.corprole & const.corpRoleDirector:
            if self.structureInfo.unanchoring is not None:
                return True
        return False

    def StructureStateChanged(self, structureID, newStructureState):
        self.structureInfo.state = newStructureState
        self.on_structure_state_changed(structureID)
