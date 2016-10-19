#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\dogma\effects\modifiereffect.py
from dogma.effects import Effect
import dogma.const as dgmconst

def IsPassiveEffect(effectInfo):
    return effectInfo.effectCategory in dgmconst.dgmPassiveEffectCategories


class ModifierEffect(Effect):
    __modifier_only__ = True

    def __init__(self, effectInfo, modifiers, side_effects = None):
        self.isPythonEffect = False
        self.__modifies_ship__ = IsPassiveEffect(effectInfo) and any((m.IsShipModifier() for m in modifiers))
        self.__modifies_structure__ = IsPassiveEffect(effectInfo) and any((m.IsStructureModifier() for m in modifiers))
        self.__modifies_character__ = IsPassiveEffect(effectInfo) and any((m.IsCharModifier() for m in modifiers))
        self.effects = modifiers
        if side_effects:
            self.effects.extend(side_effects)

    def Start(self, *args):
        map(lambda e: e.Start(*args), self.effects)

    def Stop(self, *args):
        map(lambda e: e.Stop(*args), self.effects)

    RestrictedStop = Stop
