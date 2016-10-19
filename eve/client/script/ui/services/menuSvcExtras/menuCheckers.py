#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\services\menuSvcExtras\menuCheckers.py
import util
import const
import inventorycommon.const as invConst

def check_bundle(func):

    def check_bundle_or_call_function(*args, **kwargs):
        bundle = args[-1]
        r = getattr(bundle, 'get', lambda x, y: None)(func.__name__, None)
        if not r:
            r = bundle[func.__name__] = func(*args, **kwargs)
        return r

    return check_bundle_or_call_function


def OfferCreateContract(invItem, knownchecks):
    if _IsActiveShip(invItem, knownchecks):
        return False
    if _IsStation(invItem, knownchecks):
        return False
    if not _IsMineOrCorps(invItem, knownchecks):
        return False
    if _IsDirectlyInPersonalHangar(invItem, knownchecks):
        return True
    if _IsCorpOwned(invItem, knownchecks) and _IsInCorpDeliveries(invItem, knownchecks):
        return True
    if _IsInDockableCorpOffice(invItem, knownchecks) and _CanTakeFromCorpDivision(_GetLocationIDOfItemInCorpOffice(invItem, knownchecks), invItem.flagID, knownchecks):
        return True
    return False


def OfferDeliverTo(invItem, knownchecks):
    if not session.structureid:
        return False
    if invItem.locationID != session.structureid:
        return False
    if _IsActiveShip(invItem, knownchecks):
        return False
    if not _IsMineOrCorps(invItem, knownchecks):
        return False
    if _IsCorpOwned(invItem, knownchecks) and _IsInCorpDeliveries(invItem, knownchecks):
        return True
    if _IsDirectlyInPersonalStructureHangar(invItem, knownchecks):
        return True
    if _IsInDockableCorpOffice(invItem, knownchecks) and _CanTakeFromCorpDivision(_GetLocationIDOfItemInCorpOffice(invItem, knownchecks), invItem.flagID, knownchecks):
        return True
    return False


def _IsStation(invItem, *args):
    return util.IsStation(invItem.itemID)


def _IsInCorpDeliveries(invItem, *args):
    return invItem.flagID == const.flagCorpMarket


def _IsActiveShip(invItem, *args):
    return invItem.itemID == util.GetActiveShip()


def _IsMine(invItem, *args):
    return invItem.ownerID == session.charid


def _IsCorpOwned(invItem, *args):
    return invItem.ownerID == session.corpid


def _IsMineOrCorps(invItem, *args):
    return _IsMine(invItem, *args) or _IsCorpOwned(invItem, *args)


def _IsDirectlyInPersonalNPCStationHangar(invItem, *args):
    return util.IsStation(invItem.locationID) and invItem.flagID == const.flagHangar


def _IsDirectlyInPersonalStructureHangar(invItem, *args):
    if invItem.flagID == const.flagHangar and _IsStructure(invItem, *args):
        return True
    return False


def _IsDirectlyInPersonalHangar(invItem, *args):
    return _IsDirectlyInPersonalNPCStationHangar(invItem, *args) or _IsDirectlyInPersonalStructureHangar(invItem, *args)


def _IsInDockableCorpOffice(invItem, *args):
    if invItem.ownerID != session.corpid:
        return False
    if util.IsNPC(invItem.ownerID):
        return False
    return _GetLocationIDOfItemInCorpOffice(invItem, *args) and invItem.flagID in invConst.flagStructureCorpOfficeFlags + invConst.flagCorpSAGs


def _CanTakeFromCorpDivision(stationID, flagID, *args):
    if flagID not in invConst.flagStructureCorpOfficeFlags + (invConst.flagHangar,):
        return False
    if stationID is None:
        return False
    roleRequired = const.corpHangarTakeRolesByFlag[flagID]
    if stationID == session.hqID:
        rolesToUse = session.rolesAtHQ
    elif stationID == session.baseID:
        rolesToUse = session.rolesAtBase
    else:
        rolesToUse = session.rolesAtOther
    if roleRequired & rolesToUse:
        return True
    return False


@check_bundle
def _IsStructure(invItem, *args):
    return sm.GetService('structureDirectory').GetStructureInfo(invItem.locationID) is not None


@check_bundle
def _GetLocationIDOfItemInCorpOffice(invItem, *args):
    for office in sm.StartService('corp').GetMyCorporationsOffices():
        if office.officeID and office.officeID == invItem.locationID:
            return office.locationID
        if office.locationID == office.officeFolderID and invItem.locationID == office.locationID:
            return invItem.locationID
