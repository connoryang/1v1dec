#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\camera\sceneContainerCamera.py
from eve.client.script.ui.camera.baseCamera import Camera

class SceneContainerCamera(Camera):

    def __init__(self):
        Camera.__init__(self)
        self._aspectRatio = 1.0

    def UpdateViewportSize(self, width, height):
        self._aspectRatio = float(width) / height

    def GetAspectRatio(self):
        return self._aspectRatio

    def OnActivated(self, **kwargs):
        Camera.OnActivated(self, **kwargs)
        sm.GetService('sceneManager').RegisterForCameraUpdate(self)

    def OnDeactivated(self):
        Camera.OnActivated(self)
        sm.GetService('sceneManager').UnregisterForCameraUpdate(self)
