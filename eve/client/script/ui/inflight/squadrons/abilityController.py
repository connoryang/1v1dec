#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\inflight\squadrons\abilityController.py
from eve.client.script.ui.inflight.squadrons.shipFighterState import GetShipFighterState
import fighters

class AbilityController(object):

    def __init__(self, abilityID, fighterID, slotID, fighterTypeID):
        self.abilityID = abilityID
        self.fighterID = fighterID
        self.slotID = slotID
        self.fighterTypeID = fighterTypeID
        self.shipFighterState = GetShipFighterState()

    def GetAbilityInfo(self):
        return fighters.AbilityStorage()[self.abilityID]

    def OnAbilityClick(self, targetMode):
        if self.shipFighterState.IsAbilityActive(self.fighterID, self.slotID):
            self.DeactivateAbility()
        else:
            self.ActivateAbility(targetMode)

    def ActivateAbility(self, targetMode):
        if self.fighterID is None:
            raise RuntimeError('Attempt to activate ability on null fighter')
        if targetMode == fighters.TARGET_MODE_UNTARGETED:
            self._OnActivateAbilityOnSelf()
        elif targetMode == fighters.TARGET_MODE_ITEMTARGETED:
            targetID = sm.GetService('target').GetActiveTargetID()
            self._OnActivateAbilityOnTarget(targetID)
        elif targetMode == fighters.TARGET_MODE_POINTTARGETED:
            eveCommands = sm.GetService('cmd')
            eveCommands.CmdAimFighterAbility(self.fighterID, self.slotID)
        else:
            raise ValueError('ActivateAbility got unexpected targetmode')

    def DeactivateAbility(self):
        self._OnDeactivateAbility()

    def _OnActivateAbilityOnTarget(self, targetID):
        sm.GetService('fighters').ActivateAbilitySlotsOnTarget([self.fighterID], self.slotID, targetID)

    def _OnActivateAbilityOnSelf(self):
        sm.GetService('fighters').ActivateAbilitySlotsOnSelf([self.fighterID], self.slotID)

    def _OnDeactivateAbility(self):
        sm.GetService('fighters').DeactivateAbilitySlots([self.fighterID], self.slotID)
