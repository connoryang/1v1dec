#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\inventorycommon\typeHelpers.py
try:
    import eve.common.script.sys.eveCfg
    fsdDustIcons = eve.common.script.sys.eveCfg.CfgFsdDustIcons
    icons = eve.common.script.sys.eveCfg.CfgIcons
    sounds = eve.common.script.sys.eveCfg.CfgSounds
    invcontrabandFactionsByType = eve.common.script.sys.eveCfg.CfgInvcontrabandFactionsByType
    shiptypes = eve.common.script.sys.eveCfg.CfgShiptypes
    _averageMarketPrice = eve.common.script.sys.eveCfg.CfgAverageMarketPrice
except ImportError:
    fsdDustIcons = []
    icons = None
    sounds = None
    invcontrabandFactionsByType = None
    shiptypes = None
    _averageMarketPrice = None

import evetypes
import const
import evegraphics.fsd.graphicIDs as fsdGraphicIDs
import logging
log = logging.getLogger(__name__)

def GetGraphic(typeID):
    try:
        return fsdGraphicIDs.GetGraphic(evetypes.GetGraphicID(typeID))
    except Exception:
        pass


def GetGraphicFile(typeID):
    return fsdGraphicIDs.GetGraphicFile(evetypes.GetGraphicID(typeID), '')


def GetAnimationStates(typeID):
    return fsdGraphicIDs.GetAnimationStates(evetypes.GetGraphicID(typeID), [])


def GetIcon(typeID):
    if typeID >= const.minDustTypeID:
        return fsdDustIcons().get(typeID, None)
    try:
        iconID = evetypes.GetIconID(typeID)
        return icons().Get(iconID)
    except Exception:
        pass


def GetIconFile(typeID):
    try:
        iconID = evetypes.GetIconID(typeID)
        return icons().Get(iconID).iconFile
    except Exception:
        return ''


def GetHoloIconPath(typeID):
    try:
        g = GetGraphic(typeID)
        return fsdGraphicIDs.GetIconFolder(g) + '/' + fsdGraphicIDs.GetSofHullName(g) + '_isis.png'
    except Exception:
        typeString = typeID if typeID is not None else 'None'
        exceptionMsg = 'Failed to find respath to the holographic icon for typeID: %s' % typeString
        log.exception(exceptionMsg)
        return


def GetSound(typeID):
    try:
        soundID = evetypes.GetSoundID(typeID)
        return sounds().Get(soundID)
    except Exception:
        pass


def GetIllegality(typeID, factionID = None):
    if factionID:
        return invcontrabandFactionsByType().get(typeID, {}).get(factionID, None)
    else:
        return invcontrabandFactionsByType().get(typeID, {})


def GetShipType(typeID):
    return shiptypes().Get(typeID)


def GetAdjustedAveragePrice(typeID):
    try:
        return _averageMarketPrice()[typeID].adjustedPrice
    except KeyError:
        return None


def GetAveragePrice(typeID):
    try:
        return _averageMarketPrice()[typeID].averagePrice
    except KeyError:
        return None
