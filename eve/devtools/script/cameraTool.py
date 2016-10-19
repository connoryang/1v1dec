#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\devtools\script\cameraTool.py
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.util.color import Color
from eve.client.script.ui.control.buttons import Button
from eve.client.script.ui.control.eveLabel import Label
from eve.client.script.ui.control.eveWindow import Window
import carbonui.const as uiconst
import evecamera
import uthread
import blue
BUTTONHINT = '1.\tPerform "Look at" to attach to an item you want to examine (important to achieve proper pan sensitivity).\nYou can orbit while attached.\n\n2.\tDetach camera using right-drag. Move around using pan, rotate and zoom to cursor.\n\n3.\tTake a close look by using ALT+zoom\n'

class CameraTool(Window):
    default_caption = ('Camera Tool',)
    default_windowID = 'CameraToolID'
    default_width = 250
    default_height = 150
    default_topParentHeight = 0
    default_minSize = (300, 300)

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.oldCamID = None
        self.mainCont = Container(parent=self.sr.main, padding=5)
        Button(parent=self.mainCont, align=uiconst.TOTOP, label='Toggle Debug Camera', func=self.ToggleDebugCam, hint=BUTTONHINT)
        self.atLabel = Label(parent=self.mainCont, align=uiconst.TOTOP)
        stateCont = Container(parent=self.mainCont, align=uiconst.TOTOP, height=20, padTop=5)
        self.orbitLabel = StateCont(parent=stateCont, align=uiconst.TOLEFT, text='ORBIT', padRight=2)
        self.zoomLabel = StateCont(parent=stateCont, align=uiconst.TOLEFT, text='ZOOM', padRight=2)
        self.fovZoomLabel = StateCont(parent=stateCont, align=uiconst.TOLEFT, text='FOVZOOM', padRight=2)
        self.panLabel = StateCont(parent=stateCont, align=uiconst.TOLEFT, text='PAN', padRight=2)
        self.rotateLabel = StateCont(parent=stateCont, align=uiconst.TOLEFT, text='ROTATE', padRight=2)
        uthread.new(self.Update)

    def Update(self):
        while not self.destroyed:
            try:
                cam = sm.GetService('sceneManager').GetActiveCamera()
                text = 'CameraID: <b>%s</b>' % cam.cameraID
                text += '\n\n_atPosition: %2.5f, %2.5f, %2.5f' % cam._atPosition
                atOffset = cam._atOffset or (0, 0, 0)
                text += '\n_atOffset: %2.5f, %2.5f, %2.5f' % atOffset
                text += '\n_eyePosition: %2.5f, %2.5f, %2.5f' % cam._eyePosition
                eyeOffset = cam._eyeOffset or (0, 0, 0)
                text += '\n_eyeOffset: %2.5f, %2.5f, %2.5f' % eyeOffset
                eyeAndAtOffset = cam._eyeAndAtOffset or (0, 0, 0)
                text += '\n_eyeAndAtOffset: %2.5f, %2.5f, %2.5f' % eyeAndAtOffset
                text += '\nzoomProportion: %2.2f' % cam.GetZoomProportion()
                text += '\nminZoom: %2.2f' % cam.minZoom
                text += '\nmaxZoom: %2.2f' % cam.maxZoom
                text += '\nfov: %2.2f' % cam.fov
                text += '\nznear: %2.1f' % cam._nearClip
                text += '\nzfar: %2.1f' % cam._farClip
                self.atLabel.text = text
                self.zoomLabel.SetActive(cam.zoomTarget is not None)
                self.fovZoomLabel.SetActive(cam.fovTarget is not None)
                self.panLabel.SetActive(cam.panTarget is not None)
                self.orbitLabel.SetActive(cam.orbitTarget is not None)
                self.rotateLabel.SetActive(cam.rotateUpdateThread is not None)
            except:
                raise
            finally:
                blue.synchro.Yield()

    def ToggleDebugCam(self, *args):
        sceneMan = sm.GetService('sceneManager')
        activeCamID = sceneMan.GetActiveCamera().cameraID
        if activeCamID == evecamera.CAM_DEBUG:
            sceneMan.SetPrimaryCamera(self.oldCamID)
            self.oldCamID = None
        else:
            self.oldCamID = activeCamID
            sceneMan.SetPrimaryCamera(evecamera.CAM_DEBUG)


COLOR_ON = Color.GREEN
COLOR_OFF = Color.GRAY1

class StateCont(ContainerAutoSize):

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.bgFill = Fill(bgParent=self, color=COLOR_OFF)
        self.label = Label(parent=self, align=uiconst.CENTERLEFT, text=attributes.text, padLeft=5, padRight=5)

    def SetActive(self, isActive):
        if isActive:
            self.bgFill.SetRGB(*COLOR_ON)
        else:
            self.bgFill.SetRGB(*COLOR_OFF)
