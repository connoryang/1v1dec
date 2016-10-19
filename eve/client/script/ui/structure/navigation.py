#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\structure\navigation.py
import evecamera
import carbonui.const as uiconst
from carbonui.uicore import uicorebase as uicore
from carbonui.control.layer import LayerCore
from eve.client.script.ui.camera.shipOrbitCameraController import ShipOrbitCameraController

class StructureLayer(LayerCore):
    __notifyevents__ = ['OnActiveCameraChanged']
    __guid__ = 'uicls.StructureLayer'

    def __init__(self, *args, **kwargs):
        self.cameraController = None
        LayerCore.__init__(self, *args, **kwargs)

    def OnOpenView(self):
        sm.GetService('sceneManager').SetPrimaryCamera(evecamera.CAM_SHIPORBIT)

    def OnActiveCameraChanged(self, cameraID):
        if cameraID == evecamera.CAM_SHIPORBIT:
            self.cameraController = ShipOrbitCameraController()
        else:
            self.cameraController = None

    def OnMouseDown(self, *args):
        if self.cameraController:
            self.cameraController.OnMouseDown(*args)
        if uicore.uilib.leftbtn:
            self.SetCursor(uiconst.UICURSOR_DRAGGABLE, True)

    def OnMouseUp(self, button, *args):
        if self.cameraController:
            self.cameraController.OnMouseUp(button, *args)
        if not uicore.uilib.leftbtn:
            self.SetCursor(None, False)

    def OnMouseMove(self, *args):
        if uicore.IsDragging():
            return
        if self.cameraController:
            self.cameraController.OnMouseMove(*args)

    def OnMouseWheel(self, *args):
        if self.cameraController:
            self.cameraController.OnMouseWheel(*args)

    def OnDblClick(self, *args):
        uicore.cmd.OpenInventory()

    def GetMenu(self):
        return sm.GetService('menu').CelestialMenu(session.structureid)

    def SetCursor(self, cursor, clip):
        self.cursor = cursor
        if clip:
            uicore.uilib.ClipCursor(0, 0, uicore.desktop.width, uicore.desktop.height)
            uicore.uilib.SetCapture(self)
        else:
            uicore.uilib.UnclipCursor()
            if uicore.uilib.GetCapture() == self:
                uicore.uilib.ReleaseCapture()
