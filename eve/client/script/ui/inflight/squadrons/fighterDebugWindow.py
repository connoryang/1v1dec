#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\inflight\squadrons\fighterDebugWindow.py
from appConst import defaultPadding
from carbonui import uicore
from carbonui.const import TOPLEFT
from carbonui.primitives.container import Container
from eve.client.script.ui.control.buttons import Button, ButtonIcon
from eve.client.script.ui.control.eveLabel import Label
from eve.client.script.ui.control.eveSinglelineEdit import SinglelineEdit
from eve.client.script.ui.control.eveWindow import Window
from fighters import ABILITY_SLOT_0, ABILITY_SLOT_1, ABILITY_SLOT_2
from spacecomponents.client.components.behavior import EnableDebugging

class FighterDebugWindow(Window):
    default_windowID = 'FighterDebugWindow'
    default_width = 250
    default_height = 360
    default_caption = 'Fighter debugger'
    default_icon = '41_13'
    currentFighterID = None

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.SetTopparentHeight(0)
        self.SetMinSize([250, 360])
        self.MakeUnResizeable()
        mainCont = Container(name='mainCont', parent=self.sr.main, pos=(defaultPadding,
         defaultPadding,
         defaultPadding,
         defaultPadding))
        Label(text='Fighter ID', parent=mainCont, pos=(10, 10, 0, 0), align=TOPLEFT)
        self.fighterIDBox = SinglelineEdit(name='fighterID', parent=mainCont, pos=(80, 10, 130, 20), align=TOPLEFT, OnChange=self.OnFighterIDBoxChange)
        self.fighterIDBox.SetText(self._GetFighterID())
        Button(parent=mainCont, name='DebugFighter', label='DBG', pos=(220, 10, 100, 0), fixedwidth=20, func=self.OnDebugFighterButton, align=TOPLEFT)
        Label(text='Target ID', parent=mainCont, pos=(10, 40, 0, 0), align=TOPLEFT)
        self.targetIDBox = SinglelineEdit(name='targetID', parent=mainCont, pos=(80, 40, 160, 20), align=TOPLEFT)
        self.targetIDBox.SetText(session.shipid)
        Button(parent=mainCont, name='OrbitTarget', label='Orbit Target', pos=(10, 70, 0, 0), fixedwidth=110, func=self.OnOrbitTargetButton)
        Button(parent=mainCont, name='OrbitMe', label='Orbit Me', pos=(130, 70, 0, 0), fixedwidth=110, func=self.OnOrbitMeButton)
        Button(parent=mainCont, name='StopMovement', label='Stop movement', pos=(10, 100, 0, 0), fixedwidth=110, func=self.OnMoveStopButton)
        Label(text='x,y,z', parent=mainCont, pos=(10, 130, 0, 0), align=TOPLEFT)
        self.gotoPosBox = SinglelineEdit(name='gotoPos', parent=mainCont, pos=(40, 130, 190, 20), align=TOPLEFT)
        ButtonIcon(name='pickXYZ', parent=mainCont, pos=(230, 130, 16, 16), align=TOPLEFT, width=16, iconSize=16, texturePath='res:/UI/Texture/Icons/38_16_150.png', hint='Pick random position near target', func=self.OnPickXYZ)
        Button(parent=mainCont, name='GotoPoint', label='Goto this point', pos=(130, 150, 0, 0), fixedwidth=110, func=self.OnGotoPointButton)
        Button(parent=mainCont, name='ToggleMoveMode', label='Toggle Movement', pos=(10, 150, 0, 0), fixedwidth=110, func=self.OnToggleMoveButton)
        Label(text='Ability 0', parent=mainCont, pos=(10, 180, 0, 0), align=TOPLEFT)
        Button(parent=mainCont, name='ActivateAbilityOnTarget', label='Activate (target)', pos=(10, 200, 0, 0), fixedwidth=80, func=self.OnActivateAbilityOnTarget, args=(ABILITY_SLOT_0,))
        Button(parent=mainCont, name='ActivateAbilityOnSelf', label='Activate (self)', pos=(95, 200, 0, 0), fixedwidth=80, func=self.OnActivateAbilityOnSelf, args=(ABILITY_SLOT_0,))
        Button(parent=mainCont, name='DeactivateAbility', label='Deactivate', pos=(180, 200, 0, 0), fixedwidth=60, func=self.OnDeactivateAbility, args=(ABILITY_SLOT_0,))
        Label(text='Ability 1', parent=mainCont, pos=(10, 230, 0, 0), align=TOPLEFT)
        Button(parent=mainCont, name='ActivateAbilityOnTarget', label='Activate (target)', pos=(10, 250, 0, 0), fixedwidth=80, func=self.OnActivateAbilityOnTarget, args=(ABILITY_SLOT_1,))
        Button(parent=mainCont, name='ActivateAbilityOnSelf', label='Activate (self)', pos=(95, 250, 0, 0), fixedwidth=80, func=self.OnActivateAbilityOnSelf, args=(ABILITY_SLOT_1,))
        Button(parent=mainCont, name='DeactivateAbility', label='Deactivate', pos=(180, 250, 0, 0), fixedwidth=60, func=self.OnDeactivateAbility, args=(ABILITY_SLOT_1,))
        Label(text='Ability 2', parent=mainCont, pos=(10, 280, 0, 0), align=TOPLEFT)
        Button(parent=mainCont, name='ActivateAbilityOnTarget', label='Activate (target)', pos=(10, 300, 0, 0), fixedwidth=80, func=self.OnActivateAbilityOnTarget, args=(ABILITY_SLOT_2,))
        Button(parent=mainCont, name='ActivateAbilityOnSelf', label='Activate (self)', pos=(95, 300, 0, 0), fixedwidth=80, func=self.OnActivateAbilityOnSelf, args=(ABILITY_SLOT_2,))
        Button(parent=mainCont, name='DeactivateAbility', label='Deactivate', pos=(180, 300, 0, 0), fixedwidth=60, func=self.OnDeactivateAbility, args=(ABILITY_SLOT_2,))

    def _GetFighterID(self):
        return self.currentFighterID

    def _GetTargetID(self):
        try:
            return int(self.targetIDBox.text.strip())
        except ValueError:
            return None

    def OnFighterIDBoxChange(self, *args):
        try:
            self.currentFighterID = int(self.fighterIDBox.text.strip())
        except ValueError:
            pass

    def OnDebugFighterButton(self, *args):
        self._OnDebugFighterButton(*args)

    def _OnDebugFighterButton(self, *args):
        fighterID = self._GetFighterID()
        if fighterID is not None:
            EnableDebugging(fighterID)

    def OnPickXYZ(self, *args):
        self._OnPickXYZ(*args)

    def _OnPickXYZ(self, *args):
        michelle = sm.GetService('michelle')
        targetID = self._GetTargetID() or session.shipid
        ball = michelle.GetBall(targetID)
        if ball:
            import random
            shipPos = geo2.VectorD(ball.x, ball.y, ball.z)
            offsetRange = ball.radius + 2000
            offset = geo2.Vector(random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1, 1))
            targetPos = geo2.Vec3AddD(shipPos, geo2.Vec3Scale(geo2.Vec3Normalize(offset), offsetRange))
            self.gotoPosBox.SetText('%.0f, %.0f, %0.f' % (targetPos[0], targetPos[1], targetPos[2]))

    def OnGotoPointButton(self, *args):
        self._OnGotoPointButton(*args)

    def _OnGotoPointButton(self, *args):
        fighterID = self._GetFighterID()
        if fighterID is not None:
            point = geo2.VectorD([ float(v.strip()) for v in self.gotoPosBox.text.strip().split(',') ])
            sm.GetService('fighters').CmdGotoPoint([fighterID], list(point))

    def OnToggleMoveButton(self, *args):
        self._OnOnToggleMoveButton(*args)

    def _OnOnToggleMoveButton(self, *args):
        selectedSquadrons = uicore.layer.shipui.fighterCont.GetSelectedSquadrons()
        selectedIDs = [ squadron.fighterItemID for squadron in selectedSquadrons ]
        fighterID = self._GetFighterID()
        if len(selectedIDs) > 0:
            uicore.layer.inflight.positionalControl.StartFighterMoveCommand(selectedIDs)
        elif fighterID is not None:
            uicore.layer.inflight.positionalControl.StartFighterMoveCommand([fighterID])

    def OnOrbitTargetButton(self, *args):
        self._OnOrbitTargetButton(*args)

    def _OnOrbitTargetButton(self, *args):
        fighterID = self._GetFighterID()
        targetID = self._GetTargetID()
        if fighterID is not None and targetID is not None:
            sm.GetService('fighters').CmdMovementOrbit([fighterID], targetID, 5000)

    def OnOrbitMeButton(self, *args):
        self._OnOrbitMeButton(*args)

    def _OnOrbitMeButton(self, *args):
        fighterID = self._GetFighterID()
        if fighterID is not None:
            sm.GetService('fighters').CmdMovementOrbit([fighterID], session.shipid, 5000)

    def OnMoveStopButton(self, *args):
        self._OnMoveStopButton(*args)

    def _OnMoveStopButton(self, *args):
        fighterID = self._GetFighterID()
        if fighterID is not None:
            sm.GetService('fighters').CmdMovementStop([fighterID])

    def OnActivateAbilityOnTarget(self, abilitySlotID):
        self._OnActivateAbilityOnTarget(abilitySlotID)

    def _OnActivateAbilityOnTarget(self, abilitySlotID):
        fighterID = self._GetFighterID()
        targetID = self._GetTargetID()
        if fighterID is not None and targetID is not None:
            sm.GetService('fighters').ActivateAbilitySlotsOnTarget([fighterID], abilitySlotID, targetID)

    def OnActivateAbilityOnSelf(self, abilitySlotID):
        self._OnActivateAbilityOnSelf(abilitySlotID)

    def _OnActivateAbilityOnSelf(self, abilitySlotID):
        fighterID = self._GetFighterID()
        if fighterID is not None:
            sm.GetService('fighters').ActivateAbilitySlotsOnSelf([fighterID], abilitySlotID)

    def OnDeactivateAbility(self, abilitySlotID):
        self._OnDeactivateAbility(abilitySlotID)

    def _OnDeactivateAbility(self, abilitySlotID):
        fighterID = self._GetFighterID()
        if fighterID is not None:
            sm.GetService('fighters').DeactivateAbilitySlots([fighterID], abilitySlotID)
