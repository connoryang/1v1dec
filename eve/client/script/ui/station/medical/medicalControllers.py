#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\station\medical\medicalControllers.py
import blue
from carbonui import const as uiconst
from signals import Signal

class MedicalControllerBase(object):
    showRemoteStations = False
    canActivateClone = False

    def __init__(self):
        self.on_home_station_changed = Signal()

    def SetHomeStation(self, locationID):
        pass

    def GetPotentialHomeStations(self):
        stations, remoteStationDate = [], None
        return (stations, remoteStationDate)

    def VerifiedDocked(self):
        raise UserError('MustBeDocked')

    def HasAbilityToActivateClone(self):
        return self.canActivateClone

    def ShowRemoteStations(self):
        return self.showRemoteStations

    def ActivateClone(self):
        pass

    def GetHomeStation(self):
        return self.GetHomeStationRow().stationID

    def GetHomeStationRow(self):
        return sm.RemoteSvc('charMgr').GetHomeStationRow()

    def _VerifyStationIsValid(self, stationID):
        stations, remoteStationDate = self.GetPotentialHomeStations()
        try:
            station = next((station for station in stations if station.stationID == stationID))
        except StopIteration:
            raise UserError('InvalidHomeStation')

        if stationID == self.GetHomeStation():
            raise UserError('MedicalYouAlreadyHaveACloneContractAtThatStation')
        if station.isRemote and remoteStationDate is not None and remoteStationDate > blue.os.GetWallclockTime():
            raise UserError('HomeStationRemoteCooldown', {'nextDate': remoteStationDate})
        if station.isRemote:
            if eve.Message('AskAcceptRemoteCloneContractCost', {'cost': const.costCloneContract}, uiconst.YESNO) != uiconst.ID_YES:
                return False
        elif eve.Message('AskAcceptCloneContractCost', {'cost': const.costCloneContract}, uiconst.YESNO) != uiconst.ID_YES:
            return False
        self.VerifiedDocked()
        return True

    def _InvalidateHomeStationCalls(self):
        sm.GetService('objectCaching').InvalidateCachedMethodCall('charMgr', 'GetHomeStation')
        sm.GetService('objectCaching').InvalidateCachedMethodCall('charMgr', 'GetHomeStationRow')


class MedicalControllerStation(MedicalControllerBase):
    showRemoteStations = True
    canActivateClone = True

    def SetHomeStation(self, stationID, *args):
        self.VerifiedDocked()
        stationOk = self._VerifyStationIsValid(stationID)
        if not stationOk:
            return
        try:
            sm.GetService('corp').GetCorpStationManager().SetHomeStation(stationID)
        finally:
            pass

        self._InvalidateHomeStationCalls()
        self.on_home_station_changed()

    def GetPotentialHomeStations(self):
        if session.stationid2:
            return sm.GetService('corp').GetCorpStationManager().GetPotentialHomeStations()
        else:
            return MedicalControllerBase.GetPotentialHomeStations(self)

    def VerifiedDocked(self):
        if not session.stationid2:
            raise UserError('MustBeDocked')

    def ActivateClone(self):
        stationMgr = sm.GetService('corp').GetCorpStationManager()
        sm.GetService('sessionMgr').PerformSessionChange('clonejump', stationMgr.ActivateClone)


class MedicalControllerStructure(MedicalControllerBase):

    def GetPotentialHomeStations(self):
        stations, remoteStationDate = sm.RemoteSvc('structureMedical').GetPotentialHomeStations()
        return (stations, remoteStationDate)

    def SetHomeStation(self, stationID):
        if stationID != session.structureid:
            stationOk = self._VerifyStationIsValid(stationID)
            if not stationOk:
                return
        sm.RemoteSvc('structureMedical').ChangeCloneToStructure(stationID)
        self._InvalidateHomeStationCalls()
        self.on_home_station_changed()

    def VerifiedDocked(self):
        if not session.structureid:
            raise UserError('MustBeDocked')
