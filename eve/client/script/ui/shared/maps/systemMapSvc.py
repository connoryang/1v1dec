#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\maps\systemMapSvc.py
from eve.client.script.ui.station import stationServiceConst
from eve.client.script.ui.camera.systemMapCamera2 import SystemMapCamera2
import evecamera
import evetypes
import service
from service import SERVICE_START_PENDING, SERVICE_RUNNING
import base
import blue
import log
from eve.client.script.ui.control.eveHint import BubbleHint
from eve.client.script.ui.inflight.bracket import SimpleBracket, Bracket
from eve.client.script.ui.inflight.probeBracket import ProbeBracket
from eve.client.script.ui.inflight.scanner import Scanner
from eve.client.script.ui.shared.maps.label import TransformableLabel
from eve.client.script.ui.shared.maps.route import MapRoute
import trinity
import uix
import uiutil
import uthread
import util
import xtriui
import sys
import state
import bracketUtils
import maputils
import carbonui.const as uiconst
import localization
import telemetry
import const
import uiprimitives
from mapcommon import SYSTEMMAP_SCALE, ZOOM_FAR_SYSTEMMAP
from eve.common.script.mgt.entityConst import POS_STRUCTURE_STATE
import geo2
from math import sin, cos, pi
NEUTRAL_COLOR = (0.25,
 0.25,
 0.25,
 1.0)

class SystemMapSvc(service.Service):
    __guid__ = 'svc.systemmap'
    __notifyevents__ = ['OnSessionChanged',
     'OnStateChange',
     'OnBookmarkCreated',
     'OnBookmarksDeleted',
     'OnSolarsystemMapSettingsChange',
     'OnTacticalOverlayChange',
     'OnNewScanResult',
     'DoBallsAdded',
     'DoBallRemove',
     'OnSystemScanBegun',
     'OnProbeRemoved',
     'OnProbeAdded',
     'OnProbeStateChanged',
     'OnProbeStateUpdated',
     'OnProbeWarpStart',
     'OnProbeWarpEnd',
     'OnDistributionDungeonEntered',
     'OnEscalatingPathDungeonEntered',
     'OnSlimItemChange',
     'OnMapReset',
     'OnMapModeChangeDone',
     'DoBallsRemove']
    __servicename__ = 'systemmap'
    __displayname__ = 'System Map Client Service'
    __dependencies__ = ['station',
     'map',
     'settings',
     'facwar',
     'securityOfficeSvc']
    __update_on_reload__ = 0

    def Run(self, memStream = None):
        self.state = SERVICE_START_PENDING
        self.LogInfo('Starting System Map Client Svc')
        self.Reset()
        self.state = SERVICE_RUNNING

    def Stop(self, memStream = None):
        if trinity.device is None:
            return
        self.LogInfo('Map svc')
        self.Reset()

    def CleanUp(self):
        self.Reset()
        scene = sm.GetService('sceneManager').GetRegisteredScene('systemmap')
        if scene:
            del scene.objects[:]
        sm.GetService('sceneManager').UnregisterScene('systemmap')
        sm.GetService('sceneManager').UnregisterCamera(evecamera.CAM_SYSTEMMAP)

    def Open(self):
        from eve.client.script.ui.shared.mapView.mapViewUtil import OpenSolarSystemMap
        OpenSolarSystemMap()

    def OnMapModeChangeDone(self, mapMode):
        if mapMode == 'systemmap':
            if self.updateDisplayInfomationWorkerRunning == False:
                self.updateDisplayInfomationWorkerRunning = True
                uthread.new(self.UpdateDisplayInformationWorker).context = 'systemMapSvc::UpdateDisplayInformationWorker'

    def UpdateDisplayInformationWorker(self):
        while sm.GetService('viewState').IsViewActive('systemmap'):
            startTime = blue.os.GetWallclockTime()
            for panel in self.bracketPanels[:]:
                if panel and not panel.destroyed:
                    if panel.ball:
                        panel.ball.GetVectorAt(blue.os.GetSimTime())
                    if getattr(panel, 'hasBubbleHintShowing', False):
                        if panel.itemID and panel.slimItem and hasattr(panel.sr, 'bubble'):
                            if panel.sr.bubble.state != uiconst.UI_HIDDEN:
                                hintText = self.GetBubbleHint(panel.itemID, panel.slimItem, bracket=panel, extended=0)
                                panel.ShowBubble(hintText)
                blue.pyos.BeNice()

            diff = blue.os.TimeDiffInMs(startTime, blue.os.GetWallclockTime())
            sleep = max(500, 2000 - diff)
            blue.pyos.synchro.SleepWallclock(sleep)

        self.updateDisplayInfomationWorkerRunning = False

    def OnMapReset(self):
        self.Reset()

    def InitMap(self):
        title = localization.GetByLabel('UI/Map/StarMap/InitializingMap')
        loadLabel = localization.GetByLabel('UI/Map/StarMap/BuildingModel')
        sm.GetService('loading').ProgressWnd(title, loadLabel, 0, 3)
        sceneManager = sm.GetService('sceneManager')
        registered = sceneManager.GetRegisteredScene('systemmap')
        camera = sceneManager.GetRegisteredCamera(evecamera.CAM_SYSTEMMAP)
        if registered is None or self.currentSolarsystemID != eve.session.solarsystemid2:
            cameraFov = 0.7
            scene = trinity.Load('res:/dx9/scene/systemMap.red')
            lineSet = self.map.CreateLineSet()
            lineSet.scaling = (SYSTEMMAP_SCALE, SYSTEMMAP_SCALE, SYSTEMMAP_SCALE)
            scene.objects.append(lineSet)
            self.orbitLineSet = lineSet
            ssmap, self.solarsystemSunID = self.DrawSolarSystem(eve.session.solarsystemid2)
            self.currentSolarsystemID = eve.session.solarsystemid2
            if camera is None:
                camera = SystemMapCamera2()
                camera.idleMove = 0
                camera.friction = 25.0
                camera.fieldOfView = cameraFov
                camera.frontClip = 0.3
                camera.backClip = 30000.0
                for each in camera.zoomCurve.keys:
                    each.value = cameraFov

                camera.translationFromParent = settings.user.ui.Get('systemmapTFP', 0.8 * ZOOM_FAR_SYSTEMMAP)
                if camera.translationFromParent < 0:
                    camera.translationFromParent = -camera.translationFromParent
                camera.OrbitParent(0.0, 10.0)
                sceneManager.RegisterCamera(camera)
            ssmap.scaling = (SYSTEMMAP_SCALE, SYSTEMMAP_SCALE, SYSTEMMAP_SCALE)
            scene.objects.append(ssmap)
            self.currentSolarsystem = ssmap
            sceneManager.RegisterScene(scene, 'systemmap')
            sm.GetService('viewState').GetView('systemmap').layer.SetInterest(eve.session.shipid, interpolate=False)
            self.lastHighlightItemsWithinProbeRange = blue.os.GetWallclockTime()
        sceneManager.SetRegisteredScenes('systemmap')
        sceneManager.SetSecondaryCamera(evecamera.CAM_SYSTEMMAP)
        sm.GetService('loading').ProgressWnd(title, loadLabel, 1, 3)
        self.LoadProbesAndScanResult()
        self.LoadBookmarks()
        self.LoadSolarsystemBrackets()
        self.LoadBeacons()
        self.LoadSatellites()
        self.LoadSovereigntyStructures()
        self.LoadDungeons()
        sm.GetService('loading').ProgressWnd(title, loadLabel, 2, 3)
        uthread.new(self.ShowRanges, sm.GetService('tactical').IsTacticalOverlayActive())
        scanner = Scanner.GetIfOpen()
        if scanner is not None:
            scanner.Refresh()
        sm.GetService('loading').StopCycle()

    def OnSessionChanged(self, isremote, session, change):
        if session.charid is None:
            return
        if 'solarsystemid' in change:
            if sm.GetService('viewState').IsViewActive('systemmap'):
                self.InitMap()
            else:
                self.ClearAllBrackets()

    def DoBallsAdded(self, *args, **kw):
        import stackless
        import blue
        t = stackless.getcurrent()
        timer = t.PushTimer(blue.pyos.taskletTimer.GetCurrent() + '::map')
        try:
            return self.DoBallsAdded_(*args, **kw)
        finally:
            t.PopTimer(timer)

    def DoBallsAdded_(self, lst, ignoreMoons = 0, ignoreAsteroids = 1):
        if sm.GetService('viewState').IsViewActive('systemmap'):
            groupIDs = []
            for ball, slimItem in lst:
                groupIDs.append(slimItem.groupID)
                if ball.id == session.shipid:
                    self.LoadSolarsystemBrackets(1)

            if const.groupCosmicSignature in groupIDs or const.groupCosmicAnomaly in groupIDs:
                uthread.worker('MapMgr::LoadDungeons', self.LoadDungeons)
            if const.groupScannerProbe in groupIDs:
                self.loadProbeAndScanResultTimer = base.AutoTimer(250, self.LoadProbesAndScanResult)
            if slimItem.groupID in const.sovereigntyClaimStructuresGroups:
                self.LoadSovereigntyStructures()

    @telemetry.ZONE_METHOD
    def DoBallsRemove(self, pythonBalls, isRelease):
        for ball, slimItem, terminal in pythonBalls:
            self.DoBallRemove(ball, slimItem, terminal)

    def DoBallRemove(self, ball, slimItem, terminal):
        if not trinity.device:
            return
        if sm.GetService('viewState').IsViewActive('systemmap'):
            if slimItem.groupID == const.groupScannerProbe:
                self.loadProbeAndScanResultTimer = base.AutoTimer(250, self.LoadProbesAndScanResult)
            if slimItem.groupID in const.sovereigntyClaimStructuresGroups:
                self.LoadSovereigntyStructures()

    def OnProbeWarpStart(self, probeID, fromPos, toPos, startTime, duration):
        uthread.worker('MapMgr::OnProbeWarpStart_Thread', self.OnProbeWarpStart_Thread, probeID, fromPos, toPos, startTime, duration)

    def OnProbeWarpStart_Thread(self, probeID, fromPos, toPos, startTime, duration):
        scene = sm.GetService('sceneManager').GetRegisteredScene('systemmap')
        if scene is None:
            return
        if not hasattr(self, 'probeRoutes'):
            self.probeRoutes = {}
        scanSvc = sm.GetService('scanSvc')
        data = scanSvc.GetProbeData()
        if probeID not in data:
            return
        probe = data[probeID]
        route = MapRoute()
        route.ballScale = 0.4
        route.timeBase = duration
        route.scale = SYSTEMMAP_SCALE
        route.lineColor = (0.0, 1.0, 0.0, 0.1)
        route.resPath = 'res:/dx9/model/Sprite/ProbeRouteSprite.red'
        route.name = 'probeRoute_' + str(probeID)
        route.DrawRoute((probe.pos, probe.destination), usePoints=True, drawLines=True, blinking=False)
        scene.objects.append(route.model)
        scene.objects.append(route.lineSet)
        self.probeRoutes[probeID] = route
        self.loadProbeAndScanResultTimer = base.AutoTimer(250, self.LoadProbesAndScanResult)

    def OnProbeWarpEnd(self, probeID):
        uthread.worker('MapMgr::OnProbeWarpEnd_Thread', self.OnProbeWarpEnd_Thread, probeID)

    def OnProbeWarpEnd_Thread(self, probeID):
        if hasattr(self, 'probeRoutes') and probeID in self.probeRoutes:
            scene = sm.GetService('sceneManager').GetRegisteredScene('systemmap')
            if scene is None:
                return
            route = self.probeRoutes[probeID]
            if route.model in scene.objects:
                scene.objects.remove(route.model)
            if route.lineSet in scene.objects:
                scene.objects.remove(route.lineSet)
            del self.probeRoutes[probeID]
        self.loadProbeAndScanResultTimer = base.AutoTimer(250, self.LoadProbesAndScanResult)

    def OnSystemScanBegun(self, *args):
        self.LoadProbesAndScanResult_Delayed()

    def OnProbeRemoved(self, probeID):
        self.LoadProbesAndScanResult_Delayed()

    def OnProbeAdded(self, probe):
        self.LoadProbesAndScanResult_Delayed()

    def OnProbeStateChanged(self, probeID, probeState):
        self.LoadProbesAndScanResult_Delayed()

    def OnProbeStateUpdated(self, probeID, probeState):
        self.LoadProbesAndScanResult_Delayed()

    def LoadProbesAndScanResult_Delayed(self):
        self.loadProbeAndScanResultTimer = base.AutoTimer(250, self.LoadProbesAndScanResult)

    def OnStateChange(self, itemID, flag, true, *args):
        if not sm.GetService('viewState').IsViewActive('starmap', 'systemmap'):
            return None
        if flag == state.gbTravelTo:
            self.broadcastBrackets = self.broadcastBrackets or {}
            gbID, charID = args
            if true:
                self.broadcastBrackets[itemID] = (gbID, sm.GetService('starmap').MakeBroadcastBracket('TravelTo', itemID, charID))
            else:
                lastGBID, bracket = self.broadcastBrackets.get(itemID, (None, None))
                if lastGBID == gbID:
                    del self.broadcastBrackets[itemID]
        bracket = self.GetBracket(itemID)
        if bracket:
            bracket.OnStateChange(itemID, flag, true, *args)

    def OnBookmarkCreated(self, bookmarkID, comment, itemTypeID = None):
        if sm.GetService('viewState').IsViewActive('systemmap'):
            self.LoadBookmarks()
            sm.GetService('bracket').ResetOverlaps()

    def OnBookmarksDeleted(self, bookmarkIDs):
        if sm.GetService('viewState').IsViewActive('systemmap'):
            self.LoadBookmarks()
            sm.GetService('bracket').ResetOverlaps()

    def OnSolarsystemMapSettingsChange(self, change, *args):
        if sm.GetService('viewState').IsViewActive('systemmap') and change == 'brackets':
            self.LoadBookmarks()
            self.LoadProbesAndScanResult()
            self.LoadSolarsystemBrackets(1)
            self.LoadBeacons()
            self.LoadSatellites()
            self.LoadSovereigntyStructures()
            self.LoadDungeons()

    def OnDistributionDungeonEntered(self, row):
        self.LoadDungeons()

    def OnEscalatingPathDungeonEntered(self, row):
        self.LoadDungeons()

    def OnTacticalOverlayChange(self):
        on = sm.GetService('tactical').IsTacticalOverlayActive()
        if sm.GetService('viewState').IsViewActive('systemmap'):
            self.ShowRanges(on)

    def OnNewScanResult(self, results):
        if sm.GetService('viewState').IsViewActive('systemmap'):
            self.LoadProbesAndScanResult(results)

    def Reset(self):
        self.LogInfo('System Map Reset')
        self.currentSolarsystemID = None
        self.currentSolarsystem = None
        self.solarsystemBracketsLoaded = None
        self.solarsystemHierarchyData = {}
        self.expandingHint = None
        self.talking = set()
        rangeCircleTF = getattr(self, 'rangeCircleTF', None)
        if rangeCircleTF:
            for each in rangeCircleTF.curveSets[:]:
                rangeCircleTF.curveSets.remove(each)

        self.rangeCircleTF = None
        self.rangeLineSet = None
        self.ssitems = None
        self.broadcastBrackets = None
        self.taxLevel = None
        self.mapStars = None
        self.starParticles = None
        self.solarSystemJumpLineSet = None
        self.cursor = None
        self.uicursor = None
        self.minimizedWindows = []
        self.activeMap = ''
        toRemove = getattr(self, 'bracketPanels', [])
        for each in toRemove:
            each.Close()

        self.bracketPanels = []
        self.updateDisplayInfomationWorkerRunning = False

    def GetBracket(self, itemID):
        wnd = uicore.layer.systemMapBrackets
        for each in wnd.children:
            if getattr(each, 'IsBracket', 0) and getattr(each, 'itemID', None) == itemID:
                return each

    def GetSolarsystemHierarchy(self, solarsystemID = None, toplevel = None):
        toplevel = toplevel or (const.groupPlanet,
         const.groupSun,
         const.groupStargate,
         const.groupStation)
        solarsystemID = solarsystemID or self.currentSolarsystemID
        if not solarsystemID:
            return ({}, {})
        if (solarsystemID, toplevel) in self.solarsystemHierarchyData:
            return self.solarsystemHierarchyData[solarsystemID, toplevel]
        ssData = self.GetSolarsystemData(solarsystemID).Index('itemID')
        groups = {}
        noOrbitID = []
        for id in ssData:
            each = ssData[id]
            if evetypes.GetGroupID(each.typeID) in toplevel:
                if each.itemID not in groups:
                    groups[each.itemID] = []
            elif each.orbitID is None:
                noOrbitID.append(each)

        for each in noOrbitID:
            if evetypes.GetGroupID(each.typeID) == const.groupSun:
                continue
            pos = trinity.TriVector(each.x, each.y, each.z)
            lst = []
            for parentID, orbits in groups.iteritems():
                parentItem = ssData[parentID]
                parentPos = trinity.TriVector(parentItem.x, parentItem.y, parentItem.z)
                dist = (pos - parentPos).Length()
                lst.append((dist, parentID))

            lst.sort()
            groups[lst[0][1]].append(each)

        parentLess = []
        for id in ssData:
            each = ssData[id]
            if each.itemID not in groups:
                if each.orbitID in groups:
                    groups[each.orbitID].append(each)
                elif each.orbitID:
                    parent = ssData[each.orbitID]
                    if parent.orbitID in groups:
                        groups[parent.orbitID].append(each)
                    else:
                        parentLess.append(each)

        self.solarsystemHierarchyData[solarsystemID, toplevel] = (groups, ssData)
        return (groups, ssData)

    def ClearAllBrackets(self):
        solarsystem = self.GetCurrentSolarSystem()
        bracketWnd = uicore.layer.systemMapBrackets
        for each in bracketWnd.children[:]:
            each.Close()

        self.solarsystemBracketsLoaded = None

    def ClearBrackets(self, _ui = None, _tf = None):
        solarsystem = self.GetCurrentSolarSystem()
        if solarsystem and _tf:
            for tf in solarsystem.children[:]:
                if hasattr(tf, 'name') and tf.name.startswith(_tf):
                    solarsystem.children.remove(tf)

        bracketWnd = uicore.layer.systemMapBrackets
        for each in bracketWnd.children[:]:
            if each.name == _ui:
                each.Close()

    def LoadBookmarks(self):
        self.ClearBrackets('__bookmarkbracket', 'bm_')
        if 'bookmark' not in maputils.GetVisibleSolarsystemBrackets():
            return
        bookmarks = sm.GetService('bookmarkSvc').GetBookmarks()
        ballPark = sm.GetService('michelle').GetBallpark()
        bracketWnd = uicore.layer.systemMapBrackets
        solarsystem = self.GetCurrentSolarSystem()
        showhint = maputils.GetHintsOnSolarsystemBrackets()
        suppressBubbleHints = Scanner.GetIfOpen() is not None
        showBubbleHint = not suppressBubbleHints and 'bookmark' in showhint
        for bookmark in bookmarks.itervalues():
            pos = None
            if bookmark.locationID != eve.session.solarsystemid2:
                continue
            if bookmark.x is None:
                if bookmark.itemID is not None:
                    if ballPark and bookmark.itemID in ballPark.balls:
                        ball = ballPark.balls[bookmark.itemID]
                        pos = (ball.x, ball.y, ball.z)
                    elif solarsystem:
                        for tf in solarsystem.children:
                            try:
                                itemID = int(tf.name)
                            except:
                                sys.exc_clear()
                                continue

                            if itemID == bookmark.itemID:
                                pos = tf.translation
                                break
                        else:
                            self.LogError('Didnt find propper item to track for bookmark', bookmark)
                            continue

                    else:
                        self.LogError('No ballpark or solarsystem to search for transform to track', bookmark)
                        continue
                else:
                    self.LogError('Cannot draw bookmark into solarsystem view', bookmark)
                    continue
            else:
                pos = (bookmark.x, bookmark.y, bookmark.z)
            if solarsystem and pos:
                panel = BookmarkBracket()
                panel.name = '__bookmarkbracket'
                panel.align = uiconst.NOALIGN
                panel.state = uiconst.UI_NORMAL
                panel.width = panel.height = 16
                panel.dock = 0
                panel.minDispRange = 0.0
                panel.maxDispRange = 1e+32
                panel.inflight = False
                panel.color = None
                panel.invisible = False
                panel.fadeColor = 0
                panel.OnDblClick = (self.OnBracketDoubleClick, panel)
                tf = trinity.EveTransform()
                tf.name = 'bm_%d' % bookmark.bookmarkID
                solarsystem.children.append(tf)
                panel.trackTransform = tf
                tf.translation = geo2.Vector(*pos)
                panel.Startup(bookmark, showBubbleHint)
                bracketWnd.children.insert(0, panel)

    def HighlightItemsWithinProbeRange(self):
        if not sm.GetService('viewState').IsViewActive('systemmap'):
            return
        timeDiff = blue.os.TimeDiffInMs(self.lastHighlightItemsWithinProbeRange, blue.os.GetWallclockTime())
        if timeDiff > 200.0:
            self.lastHighlightItemsWithinProbeRange = blue.os.GetWallclockTime()
        else:
            return
        scannerWnd = Scanner.GetIfOpen()
        bracketWnd = uicore.layer.systemMapBrackets
        scanSvc = sm.GetService('scanSvc')
        probeData = scanSvc.GetProbeData()
        validProbes = [ probeID for probeID, probe in probeData.iteritems() if probe.state != const.probeStateInactive ]
        reset = not bool(validProbes)
        inRangeOfProbe = []
        if scannerWnd:
            probeControls = scannerWnd.GetProbeSpheres()
            for probeID in validProbes:
                if probeID not in probeControls:
                    continue
                probeControl = probeControls[probeID]
                pPos = probeControl.GetPosition()
                pRange = probeControl.GetRange()
                for bracket in bracketWnd.children:
                    cls = getattr(bracket, '__class__', None)
                    if not cls or not issubclass(cls, SimpleBracket) or issubclass(cls, ProbeBracket):
                        continue
                    if bracket.trackTransform:
                        bPos = geo2.Vector(*bracket.trackTransform.translation)
                        if pRange > geo2.Vec3Length(pPos - bPos):
                            inRangeOfProbe.append(bracket)

        else:
            reset = True
        for bracket in bracketWnd.children:
            cls = getattr(bracket, '__class__', None)
            if not cls or not issubclass(cls, SimpleBracket) or issubclass(cls, ProbeBracket):
                continue
            if bracket.name == '__iamherebracket':
                continue
            if reset or bracket in inRangeOfProbe:
                bracket.opacity = 1.0
            else:
                bracket.opacity = 0.4

    def LoadProbesAndScanResult(self, *args):
        self.ClearBrackets('__probebracket', 'pr_')
        sm.ScatterEvent('OnProbeScanner_LoadProbesAndScanResult')
        self.loadProbeAndScanResultTimer = None
        solarsystem = self.GetCurrentSolarSystem()
        if solarsystem is None:
            return
        if not eve.session.IsItSafe():
            return
        scanSvc = sm.GetService('scanSvc')
        if not sm.GetService('viewState').IsViewActive('systemmap'):
            return
        bracketWnd = uicore.layer.systemMapBrackets
        visible = maputils.GetVisibleSolarsystemBrackets()
        activeProbes = sm.GetService('scanSvc').GetActiveProbes()
        scannerWnd = Scanner.GetIfOpen()
        showhint = maputils.GetHintsOnSolarsystemBrackets()
        suppressBubbleHints = scannerWnd is not None
        probes = scanSvc.GetProbeData()
        if const.groupScannerProbe in visible and probes is not None and len(probes) > 0:
            for probe in probes.itervalues():
                if scannerWnd and probe.probeID in activeProbes:
                    continue
                panel = ProbeBracket()
                panel.name = '__probebracket'
                panel.align = uiconst.ABSOLUTE
                panel.state = uiconst.UI_NORMAL
                panel.width = panel.height = 16
                panel.dock = 0
                panel.minDispRange = 0.0
                panel.maxDispRange = 1e+32
                panel.inflight = False
                panel.color = None
                panel.invisible = False
                panel.fadeColor = False
                panel.showLabel = bracketUtils.SHOWLABELS_ONMOUSEENTER
                panel.probe = probe
                tf = trinity.EveTransform()
                tf.name = 'pr_%d' % probe.probeID
                solarsystem.children.append(tf)
                panel.displayName = scanSvc.GetProbeLabel(probe.probeID)
                panel.showDistance = 0
                panel.Startup(probe.probeID, probe.typeID, 'ui_38_16_120')
                bracketWnd.children.insert(0, panel)
                panel.trackTransform = tf
                tf.translation = probe.pos
                slimItem = util.KeyVal()
                slimItem.jumps = []
                slimItem.itemID = probe.probeID
                slimItem.typeID = probe.typeID
                slimItem.groupID = evetypes.GetGroupID(probe.typeID)
                slimItem.categoryID = evetypes.GetCategoryID(probe.typeID)
                if not suppressBubbleHints and slimItem.groupID in showhint:
                    panel.sr.icon.SetAlign(uiconst.CENTER)
                    panel.ShowBubble(self.GetBubbleHint(probe.probeID, slimItem, bracket=panel, extended=0))

        sm.GetService('viewState').GetView('systemmap').layer.SendMessage(uiconst.UI_MOUSEENTER)
        self.HighlightItemsWithinProbeRange()

    def GetSolarsystem(self):
        return getattr(self, 'currentSolarsystem', None)

    def RefreshBubble(self, bubble):
        bracket = bubble.parent
        if bracket is None:
            log.LogTraceback('RefreshBubble: no bracket')
            return
        if bubble.expanded:
            bubble.ShowHint(bracket.expandedHint)
        else:
            bubble.ShowHint(bracket.collapsedHint)
        bracket.sr.bubble.sr.ExpandBubbleHint = lambda *args: self.ExpandBubbleHint(*args)

    def ShowRanges(self, on = 1):
        scene = sm.GetService('sceneManager').GetRegisteredScene('systemmap')
        if self.rangeCircleTF:
            for each in self.rangeCircleTF.curveSets[:]:
                self.rangeCircleTF.curveSets.remove(each)

            if self.rangeCircleTF in scene.objects:
                scene.objects.remove(self.rangeCircleTF)
        if self.rangeLineSet and self.rangeLineSet in scene.objects:
            scene.objects.remove(self.rangeLineSet)
        self.rangeLineSet = None
        self.rangeCircleTF = None
        if not on:
            return
        ranges = trinity.EveRootTransform()
        ranges.name = 'rangeCircleLabels'
        ranges.scaling = (SYSTEMMAP_SCALE, SYSTEMMAP_SCALE, SYSTEMMAP_SCALE)
        scene.objects.append(ranges)
        self.rangeCircleTF = ranges
        lineSet = self.map.CreateLineSet()
        for r in [5,
         10,
         15,
         20,
         25]:
            color = 0.25
            if r in (10, 20):
                color = 0.33
            radius = r * const.AU
            self.AddCircle(lineSet, radius * SYSTEMMAP_SCALE, color=color)
            self.AddRangeLabel(ranges, util.FmtDist(radius, 0), radius)

        lineSet.SubmitChanges()
        scene.objects.append(lineSet)
        self.rangeLineSet = lineSet
        for each in ranges.curveSets[:]:
            ranges.curveSets.remove(each)

        if eve.session.solarsystemid:
            t = 0
            sunBall = sm.GetService('michelle').GetBall(self.solarsystemSunID)
            while sunBall is None:
                blue.pyos.synchro.SleepWallclock(1000)
                sunBall = sm.GetService('michelle').GetBall(self.solarsystemSunID)
                t += 1
                if t == 15:
                    return

            vectorCurve = trinity.TriVectorCurve()
            vectorCurve.value = (-SYSTEMMAP_SCALE, -SYSTEMMAP_SCALE, -SYSTEMMAP_SCALE)
            vectorSequencer = trinity.TriVectorSequencer()
            vectorSequencer.operator = trinity.TRIOP_MULTIPLY
            vectorSequencer.functions.append(sunBall)
            vectorSequencer.functions.append(vectorCurve)
            binding = trinity.TriValueBinding()
            binding.sourceAttribute = 'value'
            binding.destinationAttribute = 'translation'
            binding.scale = 1.0
            binding.sourceObject = vectorSequencer
            binding.destinationObject = ranges
            curveSet = trinity.TriCurveSet()
            curveSet.name = 'translationCurveSet'
            curveSet.playOnLoad = True
            curveSet.curves.append(vectorSequencer)
            curveSet.bindings.append(binding)
            ranges.curveSets.append(curveSet)
            curveSet.Play()
            lineSet.translationCurve = vectorSequencer
        else:
            pos = maputils.GetMyPos()
            vectorCurve = trinity.TriVectorCurve()
            vectorCurve.value = (pos.x * SYSTEMMAP_SCALE, pos.y * SYSTEMMAP_SCALE, pos.z * SYSTEMMAP_SCALE)
            ranges.translationCurve = vectorCurve
            lineSet.translationCurve = vectorCurve

    def AddRangeLabel(self, parent, text, radius):
        for x, z in [(0.0, radius),
         (radius, 0.0),
         (0.0, -radius),
         (-radius, 0.0)]:
            label = TransformableLabel(text, parent, shadow=0, hspace=0)
            label.transform.translation = (x, 0.0, z)
            scale = geo2.Vector(*label.transform.scaling) * 1250000000.0
            label.transform.scaling = scale
            label.SetDiffuseColor((0.7, 0.7, 0.7, 1.0))

    def AddCircle(self, lineSet, radius, numberOfPoints = 256, color = 0.35):
        color = (color,
         color,
         color,
         color)
        step = pi * 2.0 / numberOfPoints
        points = []
        for idx in range(numberOfPoints):
            angle = idx * step
            x = cos(angle) * radius
            z = sin(angle) * radius
            points.append((x, 0.0, z))

        for idx1 in range(numberOfPoints):
            idx2 = (idx1 + 1) % numberOfPoints
            lineSet.AddLine(points[idx1], color, points[idx2], color)

    def LoadSolarsystemBrackets(self, reload = 0):
        if self.solarsystemBracketsLoaded == eve.session.solarsystemid2 and not reload:
            return
        bracketWnd = uicore.layer.systemMapBrackets
        bp = sm.GetService('michelle').GetBallpark()
        groups, ssData = self.GetSolarsystemHierarchy(self.currentSolarsystemID)
        self.ClearBrackets('__solarsystembracket')
        self.ClearBrackets('__iamherebracket')
        solarsystem = self.GetCurrentSolarSystem()
        if solarsystem is None:
            return
        self.solarsystemBracketsLoaded = eve.session.solarsystemid2
        validGroups = groups
        inf = 1e+32
        visible = maputils.GetVisibleSolarsystemBrackets()
        showhint = maputils.GetHintsOnSolarsystemBrackets()
        self.bracketPanels = []
        bracket = Bracket(parent=bracketWnd, name='__iamherebracket', align=uiconst.NOALIGN, state=uiconst.UI_PICKCHILDREN)
        bubble = BubbleHint(parent=bracket, name='bubblehint', align=uiconst.TOPLEFT, width=0, height=0, idx=0, state=uiconst.UI_PICKCHILDREN)
        bubble.ShowHint(localization.GetByLabel('UI/Map/StarMap/lblYouAreHere'), 2)
        bb = trinity.device.GetRenderContext().GetDefaultBackBuffer()
        if bb.width & 1:
            bracket.projectBracket.offsetX = 0.5
        if bb.height & 1:
            bracket.projectBracket.offsetY = 0.5
        if eve.session.stationid:
            pos = maputils.GetMyPos()
            tf = trinity.EveTransform()
            tf.name = 'mypos'
            tf.translation = (pos.x, pos.y, pos.z)
            solarsystem.children.append(tf)
            bracket.trackTransform = tf
        elif eve.session.solarsystemid:
            sunBall = sm.GetService('michelle').GetBall(self.solarsystemSunID)
            bracket.trackBall = sunBall
            bracket.ballTrackingScaling = -SYSTEMMAP_SCALE
        self.bracketPanels.append(bracket)
        suppressBubbleHints = Scanner.GetIfOpen() is not None
        for tf in solarsystem.children:
            try:
                itemID = int(tf.name)
                itemData = ssData[itemID]
            except:
                sys.exc_clear()
                continue

            if bp is not None and bp.slimItems:
                slimItem = bp.GetInvItem(itemID)
                if slimItem is None:
                    self.LogError('slimItem is None but I was expecting it to be something relevant', itemID, session.solarsystemid)
                    continue
                ball = bp.GetBall(itemID)
                if evetypes.GetGroupID(slimItem.typeID) not in visible:
                    continue
            else:
                if evetypes.GetGroupID(itemData.typeID) not in visible:
                    continue
                ball = None
                slimItem = util.KeyVal()
                slimItem.jumps = []
                slimItem.itemID = itemData.itemID
                slimItem.ballID = None
                slimItem.charID = None
                slimItem.ownerID = None
                slimItem.typeID = itemData.typeID
                slimItem.groupID = evetypes.GetGroupID(itemData.typeID)
                slimItem.categoryID = evetypes.GetCategoryID(itemData.typeID)
                slimItem.corpID = getattr(itemData, 'corpID', None)
                slimItem.locationID = getattr(itemData, 'locationID', None)
                slimItem.warFactionID = getattr(itemData, 'warFactionID', 0)
                slimItem.allianceID = getattr(itemData, 'allianceID', None)
            panel = Bracket(name='__solarsystembracket', align=uiconst.NOALIGN, state=uiconst.UI_NORMAL, width=16, height=16)
            panel.data = sm.GetService('bracket').GetBracketProps(slimItem, ball)
            try:
                displayName = uix.GetSlimItemName(slimItem)
            except:
                sys.exc_clear()
                continue

            if slimItem.groupID == const.groupStation:
                displayName = uix.EditStationName(displayName, usename=1)
            _iconNo, _dockType, _minDist, _maxDist, _iconOffset, _logflag = panel.data
            panel.displayName = displayName
            bracketWnd.children.insert(0, panel)
            panel.trackTransform = tf
            bb = trinity.device.GetRenderContext().GetDefaultBackBuffer()
            if bb.width & 1:
                panel.projectBracket.offsetX = 0.5
            if bb.height & 1:
                panel.projectBracket.offsetY = 0.5
            panel.dock = 0
            panel.minDispRange = 0.0
            panel.maxDispRange = 1e+32
            panel.inflight = False
            panel.color = None
            panel.invisible = False
            panel.updateItem = False
            panel.fadeColor = 0
            panel.sr.slimItem = slimItem
            panel.ssData = itemData
            panel.groupID = slimItem.groupID
            panel.ball = ball
            panel.Startup(slimItem, ball, tf)
            panel.OnDblClick = (self.OnBracketDoubleClick, panel)
            if not suppressBubbleHints and slimItem.groupID in showhint:
                panel.hasBubbleHintShowing = True
                panel.pickState = uiconst.TR2_SPS_CHILDREN
                panel.width = panel.height = 800
                panel.sr.icon.SetAlign(uiconst.CENTER)
                panel.ShowBubble(self.GetBubbleHint(itemID, slimItem, bracket=panel, extended=0))
                panel.showLabel = 0
                if slimItem.groupID in (const.groupStation,):
                    panel.sr.bubble.sr.ExpandHint = self.ExpandBubbleHint
            self.bracketPanels.append(panel)

        self.SortBubbles()

    def LoadBeacons(self):
        self.LoadBallparkItems('__beaconbracket', 'beacon_', [const.groupBeacon], overrideWidthHeight=(800, 800))

    def LoadSatellites(self):
        self.LoadBallparkItems('__satellitebracket', 'satellite_', [const.groupSatellite], overrideWidthHeight=(800, 800))

    def LoadSovereigntyStructures(self):
        self.LoadBallparkItems('__sovereigntybracket', 'sovereignty_', [const.groupSovereigntyClaimMarkers, const.groupSovereigntyDisruptionStructures], overrideWidthHeight=(800, 800))

    def LoadBallparkItems(self, bracketName, bracketPrefix, itemGroupIDs, overrideWidthHeight = None):
        solarsystem = self.GetSolarsystem()
        if solarsystem is None:
            log.LogInfo('no solar system (', bracketPrefix, 'Structures)')
            return
        self.ClearBrackets(bracketName, bracketPrefix)
        itemGroupIDlist = []
        visibleGroups = maputils.GetVisibleSolarsystemBrackets()
        for groupID in itemGroupIDs:
            if groupID in visibleGroups:
                itemGroupIDlist.append(groupID)

        if not itemGroupIDlist:
            return
        ballpark = sm.GetService('michelle').GetBallpark()
        if ballpark is None:
            return
        showhint = maputils.GetHintsOnSolarsystemBrackets()
        bracketWnd = uicore.layer.systemMapBrackets
        for itemID, ball in ballpark.balls.iteritems():
            if ballpark is None:
                break
            slimItem = ballpark.GetInvItem(itemID)
            if not slimItem:
                continue
            if slimItem.groupID not in itemGroupIDlist:
                continue
            panel = Bracket(name=bracketName, align=uiconst.NOALIGN, state=uiconst.UI_NORMAL, width=16, height=16)
            panel.data = sm.GetService('bracket').GetBracketProps(slimItem, ball)
            try:
                displayName = uix.GetSlimItemName(slimItem)
            except:
                sys.exc_clear()
                continue

            _iconNo, _dockType, _minDist, _maxDist, _iconOffset, _logflag = panel.data
            panel.displayName = displayName
            bracketWnd.children.insert(0, panel)
            tracker = trinity.EveTransform()
            tracker.name = '%s%d' % (bracketPrefix, itemID)
            tracker.translation = (ball.x, ball.y, ball.z)
            solarsystem.children.append(tracker)
            panel.trackTransform = tracker
            panel.dock = 0
            panel.minDispRange = 0.0
            panel.maxDispRange = 1e+32
            panel.inflight = False
            panel.color = None
            panel.invisible = False
            panel.updateItem = False
            panel.fadeColor = 0
            panel.sr.slimItem = slimItem
            panel.groupID = slimItem.groupID
            panel.Startup(slimItem, ball)
            if slimItem.groupID in showhint:
                if overrideWidthHeight is not None:
                    panel.width, panel.height = overrideWidthHeight
                panel.hasBubbleHintShowing = True
                panel.pickState = uiconst.TR2_SPS_CHILDREN
                panel.sr.icon.SetAlign(uiconst.CENTER)
                panel.ShowBubble(self.GetBubbleHint(itemID, slimItem, bracket=panel, extended=0))
                panel.showLabel = 0
                panel.sr.bubble.sr.ExpandHint = self.ExpandBubbleHint

        self.SortBubbles()

    def OnSlimItemChange(self, oldItem, newItem):
        if newItem.groupID in const.sovereigntyClaimStructuresGroups:
            self.LoadSovereigntyStructures()

    def LoadDungeons(self):
        self.ClearBrackets('__dungeonbracket', 'dg_')
        if not eve.session.solarsystemid:
            return
        escalatingPath = sm.GetService('dungeonTracking').GetEscalatingPathDungeonsEntered()
        knownDungeons = sm.GetService('dungeonTracking').GetDistributionDungeonsEntered()
        self._LoadDungeons(escalatingPath)
        self._LoadDungeons(knownDungeons)

    def _LoadDungeons(self, data):
        solarsystem = self.GetCurrentSolarSystem()
        if solarsystem is None:
            return
        if not data:
            return
        bracketWnd = uicore.layer.systemMapBrackets
        for each in data:
            panel = SimpleBracket()
            bracketWnd.children.insert(0, panel)
            panel.name = '__dungeonbracket'
            panel.align = uiconst.NOALIGN
            panel.state = uiconst.UI_NORMAL
            panel.dock = 0
            panel.minDispRange = 0.0
            panel.maxDispRange = 1e+32
            panel.inflight = False
            panel.color = None
            panel.invisible = False
            panel.fadeColor = False
            tf = trinity.EveTransform()
            tf.name = 'dg_%s_%s' % (repr(each.name), getattr(each, 'ballID', -1))
            solarsystem.children.append(tf)
            panel.trackTransform = tf
            tf.translation = (each.x, each.y, each.z)
            panel.displayName = each.name
            panel.Startup(tf.name, None, None, 'ui_38_16_14')
            panel.sr.icon.SetAlign(uiconst.CENTER)
            panel.ShowBubble(each.name)
            panel.showLabel = 0

        self.SortBubbles()

    def GetBubbleHint(self, itemID, slimItem = None, mapData = None, bracket = None, extended = 0):
        if extended and getattr(bracket, 'expandedHint', None):
            return bracket.expandedHint
        if not extended and getattr(bracket, 'collapsedHint', None):
            return bracket.collapsedHint
        if eve.session.solarsystemid and slimItem is None:
            slimItem = sm.GetService('michelle').GetItem(itemID)
        if slimItem is None and mapData is None:
            mapData = self.map.GetItem(itemID)
            if mapData is None:
                return ''
        typeID = None
        groupID = None
        orbitID = None
        hint = []
        if slimItem:
            groupID = slimItem.groupID
            typeID = slimItem.typeID
            displayName = uix.GetSlimItemName(slimItem)
        if mapData:
            displayName = mapData.itemName
            if groupID is None:
                if hasattr(mapData, 'groupID'):
                    groupID = mapData.groupID
                else:
                    groupID = evetypes.GetGroupID(mapData.typeID)
            if hasattr(mapData, 'orbitID'):
                orbitID = mapData.orbitID
            typeID = mapData.typeID
        if groupID is None:
            return hint
        ball = None
        transform = None
        if bracket:
            ball = bracket.trackBall or getattr(bracket.sr, 'trackBall', None)
            transform = bracket.trackTransform
        if groupID == const.groupStation:
            displayName = self.map.GetStation(itemID).stationName
            displayName = uix.EditStationName(displayName, usename=1)
        hint.append(('<b>' + displayName + '</b>', ('OnClick', 'ShowInfo', (typeID, itemID))))
        import maputils
        if groupID == const.groupSolarSystem:
            ss = self.map.GetSecurityStatus(itemID)
            if ss is not None:
                hint.append(localization.GetByLabel('UI/Map/StarMap/hintSecurityStatus', level=ss))
        else:
            distance = maputils.GetDistance(slimItem, mapData, ball, transform)
            if distance is not None:
                hint.append(localization.GetByLabel('UI/Map/StarMap/lblDistance', distance=util.FmtDist(distance)))
        if extended:
            if groupID == const.groupBeacon:
                if eve.session.solarsystemid:
                    beacon = sm.GetService('michelle').GetItem(itemID)
                    if beacon and hasattr(beacon, 'dunDescriptionID') and beacon.dunDescriptionID:
                        desc = localization.GetByMessageID(beacon.dunDescriptionID)
                        hint.append(desc)
            elif groupID in const.sovereigntyClaimStructuresGroups:
                if eve.session.solarsystemid:
                    stateName, stateTimestamp, stateDelay = sm.GetService('pwn').GetStructureState(slimItem)
                    hint.append(POS_STRUCTURE_STATE[stateName])
            elif groupID == const.groupSolarSystem:
                labelPathDict = {const.groupCharacter: 'UI/Common/Groups/CountedGroupCharacter',
                 const.groupDecorations: 'UI/Common/Groups/CountedGroupDecorations',
                 const.groupConstellation: 'UI/Common/Groups/CountedGroupConstellation',
                 const.groupAsteroidBelt: 'UI/Common/Groups/CountedGroupAsteroidBelt',
                 const.groupStargate: 'UI/Common/Groups/CountedGroupStargate',
                 const.groupClone: 'UI/Common/Groups/CountedGroupClone',
                 const.groupRegion: 'UI/Common/Groups/CountedGroupRegion',
                 const.groupStation: 'UI/Common/Groups/CountedGroupStation',
                 const.groupMoon: 'UI/Common/Groups/CountedGroupMoon',
                 const.groupBooster: 'UI/Common/Groups/CountedGroupBooster',
                 const.groupFaction: 'UI/Common/Groups/CountedGroupFaction',
                 const.groupSolarSystem: 'UI/Common/Groups/CountedGroupSolarSystem',
                 const.groupAlliance: 'UI/Common/Groups/CountedGroupAlliance',
                 const.groupCorporation: 'UI/Common/Groups/CountedGroupCorporation',
                 const.groupSilo: 'UI/Common/Groups/CountedGroupSilo',
                 const.groupSecondarySun: 'UI/Common/Groups/CountedGroupSecondarySun'}
                hint.append('<dotline>')
                groups, ssData = self.GetSolarsystemHierarchy(itemID, (const.groupPlanet,))
                for id, orbits in groups.iteritems():
                    planet = ssData[id]
                    hint.append((localization.GetByLabel('UI/Map/StarMap/PlanetName', planet=planet.itemID), ('OnClick', 'ShowInfo', (planet.typeID, planet.itemID))))
                    byGroup = {}
                    for orbit in orbits:
                        _groupID = evetypes.GetGroupID(orbit.typeID)
                        if _groupID not in byGroup:
                            byGroup[_groupID] = []
                        byGroup[_groupID].append(orbit)

                    groupEntries = []
                    for _groupID, orbits in byGroup.iteritems():
                        if _groupID not in (const.groupStation, const.groupStargate, const.groupSecondarySun):
                            labelName = labelPathDict.get(_groupID)
                            groupEntries.append(localization.GetByLabel(labelName, amount=len(orbits)))

                    if len(groupEntries):
                        hint.append(localization.formatters.FormatGenericList(groupEntries))
                    for station in byGroup.get(const.groupStation, []):
                        itemName = self.map.GetStation(station.itemID).stationName
                        hint.append((uix.EditStationName(itemName, usename=1), ('OnMouseEnter', 'ShowSubhint', ('GetBubbleHint', (station.itemID,
                            None,
                            station,
                            None,
                            1)))))

                    for stargate in byGroup.get(const.groupStargate, []):
                        hint.append((stargate.itemName, ('OnClick', 'ShowInfo', (stargate.typeID, stargate.itemID))))

                    hint.append('<dotline>')

                hint = hint[:-1]
            elif groupID == const.groupStation:
                services = []
                stationInfo, opservices, _services = sm.GetService('ui').GetStation(itemID, 1)
                opservDict = {}
                for each in opservices:
                    if each.operationID not in opservDict:
                        opservDict[each.operationID] = []
                    opservDict[each.operationID].append(each.serviceID)

                for info in stationServiceConst.serviceData:
                    for bit in info.serviceIDs:
                        if bit == const.stationServiceNavyOffices and not self.facwar.CheckOwnerInFaction(stationInfo.ownerID):
                            continue
                        if bit == const.stationServiceSecurityOffice and not self.securityOfficeSvc.CanAccessServiceInStation(itemID):
                            continue
                        if bit in opservDict[stationInfo.operationID]:
                            services.append(info.label)
                            break

                if services:
                    services = localization.util.Sort(services)
                    hint.append('<dotline>')
                    hint.append((localization.GetByLabel('UI/Map/StarMap/ServicesCaption'), ('OnMouseEnter', 'ShowSubhint', (services,))))
                agentsByStationID = sm.GetService('agents').GetAgentsByStationID()
                agentByStation = {}
                for agent in agentsByStationID[itemID]:
                    if agent.agentTypeID in (const.agentTypeBasicAgent, const.agentTypeResearchAgent, const.agentTypeFactionalWarfareAgent) and agent.stationID:
                        if agent.stationID not in agentByStation:
                            agentByStation[agent.stationID] = []
                        agentByStation[agent.stationID].append(agent)

                agents = []
                if itemID in agentByStation:
                    npcDivisions = sm.GetService('agents').GetDivisions()
                    agentsAtStation = agentByStation[itemID]
                    for agent in agentsAtStation:
                        agentsub = []
                        agentsub.append(localization.GetByLabel('UI/Map/StarMap/DivisionName', divisionName=npcDivisions[agent.divisionID].divisionName))
                        agentsub.append(localization.GetByLabel('UI/Map/StarMap/AgentLevel', agentLevel=uiutil.GetLevel(agent.level)))
                        isLimitedToFacWar = False
                        if agent.agentTypeID == const.agentTypeFactionalWarfareAgent and self.facwar.GetCorporationWarFactionID(agent.corporationID) != session.warfactionid:
                            isLimitedToFacWar = True
                        if agent.agentTypeID in (const.agentTypeResearchAgent,
                         const.agentTypeBasicAgent,
                         const.agentTypeEventMissionAgent,
                         const.agentTypeCareerAgent,
                         const.agentTypeFactionalWarfareAgent) and sm.GetService('standing').CanUseAgent(agent.factionID, agent.corporationID, agent.agentID, agent.level, agent.agentTypeID) and isLimitedToFacWar == False:
                            agentsub.append(localization.GetByLabel('UI/Map/StarMap/AvailableToYou'))
                        else:
                            agentsub.append(localization.GetByLabel('UI/Map/StarMap/NotAvailableToYou'))
                        agents.append((cfg.eveowners.Get(agent.agentID).name, ('OnMouseEnter', 'ShowSubhint', (agentsub,))))

                if agents:
                    hint.append('<dotline>')
                    hint.append((localization.GetByLabel('UI/Map/StarMap/AgentsCaption'), ('OnMouseEnter', 'ShowSubhint', (agents,))))
                myassets = sm.GetService('assets').GetAll('sysitems', blueprintOnly=0, isCorp=0)
                for solarsystemID, station in myassets:
                    if station.stationID == itemID:
                        hint.append('<dotline>')
                        hint.append((localization.GetByLabel('UI/Map/StarMap/MyAssetsCount', amount=station.itemCount), ('OnClick', 'OpenAssets', (station.stationID,))))

                try:
                    if (const.corpRoleAccountant | const.corpRoleJuniorAccountant) & eve.session.corprole == 1:
                        corpassets = sm.GetService('assets').GetAll('sysitems', blueprintOnly=0, isCorp=1)
                        for solarsystemID, station in myassets:
                            if station.stationID == itemID:
                                hint.append('<dotline>')
                                hint.append(localization.GetByLabel('UI/Map/StarMap/MyAssetsCount', amount=station.itemCount))

                except RuntimeError as what:
                    if what.args[0] != 'NotSupported':
                        log.LogException()
                    sys.exc_clear()

                officeData = sm.RemoteSvc('config').GetMapOffices(stationInfo.solarSystemID)
                offices = []
                for office in officeData:
                    if office.stationID == itemID:
                        offices.append((cfg.eveowners.Get(office.corporationID).name, ('OnClick', 'ShowInfo', (const.groupCorporation, office.corporationID))))

                if offices:
                    hint.append('<dotline>')
                    hint.append((localization.GetByLabel('UI/Map/StarMap/OfficesCaption'), ('OnMouseEnter', 'ShowSubhint', (offices,))))
        return hint

    def CollapseBubbles(self, ignore = []):
        bracketWnd = uicore.layer.systemMapBrackets
        for bracket in bracketWnd.children[:]:
            if getattr(bracket, 'IsBracket', 0) and getattr(bracket.sr, 'bubble', None) is not None:
                if bracket in ignore:
                    continue
                bracket.sr.bubble.ClearSubs()
                self._ExpandBubbleHint(bracket.sr.bubble, 0)

        self.expandingHint = 0

    def ExpandBubbleHint(self, bubble, expand = 1):
        if self.expandingHint:
            return
        uthread.new(self._ExpandBubbleHint, bubble, expand)

    def _ExpandBubbleHint(self, bubble, expand = 1):
        bracket = bubble.parent
        if not bracket:
            return
        if not expand and util.GetAttrs(bubble, 'sr', 'CollapseCleanup'):
            force = bubble.sr.CollapseCleanup(bracket)
        else:
            force = False
        if bubble.destroyed:
            return
        if not force and expand == bubble.expanded:
            return
        if expand:
            uiutil.SetOrder(bracket, 0)
            blue.pyos.synchro.Yield()
            self.CollapseBubbles([bracket])
        self.expandingHint = id(bracket)
        hint = self.GetBubbleHint(bracket.itemID, getattr(bracket, 'slimItem', None), bracket=bracket, extended=expand)
        if bubble.destroyed:
            return
        currentHint, pointer = bubble.data
        if hint != currentHint:
            bubble.ShowHint(hint, pointer)
        bubble.expanded = expand
        self.expandingHint = 0

    def SortBubbles(self, ignore = []):
        last = getattr(self, 'lastBubbleSort', None)
        if last and blue.os.TimeDiffInMs(last, blue.os.GetWallclockTime()) < 500:
            return
        bracketWnd = uicore.layer.systemMapBrackets
        order = []
        cameraParent = sm.GetService('sceneManager').GetRegisteredCamera(evecamera.CAM_SYSTEMMAP).GetCameraParent()
        if cameraParent is None:
            return
        camPos = cameraParent.translation
        for bracket in bracketWnd.children:
            if getattr(bracket, 'IsBracket', 0) and getattr(bracket, 'trackTransform', None) is not None and getattr(bracket.sr, 'bubble', None) is not None:
                bracketPos = geo2.Vector(*bracket.trackTransform.translation)
                order.append((geo2.Vec3LengthSq(camPos - bracketPos), bracket))

        order = uiutil.SortListOfTuples(order)
        order.reverse()
        for bracket in order:
            uiutil.SetOrder(bracket, 0)

        self.lastBubbleSort = blue.os.GetWallclockTime()

    def GetCurrentSolarSystem(self):
        return self.currentSolarsystem

    def GetSolarsystemData(self, ssid):
        self.ssitems = self.ssitems or {}
        if ssid not in self.ssitems:
            self.ssitems[ssid] = self.map.GetSolarsystemItems(ssid)
        return self.ssitems[ssid]

    def DrawSolarSystem(self, ssid):
        ssitems = self.GetSolarsystemData(ssid)
        parent = trinity.EveTransform()
        parent.name = 'solarsystem_%s' % ssid
        orbits = []
        objects = {}
        sunID = None
        pm = (const.groupPlanet, const.groupMoon)
        for each in ssitems:
            if each.itemID == each.locationID:
                continue
            groupID = evetypes.GetGroupID(each.typeID)
            if groupID == const.groupSecondarySun:
                continue
            transform = trinity.EveTransform()
            if groupID in pm:
                parentID = self.FindCelestialParent(each, ssitems)
                orbits.append([each.itemID, parentID])
            elif groupID == const.groupSun:
                sunID = each.itemID
            pos = geo2.Vector(each.x, each.y, each.z)
            transform.translation = pos
            transform.name = str(each.itemID)
            parent.children.append(transform)
            objects[each.itemID] = transform

        for childID, parentID in orbits:
            if childID in objects and parentID in objects:
                self.Add3DCircle(objects[childID], objects[parentID])

        cfg.evelocations.Prime(objects.keys(), 0)
        self.orbitLineSet.SubmitChanges()
        return (parent, sunID)

    def FindCelestialParent(self, body, ssitems):
        bodyPos = geo2.Vector(body.x, body.y, body.z)
        planets = []
        groupID = evetypes.GetGroupID(body.typeID)
        if groupID == const.groupPlanet or groupID == const.groupStargate:
            for object in ssitems:
                typeinfo2 = evetypes.GetGroupID(object.typeID)
                if typeinfo2 == const.groupSun:
                    return object.itemID

        for each in ssitems:
            if each.itemID == body.itemID:
                continue
            if evetypes.GetGroupID(each.typeID) != const.groupPlanet:
                continue
            pos = geo2.Vector(each.x, each.y, each.z)
            diffPos = pos - bodyPos
            planets.append([geo2.Vec3Length(diffPos), each])

        planets.sort()
        return planets[0][1].itemID

    def Add3DCircle(self, orbitem, parent, points = 256):
        orbitPos = geo2.Vector(*orbitem.translation)
        parentPos = geo2.Vector(*parent.translation)
        dirVec = orbitPos - parentPos
        radius = geo2.Vec3Length(dirVec)
        if radius == 0:
            return
        fwdVec = geo2.Vector(-1.0, 0.0, 0.0)
        dirVec = geo2.Vec3Normalize(dirVec)
        fwdVec = geo2.Vec3Normalize(fwdVec)
        color = (0.3, 0.3, 0.3, 1.0)
        stepSize = pi * 2.0 / points
        lineSet = self.orbitLineSet
        rotation = geo2.QuaternionRotationArc(fwdVec, dirVec)
        matrix = geo2.MatrixAffineTransformation(1.0, geo2.Vector(0.0, 0.0, 0.0), rotation, geo2.Vector(*parent.translation))
        coordinates = []
        for step in range(points):
            angle = step * stepSize
            x = cos(angle) * radius
            z = sin(angle) * radius
            pos = geo2.Vector(x, 0.0, z)
            pos = geo2.Vec3TransformCoord(pos, matrix)
            coordinates.append(pos)

        for start in xrange(points):
            end = (start + 1) % points
            lineSet.AddLine(coordinates[start], color, coordinates[end], color)

    def OnBracketDoubleClick(self, _bracket, *args):
        if _bracket.itemID is not None:
            sm.GetService('viewState').GetView('systemmap').layer.SetInterest(_bracket.itemID)


class BookmarkBracket(SimpleBracket):
    __guid__ = 'xtriui.BookmarkBracket'

    def Startup(self, bookmark, showBubbleHint):
        if bookmark.ownerID == session.corpid:
            iconNo = 'ui_38_16_257'
        else:
            iconNo = 'ui_38_16_150'
        itemID = ('bookmark', bookmark.bookmarkID)
        caption, note = sm.GetService('addressbook').UnzipMemo(bookmark.memo)
        self.displayName = localization.GetByLabel('UI/Map/StarMap/hintSystemBookmark', memo=caption)
        self.bmData = bookmark
        if showBubbleHint:
            myPos = maputils.GetMyPos()
            distance = (trinity.TriVector(*self.trackTransform.translation) - myPos).Length()
            self.ShowBubble([localization.GetByLabel('UI/Map/StarMap/lblBoldName', name=caption), localization.GetByLabel('UI/Map/StarMap/lblDistance', distance=util.FmtDist(distance))])
        xtriui.SimpleBracket.Startup(self, itemID, None, None, iconNo)

    def GetMenu(self, *args):
        bmData = getattr(self, 'bmData', None)
        if bmData is not None:
            m = sm.GetService('menu').CelestialMenu(bmData.itemID, bookmark=bmData)
            m.append((uiutil.MenuLabel('UI/Map/StarMap/EditViewLocation'), sm.GetService('addressbook').EditBookmark, (bmData,)))
            return m

    def OnMouseDown(self, *args):
        bookMarkInfo = getattr(self, 'bmData', None)
        if bookMarkInfo is None:
            return
        sm.GetService('menu').TryExpandActionMenu(itemID=bookMarkInfo.itemID, clickedObject=self, bookmarkInfo=bookMarkInfo)

    def GetRadialMenuIndicator(self, create = True, *args):
        radialMenuSprite = getattr(self, 'radialMenuSprite', None)
        if radialMenuSprite and not radialMenuSprite.destroyed:
            return radialMenuSprite
        if not create:
            return
        radialMenuSprite = uiprimitives.Sprite(name='radialMenuSprite', parent=self, texturePath='res:/UI/Texture/classes/RadialMenu/bracketHilite.png', pos=(0, 0, 20, 20), color=(0.5, 0.5, 0.5, 0.5), idx=-1, align=uiconst.CENTER)
        self.radialMenuSprite = radialMenuSprite
        return radialMenuSprite

    def ShowRadialMenuIndicator(self, slimItem, *args):
        mySprite = self.GetRadialMenuIndicator(create=True)
        mySprite.display = True

    def HideRadialMenuIndicator(self, slimItem, *args):
        mySprite = self.GetRadialMenuIndicator(create=False)
        if mySprite:
            mySprite.display = False
