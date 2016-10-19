#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\inflight\squadrons\abilitiesCont.py
import carbonui.const as uiconst
from carbonui.primitives.container import Container
from eve.client.script.ui.inflight.squadrons.abilityController import AbilityController
from eve.client.script.ui.inflight.squadrons.abilityIcon import AbilityIcon
from fighters import IterTypeAbilities

class AbilitiesCont(Container):
    default_width = 64
    default_height = 150
    default_align = uiconst.TOPLEFT

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.abilityIcons = {}

    def SetNewSquadron(self, fighterItemID, typeID):
        self.fighterID = fighterItemID
        self.fighterTypeID = typeID
        self._SetupAbilityIcons()

    def _SetupAbilityIcons(self):
        self._RemoveAbilityIcons()
        for slotID, typeAbility in IterTypeAbilities(self.fighterTypeID):
            if typeAbility is not None:
                self._AddAbilityIcon(slotID, typeAbility.abilityID)

    def _RemoveAbilityIcons(self):
        for icon in self.abilityIcons.itervalues():
            icon.Close()

        self.abilityIcons.clear()

    def _AddAbilityIcon(self, slotID, abilityID):
        abilityController = AbilityController(abilityID, self.fighterID, slotID, self.fighterTypeID)
        self.abilityIcons[slotID] = AbilityIcon(parent=self, controller=abilityController, fighterID=self.fighterID, fighterTypeID=self.fighterTypeID, align=uiconst.TOBOTTOM, top=2)

    def HideModules(self):
        self.display = False

    def ShowModules(self):
        self.display = True
