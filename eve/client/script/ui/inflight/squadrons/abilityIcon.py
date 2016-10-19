#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\inflight\squadrons\abilityIcon.py
from appConst import shipSafetyLevelNone
from carbon.common.lib.const import MSEC
from carbonui.primitives.container import Container
import carbonui.const as uiconst
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from eve.client.script.ui.crimewatch import crimewatchConst
from eve.client.script.ui.crimewatch.crimewatchConst import Colors as CrimeWatchColors
from eve.client.script.ui.control.eveIcon import Icon
from eve.client.script.ui.control.eveLabel import EveLabelSmall, Label
from eve.client.script.ui.inflight.shipModuleButton.ramps import ShipModuleButtonRamps, ShipModuleReactivationTimer
from eve.client.script.ui.inflight.shipModuleButton.shipmodulebutton import GLOWCOLOR, BUSYCOLOR
from eve.client.script.ui.inflight.squadrons.shipFighterState import GetShipFighterState
from eve.client.script.ui.inflight.squadrons.squadronAbilityTooltip import SquadronTooltipModuleWrapper
from fighters import GetChargeCountForTypeAndSlot, GetAbilityIDForSlot
from fighters.abilityAttributes import GetDogmaEffectIDForAbilityID
from localization import GetByMessageID, GetByLabel
import trinity
import uthread
import blue

class AbilityIcon(Container):
    default_width = 48
    default_height = 48
    default_align = uiconst.TOPLEFT
    default_state = uiconst.UI_NORMAL
    tooltipPanelClassInfo = SquadronTooltipModuleWrapper()

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.activeCurve = None
        self.activationPendingCurve = None
        self.deactivationCurve = None
        self.ramp_active = False
        self.buttonDisabled = False
        self.shipFighterState = GetShipFighterState()
        self.crimewatchSvc = sm.GetService('crimewatchSvc')
        self.innerCont = Container(name='innerCont', parent=self, align=uiconst.TOBOTTOM, height=self.height)
        self.stateLabel = EveLabelSmall(parent=self.innerCont, align=uiconst.CENTER)
        self.controller = attributes.controller
        self.slotID = self.controller.slotID
        self.fighterID = attributes.fighterID
        self.fighterTypeID = attributes.fighterTypeID
        ability = self.GetAbilityInfo()
        self.abilityNameID = ability.displayNameID
        iconID = ability.iconID
        self.abilityIcon = Icon(parent=self.innerCont, align=uiconst.CENTER, width=32, height=32, icon=iconID, state=uiconst.UI_DISABLED)
        self.hilite = Sprite(parent=self.innerCont, name='hilite', width=44, height=44, align=uiconst.CENTER, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/ShipUI/slotHilite.png', blendMode=trinity.TR2_SBM_ADDX2)
        self.hilite.display = False
        bgSprite = Sprite(parent=self.innerCont, align=uiconst.CENTER, width=64, height=64, texturePath='res:/UI/Texture/classes/ShipUI/Fighters/slotFighterAbility.png', state=uiconst.UI_DISABLED)
        self.abilityIcon.SetSize(32, 32)
        self.DrawQtyCont()
        self.DrawTimer()
        self.DrawCoolDownTimer()
        self.DrawSafetyGlow()
        self.targetMode = ability.targetMode
        abilityID = GetAbilityIDForSlot(self.fighterTypeID, self.slotID)
        effectID = GetDogmaEffectIDForAbilityID(abilityID)
        self.abilityEffect = cfg.dgmeffects.Get(effectID)
        self.OnAbilityStatusUpdated(self.fighterID, self.slotID)
        self.shipFighterState.signalOnAbilityActivationStatusUpdate.connect(self.OnAbilityStatusUpdated)

    def GetSafetyWarning(self):
        requiredSafetyLevel = self.GetRequiredSafetyLevel()
        if self.crimewatchSvc.CheckUnsafe(requiredSafetyLevel):
            return requiredSafetyLevel
        else:
            return None

    def GetRequiredSafetyLevel(self):
        requiredSafetyLevel = self.crimewatchSvc.GetRequiredSafetyLevelForEffect(self.abilityEffect)
        return requiredSafetyLevel

    def OnMouseEnter(self, *args):
        self.hilite.display = True
        requiredSafetyLevel = self.GetSafetyWarning()
        if requiredSafetyLevel is not None:
            if requiredSafetyLevel == const.shipSafetyLevelNone:
                color = crimewatchConst.Colors.Criminal
            else:
                color = crimewatchConst.Colors.Suspect
            self.safetyGlow.color.SetRGBA(*color.GetRGBA())
            self.safetyGlow.display = True

    def OnMouseExit(self, *args):
        self.hilite.display = False
        self.safetyGlow.display = False

    def DrawSafetyGlow(self):
        self.safetyGlow = Sprite(parent=self.innerCont, name='safetyGlow', width=64, height=64, padding=2, align=uiconst.CENTER, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/ShipUI/slotGlow.png', color=crimewatchConst.Colors.Yellow.GetRGBA())
        self.safetyGlow.display = False

    def DrawTimer(self):
        self.glow = Sprite(parent=self.innerCont, name='glow', width=64, height=64, padding=2, align=uiconst.CENTER, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/ShipUI/slotGlow.png', color=GLOWCOLOR)
        self.glow.display = False
        self.busy = Sprite(parent=self.innerCont, name='busy', width=64, height=64, padding=2, align=uiconst.CENTER, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/ShipUI/slotGlow.png', color=BUSYCOLOR)
        self.busy.display = False
        self.ramps = ShipModuleButtonRamps(parent=self.innerCont, idx=0, top=-8)
        self.ramps.display = False

    def DrawCoolDownTimer(self):
        self.coolDownRamps = ShipModuleReactivationTimer(parent=self.innerCont, name='coolDown', idx=-1)
        self.coolDownRamps.display = False

    def DrawQtyCont(self):
        self.quantityParent = Container(parent=self.innerCont, name='quantityParent', pos=(16, 6, 24, 10), align=uiconst.BOTTOMRIGHT, state=uiconst.UI_DISABLED, idx=0)
        self.chargeCountLabel = Label(text='', parent=self.quantityParent, fontsize=9, letterspace=1, left=3, width=30, state=uiconst.UI_DISABLED)
        underlay = Sprite(parent=self.quantityParent, align=uiconst.TOALL, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/ShipUI/slotQuantityUnderlay.png', color=(0, 0, 0, 1))

    def GetAbilityInfo(self):
        ability = self.controller.GetAbilityInfo()
        return ability

    def OnAbilityStatusUpdated(self, fighterID, slotID):
        if fighterID == self.fighterID and slotID == self.slotID:
            abilityActivationStatus = self.shipFighterState.GetAbilityActivationStatus(self.fighterID, self.slotID)
            if abilityActivationStatus:
                if abilityActivationStatus.isPending:
                    self._StartActivationPendingAnimation()
                else:
                    self._StopActivationPendingAnimation()
                if abilityActivationStatus.isDeactivating:
                    self._StartDeactivationAnimation()
                else:
                    self._StopDeactivationAnimation()
                if not abilityActivationStatus.isPending and not abilityActivationStatus.isDeactivating:
                    self._StartActiveAnimation()
                    self.buttonDisabled = False
                else:
                    self._StopActiveAnimation()
                    self.buttonDisabled = True
                if abilityActivationStatus.startTime and abilityActivationStatus.durationMs:
                    self._StartCycleAnimation(abilityActivationStatus.startTime, abilityActivationStatus.durationMs)
                else:
                    self._StopCycleAnimation()
            else:
                self._StopActivationPendingAnimation()
                self._StopDeactivationAnimation()
                self._StopActiveAnimation()
                self._StopCycleAnimation()
                cooldown = self.shipFighterState.GetAbilityCooldown(self.fighterID, self.slotID)
                if cooldown is not None:
                    self.buttonDisabled = True
                    uthread.new(self._StartCoolDownAnimation, cooldown)
                else:
                    self.buttonDisabled = False
            self._UpdateChargeCountLabel()

    def _UpdateChargeCountLabel(self):
        maxChargeCount = GetChargeCountForTypeAndSlot(self.fighterTypeID, self.slotID)
        if maxChargeCount is not None:
            currentChargeCount = self.shipFighterState.GetAbilityChargeCount(self.fighterID, self.slotID)
            self.quantityParent.Show()
            self.chargeCountLabel.SetText(currentChargeCount)
        else:
            self.quantityParent.Hide()

    def _StartCycleAnimation(self, startTime, durationMs):
        if self.ramp_active:
            return
        uthread.new(self._StartCycleAnimationThread, startTime, durationMs)

    def _StartCycleAnimationThread(self, startTime, durationMs):
        duration = durationMs * MSEC
        self.ramp_active = True
        self.ramps.display = True
        self.coolDownRamps.display = False
        while self.ramp_active:
            now = blue.os.GetSimTime()
            portionDone = (now - startTime) / duration
            if portionDone > 1:
                iterations = int(portionDone)
                startTime += long(duration * iterations)
                portionDone -= iterations
            self.ramps.SetRampValues(portionDone)
            blue.pyos.synchro.Yield()

    def _StopCycleAnimation(self):
        self.ramp_active = False
        self.ramps.display = False

    def _StartCoolDownAnimation(self, cooldown):
        self.coolDownRamps.display = True
        startTime, endTime = cooldown
        coolDownTime = int(endTime - startTime)
        self.coolDownRamps.AnimateTimer(startTime, coolDownTime)
        if endTime <= blue.os.GetSimTime():
            self.coolDownRamps.display = False
            self.buttonDisabled = False

    def _StartActiveAnimation(self):
        self.glow.display = True
        self.activeCurve = animations.FadeTo(self.glow, loops=uiconst.ANIM_REPEAT, curveType=uiconst.ANIM_WAVE)
        animations.SyncPlayback(self.activeCurve)

    def _StopActiveAnimation(self):
        self.glow.display = False
        if self.activeCurve:
            self.activeCurve.Stop()
            self.activeCurve = None

    def _StartActivationPendingAnimation(self):
        self.activationPendingCurve = animations.FadeTo(self.abilityIcon, loops=uiconst.ANIM_REPEAT, curveType=uiconst.ANIM_WAVE)
        animations.SyncPlayback(self.activationPendingCurve)

    def _StopActivationPendingAnimation(self):
        if self.activationPendingCurve:
            self.activationPendingCurve.Stop()
            self.activationPendingCurve = None
        animations.FadeIn(self.abilityIcon)

    def _StartDeactivationAnimation(self):
        self.busy.display = True
        self.deactivationCurve = animations.FadeTo(self.busy, loops=uiconst.ANIM_REPEAT, curveType=uiconst.ANIM_WAVE)
        animations.SyncPlayback(self.deactivationCurve)

    def _StopDeactivationAnimation(self):
        self.busy.display = False
        if self.deactivationCurve:
            self.deactivationCurve.Stop()
            self.deactivationCurve = None

    def OnClick(self, *args):
        if self.buttonDisabled:
            return
        self.controller.OnAbilityClick(self.targetMode)

    def Close(self):
        self._StopActiveAnimation()
        self._StopActivationPendingAnimation()
        self._StopDeactivationAnimation()
        self.shipFighterState.signalOnAbilityActivationStatusUpdate.disconnect(self.OnAbilityStatusUpdated)
        super(AbilityIcon, self).Close()

    def OnMouseDown(self, *args):
        if self.buttonDisabled:
            return
        self.innerCont.top = 2

    def OnMouseUp(self, *args):
        if self.buttonDisabled:
            return
        self.innerCont.top = 0
