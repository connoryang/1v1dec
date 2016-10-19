#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\station\undockQuestions.py
import structures
from carbonui import const as uiconst
from eve.client.script.ui.station.askForUndock import IsOkToBoardWithModulesLackingSkills
from eve.common.script.sys.eveCfg import IsOutpost
from eve.client.script.ui.shared.dockedUI.controllers.structureController import StructureController

def IsOkToUndock(stationTypeID = None):
    if not IsOkToUndockInUnfriendlySpace(stationTypeID):
        return False
    if not IsOkToBoardWithModulesLackingSkills(sm.GetService('clientDogmaIM').GetDogmaLocation(), uicore.Message):
        return False
    if not IsOkToUndockWithCrimewatchTimers():
        return False
    return True


def IsOkToUndockInUnfriendlySpace(stationTypeID = None):
    if settings.user.suppress.Get('suppress.AskUndockInEnemySystem', None):
        return True
    if session.structureid:
        if sm.RemoteSvc('structureSettings').CharacterHasSetting(session.structureid, structures.SETTING_HOUSING_CAN_DOCK):
            return True
        structureController = StructureController(itemID=session.structureid)
        ownerName = cfg.eveowners.Get(structureController.GetOwnerID()).ownerName
        if not _ConfirmDoUndockInEnemySystem(ownerName):
            return False
    elif IsOutpost(session.stationid2) or stationTypeID and sm.GetService('godma').GetType(stationTypeID).isPlayerOwnable == 1:
        if cfg.mapSystemCache[session.solarsystemid2].securityStatus >= 0.0:
            return True
        try:
            sm.GetService('corp').GetCorpStationManager().DoStandingCheckForStationService(const.stationServiceDocking)
        except UserError as e:
            sovHolderName = cfg.eveowners.Get(eve.stationItem.ownerID).ownerName
            if not _ConfirmDoUndockInEnemySystem(sovHolderName):
                return False

    else:
        facwarSvc = sm.GetService('facwar')
        if not facwarSvc.IsFacWarSystem(session.solarsystemid2):
            return True
        occupierID = facwarSvc.GetSystemOccupier(session.solarsystemid2)
        if not facwarSvc.IsEnemyCorporation(session.corpid, occupierID):
            return True
        sovHolderName = cfg.eveowners.Get(occupierID).ownerName
        if not _ConfirmDoUndockInEnemySystem(sovHolderName):
            return False
    return True


def _ConfirmDoUndockInEnemySystem(ownerName):
    if uicore.Message('AskUndockInEnemySystem', {'sovHolderName': ownerName}, uiconst.YESNO, suppress=uiconst.ID_YES) != uiconst.ID_YES:
        return False
    return True


def IsOkToUndockWithCrimewatchTimers():
    systemSecStatus = sm.StartService('map').GetSecurityClass(eve.session.solarsystemid2)
    crimewatchSvc = sm.GetService('crimewatchSvc')
    if crimewatchSvc.IsCriminal(session.charid):
        if systemSecStatus == const.securityClassHighSec:
            if eve.Message('UndockCriminalConfirm', {}, uiconst.YESNO) == uiconst.ID_YES:
                return True
            else:
                return False
    if systemSecStatus > const.securityClassZeroSec:
        engagements = crimewatchSvc.GetMyEngagements()
        if len(engagements):
            if eve.Message('UndockAggressionConfirm', {}, uiconst.YESNO, suppress=uiconst.ID_YES) != uiconst.ID_YES:
                return False
    return True


def IsOkToUndockWithMissingCargo():
    if settings.user.suppress.Get('suppress.CourierUndockMissingCargo', None):
        return True
    if sm.GetService('journal').CheckUndock(session.stationid2):
        return True
    return False
