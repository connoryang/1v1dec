#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\reprocessing\ui\efficiencyCalculator.py
from reprocessing.ui.util import GetSkillFromTypeID
from dogma.const import attributeRefiningYieldMutator
from inventorycommon.const import categoryAsteroid
import evetypes

def CalculateTheoreticalEfficiency(typeIDs, efficiency):
    getTypeAttribute = sm.GetService('clientDogmaStaticSvc').GetTypeAttribute
    getSkillLevel = sm.GetService('skills').MySkillLevel
    bonuses = []
    for typeID in typeIDs:
        skillBonuses = GetSkillFromTypeID(typeID, getTypeAttribute, getSkillLevel)
        totalSkillBonus = 1.0
        for _, bonus in skillBonuses:
            totalSkillBonus = totalSkillBonus * (1 + bonus / 100)

        totalImplantBonus = GetImplantBonus(typeID, getTypeAttribute)
        bonuses.append(100 * (totalSkillBonus * totalImplantBonus - 1))

    avgBonus = sum(bonuses) / len(typeIDs)
    return min(1.0, efficiency * (100 + avgBonus) / 100)


def GetImplantBonus(typeID, getTypeAttribute):
    totalImplantBonus = 1.0
    categoryID = evetypes.GetCategoryID(typeID)
    if categoryID == categoryAsteroid:
        implants = sm.GetService('godma').GetItem(session.charid).implants
        for implant in implants:
            implantBonus = getTypeAttribute(implant.typeID, attributeRefiningYieldMutator)
            if implantBonus > 0.0:
                totalImplantBonus = totalImplantBonus * (1 + implantBonus / 100)

    return totalImplantBonus
