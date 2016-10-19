#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\environment\spaceObject\LargeCollidableObject.py
from eve.client.script.environment.spaceObject.spaceObject import SpaceObject

class LargeCollidableObject(SpaceObject):

    def GetDNA(self):
        dna = SpaceObject.GetDNA(self)
        if dna and ':class?' not in dna:
            dna += ':class?stationary'
        return dna

    def Assemble(self):
        self.SetStaticRotation()
        if getattr(self.model, 'ChainAnimationEx', None) is not None:
            self.model.ChainAnimationEx('NormalLoop', 0, 0, 1.0)
        self.SetupSharedAmbientAudio()
