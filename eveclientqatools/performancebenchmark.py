#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\eveclientqatools\performancebenchmark.py
import blue
import math
import trinity
import uthread
import geo2
import uicontrols
import carbonui.const as uiconst
from carbonui.control.slider import Slider
from carbonui.primitives.sprite import Sprite
from carbonui.util.color import Color
from eve.client.script.ui.control.eveWindow import Window
from carbonui.primitives.container import Container
from eve.client.script.ui.control.eveLabel import Label
from eve.client.script.ui.control.eveCombo import Combo
from eve.client.script.ui.control.checkbox import Checkbox
from eve.client.script.ui.control.buttons import Button
from eve.client.script.ui.control.eveSinglelineEdit import SinglelineEdit
from eve.client.script.ui.control.eveLabel import EveHeaderSmall
from eve.client.script.ui.control.eveEdit import Edit
from eve.client.script.ui.control.gauge import Gauge
from eve.client.script.ui.util.uix import TextBox
from .performancebenchmarkdata import *
import pychartdir as chart
chart.setLicenseCode('DIST-0000-05de-f7ec-ffbeURDT-232Q-M544-C2XM-BD6E-C452')
BENCHMARK_MAX_DURATION_IN_MS = 600000.0
BENCHMARK_DEFAULT_DURATION_IN_MS = 30000.0
MIN_PAN_DISTANCE = 0
MAX_PAN_DISTANCE = 1000000

def ClampPan(pan):
    return min(MAX_PAN_DISTANCE, max(pan, MIN_PAN_DISTANCE))


class SceneDirector(object):

    def __init__(self):
        self.slash = sm.GetService('slash').SlashCmd
        self.initialSceneState = set([])

    def SetCamera(self, yaw, pitch, pan):
        cam = sm.GetService('sceneManager').GetActiveCamera()
        cam.SetYaw(math.radians(yaw))
        cam.SetPitch(math.radians(pitch))
        pan = ClampPan(pan)
        newPos = geo2.Vec3Add(geo2.Vec3Scale(cam.GetLookAtDirection(), pan), cam.GetAtPosition())
        cam.TransitTo(atPosition=cam.GetAtPosition(), eyePosition=newPos)

    def GoToAndReturnStartPosition(self, stayHere):
        bp = sm.GetService('michelle').GetBallpark()
        if stayHere:
            startPos = bp.GetCurrentEgoPos()
        else:
            startPos = (2500000000000.0, 0.0, 0.0)
            self.slash('/tr me pos=%s,%s,%s' % (startPos[0], startPos[1], startPos[2]))
        return startPos

    def SpawnTestcase(self, testID, startPos):
        self._SpawnShips(startPos, TEST_CASES[testID])

    def _SpawnShips(self, startPos, testCase):
        scene = sm.GetService('sceneManager').GetRegisteredScene('default')
        self.initialSceneState = set(scene.objects)
        yCount = 0
        xPos = startPos[0]
        for cntr in xrange(testCase.number_of_rows ** 2):
            typeId = testCase.ship_list[cntr % len(testCase.ship_list)]
            if yCount >= testCase.number_of_rows:
                xPos += testCase.distance_between_ships
                yCount = 0
            for zCount in xrange(testCase.number_of_rows):
                self.slash('/spawn %s pos=%s,%s,%s' % (typeId,
                 xPos,
                 yCount * testCase.distance_between_ships + startPos[1],
                 zCount * testCase.distance_between_ships + startPos[2]))

            yCount += 1

    def ClearAll(self, *args):
        scene = sm.GetService('sceneManager').GetRegisteredScene('default')
        ids = []
        for each in scene.objects:
            if each.__bluetype__ != 'trinity.EveShip2':
                continue
            ball = each.translationCurve
            if ball.id != session.shipid:
                ids.append(ball.id)

        for bid in ids:
            self.slash('/unspawn %s' % str(bid))

    def ApplyDamage(self, *args):
        scene = sm.GetService('sceneManager').GetRegisteredScene('default')
        additions = set(scene.objects) - self.initialSceneState
        for each in additions:
            if each.name.startswith('10000'):
                self.slash('/heal %s 0.5' % each.name)


class PerformanceBenchmarkWindow(Window):
    default_caption = 'Performance Tools'
    default_windowID = 'PerformanceToolsWindowID'
    default_width = 220
    default_height = 200
    default_topParentHeight = 0
    default_minSize = (default_width, default_height)
    default_wontUseThis = 10

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.lastPitch = 0.0
        self.lastYaw = 0.0
        self.camLock = False
        self.benchmarkDuration = BENCHMARK_DEFAULT_DURATION_IN_MS
        self.benchmarkRunning = False
        self.sceneDirector = SceneDirector()
        self.testOptions = [('classic cube of death', CUBE_CLASSIC),
         ('capital wrecks of death', CUBE_CAPITAL_WRECKS),
         ('AmarrCube', CUBE_AMARR),
         ('CaldariCube', CUBE_CALDARI),
         ('GallenteCube', CUBE_GALLENTE),
         ('MinmatarCube', CUBE_MINMATAR),
         ('UltraLODCube', CUBE_LOD),
         ('Add More Here', CUBE_ADD_MORE_HERE)]
        self.testCaseDescription = {CUBE_CLASSIC: 'Spawns a cube with a lot of different ships.',
         CUBE_CAPITAL_WRECKS: 'Spawns a cube with a lot of wrecks.',
         CUBE_AMARR: 'Spawns a cube of Amarr ships.',
         CUBE_CALDARI: 'Spawns a cube of Caldari ships.',
         CUBE_GALLENTE: 'Spawns a cube of Gallente ships.',
         CUBE_MINMATAR: 'Spawns a cube of Minmatar ships.',
         CUBE_LOD: 'Spawns a cube of ships around the camera.',
         CUBE_ADD_MORE_HERE: 'Does nothing useful.'}
        self.camPresetOptions = [('None', CAMERA_PRESET_NONE),
         ('Deathcube Far', CAMERA_PRESET_FAR),
         ('Deathcube Near', CAMERA_PRESET_NEAR),
         ('Deathcube UltraLOD', CAMERA_PRESET_ULTRA_LOD)]
        self._AddHeader('Test Cases')
        self._SetupTestCasePanel(self.sr.main)
        self._AddHeader('Camera')
        self._SetupCameraPanel(self.sr.main)
        self._AddHeader('Duration')
        self._SetupDurationPanel(self.sr.main)
        self.benchmarkButton = Button(name='myButton', parent=self.sr.main, align=uiconst.CENTERBOTTOM, label='Start Benchmark', func=self.ToggleBenchmark, width=40, padding=(0, 0, 0, 6))

    def _AddHeader(self, text):
        EveHeaderSmall(parent=self.sr.main, text=text, align=uiconst.TOTOP, padding=(8, 6, 0, 3))

    def _SetupTestCasePanel(self, mainCont):
        cont = Container(name='cont', parent=mainCont, align=uiconst.TOTOP, padLeft=4, padRight=4, height=40)
        self.testCombo = Combo(parent=cont, align=uiconst.TOTOP, options=self.testOptions, callback=self.TestComboChanged)
        self.testCombo.SetHint(self.testCaseDescription[1])
        buttonBox = Container(name='buttonBox', parent=cont, align=uiconst.TOTOP, padTop=3, height=20)
        self.stayHereCheckbox = Checkbox(parent=buttonBox, text=u'Stay where you are', align=uiconst.TOLEFT, checked=False, height=18, width=120)
        Button(parent=buttonBox, label='Spawn', align=uiconst.TORIGHT, func=self.SpawnTestcase, width=40, height=18)
        Button(parent=buttonBox, label='Clear', align=uiconst.TORIGHT, func=self.sceneDirector.ClearAll, width=40, height=18)
        Button(parent=buttonBox, label='Damage', align=uiconst.TORIGHT, func=self.sceneDirector.ApplyDamage, width=40, height=18, hint='Wait for ships to load before calling this')

    def _SetupCameraPanel(self, mainCont):
        presetCont = Container(name='presetCont', parent=mainCont, align=uiconst.TOTOP, height=20, padLeft=4, padRight=4)
        Label(name='presetCombo', parent=presetCont, align=uiconst.TOLEFT, width=40, text='Preset')
        self.cboCamPresets = Combo(parent=presetCont, align=uiconst.TOTOP, options=self.camPresetOptions, callback=self.OnCamPreset)
        pitchCont = Container(name='pitchCont', parent=mainCont, align=uiconst.TOTOP, height=20, padLeft=4, padRight=4)
        Label(name='pitchLabel', parent=pitchCont, align=uiconst.TOLEFT, width=40, padTop=3, text='Pitch')
        self.pitchField = SinglelineEdit(name='pitchField', parent=pitchCont, align=uiconst.TOTOP, floats=[-90.0, 90.0, 1], setvalue=str(self.lastPitch))
        self.pitchField.OnChange = self.OnCamChange
        yawCont = Container(name='yawCont', parent=mainCont, align=uiconst.TOTOP, height=20, padLeft=4, padRight=4)
        Label(name='yawLabel', parent=yawCont, align=uiconst.TOLEFT, width=40, padTop=3, text='Yaw')
        self.yawField = SinglelineEdit(name='yawField', parent=yawCont, align=uiconst.TOTOP, floats=[-180.0, 180.0, 1], setvalue=str(self.lastYaw))
        self.yawField.OnChange = self.OnCamChange
        panCont = Container(name='panCont', parent=mainCont, align=uiconst.TOTOP, height=20, padLeft=4, padRight=4)
        Label(name='panLabel', parent=panCont, align=uiconst.TOLEFT, width=40, padTop=3, text='Pan')
        self.panField = SinglelineEdit(name='panField', parent=panCont, align=uiconst.TOTOP, ints=[MIN_PAN_DISTANCE, MAX_PAN_DISTANCE], setvalue=0)
        self.panField.OnChange = self.OnCamChange
        buttonBox = Container(name='buttonBox', parent=mainCont, align=uiconst.TOTOP, padTop=3, height=20)
        Button(parent=buttonBox, label='Capture camera coords', align=uiconst.TORIGHT, func=self.OnStoreCurrentCameraValues, width=40, height=18, hint='Captures the current camera coordinates and saves them in the input fields')
        uthread.new(self._GetCurrentCameraValues)

    def _SetupDurationPanel(self, parent):
        maxSeconds = int(BENCHMARK_MAX_DURATION_IN_MS / 1000)
        defaultSeconds = int(BENCHMARK_DEFAULT_DURATION_IN_MS / 1000)
        self.durationSlider = Slider(name='mySlider', parent=parent, minValue=1, maxValue=maxSeconds, startVal=defaultSeconds, increments=[ i + 1 for i in xrange(maxSeconds) ], onsetvaluefunc=self._OnTimeChanged, align=uiconst.TOTOP, padLeft=10, padRight=10)
        self.progress = Gauge(name='progress', parent=parent, color=Color.WHITE, align=uiconst.TOTOP, padTop=20, padLeft=10, padRight=10)
        self._OnTimeChanged(self.durationSlider)

    def _OnTimeChanged(self, slider):
        self.benchmarkDuration = slider.GetValue() * 1000

    def TestComboChanged(self, *args):
        self.testCombo.SetHint(self.testCaseDescription[self.testCombo.GetValue()])

    def OnCamChange(self, *args):
        if self.camLock:
            return
        self.lastPitch = float(self.pitchField.GetValue())
        self.lastYaw = float(self.yawField.GetValue())
        self.pan = int(self.panField.GetValue())
        self.sceneDirector.SetCamera(self.lastYaw, self.lastPitch, self.pan)

    def OnCamPreset(self, *args):
        presId = self.cboCamPresets.GetValue()
        if presId == 0:
            return
        pitch, yaw, pan = CAMERA_PRESETS[presId]
        self.camLock = True
        self.pitchField.SetValue(pitch)
        self.yawField.SetValue(yaw)
        self.panField.SetValue(pan)
        self.camLock = False
        self.OnCamChange()

    def _GetMemoryUsage(self):
        try:
            meg = 1.0 / 1024.0 / 1024.0
            mem, pymem, workingset, pagefaults, bluemem = blue.pyos.cpuUsage[-1][2]
            return mem * meg
        except:
            pass

        return 0

    def ToggleBenchmark(self, *args):
        self.progress.SetValue(0)

        def _thread():
            frameTimes = []
            graphData = {}
            t0 = blue.os.GetWallclockTime()
            startTime = blue.os.GetWallclockTime()
            startMem = self._GetMemoryUsage()
            while self.benchmarkRunning:
                blue.synchro.Yield()
                t1 = blue.os.GetWallclockTime()
                ms = float(blue.os.TimeDiffInUs(t0, t1)) / 1000.0
                t0 = t1
                frameTimes.append(ms)
                timeFromStartInMs = float(blue.os.TimeDiffInUs(startTime, t1)) / 1000.0
                graphData[timeFromStartInMs] = ms
                if blue.os.TimeDiffInMs(startTime, t1) > self.benchmarkDuration:
                    self.benchmarkRunning = False
                    break
                self.progress.SetValue(timeFromStartInMs / self.benchmarkDuration, animate=False)

            frameTimes.sort()
            median = frameTimes[len(frameTimes) / 2]
            minMS = frameTimes[0]
            maxMS = frameTimes[-1]
            summed = reduce(lambda x, y: x + y, frameTimes)
            avg = summed / len(frameTimes)
            result = 'Min: %0.1fms Max: %0.1fms\n' % (minMS, maxMS)
            result += 'Median:  %0.1fms %0.1ffps\n' % (median, 1000.0 / median)
            result += 'Average: %0.1fms %0.1ffps\n' % (avg, 1000.0 / avg)
            endMem = self._GetMemoryUsage()
            result += 'Start Memory Usage: %0.1fmb\n' % (startMem,)
            result += 'End Memory Usage: %0.1fmb\n' % (endMem,)
            ResultDialog.Open(resultText=result, graphData=graphData)
            self.benchmarkButton.SetLabel('Start Benchmark')

        if self.benchmarkRunning:
            self.benchmarkRunning = False
        else:
            self.benchmarkRunning = True
            self.benchmarkButton.SetLabel('Stop Benchmark')
            uthread.new(_thread)

    def OnStoreCurrentCameraValues(self, *args):
        self._GetCurrentCameraValues()

    def _GetCurrentCameraValues(self):
        self.camLock = True
        cam = sm.GetService('sceneManager').GetActiveCamera()
        self.lastPitch = math.degrees(cam.pitch)
        self.lastYaw = math.degrees(cam.yaw)
        self.pan = pan = ClampPan(int(cam.GetZoomDistance()))
        self.pitchField.SetValue(self.lastPitch)
        self.yawField.SetValue(self.lastYaw)
        self.panField.SetValue(self.pan)
        self.camLock = False
        self.OnCamChange()

    def SpawnTestcase(self, *args):
        testID = self.testCombo.GetValue()
        stayHere = self.stayHereCheckbox.GetValue()
        startPos = self.sceneDirector.GoToAndReturnStartPosition(stayHere)
        self.sceneDirector.SpawnTestcase(testID, startPos)


class ResultDialog(Window):
    default_width = 500
    default_height = 500
    default_topParentHeight = 0

    def __init__(self, **kw):
        self.resultText = None
        self.graphData = None
        self.graphContainer = None
        self.resultContainer = None
        super(ResultDialog, self).__init__(**kw)

    def ApplyAttributes(self, *args):
        super(ResultDialog, self).ApplyAttributes(*args)
        self.graphData = args[0].get('graphData', {})
        self.resultText = args[0].get('resultText', '')
        self.resultContainer = Container(name='resultContainer', parent=self.sr.main, align=uiconst.TOBOTTOM, width=self.width, height=self.height / 4.0)
        Edit(name='resultText', parent=self.resultContainer, align=uiconst.TOALL, setvalue=self.resultText.replace('\n', '<br>'), readonly=True)
        self.graphContainer = Container(name='graphContainer', parent=self.sr.main, align=uiconst.TOTOP, width=self.width, height=3.0 * self.height / 4.0)
        self.CreateGraph(self.graphData, self.graphContainer)

    def CreateGraph(self, data, parent):
        l = [ (k, v) for k, v in data.iteritems() ]
        l.sort(key=lambda x: x[0])
        yData = [ x[1] for x in l ]
        xData = [ '%.1fs' % (x[0] / 1000.0) for x in l ]
        fontSize = 7.5
        fontFace = 'arial.ttc'
        width = parent.width
        height = int(parent.height * 0.4)
        c = chart.XYChart(width, height, bgColor=chart.Transparent)
        c.addTitle('Frametime in ms')
        c.setColors(chart.whiteOnBlackPalette)
        c.setBackground(chart.Transparent)
        c.setTransparentColor(-1)
        c.setAntiAlias(1, 1)
        offsX = 60
        offsY = 17
        canvasWidth = width - 1 * offsX - 50
        canvasHeight = height - offsY * 2.5
        c.setPlotArea(offsX, offsY, canvasWidth, canvasHeight, 1711276032, -1, -1, 5592405)
        c.addLegend(85, 18, 0, fontFace, fontSize).setBackground(chart.Transparent)
        c.addLineLayer(yData)
        c.yAxis().setTitle('ms')
        c.xAxis().setLabels(xData)
        c.xAxis().setLabelStep(len(data) / 5)
        buf = c.makeChart2(chart.PNG)
        hostBitmap = trinity.Tr2HostBitmap(width, height, 1, trinity.PIXEL_FORMAT.B8G8R8A8_UNORM)
        hostBitmap.LoadFromPngInMemory(buf)
        graphSprite = Sprite(parent=parent, align=uiconst.TOALL)
        graphSprite.texture.atlasTexture = uicore.uilib.CreateTexture(width, height)
        graphSprite.texture.atlasTexture.CopyFromHostBitmap(hostBitmap)
        return graphSprite
