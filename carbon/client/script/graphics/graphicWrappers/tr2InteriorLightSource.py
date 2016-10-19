#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\client\script\graphics\graphicWrappers\tr2InteriorLightSource.py
import util
import weakref

class Tr2InteriorLightSource(util.BlueClassNotifyWrap('trinity.Tr2InteriorLightSource')):
    __guid__ = 'graphicWrappers.Tr2InteriorLightSource'
    _alwaysEditableMembers = ['renderDebugInfo', 'renderDebugType']

    @staticmethod
    def Wrap(triObject, resPath):
        Tr2InteriorLightSource(triObject)
        triObject.AddNotify('position', triObject._TransformChange)
        triObject.AddNotify('radius', triObject._TransformChange)
        triObject.AddNotify('color', triObject._TransformChange)
        triObject.AddNotify('falloff', triObject._TransformChange)
        triObject.scene = None
        return triObject

    def AddToScene(self, scene):
        scene.AddLight(self)
        self.scene = weakref.ref(scene)

    def RemoveFromScene(self, scene):
        scene.RemoveLight(self)
        self.scene = None

    def _TransformChange(self, transform):
        self.OnTransformChange()

    def OnTransformChange(self):
        pass

    def GetPosition(self):
        return self.position

    def SetPosition(self, pos):
        self.position = pos

    def GetColor(self):
        return self.color[:3]

    def SetColor(self, color):
        self.color = (color[0],
         color[1],
         color[2],
         1)

    def GetRadius(self):
        return self.radius

    def SetRadius(self, radius):
        self.radius = radius

    def GetFalloff(self):
        return self.falloff

    def SetFalloff(self, falloff):
        self.falloff = falloff
