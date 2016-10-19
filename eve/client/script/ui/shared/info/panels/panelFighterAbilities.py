#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\info\panels\panelFighterAbilities.py
from appConst import defaultPadding
from carbonui.primitives.container import Container
from dogma import units
from dogma.attributes.format import FormatValue
from dogma.const import unitMilliseconds
from eve.client.script.ui.control.eveScroll import Scroll
from eve.client.script.ui.control import entries as listentry
from fighters import IterTypeAbilities
import fighters
from fighters.abilityAttributes import GetDogmaAttributeIDsForAbilityID, GetAbilityRangeAndFalloffAttributeIDs, GetAbilityDurationAttributeID
from localization import GetByLabel, GetByMessageID

class PanelFighterAbilities(Container):

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.typeID = attributes.typeID
        self.infoSvc = sm.GetService('info')
        self.dogmaStaticMgr = sm.GetService('clientDogmaStaticSvc')

    def Load(self):
        self.Flush()
        self.scroll = Scroll(name='abilityScroll', parent=self, padding=defaultPadding)
        contentList = self._GetContentList()
        self.scroll.Load(contentList=contentList)

    def _GetContentList(self):
        contentList = []
        for slotID, typeAbility in IterTypeAbilities(self.typeID):
            if typeAbility is not None:
                abilityID = typeAbility.abilityID
                ability = fighters.AbilityStorage()[abilityID]
                self._AddAbilityHeader(contentList, ability)
                self._AddRestrictionEntries(contentList, ability)
                self._AddRangeEntries(contentList, abilityID)
                self._AddDurationEntry(contentList, abilityID)
                self._AddCooldownEntry(contentList, typeAbility)
                self._AddChargeCountEntry(contentList, typeAbility)
                self._AddAttributeEntries(contentList, abilityID)

        return contentList

    def _AddAbilityHeader(self, contentList, ability):
        headerEntry = listentry.Get('Header', {'label': GetByMessageID(ability.displayNameID)})
        contentList.append(headerEntry)

    def _AddRestrictionEntries(self, contentList, ability):
        if ability.disallowInHighSec:
            disallowInHighSecLabel = {'label': GetByLabel('UI/Fighters/AbilityDisallowedInHighSec'),
             'text': '',
             'iconID': '77_12'}
            contentList.append(listentry.Get('LabelTextSides', disallowInHighSecLabel))
        if ability.disallowInLowSec:
            disallowInHighLowLabel = {'label': GetByLabel('UI/Fighters/AbilityDisallowedInLowSec'),
             'text': '',
             'iconID': '77_12'}
            contentList.append(listentry.Get('LabelTextSides', disallowInHighLowLabel))

    def _AddRangeEntries(self, contentList, abilityID):
        rangeAttributeID, falloffAttributeID = GetAbilityRangeAndFalloffAttributeIDs(self.dogmaStaticMgr, abilityID)
        contentList.extend(self.infoSvc.GetAttributeScrollListForType(self.typeID, attrList=[rangeAttributeID, falloffAttributeID]))

    def _AddDurationEntry(self, contentList, abilityID):
        durationAttributeID = GetAbilityDurationAttributeID(self.dogmaStaticMgr, abilityID)
        contentList.extend(self.infoSvc.GetAttributeScrollListForType(self.typeID, attrList=[durationAttributeID]))

    def _AddCooldownEntry(self, contentList, typeAbility):
        if typeAbility.cooldownSeconds:
            cooldownData = {'label': GetByLabel('UI/Fighters/AbilityCooldown'),
             'text': FmtFSDTimeAttribute(typeAbility.cooldownSeconds),
             'iconID': '22_16'}
            contentList.append(listentry.Get('LabelTextSides', cooldownData))

    def _AddChargeCountEntry(self, contentList, typeAbility):
        if typeAbility.charges is not None:
            chargeCountData = {'label': GetByLabel('UI/Fighters/AbilityChargeCount'),
             'text': typeAbility.charges.chargeCount,
             'iconID': '22_21'}
            contentList.append(listentry.Get('LabelTextSides', chargeCountData))
            rearmTimeData = {'label': GetByLabel('UI/Fighters/RearmTimePerCharge'),
             'text': FmtFSDTimeAttribute(typeAbility.charges.rearmTimeSeconds),
             'iconID': '22_16'}
            contentList.append(listentry.Get('LabelTextSides', rearmTimeData))

    def _AddAttributeEntries(self, contentList, abilityID):
        abilityAttributeIDs = GetDogmaAttributeIDsForAbilityID(abilityID)
        if abilityAttributeIDs:
            contentList.extend(self.infoSvc.GetAttributeScrollListForType(self.typeID, attrList=abilityAttributeIDs))


def FmtFSDTimeAttribute(valueSeconds):
    numberText = FormatValue(valueSeconds * 1000, unitMilliseconds)
    return GetByLabel('UI/InfoWindow/ValueAndUnit', value=numberText, unit=units.GetDisplayName(unitMilliseconds))
