#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\control\damageRing.py
import trinity
from carbonui.primitives import container
from carbonui.primitives import transform
from carbonui.primitives import sprite
from carbonui import const as uiconst
from carbonui.uicore import uicorebase as uicore

class DamageRing(container.Container):
    default_width = 70
    default_height = 70
    default_align = uiconst.CENTER
    default_state = uiconst.UI_DISABLED

    def ApplyAttributes(self, attributes):
        container.Container.ApplyAttributes(self, attributes)
        self.content = transform.Transform(parent=self, name='content', align=uiconst.CENTER, pos=(0, 0, 70, 70), state=uiconst.UI_NORMAL)
        self.background = sprite.Sprite(name='icon', parent=self.content, pos=(0, 0, 70, 70), texturePath='res:/UI/Texture/classes/DamageRing/background.png', state=uiconst.UI_DISABLED, align=uiconst.CENTER)
        self.shield = DamageSegment(name='shield', parent=self.content, texturePath='res:/UI/Texture/classes/DamageRing/shield.png', offset=-0.98)
        self.armor = DamageSegment(name='armor', parent=self.content, texturePath='res:/UI/Texture/classes/DamageRing/armor.png', offset=-5.17)
        self.hull = DamageSegment(name='hull', parent=self.content, texturePath='res:/UI/Texture/classes/DamageRing/hull.png', offset=-3.1)

    def SetDamage(self, damage):
        self.shield.value, self.armor.value, self.hull.value = damage


class DamageSegment(sprite.Sprite):
    default_align = uiconst.CENTER
    default_state = uiconst.UI_DISABLED
    default_width = 70
    default_height = 70
    default_pos = (0, 0, 70, 70)
    default_blendMode = 1
    default_spriteEffect = trinity.TR2_SFX_MODULATE
    default_textureSecondaryPath = 'res:/UI/Texture/classes/DamageRing/color.png'

    def ApplyAttributes(self, attributes):
        sprite.Sprite.ApplyAttributes(self, attributes)
        self.offset = attributes.get('offset', 0)
        self.range = attributes.get('range', 1.98)
        self.textureSecondary.useTransform = True
        self.textureSecondary.rotation = self.rotation

    def GetValue(self):
        return 1.0 - (self.offset - self.textureSecondary.rotation) / self.range

    def SetValue(self, value):
        value = min(max(value, 0.0), 1.0)
        start = self.textureSecondary.rotation
        end = self.offset + (1 - value) * self.range
        uicore.animations.MorphScalar(self.textureSecondary, 'rotation', start, end, duration=0.5)

    value = property(GetValue, SetValue)
