#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\view\structureView.py
from eve.client.script.ui.services.viewStateSvc import View
from eve.client.script.ui.structure.navigation import StructureLayer
from eve.client.script.ui.view.viewStateConst import ViewState

class StructureView(View):
    __guid__ = 'viewstate.StructureView'
    __suppressedOverlays__ = {'shipui', 'target'}
    __overlays__ = {'sidePanels'}
    __notifyevents__ = ['OnBallparkSetState']
    __dependencies__ = ['cameraClient', 'autoPilot']
    __layerClass__ = StructureLayer

    def ShowView(self, **kwargs):
        self.cameraClient.Enable()
        self.autoPilot.SetOff()
        settings.user.ui.Set('defaultStructureView', ViewState.Structure)
        sm.GetService('sceneManager').SetPrimaryCamera('shiporbit')

    def HideView(self):
        self.cameraClient.Disable()

    def OnBallparkSetState(self):
        if self.IsActive():
            sm.GetService('sceneManager').SetPrimaryCamera('shiporbit')
