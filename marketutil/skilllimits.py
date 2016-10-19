#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\marketutil\skilllimits.py
from collections import defaultdict
import inventorycommon.const as invconst
from eve.common.lib.appConst import rangeStation, rangeSolarSystem, rangeRegion, marketCommissionPercentage, mktTransactionTax
from eve.common.script.sys.idCheckers import IsStation
JUMPS_PER_SKILL_LEVEL = {0: rangeStation,
 1: rangeSolarSystem,
 2: 5,
 3: 10,
 4: 20,
 5: rangeRegion}

class SkillLimits(dict):

    def __init__(self, GetBaseTax, skillLevels, GetDynamicBaseTax, doSkillsApply):
        self.GetDynamicBaseTax = GetDynamicBaseTax
        self.GetBaseTax = GetBaseTax
        self.skillLevels = skillLevels
        self.doSkillsApply = doSkillsApply

    def GetBrokersFeeForLocation(self, locationID):
        baseTax = self.GetDynamicBaseTax(locationID)
        transactionTax = baseTax / 100.0
        if self.doSkillsApply:
            transactionTax -= self.skillLevels.broker * 0.1 / 100
        return transactionTax


def GetSkillLimits(GetBaseTax, GetMarketSkills, GetDynamicBaseTax, doSkillsApply):
    typeIDs = [invconst.typeRetail,
     invconst.typeTrade,
     invconst.typeWholesale,
     invconst.typeAccounting,
     invconst.typeBrokerRelations,
     invconst.typeTycoon,
     invconst.typeMarketing,
     invconst.typeProcurement,
     invconst.typeVisibility,
     invconst.typeDaytrading,
     invconst.typeMarginTrading]
    skillLevels = GetMarketSkills(typeIDs)
    limits = SkillLimits(GetBaseTax, skillLevels, GetDynamicBaseTax, doSkillsApply)
    maxOrderCount = 5 + skillLevels.trade * 4 + skillLevels.retail * 8 + skillLevels.wholeSale * 16 + skillLevels.tycoon * 32
    limits['cnt'] = maxOrderCount
    transactionTax = mktTransactionTax / 100.0
    transactionTax *= 1 - skillLevels.accounting * 0.1
    limits['acc'] = transactionTax
    limits['ask'] = JUMPS_PER_SKILL_LEVEL[skillLevels.marketing]
    limits['bid'] = JUMPS_PER_SKILL_LEVEL[skillLevels.procurement]
    limits['vis'] = JUMPS_PER_SKILL_LEVEL[skillLevels.visibility]
    limits['mod'] = JUMPS_PER_SKILL_LEVEL[skillLevels.daytrading]
    limits['esc'] = 0.75 ** skillLevels.margin
    return limits
