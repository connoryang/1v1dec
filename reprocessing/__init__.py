#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\reprocessing\__init__.py
import itertools
import evetypes
import dogma.const as dgmconst
BASIC_ORES = {462,
 460,
 459,
 469,
 457,
 458}
ADVANCED_ORES = {450,
 451,
 452,
 453,
 454,
 455,
 456,
 461,
 467,
 468}
CAL_AMARR_ICE = {16262,
 17978,
 28434,
 28436,
 16265,
 17976,
 28441,
 28444}
GAL_MIN_ICE = {16264,
 17975,
 28433,
 28443,
 16263,
 17977,
 28438,
 28442}
SPECIAL_ICE = {16266,
 28439,
 16267,
 28435,
 16268,
 28437,
 16269,
 28440}
TYPES_BY_REFINING_ATTRIBUTE = {dgmconst.attributeRefiningYieldBasicOre: set(itertools.chain(*(evetypes.GetTypeIDsByGroup(groupID) for groupID in BASIC_ORES))),
 dgmconst.attributeRefiningYieldAdvancedOre: set(itertools.chain(*(evetypes.GetTypeIDsByGroup(groupID) for groupID in ADVANCED_ORES))),
 dgmconst.attributeRefiningYieldCalAmarrIce: CAL_AMARR_ICE,
 dgmconst.attributeRefiningYieldGalMinIce: GAL_MIN_ICE,
 dgmconst.attributeRefiningYieldSpecialIce: SPECIAL_ICE}

def GetRefiningYieldMultiplierAttributeIDForType(typeID):
    return REFINING_YIELD_ATTRIBUTE_BY_TYPE.get(typeID, dgmconst.attributeRefiningYieldMultiplier)
