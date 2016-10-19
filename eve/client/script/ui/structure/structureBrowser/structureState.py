#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\structure\structureBrowser\structureState.py
from carbonui.primitives.container import Container
import carbonui.const as uiconst
from carbonui.primitives.sprite import Sprite
from localization import GetByLabel
import structures
SHIELD_TEXTURE_PATH = 'res:/UI/Texture/classes/StructureBrowser/shield.png'
ARMOR_TEXTURE_PATH = 'res:/UI/Texture/classes/StructureBrowser/armor.png'
HULL_TEXTURE_PATH = 'res:/UI/Texture/classes/StructureBrowser/hull.png'
UNDER_ATTACK_TEXTURE_PATH = 'res:/UI/Texture/classes/StructureBrowser/attackState.png'
NO_ATTACK_TEXTURE_PATH = 'res:/UI/Texture/classes/StructureBrowser/notAttackState.png'
GREY = (125 / 255.0, 125 / 255.0, 125 / 255.0)
YELLOW = (251 / 255.0, 176 / 255.0, 64 / 255.0)
RED = (239 / 255.0, 65 / 255.0, 54 / 255.0)
BLUE = (153 / 255.0, 211 / 255.0, 255 / 255.0)
FULL_OPACITY = 1.0
LOW_OPACITY = 0.25
SECURE_STATES = [structures.STATE_ONLINE, structures.STATE_SHIELD_REINFORCE, structures.STATE_ARMOR_REINFORCE]
VULNERABLE_STATES = [structures.STATE_SHIELD_VULNERABLE, structures.STATE_ARMOR_VULNERABLE, structures.STATE_HULL_VULNERABLE]
hintDict = {(structures.STATE_ONLINE, 0): 'UI/StructureBrowser/StateOnline',
 (structures.STATE_SHIELD_REINFORCE, 0): 'UI/StructureBrowser/StateShieldReinforced',
 (structures.STATE_ARMOR_REINFORCE, 0): 'UI/StructureBrowser/StateArmorReinforced',
 (structures.STATE_SHIELD_VULNERABLE, 0): 'UI/StructureBrowser/StateShieldVulnerable',
 (structures.STATE_ARMOR_VULNERABLE, 0): 'UI/StructureBrowser/StateArmorVulnerable',
 (structures.STATE_HULL_VULNERABLE, 0): 'UI/StructureBrowser/StateHullVulnerable',
 (structures.STATE_SHIELD_VULNERABLE, 1): 'UI/StructureBrowser/StateShieldVulnerableAttack',
 (structures.STATE_ARMOR_VULNERABLE, 1): 'UI/StructureBrowser/StateArmorVulnerableAttack',
 (structures.STATE_HULL_VULNERABLE, 1): 'UI/StructureBrowser/StateHullVulnerableAttack'}

class StructureStateIcon(Container):
    default_width = 32
    default_height = 32
    default_align = uiconst.CENTER
    default_state = uiconst.UI_NORMAL
    default_name = 'StructureStateIcon'

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        structureState = attributes.get('structureState', None)
        underAttack = attributes.get('underAttack', False)
        self.shield = Sprite(name='shield', parent=self, align=uiconst.TOALL, texturePath=SHIELD_TEXTURE_PATH, state=uiconst.UI_DISABLED, opacity=0)
        self.armor = Sprite(name='armor', parent=self, align=uiconst.TOALL, texturePath=ARMOR_TEXTURE_PATH, state=uiconst.UI_DISABLED, opacity=0)
        self.hull = Sprite(name='hull', parent=self, align=uiconst.TOALL, texturePath=HULL_TEXTURE_PATH, state=uiconst.UI_DISABLED, opacity=0)
        self.attackSprite = Sprite(parent=self, align=uiconst.TOALL, texturePath='', state=uiconst.UI_DISABLED)
        if structureState is not None:
            self.SetStructureState(structureState, underAttack=underAttack)

    def SetStructureState(self, structureState, underAttack = False):
        if structureState not in SECURE_STATES + VULNERABLE_STATES:
            self.display = False
            return
        self.display = True
        opacity, stateColor = self._GetStateColorAndOpacity(structureState, underAttack)
        self._SetAttackSprite(underAttack, stateColor, opacity)
        self.SetHintForIcon(structureState, underAttack)
        if structureState in (structures.STATE_ONLINE, structures.STATE_SHIELD_VULNERABLE):
            self._SetColorAndOpacity(self.shield, stateColor, opacity)
            self._SetColorAndOpacity(self.armor, stateColor, LOW_OPACITY)
            self._SetColorAndOpacity(self.hull, stateColor, LOW_OPACITY)
        elif structureState in (structures.STATE_SHIELD_REINFORCE, structures.STATE_ARMOR_VULNERABLE):
            self._SetColorAndOpacity(self.shield, GREY, LOW_OPACITY)
            self._SetColorAndOpacity(self.armor, stateColor, opacity)
            self._SetColorAndOpacity(self.hull, stateColor, LOW_OPACITY)
        elif structureState in (structures.STATE_ARMOR_REINFORCE, structures.STATE_HULL_VULNERABLE):
            self._SetColorAndOpacity(self.shield, GREY, LOW_OPACITY)
            self._SetColorAndOpacity(self.armor, GREY, LOW_OPACITY)
            self._SetColorAndOpacity(self.hull, stateColor, opacity)
        if structureState == structures.STATE_ONLINE:
            self.opacity = 0.25
        else:
            self.opacity = 1.0

    def _GetStateColorAndOpacity(self, state, underAttack):
        accentOpacity = FULL_OPACITY
        if state in SECURE_STATES:
            stateColor = BLUE
            accentOpacity = LOW_OPACITY
        elif underAttack:
            stateColor = RED
        else:
            stateColor = YELLOW
        return (accentOpacity, stateColor)

    def _SetColorAndOpacity(self, uiObject, color, opacity):
        newColor = color + (opacity,)
        uiObject.SetRGBA(*newColor)

    def _SetAttackSprite(self, isUnderAttack, stateColor, opacity):
        if isUnderAttack:
            texturePath = UNDER_ATTACK_TEXTURE_PATH
        else:
            texturePath = NO_ATTACK_TEXTURE_PATH
        self.attackSprite.SetTexturePath(texturePath)
        newColor = stateColor + (opacity,)
        self.attackSprite.SetRGBA(*newColor)

    def SetHintForIcon(self, structureState, isUnderAttack):
        hintPath = hintDict.get((structureState, isUnderAttack), None)
        if hintPath:
            self.hint = GetByLabel(hintPath)
        else:
            self.hint = ''
