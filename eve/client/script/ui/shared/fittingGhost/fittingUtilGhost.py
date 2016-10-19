#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\fittingGhost\fittingUtilGhost.py
import evetypes
import inventorycommon.const as invConst
import dogma.const as dogmaConst
import blue
from utillib import KeyVal
FONTCOLOR_DEFAULT = '<color=0xc0ffffff>'
FONTCOLOR_RED = '<color=0xffff0000>'
FONTCOLOR_GREEN = '<color=0xff00ff00>'
END_COLOR = '</color>'
PASSIVESHIELDRECHARGE = 0
SHIELDBOOSTRATEACTIVE = 1
ARMORREPAIRRATEACTIVE = 2
HULLREPAIRRATEACTIVE = 3

def GetColoredText(isBetter, text):
    if isBetter is None:
        returnString = FONTCOLOR_DEFAULT
    elif isBetter:
        returnString = FONTCOLOR_GREEN
    else:
        returnString = FONTCOLOR_RED
    returnString += text
    returnString += END_COLOR
    return returnString


def GetTypeAttributesByID(typeID):
    if not typeID:
        return {}
    return {attribute.attributeID:attribute.value for attribute in cfg.dgmtypeattribs.get(typeID, [])}


def IsEffectActivatable(isDefault, effectInfo):
    return isDefault and effectInfo.effectCategory in (const.dgmEffActivation, const.dgmEffTarget) and effectInfo.effectName != 'online'


def GetDefaultAndOverheatEffectForType(typeID):
    possibleEffects = cfg.dgmtypeeffects.get(typeID, [])
    typeEffectInfo = KeyVal(defaultEffect=None, overloadEffect=None, isActivatable=False)
    for eachEffect in possibleEffects:
        effect = cfg.dgmeffects.Get(eachEffect.effectID)
        if eachEffect.isDefault:
            typeEffectInfo.isActivatable = IsEffectActivatable(eachEffect.isDefault, effect)
            typeEffectInfo.defaultEffect = effect
        if effect.effectCategory == dogmaConst.dgmEffOverload:
            typeEffectInfo.overloadEffect = effect

    return typeEffectInfo


def GetScaleFactor():
    dw = uicore.desktop.width
    minWidth = 1400
    return min(1.0, max(0.75, dw / float(minWidth)))


def GetBaseShapeSize():
    return int(640 * GetScaleFactor())


def IsCharge(typeID):
    return evetypes.GetCategoryID(typeID) in (const.categoryCharge, const.groupFrequencyCrystal)


def GetPowerType(flagID):
    if flagID in invConst.loSlotFlags:
        return dogmaConst.effectLoPower
    if flagID in invConst.medSlotFlags:
        return dogmaConst.effectMedPower
    if flagID in invConst.hiSlotFlags:
        return dogmaConst.effectHiPower
    if flagID in invConst.subSystemSlotFlags:
        return dogmaConst.effectSubSystem
    if flagID in invConst.rigSlotFlags:
        return dogmaConst.effectRigSlot
    if flagID in invConst.serviceSlotFlags:
        return dogmaConst.effectServiceSlot


def CheckChargeForLauncher(dogmaStaticMgr, itemTypeID, chargeTypeID):
    if chargeTypeID is None:
        return False
    chargeGroupID = evetypes.GetGroupID(chargeTypeID)
    for attributeID in dogmaStaticMgr.GetChargeGroupAttributes():
        desiredChargeGroupID = dogmaStaticMgr.GetTypeAttribute2(itemTypeID, attributeID)
        if desiredChargeGroupID == 0:
            continue
        if int(desiredChargeGroupID) == chargeGroupID:
            break
    else:
        return False

    wantChargeSize = dogmaStaticMgr.GetTypeAttribute2(itemTypeID, dogmaConst.attributeChargeSize)
    if wantChargeSize > 0:
        gotChargeSize = dogmaStaticMgr.GetTypeAttribute2(chargeTypeID, dogmaConst.attributeChargeSize)
        if gotChargeSize != wantChargeSize:
            return False
    return True


allPowerEffects = (dogmaConst.effectHiPower,
 dogmaConst.effectMedPower,
 dogmaConst.effectLoPower,
 dogmaConst.effectSubSystem,
 dogmaConst.effectRigSlot,
 dogmaConst.effectServiceSlot)
AVAILABLEFLAGS = {dogmaConst.effectLoPower: (invConst.flagLoSlot0, 8),
 dogmaConst.effectMedPower: (invConst.flagMedSlot0, 8),
 dogmaConst.effectHiPower: (invConst.flagHiSlot0, 8),
 dogmaConst.effectRigSlot: (invConst.flagRigSlot0, 3),
 dogmaConst.effectServiceSlot: (invConst.flagServiceSlot0, 8)}

def GetFlagIdToUse(typeID, flag, flagsInUse):
    if flag != const.flagAutoFit:
        return flag
    return GetNextAvailableFlag(typeID, flagsInUse)


def GetNextAvailableFlag(typeID, flagsInUse):
    effectID = None
    for effect in cfg.dgmtypeeffects.get(typeID, []):
        if effect.effectID in allPowerEffects:
            effectID = effect.effectID

    start, num = AVAILABLEFLAGS.get(effectID)
    for x in xrange(start, start + num):
        if x not in flagsInUse:
            return x
