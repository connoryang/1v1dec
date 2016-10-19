#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\dockedUI\controllers\baseController.py
import blue
from eve.client.script.ui.station import stationServiceConst
from utillib import KeyVal

class BaseStationController(object):

    def __init__(self, itemID = None):
        self.serviceAccessCache = {}

    def Undock(self):
        pass

    def ChangeDockedMode(self, viewState):
        pass

    def CorpsWithOffices(self):
        return []

    def GetNumberOfUnrentedOffices(self):
        return 0

    def DoesOfficeExist(self):
        return False

    def CanRent(self):
        return self._HasRole(const.corpRoleCanRentOffice)

    def CanMoveHQ(self):
        return self._HasRole(const.corpRoleDirector)

    def CanUnrent(self):
        return self._HasRole(const.corpRoleDirector)

    def IsHqAllowed(self):
        return True

    def _HasRole(self, corpRole):
        return session.corprole & corpRole == corpRole

    def IsMyHQ(self):
        return False

    def MyCorpIsOwner(self):
        return False

    def GetCostForOpeningOffice(self):
        return 0

    def RentOffice(self, cost):
        pass

    def GetMyCorpOffice(self):
        return None

    def CorpHasItemsInstaton(self):
        return False

    def UnrentOffice(self):
        pass

    def SetHQ(self):
        pass

    def GetCostForGettingCorpJunkBack(self):
        return 0

    def ReleaseImpoundedItems(self, cost):
        pass

    def OpenStationMgmt(self):
        pass

    def GetServicesInStation(self):
        pass

    def GetGuests(self):
        return {}

    def PerformAndGetErrorForStandingCheck(self, stationServiceID):
        return None

    def RemoveServiceFromCache(self, serviceID):
        pass

    def GetAgents(self):
        return []

    def GetOwnerID(self):
        return None

    def HasCorpImpountedItems(self):
        return False

    def GetStationItemsAndShipsClasses(self):
        return (None, None)

    def GetItemID(self):
        return None

    def InProcessOfUndocking(self):
        return False

    def IsRestrictedByGraphicsSettings(self):
        return False

    def IsExiting(self):
        return False

    def GetDisabledDockingModeHint(self):
        return None

    def GetDockedModeTextPath(self, viewName = None):
        return None

    def GetCurrentStateForService(self, serviceID):
        return KeyVal(isEnabled=True)

    def _GetServiceInfoAvailable(self, servicesAtLocation):
        haveServices = []
        for serviceData in stationServiceConst.serviceData:
            if stationServiceConst.serviceIDAlwaysPresent in serviceData.maskServiceIDs:
                haveServices.append(serviceData)
            if serviceData.serviceID in servicesAtLocation:
                haveServices.append(serviceData)

        return haveServices

    def IsControlable(self):
        return False

    def TakeControl(self):
        pass

    def CanTakeControl(self):
        return False

    def GetCharInControl(self):
        return None
