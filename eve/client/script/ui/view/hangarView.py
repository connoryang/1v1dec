#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\view\hangarView.py
import telemetry
from billboards import get_billboard_fallback_image, get_billboard_video_path
import const
import evecamera
import uicls
import uthread
import evetypes
from eve.client.script.ui.camera.cameraUtil import IsDynamicCameraMovementEnabled
from eveSpaceObject import spaceobjaudio
from evegraphics.fsd.graphicIDs import GetGraphicFile
from videoplayer import playlistresource
from eve.client.script.ui.services.viewStateSvc import View
from hangarBehaviours import capitalHangarBehaviours, defaultHangarBehaviours
from eve.client.script.ui.view.viewStateConst import ViewState
from eveSpaceObject import spaceobjanimation
import inventorycommon.const as invconst
AMARR_NORMAL_HANGAR_SIZE = 'AMARR_NORMAL'
CALDARI_NORMAL_HANGAR_SIZE = 'CALDARI_NORMAL'
GALLENTE_NORMAL_HANGAR_SIZE = 'GALLENTE_NORMAL'
MINMATAR_NORMAL_HANGAR_SIZE = 'MINMTAR_NORMAL'
CITADEL_NORMAL_HANGAR_SIZE = 'CITADEL_NORMAL'
CITADEL_CAPITAL_HANGAR_SIZE = 'CITADEL_LARGE'
EXIT_AUDIO_EVENT_FOR_HANGAR_TYPE = {AMARR_NORMAL_HANGAR_SIZE: 'music_switch_race_amarr',
 CALDARI_NORMAL_HANGAR_SIZE: 'music_switch_race_caldari',
 GALLENTE_NORMAL_HANGAR_SIZE: 'music_switch_race_gallente',
 MINMATAR_NORMAL_HANGAR_SIZE: 'music_switch_race_minmatar',
 CITADEL_CAPITAL_HANGAR_SIZE: 'music_switch_race_caldari',
 CITADEL_NORMAL_HANGAR_SIZE: 'music_switch_race_caldari'}
ALL_DEFAULT_BEHAVIOURS = (defaultHangarBehaviours.DefaultHangarShipBehaviour, defaultHangarBehaviours.DefaultHangarTrafficBehaviour)
ALL_CAPITAL_BEHAVIOURS = (capitalHangarBehaviours.CapitalHangarShipBehaviour, capitalHangarBehaviours.CapitalHangarTrafficBehaviour)
HANGAR_BEHAVIOURS = {AMARR_NORMAL_HANGAR_SIZE: ALL_DEFAULT_BEHAVIOURS,
 CALDARI_NORMAL_HANGAR_SIZE: ALL_DEFAULT_BEHAVIOURS,
 GALLENTE_NORMAL_HANGAR_SIZE: ALL_DEFAULT_BEHAVIOURS,
 MINMATAR_NORMAL_HANGAR_SIZE: ALL_DEFAULT_BEHAVIOURS,
 CITADEL_NORMAL_HANGAR_SIZE: ALL_DEFAULT_BEHAVIOURS,
 CITADEL_CAPITAL_HANGAR_SIZE: ALL_CAPITAL_BEHAVIOURS}
HANGAR_GRAPHIC_ID = {AMARR_NORMAL_HANGAR_SIZE: 20273,
 CALDARI_NORMAL_HANGAR_SIZE: 20271,
 GALLENTE_NORMAL_HANGAR_SIZE: 20274,
 MINMATAR_NORMAL_HANGAR_SIZE: 20272,
 CITADEL_NORMAL_HANGAR_SIZE: 21259,
 CITADEL_CAPITAL_HANGAR_SIZE: 21260}
USE_CITADEL_HANGAR = False
REPLACE_DOCK = 1
REPLACE_SWITCHSHIPS = 2
REPLACE_UPDATE = 3

def ShipNeedsBigHangar(shipTypeID):
    typeGroup = evetypes.GetGroupID(shipTypeID)
    return typeGroup in (const.groupSupercarrier, const.groupTitan)


def GetHangarType(stationTypeID, shipTypeID):
    if USE_CITADEL_HANGAR or evetypes.GetCategoryID(stationTypeID) == const.categoryStructure:
        hangarType = CITADEL_NORMAL_HANGAR_SIZE
        if shipTypeID and ShipNeedsBigHangar(shipTypeID):
            hangarType = CITADEL_CAPITAL_HANGAR_SIZE
    else:
        raceID = evetypes.GetRaceID(stationTypeID)
        if raceID == const.raceAmarr:
            hangarType = AMARR_NORMAL_HANGAR_SIZE
        elif raceID == const.raceCaldari:
            hangarType = CALDARI_NORMAL_HANGAR_SIZE
        elif raceID == const.raceGallente:
            hangarType = GALLENTE_NORMAL_HANGAR_SIZE
        elif raceID == const.raceMinmatar:
            hangarType = MINMATAR_NORMAL_HANGAR_SIZE
        else:
            hangarType = GALLENTE_NORMAL_HANGAR_SIZE
    return hangarType


def GetHangarBehaviours(stationTypeID, shipTypeID):
    return HANGAR_BEHAVIOURS[GetHangarType(stationTypeID, shipTypeID)]


def GetHangarGraphicID(stationTypeID, shipTypeID):
    return HANGAR_GRAPHIC_ID[GetHangarType(stationTypeID, shipTypeID)]


class HangarView(View):
    __guid__ = 'viewstate.HangarView'
    __notifyevents__ = ['OnDogmaItemChange',
     'ProcessActiveShipChanged',
     'OnActiveShipSkinChange',
     'OnDamageStateChanged',
     'OnStanceActive']
    __dependencies__ = ['godma',
     'loading',
     'station',
     'invCache',
     't3ShipSvc',
     'sceneManager',
     'clientDogmaIM',
     'skinSvc']
    __overlays__ = {'sidePanels'}
    __layerClass__ = uicls.HangarLayer

    def __init__(self):
        View.__init__(self)
        self.scenePath = ''
        self.activeShipItem = None
        self.activeShipModel = None
        self.activeHangarScene = None
        self.generalAudioEntity = None
        self.currentGraphicID = -1
        self.shipBehaviour = None
        self.trafficBehaviour = None
        playlistresource.register_resource_constructor('hangarvideos', 1024, 576, playlistresource.shuffled_videos(get_billboard_video_path()), get_billboard_fallback_image())

    def GetActiveShipTypeID(self):
        if self.activeShipItem is None:
            return
        return self.activeShipItem.typeID

    def GetActiveShipItemID(self):
        if self.activeShipItem is None:
            return
        return self.activeShipItem.itemID

    @telemetry.ZONE_METHOD
    def ShowView(self, **kwargs):
        View.ShowView(self, **kwargs)
        self.activeShipModel = None
        self.activeShipItem = self.GetShipItemFromHangar(session.shipid)
        scMethod, tcMethod = GetHangarBehaviours(self.GetStationType(), self.GetActiveShipTypeID())
        self.shipBehaviour = scMethod()
        self.trafficBehaviour = tcMethod()
        self.LoadAndSetupScene(self.GetActiveShipTypeID())
        settings.user.ui.Set('defaultDockingView', ViewState.Hangar)
        if session.structureid:
            settings.user.ui.Set('defaultStructureView', ViewState.Hangar)

    def OnDocking(self):
        uthread.new(self.ReplaceExistingShipModel, REPLACE_DOCK)

    def OnHangarToHangar(self):
        uthread.new(self.ReplaceExistingShipModel, REPLACE_SWITCHSHIPS)

    def LoadAndSetupScene(self, shipTypeID):
        self.activeHangarScene = self.LoadScene(shipTypeID)
        self.StartHangarAnimations(self.activeHangarScene)
        self.trafficBehaviour.Setup(self.activeHangarScene)
        self.shipBehaviour.SetAnchorPoint(self.activeHangarScene)

    @telemetry.ZONE_METHOD
    def LoadView(self, change = None, **kwargs):
        self.station.CleanUp()
        self.station.StopAllStationServices()
        self.station.Setup()
        View.LoadView(self, **kwargs)

    def LoadCamera(self, cameraID = None):
        sm.GetService('sceneManager').SetPrimaryCamera(self.GetCameraID())
        self.ReplaceExistingShipModel(REPLACE_UPDATE)

    def GetCameraID(self):
        hangarType = self.GetCurrHangarType()
        if hangarType == CITADEL_CAPITAL_HANGAR_SIZE:
            return evecamera.CAM_CAPITALHANGAR
        else:
            return evecamera.CAM_HANGAR

    @telemetry.ZONE_METHOD
    def UnloadView(self):
        self.layer.camera = None
        self.trafficBehaviour.CleanUp()
        self.sceneManager.UnregisterScene(ViewState.Hangar)
        self.UnActivateSceneObjects()

    def ReloadView(self):
        self.trafficBehaviour.CleanUp()
        sm.GetService('viewState').ActivateView(ViewState.Hangar)

    def UnActivateSceneObjects(self):
        if self.activeHangarScene:
            for obj in self.activeHangarScene.objects[:]:
                self.activeHangarScene.objects.remove(obj)

        self.activeHangarScene = None
        if hasattr(self.activeShipModel, 'animationSequencer'):
            self.activeShipModel.animationSequencer = None
        self.activeShipModel = None
        self.activeShipItem = None

    def LoadScene(self, shipTypeID):
        self.currentGraphicID = GetHangarGraphicID(self.GetStationType(), shipTypeID)
        stationGraphicFile = GetGraphicFile(self.currentGraphicID)
        if stationGraphicFile is None:
            self.LogError("Could not find a graphic file for graphicID '%s', returning and showing nothing" % self.currentGraphicID)
        scene, _ = self.sceneManager.LoadScene(stationGraphicFile, registerKey=ViewState.Hangar)
        return scene

    def SetupGeneralAudioEntity(self, model):
        if model is not None and hasattr(model, 'observers'):
            self.generalAudioEntity = spaceobjaudio.SetupAudioEntity(model)
            self.SetupAnimationUpdaterAudio(model)

    def SetupAnimationUpdaterAudio(self, model):
        if hasattr(model, 'animationUpdater'):
            model.animationUpdater.eventListener = self.generalAudioEntity

    def ReplaceExistingShipModel(self, eventType):
        itemID = self.GetActiveShipItemID()
        typeID = self.GetActiveShipTypeID()
        if not itemID or not typeID:
            return
        newModel = self.shipBehaviour.LoadShipModel(itemID, typeID)
        self.SetupGeneralAudioEntity(newModel)
        isTooBig = self.IsShipTooBigToAnimate(typeID)
        if eventType == REPLACE_SWITCHSHIPS or isTooBig:
            self.layer.FadeIn(0.3, sleep=True)
        if self.activeShipModel:
            self.RemoveModelWithNameFromScene(self.activeShipModel.name)
            self.AddModelToScene(newModel)
        else:
            self.AddModelToScene(newModel)
        self.GetCamera().SetShip(newModel, typeID)
        if eventType == REPLACE_UPDATE or isTooBig or not IsDynamicCameraMovementEnabled():
            self.shipBehaviour.PlaceShip(newModel, typeID)
            self.PlayUpdateShipSequence()
        elif eventType == REPLACE_DOCK:
            duration = 12.0
            self.shipBehaviour.AnimateShipEntry(newModel, typeID, duration=duration)
            self.PlayDockSequence(duration)
        elif eventType == REPLACE_SWITCHSHIPS:
            duration = 7.0
            self.shipBehaviour.AnimateShipEntry(newModel, typeID, duration=duration)
            self.PlaySwitchShipSequence(duration)

    def IsShipTooBigToAnimate(self, typeID):
        if self.GetCurrHangarType() == CITADEL_CAPITAL_HANGAR_SIZE:
            return False
        groupID = evetypes.GetGroupID(typeID)
        return groupID in (invconst.groupSupercarrier,
         invconst.groupTitan,
         invconst.groupDreadnought,
         invconst.groupForceAux)

    def PlayDockSequence(self, duration):
        self.generalAudioEntity.SendEvent(unicode('hangar_spin_switch_ship_play'))
        endPos = self.shipBehaviour.GetAnimEndPosition()
        startPos = self.shipBehaviour.GetAnimStartPosition()
        camera = self.GetCamera()
        camera.AnimEnterHangar(self.activeShipModel, startPos=startPos, endPos=endPos, duration=duration)

    def GetCamera(self):
        return sm.GetService('sceneManager').GetRegisteredCamera(self.GetCameraID())

    def PlaySwitchShipSequence(self, duration):
        self.layer.FadeOut(1.0)
        self.generalAudioEntity.SendEvent(unicode('hangar_spin_switch_ship_play'))
        endPos = self.shipBehaviour.GetAnimEndPosition()
        startPos = self.shipBehaviour.GetAnimStartPosition()
        camera = self.GetCamera()
        camera.AnimSwitchShips(self.activeShipModel, startPos=startPos, endPos=endPos, duration=duration)

    def PlayUpdateShipSequence(self):
        self.layer.FadeOut(1.0)
        endPos = self.shipBehaviour.GetAnimEndPosition()
        self.GetCamera().PlaceShip(endPos)

    def StartHangarAnimations(self, scene):
        for obj in scene.objects:
            for fx in obj.children:
                if fx.name.startswith('sfx_'):
                    fx.display = True

    def RemoveModelWithNameFromScene(self, modelName):
        if self.activeHangarScene:
            for m in [ o for o in self.activeHangarScene.objects if o.name == modelName ]:
                self.activeHangarScene.objects.remove(m)

    def AddModelToScene(self, model):
        if self.activeHangarScene and model:
            self.activeHangarScene.objects.append(model)
        self.activeShipModel = model

    def GetStationType(self):
        if session.structureid:
            return self.invCache.GetInventory(const.containerStructure).GetTypeID()
        else:
            return eve.stationItem.stationTypeID

    def GetShipItemFromHangar(self, shipID):
        hangarInv = self.invCache.GetInventory(const.containerHangar)
        hangarItems = hangarInv.List(const.flagHangar)
        for each in hangarItems:
            if each.itemID == shipID and each.categoryID == const.categoryShip:
                return each

    @telemetry.ZONE_METHOD
    def StartExitAnimation(self):
        if self.activeHangarScene is not None:
            for curveSet in self.activeHangarScene.curveSets:
                if curveSet.name == 'Undock':
                    curveSet.scale = 1.0
                    curveSet.PlayFrom(0.0)
                    break

    @telemetry.ZONE_METHOD
    def StopExitAnimation(self):
        if self.activeHangarScene is not None:
            for curveSet in self.activeHangarScene.curveSets:
                if curveSet.name == 'Undock':
                    curveSet.scale = -1.0
                    curveSet.PlayFrom(curveSet.GetMaxCurveDuration())
                    break

    def StartExitAudio(self):
        audioService = sm.GetService('audio')
        hangarType = self.GetCurrHangarType()
        audioService.SendUIEvent(EXIT_AUDIO_EVENT_FOR_HANGAR_TYPE[hangarType])
        audioService.SendUIEvent('transition_undock_play')

    def GetCurrHangarType(self):
        return GetHangarType(self.GetStationType(), self.GetActiveShipTypeID())

    def StopExitAudio(self):
        sm.GetService('audio').SendUIEvent('transition_undock_cancel')

    def ProcessActiveShipChanged(self, shipID, oldShipID):
        if shipID == oldShipID:
            return
        newShipItem = self.GetShipItemFromHangar(shipID)
        if newShipItem is None:
            return
        self.activeShipItem = newShipItem
        if self.currentGraphicID != GetHangarGraphicID(self.GetStationType(), self.GetActiveShipTypeID()):
            self.ReloadView()
            return
        self.ReplaceExistingShipModel(REPLACE_SWITCHSHIPS)

    def OnStanceActive(self, shipID, stanceID):
        if self.activeShipModel is not None:
            spaceobjanimation.SetShipAnimationStance(self.activeShipModel, stanceID)

    def OnActiveShipSkinChange(self, itemID, skinID):
        if self.shipBehaviour.ShouldSwitchSkin(skinID) and itemID == self.GetActiveShipItemID():
            self.activeShipItem = self.GetShipItemFromHangar(itemID)
            self.layer.FadeIn(0.3, sleep=True)
            self.ReplaceExistingShipModel(REPLACE_UPDATE)

    def OnDamageStateChanged(self, itemID):
        if self.GetActiveShipItemID() == itemID:
            self.shipBehaviour.SetShipDamage(itemID, self.activeShipModel)

    def OnDogmaItemChange(self, item, change):
        if item.locationID == change.get(const.ixLocationID, None) and item.flagID == change.get(const.ixFlag):
            return
        if item.flagID in const.subSystemSlotFlags:
            self.ReplaceExistingShipModel(REPLACE_UPDATE)
        else:
            self.shipBehaviour.FitTurrets(self.activeShipItem.itemID, self.activeShipItem.typeID, self.activeShipModel)
