#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\view\spaceView.py
from billboards import load_billboard_playlist
from eve.common.script.sys.eveCfg import IsDockedInStructure
import evecamera
from viewstate import View
import uicls
import service
import carbonui.const as uiconst

class SpaceView(View):
    __guid__ = 'viewstate.SpaceView'
    __notifyevents__ = ['OnActiveCameraChanged']
    __dependencies__ = ['standing',
     'tactical',
     'map',
     'wallet',
     'space',
     'state',
     'bracket',
     'target',
     'fleet',
     'surveyScan',
     'autoPilot',
     'neocom',
     'corp',
     'alliance',
     'skillqueue',
     'dungeonTracking',
     'transmission',
     'clonejump',
     'assets',
     'charactersheet',
     'trigger',
     'contracts',
     'certificates',
     'sov',
     'turret',
     'posAnchor',
     'michelle',
     'sceneManager',
     'structureProximityTracker']
    __layerClass__ = uicls.InflightLayer
    __subLayers__ = [('l_spaceTutorial', None, None),
     ('l_bracket', None, None),
     ('l_sensorSuite', None, None),
     ('l_tactical', None, None)]
    __overlays__ = {'shipui', 'sidePanels', 'target'}

    def __init__(self):
        View.__init__(self)
        self.solarSystemID = None
        self.keyDownEvent = None

    def LoadView(self, change = None, **kwargs):
        self.solarSystemID = session.solarsystemid
        if eve.session.role & service.ROLE_CONTENT:
            sm.StartService('scenario')
        self.bracket.Reload()
        self.cachedPlayerPos = None
        self.cachedPlayerRot = None
        load_billboard_playlist()

    def LoadCamera(self, cameraID = None):
        if cameraID is None:
            sceneMan = sm.GetService('sceneManager')
            currCam = sceneMan.GetActivePrimaryCamera()
            if not (currCam and currCam.IsLocked()):
                self.ActivatePrimaryCamera()
        else:
            sm.GetService('sceneManager').SetPrimaryCamera(cameraID)

    def UnloadView(self):
        self.LogInfo('unloading: removed ballpark and cleared effects')
        uicore.layer.main.state = uiconst.UI_PICKCHILDREN

    def ShowView(self, **kwargs):
        View.ShowView(self, **kwargs)
        self.keyDownEvent = uicore.event.RegisterForTriuiEvents([uiconst.UI_KEYDOWN], self.CheckKeyDown)

    def HideView(self):
        if self.keyDownEvent:
            uicore.event.UnregisterForTriuiEvents(self.keyDownEvent)
        View.HideView(self)

    def CheckShouldReopen(self, newKwargs, cachedKwargs):
        reopen = False
        if newKwargs == cachedKwargs or 'changes' in newKwargs and 'solarsystemid' in newKwargs['changes']:
            reopen = True
        return reopen

    def CheckKeyDown(self, *args):
        ctrl = uicore.uilib.Key(uiconst.VK_CONTROL)
        alt = uicore.uilib.Key(uiconst.VK_MENU)
        shift = uicore.uilib.Key(uiconst.VK_SHIFT)
        if not ctrl and alt and not shift and session.solarsystemid:
            self.bracket.ShowAllHidden()
        return 1

    def OnActiveCameraChanged(self, cameraID):
        tacticalSvc = sm.GetService('tactical')
        if tacticalSvc.IsTacticalOverlayActive():
            tacticalSvc.ShowTacticalOverlay()
        else:
            tacticalSvc.HideTacticalOverlay()

    def GetRegisteredCameraID(self):
        if IsDockedInStructure():
            return evecamera.CAM_SHIPORBIT
        return settings.char.ui.Get('spaceCameraID', evecamera.CAM_SHIPORBIT)

    def ActivatePrimaryCamera(self):
        cameraID = self.GetRegisteredCameraID()
        sceneMan = sm.GetService('sceneManager')
        return sceneMan.SetPrimaryCamera(cameraID)
