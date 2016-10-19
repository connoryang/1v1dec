#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\crate\window.py
import blue
from carbonui import const as uiconst
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.primitives.container import Container
from carbonui.primitives.flowcontainer import FlowContainer
from carbonui.primitives.sprite import Sprite, StreamingVideoSprite
from carbonui.primitives.transform import Transform
from carbonui.primitives.vectorline import VectorLine
from carbonui.uianimations import animations
from carbonui.uicore import uicorebase as uicore
from carbonui.util import color
from eve.common.script.sys.eveCfg import IsApparel, IsBlueprint
from eve.client.script.ui import eveFontConst as fontConst
from eve.client.script.ui.control.buttons import Button
from eve.client.script.ui.control.eveIcon import Icon
from eve.client.script.ui.control.eveLabel import EveCaptionMedium, EveLabelMedium, EveStyleLabel
from eve.client.script.ui.control.eveWindow import Window
from eve.client.script.ui.control.themeColored import FillThemeColored, FrameThemeColored, GradientThemeColored
from eve.client.script.ui.control.tooltips import TooltipPersistentPanel
from eve.client.script.ui.control.pointerPanel import FadeOutPanelAndClose, RefreshPanelPosition
from eve.client.script.ui.crate.controller import LootController
from eve.client.script.ui.util import uix
import evetypes
import geo2
import itertools
import localization
import math
import random
import trinity
import uthread

class CrateWindow(Window):
    __guid__ = 'form.CrateWindow'
    default_fixedWidth = 800
    default_fixedHeight = 420
    default_width = 800
    default_height = 420
    default_windowID = 'CrateWindow'
    default_topParentHeight = 0
    default_clipChildren = False
    default_isCollapseable = False
    default_isPinable = False
    default_isStackable = False

    @classmethod
    def Open(cls, *args, **kwargs):
        wnd = cls.GetIfOpen()
        if not wnd:
            return cls(**kwargs)
        if not wnd.controller.isOpening:
            wnd.Close()
            return cls(**kwargs)
        wnd.Maximize()
        return wnd

    def ApplyAttributes(self, attributes):
        super(CrateWindow, self).ApplyAttributes(attributes)
        typeID = attributes.typeID
        itemID = attributes.itemID
        stacksize = attributes.stacksize
        self.controller = LootController(typeID, itemID, stacksize)
        self.hackingView = None
        self.Layout()
        self.controller.onOpen.connect(self.OnCrateOpen)
        self.controller.onFinish.connect(self.Close)
        uthread.new(self.AnimEntry)

    def Layout(self):
        self.HideHeader()
        self.SetCaption(self.controller.caption)
        self.splash = Splash(parent=self.GetMainArea(), align=uiconst.CENTERLEFT, pos=(120, 0, 1, 1), controller=self.controller)
        CrateDetailView(parent=self.GetMainArea(), align=uiconst.TOALL, padding=(380, 36, 24, 24), controller=self.controller)

    def OnCrateOpen(self):
        if self.hackingView:
            animations.FadeOut(self.hackingView, duration=0.2, callback=self.hackingView.Close)
        self.hackingView = HackingView(parent=self.GetMainArea(), align=uiconst.TOALL, controller=self.controller)
        uthread.new(self.hackingView.AnimEntry)

    def AnimEntry(self):
        self.splash.AnimEntry()

    def Prepare_Background_(self):
        self.sr.underlay = CrateWindowUnderlay(parent=self)


class CrateWindowUnderlay(Container):
    default_state = uiconst.UI_DISABLED

    def ApplyAttributes(self, attributes):
        super(CrateWindowUnderlay, self).ApplyAttributes(attributes)
        self.frame = FrameThemeColored(bgParent=self, colorType=uiconst.COLORTYPE_UIHILIGHTGLOW, texturePath='res:/UI/Texture/classes/ItemPacks/windowFrame.png', cornerSize=10, fillCenter=False, opacity=0.5)
        self.outerGlow = FrameThemeColored(bgParent=self, colorType=uiconst.COLORTYPE_UIHILIGHT, texturePath='res:/UI/Texture/classes/ItemPacks/boxGlow.png', cornerSize=5, offset=-2, opacity=0.0)
        self.underlay = GradientThemeColored(bgParent=self, padding=(1, 1, 1, 1), rgbData=[(0, (0.5, 0.5, 0.5))], alphaData=[(0, 0.0), (0.4, 0.9), (0.6, 1.0)], rotation=0)
        GradientThemeColored(parent=self, align=uiconst.TOTOP, height=1, alphaData=[(0, 0.0), (0.4, 0.08), (0.6, 0.1)], rotation=0, colorType=uiconst.COLORTYPE_UIHILIGHTGLOW)
        GradientThemeColored(parent=self, align=uiconst.TOBOTTOM, height=1, alphaData=[(0, 0.0), (0.4, 0.08), (0.6, 0.1)], rotation=0, colorType=uiconst.COLORTYPE_UIHILIGHTGLOW)
        FillThemeColored(parent=self, align=uiconst.TORIGHT, width=1, colorType=uiconst.COLORTYPE_UIHILIGHTGLOW, opacity=0.1)

    def AnimEntry(self):
        animations.FadeTo(self.frame, startVal=self.frame.opacity, endVal=1.0, duration=0.4, curveType=uiconst.ANIM_OVERSHOT3)
        animations.FadeTo(self.outerGlow, startVal=self.outerGlow.opacity, endVal=0.25, duration=0.4, curveType=uiconst.ANIM_OVERSHOT2)
        animations.FadeTo(self.underlay, startVal=self.underlay.opacity, endVal=1.0, duration=0.3, curveType=uiconst.ANIM_LINEAR)

    def AnimExit(self):
        animations.FadeTo(self.frame, startVal=self.frame.opacity, endVal=0.5, duration=0.6)
        animations.FadeTo(self.outerGlow, startVal=self.outerGlow.opacity, endVal=0.0, duration=0.6)
        animations.FadeTo(self.underlay, startVal=self.underlay.opacity, endVal=0.85, duration=0.3, curveType=uiconst.ANIM_LINEAR)

    def Pin(self):
        pass

    def UnPin(self):
        pass


class Splash(Container):

    def ApplyAttributes(self, attributes):
        super(Splash, self).ApplyAttributes(attributes)
        self.controller = attributes.controller
        self.flare = None
        self.Layout()
        self.controller.onOpen.connect(self.OnCrateOpen)

    def Layout(self):
        if self.controller.staticSplash:
            Sprite(parent=self, align=uiconst.TOPLEFT, left=-int(self.controller.staticSplash.width / 2.0), top=-int(self.controller.staticSplash.height / 2.0), texturePath=self.controller.staticSplash.resPath, width=self.controller.staticSplash.width, height=self.controller.staticSplash.height, color=self.controller.staticSplash.color or (1.0, 1.0, 1.0))
        if self.controller.animatedSplash:
            self.flare = StreamingVideoSprite(parent=self, align=uiconst.TOPLEFT, left=-int(self.controller.animatedSplash.width / 2.0), top=-int(self.controller.animatedSplash.height / 2.0), width=self.controller.animatedSplash.width, height=self.controller.animatedSplash.height, videoPath=self.controller.animatedSplash.resPath, videoLoop=True, blendMode=trinity.TR2_SBM_ADD, spriteEffect=trinity.TR2_SFX_COPY, color=self.controller.animatedSplash.color or (1.0, 1.0, 1.0), disableAudio=True)

    def AnimEntry(self):
        if self.flare:
            animations.FadeTo(self.flare, endVal=self.flare.opacity, duration=2.0)

    def OnCrateOpen(self):
        if self.flare:
            animations.FadeOut(self.flare)


class CrateDetailView(Container):

    def ApplyAttributes(self, attributes):
        super(CrateDetailView, self).ApplyAttributes(attributes)
        self.controller = attributes.controller
        self.Layout()
        self.controller.onOpen.connect(self.OnCrateOpen)

    def Layout(self):
        buttonCont = Container(parent=self, align=uiconst.TOBOTTOM, height=30)
        self.title = Transform(parent=self, align=uiconst.TOTOP, height=48)
        TitleLabel(parent=self.title, align=uiconst.TOPLEFT, padBottom=12, text=self.controller.caption)
        self.textScroll = ScrollContainer(parent=self, align=uiconst.TOALL, padBottom=8)
        EveLabelMedium(parent=self.textScroll, align=uiconst.TOTOP, text=self.controller.description)
        self.button = CrateButton(parent=buttonCont, align=uiconst.CENTER, label=center(localization.GetByLabel('UI/Crate/OpenCrate')), func=self.OpenCrate)

    def OpenCrate(self, button):
        button.disabled = True
        try:
            self.controller.OpenCrate()
        except Exception:
            button.disabled = False
            import log
            log.LogException()

    def OnCrateOpen(self):
        self.Disable()
        self.controller.onOpen.disconnect(self.OnCrateOpen)
        animations.MorphScalar(self.title, 'top', endVal=-24, timeOffset=0.25)
        animations.MorphVector2(self.title, 'scale', startVal=(1.0, 1.0), endVal=(0.8, 0.8), timeOffset=0.25)
        animations.FadeOut(self.textScroll, duration=0.5)
        animations.FadeOut(self.button, duration=0.5)


class CrateButton(Button):
    default_fixedwidth = 160
    default_fixedheight = 30

    def ApplyAttributes(self, attributes):
        super(CrateButton, self).ApplyAttributes(attributes)
        self.sr.label.width = 130
        self.sr.label.bold = True
        self.sr.label.fontsize = fontConst.EVE_MEDIUM_FONTSIZE


class HackingView(Container):
    default_clipChildren = True

    def ApplyAttributes(self, attributes):
        super(HackingView, self).ApplyAttributes(attributes)
        self.controller = attributes.controller
        self._claimedLootCount = 0
        self.Layout()

    def Layout(self):
        self.overlayCont = Container(parent=self, align=uiconst.TOPLEFT, top=200, left=200, width=600, height=80)
        GradientThemeColored(bgParent=self.overlayCont, padding=(1, 0, 1, 0), rgbData=[(0, (0.5, 0.5, 0.5))], alphaData=[(0, 0.0), (0.4, 0.7), (0.6, 0.8)], rotation=0)
        VectorLine(parent=self.overlayCont, align=uiconst.TOPLEFT, translationTo=(0, 0), translationFrom=(600, 0), widthTo=5, widthFrom=5, colorTo=(1.0, 1.0, 1.0, 0.0), texturePath='res:/UI/Texture/classes/ItemPacks/Hacking_HatchPattern.png', spriteEffect=trinity.TR2_SFX_COPY, textureWidth=8)
        VectorLine(parent=self.overlayCont, align=uiconst.BOTTOMLEFT, translationTo=(0, 0), translationFrom=(600, 0), widthTo=5, widthFrom=5, colorTo=(1.0, 1.0, 1.0, 0.0), texturePath='res:/UI/Texture/classes/ItemPacks/Hacking_HatchPattern.png', spriteEffect=trinity.TR2_SFX_COPY, textureWidth=8)
        labelCont = Container(parent=self.overlayCont, align=uiconst.TOALL, padding=(180, 20, 20, 20))
        self.hackingLabel = EveLabelMedium(parent=labelCont, align=uiconst.TOTOP, text=center(localization.GetByLabel('UI/Crate/HackingMessage')), opacity=0.0)
        self.progressLabel = ProgressLabel(parent=labelCont, align=uiconst.TOTOP, opacity=0.0)
        self.grid = HackingGrid(parent=self, align=uiconst.TOALL, padLeft=380, loot=self.controller.loot, onLootClaimed=self.OnLootClaimed)
        self.back = StreamingVideoSprite(parent=self, align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, width=800, height=550, top=-25, videoPath='res:/video/hacking/bgLoop_alpha.webm', spriteEffect=trinity.TR2_SFX_COPY, disableAudio=True)

    def AnimEntry(self):
        animations.FadeTo(self)
        uthread.new(self.AnimBackground)
        animations.MorphScalar(self.overlayCont, 'top', startVal=200, endVal=160, duration=0.3, timeOffset=0.5)
        animations.MorphScalar(self.overlayCont, 'height', endVal=80, duration=0.3, timeOffset=0.5)
        animations.FadeIn(self.hackingLabel, timeOffset=0.6)
        animations.FadeIn(self.progressLabel, timeOffset=0.7)
        animations.MorphScalar(self.progressLabel, 'top', startVal=10, endVal=0, duration=0.3, timeOffset=0.7)
        blue.synchro.SleepWallclock(700)
        uthread.new(self.grid.AnimObstacles)
        animations.MorphScalar(self.progressLabel, 'progress', endVal=100.0, duration=1.5, callback=self.progressLabel.Finish)
        blue.synchro.SleepWallclock(1500)
        animations.BlinkIn(self.progressLabel)
        blue.synchro.SleepWallclock(500)
        uthread.new(self.grid.AnimEntry)
        animations.FadeOut(self.hackingLabel, duration=0.4, timeOffset=0.1)
        animations.FadeOut(self.progressLabel, duration=0.4, timeOffset=0.1)
        animations.MorphScalar(self.overlayCont, 'top', startVal=160, endVal=200, duration=0.3, timeOffset=0.5)
        animations.MorphScalar(self.overlayCont, 'height', startVal=self.overlayCont.height, endVal=0, duration=0.3, timeOffset=0.5)

    def AnimBackground(self):
        animations.FadeTo(self.back, startVal=self.back.opacity, endVal=0.4, duration=0.3, sleep=True)
        animations.FadeTo(self.back, startVal=0.4, endVal=0.2, duration=6.0, loops=uiconst.ANIM_REPEAT, curveType=uiconst.ANIM_WAVE)

    def AnimBackgroundPulse(self):
        animations.FadeTo(self.back, startVal=0.6, endVal=0.4, duration=0.15, loops=3)
        blue.synchro.SleepWallclock(450)
        uthread.new(self.AnimBackground)

    def OnLootClaimed(self, item):
        self.controller.ClaimLoot(item)
        if not self.controller.loot:
            self.RevealButtons()
        uthread.new(self.AnimBackgroundPulse)

    def RevealButtons(self):
        buttonCont = FlowContainer(parent=self, align=uiconst.TOBOTTOM_NOPUSH, height=54, padLeft=380, padRight=24, centerContent=True, contentSpacing=(8, 0), idx=0)
        buttons = []
        if self.controller.stacksize > 0:
            buttons.append(CrateButton(parent=buttonCont, align=uiconst.NOALIGN, label=center(localization.GetByLabel('UI/Crate/OpenAnotherCrate', quantity=self.controller.stacksize)), func=self.OpenAnotherCrate))
        buttons.append(CrateButton(parent=buttonCont, align=uiconst.NOALIGN, label=center(localization.GetByLabel('UI/Crate/Finish')), func=self.controller.Finish, args=()))
        for button in buttons:
            animations.FadeTo(button)

    def OpenAnotherCrate(self, button):
        button.Disable()
        self.controller.OpenCrate()


class ProgressLabel(EveCaptionMedium):

    def ApplyAttributes(self, attributes):
        super(ProgressLabel, self).ApplyAttributes(attributes)
        self._progress = 0.0

    @property
    def progress(self):
        return self._progress

    @progress.setter
    def progress(self, value):
        self._progress = value
        self.UpdateProgress()

    def UpdateProgress(self):
        self.SetText(center('{}%'.format(int(self._progress))))

    def Finish(self):
        self.progress = 100


def weighted_choice(choices):
    total = sum((w for c, w in choices))
    r = random.uniform(0, total)
    upto = 0
    for c, w in choices:
        if upto + w >= r:
            return c
        upto += w


activeConnectionColor = (1.0, 0.2, 0.0)
activeConnectionAnimDuration = 0.15
HINT_TOOLTIP_SETTINGS_KEY = 'CrateWindowLootHintEnabled'

class HackingGrid(Container):
    gridWidth = 5
    gridHeight = 8
    gridTop = 55
    gridLeft = 22
    columnSpacing = 78.6
    rowSpacing = 46
    _neighborOffsetsOdd = ((-1, -1),
     (0, -1),
     (1, 0),
     (0, 1),
     (-1, 1),
     (-1, 0))
    _neighborOffsetsEven = ((0, -1),
     (1, -1),
     (1, 0),
     (1, 1),
     (0, 1),
     (-1, 0))
    _bleedHorizontalTexturePaths = ['res:/UI/Texture/classes/hacking/lineBleed/horiz01.png',
     'res:/UI/Texture/classes/hacking/lineBleed/horiz02.png',
     'res:/UI/Texture/classes/hacking/lineBleed/horiz03.png',
     'res:/UI/Texture/classes/hacking/lineBleed/horiz04.png',
     'res:/UI/Texture/classes/hacking/lineBleed/horiz05.png',
     'res:/UI/Texture/classes/hacking/lineBleed/horiz06.png',
     'res:/UI/Texture/classes/hacking/lineBleed/horiz07.png',
     'res:/UI/Texture/classes/hacking/lineBleed/horiz08.png',
     'res:/UI/Texture/classes/hacking/lineBleed/horiz09.png',
     'res:/UI/Texture/classes/hacking/lineBleed/horiz10.png',
     'res:/UI/Texture/classes/hacking/lineBleed/horiz11.png',
     'res:/UI/Texture/classes/hacking/lineBleed/horiz12.png',
     'res:/UI/Texture/classes/hacking/lineBleed/horiz13.png',
     'res:/UI/Texture/classes/hacking/lineBleed/horiz14.png',
     'res:/UI/Texture/classes/hacking/lineBleed/horiz15.png',
     'res:/UI/Texture/classes/hacking/lineBleed/horiz16.png',
     'res:/UI/Texture/classes/hacking/lineBleed/horiz17.png']
    _bleedDiagonalTexturePaths = ['res:/UI/Texture/classes/hacking/lineBleed/diag01.png',
     'res:/UI/Texture/classes/hacking/lineBleed/diag02.png',
     'res:/UI/Texture/classes/hacking/lineBleed/diag03.png',
     'res:/UI/Texture/classes/hacking/lineBleed/diag04.png',
     'res:/UI/Texture/classes/hacking/lineBleed/diag05.png',
     'res:/UI/Texture/classes/hacking/lineBleed/diag06.png',
     'res:/UI/Texture/classes/hacking/lineBleed/diag07.png',
     'res:/UI/Texture/classes/hacking/lineBleed/diag08.png',
     'res:/UI/Texture/classes/hacking/lineBleed/diag09.png',
     'res:/UI/Texture/classes/hacking/lineBleed/diag10.png',
     'res:/UI/Texture/classes/hacking/lineBleed/diag11.png']

    def ApplyAttributes(self, attributes):
        super(HackingGrid, self).ApplyAttributes(attributes)
        self.loot = attributes.loot
        self.onLootClaimed = attributes.onLootClaimed
        self._showHint = settings.user.ui.Get(HINT_TOOLTIP_SETTINGS_KEY, True)
        self._hint = None
        self._lootCells = []
        self.cellObjects = {}
        self.path = self.GeneratePath()
        self.DistributeLootOnPath()
        self.SprinkleObstacles()
        self.PunchHolesInGrid()
        for cell in self.cells:
            if cell in self.cellObjects:
                continue
            x, y = self.getCellPosition(cell)
            self.cellObjects[cell] = RegularCell(parent=self, align=uiconst.RELATIVE, left=x, top=y)

        self.DrawCellConnections()

    def DistributeLootOnPath(self):
        remainingLoot = self.loot[:]
        random.shuffle(remainingLoot)
        lootChancePerCell = len(remainingLoot) / float(len(self.path) - 2)
        accumulatedLootChance = lootChancePerCell
        for cell in self.path:
            if not remainingLoot:
                break
            if accumulatedLootChance >= 1.0:
                loot = remainingLoot.pop()
                x, y = self.getCellPosition(cell)
                self.cellObjects[cell] = ItemCell(parent=self, align=uiconst.RELATIVE, left=x - ItemCell.default_width / 2.0, top=y - ItemCell.default_height / 2.0, item=loot, onClaimed=self.OnLootClaimed)
                self._lootCells.append(cell)
                accumulatedLootChance -= 1.0
            accumulatedLootChance += lootChancePerCell

    def SprinkleObstacles(self):
        self.obstacles = []
        candidates = set(self.cells)
        candidates = list(candidates.difference(self.path))
        candidates = filter(lambda c: 0 < c[1] < self.gridHeight - 1, candidates)
        for i in xrange(random.randint(5, 7)):
            if not candidates:
                break
            cell = random.choice(candidates)
            x, y = self.getCellPosition(cell)
            obstacle = Obstacle(parent=self, align=uiconst.RELATIVE, left=x, top=y)
            self.cellObjects[cell] = obstacle
            self.obstacles.append(obstacle)
            candidates.remove(cell)
            for c in self.getCellNeighbors(cell):
                if c in candidates:
                    candidates.remove(c)

    def PunchHolesInGrid(self):
        candidates = set(self.cells)
        candidates = candidates.difference(self.path)
        candidates = list(candidates.difference(self.cellObjects.iterkeys()))
        for i in xrange(random.randint(5, 7)):
            if not candidates:
                break
            cell = random.choice(candidates)
            self.cellObjects[cell] = None
            candidates.remove(cell)

    def OnLootClaimed(self, item):
        if callable(self.onLootClaimed):
            self.onLootClaimed(item)
        self._showHint = False
        settings.user.ui.Set(HINT_TOOLTIP_SETTINGS_KEY, False)
        if self._hint:
            FadeOutPanelAndClose(self._hint)

    def AnimObstacles(self):

        def RevealThread(cell, timeOffset):
            blue.synchro.SleepWallclock(timeOffset * 1000)
            self.cellObjects[cell].AnimReveal()

        x_center, y_center = self.getCellPosition((0, 0))
        x_extent, y_extent = self.getCellPosition((self.gridWidth, self.gridHeight))
        extent = math.sqrt((x_extent - x_center) ** 2 + (y_extent - y_center) ** 2)
        timeFactor = 1.5 / extent
        for cell in self.cells:
            if self.cellObjects[cell] is None:
                continue
            x, y = self.getCellPosition(cell)
            x_offset = abs(x - x_center)
            y_offset = abs(y - y_center)
            timeOffset = timeFactor * math.sqrt(x_offset ** 2 + y_offset ** 2)
            uthread.new(RevealThread, cell, timeOffset)

    def AnimEntry(self):
        for i, cell in enumerate(self.path):
            if i == 0:
                self.DrawActiveFringeConnection(cell, self.getCellNeighbors(cell)[0])
            else:
                self.DrawActiveConnection(self.path[i - 1], cell)
            uthread.new(self.cellObjects[cell].AnimExplore)
            blue.synchro.SleepWallclock(activeConnectionAnimDuration * 1000)

        lastCell = self.getCellNeighbors(self.path[-1])[3]
        self.DrawActiveFringeConnection(self.path[-1], lastCell, inbound=False)
        uthread.new(self.RevealHint)

    def RevealHint(self):
        blue.synchro.SleepWallclock(5000)
        if self._showHint:
            cell = random.choice(self._lootCells)
            node = self.cellObjects[cell]
            self._hint = uicore.uilib.tooltipHandler.LoadPersistentTooltip(node, customTooltipClass=HintTooltip)

    def Close(self):
        if self._hint:
            FadeOutPanelAndClose(self._hint)
        super(HackingGrid, self).Close()

    def GeneratePath(self):
        path = []

        def weight(c):
            return self.gridWidth / 2.0 - abs(c - (self.gridWidth - 1) / 2.0)

        weightedColumns = [ (c, weight(c)) for c in xrange(self.gridWidth) ]
        column = weighted_choice(weightedColumns)
        path.append((column, 0))
        while True:
            horizontalMult = 0.0 if len(path) == 1 else 2.0
            weights = (0 + max(0, 2 - path[-1][0]) * horizontalMult,
             1 + max(0, 2 - path[-1][0]) * 0.5,
             1 + max(0, path[-1][0] - 2) * 0.5,
             0 + max(0, path[-1][0] - 2) * horizontalMult)
            neighbors = self.getCellNeighbors(path[-1])[2:]
            weightedNeighbors = zip(neighbors, weights)
            candidates = filter(lambda x: self.IsCellInsideGrid(x[0]), weightedNeighbors)
            nextCell = weighted_choice(candidates)
            path.append(nextCell)
            if nextCell[1] == self.gridHeight - 1:
                break

        return path

    def DrawCellConnections(self):
        for cell in self.cells:
            if self.cellObjects[cell] is None:
                continue
            neighbors = filter(self.IsCellInsideGrid, self.getCellNeighbors(cell)[:3])
            for neighbor in neighbors:
                if self.cellObjects[neighbor] is None:
                    continue
                x_origin, y_origin = self.getCellPosition(cell)
                x, y = self.getCellPosition(neighbor)
                VectorLine(parent=self, translationFrom=(x_origin, y_origin), translationTo=(x, y), colorFrom=(1, 1, 1, 0.3), colorTo=(1, 1, 1, 0.3), widthFrom=0.3, widthTo=0.3)

        self.DrawFringePaths()

    def DrawActiveConnection(self, fromCell, toCell):
        x_origin, y_origin = self.getCellPosition(fromCell)
        x, y = self.getCellPosition(toCell)
        line = VectorLine(parent=self, translationFrom=(x_origin, y_origin), translationTo=(x, y), colorFrom=color.GetColor(activeConnectionColor, alpha=0.5), colorTo=color.GetColor(activeConnectionColor, alpha=0.5), widthFrom=1, widthTo=1)
        midpoint = geo2.Vec2Lerp((x_origin, y_origin), (x, y), 0.5)
        if y_origin == y:
            texturePath = random.choice(self._bleedHorizontalTexturePaths)
            height = 50
            left = midpoint[0] - 48
            top = midpoint[1] - height / 2.0
        else:
            texturePath = random.choice(self._bleedDiagonalTexturePaths)
            height = 72
            left = midpoint[0] - 32
            top = midpoint[1] - height / 2.0
            if y_origin < y and x_origin > x or y_origin > y and x_origin < x:
                top += height
                height *= -1
        bleed = Sprite(parent=self, align=uiconst.RELATIVE, state=uiconst.UI_DISABLED, left=left, top=top, width=64, height=height, texturePath=texturePath)

        def BleedAnimation():
            animations.FadeTo(bleed, startVal=bleed.opacity, endVal=0.2, duration=5.0, loops=uiconst.ANIM_REPEAT, curveType=uiconst.ANIM_WAVE)

        animations.FadeTo(bleed, endVal=0.5, duration=0.1, loops=3, timeOffset=random.random() * 0.6, callback=BleedAnimation)
        glow = VectorLine(parent=self, translationFrom=(x_origin, y_origin), translationTo=(x, y), colorFrom=color.GetColor(activeConnectionColor, alpha=1.0), colorTo=color.GetColor(activeConnectionColor, alpha=1.0), widthFrom=30, widthTo=30, texturePath='res:/UI/Texture/classes/ItemPacks/Hacking_ConnectionGlow.png', spriteEffect=trinity.TR2_SFX_COPY)
        animations.MorphVector2(line, 'translationTo', startVal=(x_origin, y_origin), endVal=(x, y), duration=activeConnectionAnimDuration)
        animations.MorphVector2(glow, 'translationTo', startVal=(x_origin, y_origin), endVal=(x, y), duration=activeConnectionAnimDuration)
        animations.SpColorMorphTo(line, attrName='colorTo', startColor=color.GetColor(activeConnectionColor, alpha=0.0), endColor=color.GetColor(activeConnectionColor, alpha=0.5), duration=activeConnectionAnimDuration, timeOffset=activeConnectionAnimDuration)
        animations.SpColorMorphTo(glow, attrName='colorTo', startColor=color.GetColor(activeConnectionColor, alpha=0.0), endColor=color.GetColor(activeConnectionColor, alpha=1.0), duration=activeConnectionAnimDuration)
        animations.MorphScalar(glow, 'widthTo', endVal=30, duration=activeConnectionAnimDuration)

    def DrawActiveFringeConnection(self, insideCell, outsideCell, inbound = True):
        x_origin, y_origin = self.getCellPosition(insideCell)
        x, y = self.getCellPosition(outsideCell)
        line = VectorLine(parent=self, translationFrom=(x_origin, y_origin), translationTo=(x, y), colorFrom=color.GetColor(activeConnectionColor, alpha=0.5), colorTo=color.GetColor(activeConnectionColor, alpha=0.0), widthFrom=1, widthTo=1)
        VectorLine(parent=self, translationFrom=(x_origin, y_origin), translationTo=(x, y), colorFrom=color.GetColor(activeConnectionColor, alpha=1.0), colorTo=color.GetColor(activeConnectionColor, alpha=0.0), widthFrom=30, widthTo=30, texturePath='res:/UI/Texture/classes/ItemPacks/Hacking_ConnectionGlow.png', spriteEffect=trinity.TR2_SFX_COPY)
        if inbound:
            animations.MorphVector2(line, 'translationFrom', startVal=(x, y), endVal=(x_origin, y_origin), duration=activeConnectionAnimDuration)
        else:
            animations.MorphVector2(line, 'translationTo', startVal=(x_origin, y_origin), endVal=(x, y), duration=activeConnectionAnimDuration)
        animations.MorphScalar(line, 'opacity', startVal=0.0, endVal=1.0, duration=activeConnectionAnimDuration)

    def IsCellOutsideGrid(self, cell):
        col, row = cell
        return col < 0 or self.gridWidth <= col or row < 0 or self.gridHeight <= row

    def IsCellInsideGrid(self, cell):
        return not self.IsCellOutsideGrid(cell)

    def DrawFringePaths(self):
        for cell in self.cells:
            if self.cellObjects[cell] is None:
                continue
            outsideCells = filter(self.IsCellOutsideGrid, self.getCellNeighbors(cell))
            for col, row in outsideCells:
                if 0 <= col < self.gridWidth and 0 <= row < self.gridHeight:
                    continue
                x_origin, y_origin = self.getCellPosition(cell)
                x, y = self.getCellPosition((col, row))
                VectorLine(parent=self, translationFrom=(x_origin, y_origin), translationTo=(x, y), colorFrom=(1, 1, 1, 0.2), colorTo=(1, 1, 1, 0.0), widthFrom=0.5, widthTo=0.5)

    @property
    def cells(self):
        return ((x, y) for x, y in itertools.product(xrange(self.gridWidth), xrange(self.gridHeight)))

    def getCellPosition(self, coord):
        x, y = coord
        rowOffset = self.columnSpacing / 2.0 if y % 2 == 0 else 0
        return (x * self.columnSpacing + rowOffset + self.gridLeft, y * self.rowSpacing + self.gridTop)

    def getCellNeighbors(self, coord):
        column, row = coord
        neighborOffsets = self._neighborOffsetsEven if row % 2 == 0 else self._neighborOffsetsOdd
        return [ (column + c, row + r) for c, r in neighborOffsets ]


class RegularCell(Container):
    default_clipChildren = False
    default_state = uiconst.UI_DISABLED
    default_width = 1
    default_height = 1

    def ApplyAttributes(self, attributes):
        super(RegularCell, self).ApplyAttributes(attributes)
        self.Layout()

    def Layout(self):
        self.closed = Sprite(parent=self, align=uiconst.CENTER, width=64, height=64, texturePath='res:/UI/Texture/classes/hacking/tileUnflipped.png', color=(0.3, 0.3, 0.3))

    def AnimReveal(self):
        animations.SpGlowFadeOut(self.closed, duration=0.3)
        animations.MorphScalar(self.closed, 'glowExpand', startVal=0.5, endVal=10.0, duration=0.3)

    def AnimExplore(self):
        opened = Sprite(parent=self, align=uiconst.CENTER, width=40, height=40, texturePath='res:/UI/Texture/classes/hacking/tileExplored.png', color=(0.3, 0.3, 0.3), opacity=0.0, idx=0)
        animations.FadeOut(self.closed, timeOffset=activeConnectionAnimDuration / 2.0)
        animations.FadeIn(opened, duration=0.1, timeOffset=activeConnectionAnimDuration / 2.0)
        animations.SpGlowFadeOut(opened, duration=0.3, timeOffset=activeConnectionAnimDuration / 2.0 + 0.1)
        animations.MorphScalar(opened, 'glowExpand', startVal=0.5, endVal=10.0, duration=0.3, timeOffset=activeConnectionAnimDuration / 2.0 + 0.1)


class ItemCell(Container):
    default_clipChildren = False
    default_state = uiconst.UI_DISABLED
    default_width = 64
    default_height = 64

    def ApplyAttributes(self, attributes):
        super(ItemCell, self).ApplyAttributes(attributes)
        self.item = attributes.item
        self.onClaimed = attributes.onClaimed
        self.Layout()

    def Layout(self):
        self.nodeSprite = Sprite(parent=self, align=uiconst.CENTER, state=uiconst.UI_DISABLED, width=64, height=64, texturePath='res:/UI/Texture/classes/hacking/tileUnflipped.png', color=(0.3, 0.3, 0.3))
        self.frame = StreamingVideoSprite(parent=self, align=uiconst.CENTER, state=uiconst.UI_DISABLED, width=72, height=72, videoPath='res:/UI/Texture/classes/ItemPacks/nodeIntro_R4.webm', spriteEffect=trinity.TR2_SFX_COPY, disableAudio=True, color=activeConnectionColor)
        self.frame.Pause()
        self.nodeSpinner = StreamingVideoSprite(parent=self, align=uiconst.CENTER, state=uiconst.UI_DISABLED, width=64, height=64, videoPath='res:/UI/Texture/classes/ItemPacks/baseNodeLoop.webm', videoLoop=True, spriteEffect=trinity.TR2_SFX_COPY, disableAudio=True, opacity=0.0, color=activeConnectionColor)
        self.nodeSpinner.Pause()
        self.node = Sprite(parent=self, align=uiconst.CENTER, state=uiconst.UI_DISABLED, width=32, height=32, texturePath='res:/UI/Texture/classes/ItemPacks/itemNodeCenter.png', blendMode=trinity.TR2_SBM_ADDX2, color=(0.1, 0.1, 0.1), opacity=0.0)
        self.back = Sprite(parent=self, align=uiconst.CENTER, state=uiconst.UI_DISABLED, width=64, height=64, texturePath='res:/UI/Texture/classes/ItemPacks/itemNodeBack.png', color=activeConnectionColor, opacity=0.0)

    def AnimReveal(self):
        animations.FadeOut(self.nodeSprite, duration=0.1)
        animations.FadeIn(self.node, endVal=1.0, duration=0.1)
        animations.SpGlowFadeOut(self.node, duration=0.3, timeOffset=0.1)
        animations.MorphScalar(self.node, 'glowExpand', startVal=0.5, endVal=10.0, duration=0.3, timeOffset=0.1)

    def AnimExplore(self):
        self.frame.Play()
        animations.FadeOut(self.nodeSprite, duration=0.1)
        animations.FadeIn(self.nodeSpinner, duration=0.5, callback=self.Enable)
        self.nodeSpinner.Play()
        animations.FadeIn(self.back, endVal=0.1, duration=0.2)
        animations.FadeIn(self.node, endVal=1.0, duration=0.25)
        animations.SpColorMorphTo(self.node, endColor=activeConnectionColor, duration=0.2)
        animations.MorphVector2(self.node, 'scale', startVal=(0.5, 0.5), duration=0.5, sleep=True)

        def PulseNode():
            offset = random.normalvariate(2.0, 1.0)
            animations.MorphVector2(self.node, 'scale', startVal=(1.0, 1.0), endVal=(0.8, 0.8), duration=0.15, timeOffset=offset)
            blue.synchro.SleepWallclock((offset + 0.15) * 1000)
            animations.MorphVector2(self.node, 'scale', startVal=(0.8, 0.8), endVal=(1.0, 1.0), duration=0.4)
            blue.synchro.SleepWallclock(500)
            if not self.destroyed:
                uthread.new(PulseNode)

        uthread.new(PulseNode)

    def ClaimLoot(self):
        self.SetState(uiconst.UI_PICKCHILDREN)
        uthread.new(self.AnimRevealItem)
        if callable(self.onClaimed):
            self.onClaimed(self.item)

    def AnimRevealItem(self):
        self.frame.SetVideoPath('res:/UI/Texture/classes/ItemPacks/nodeHarvest_R4.webm')
        animations.FadeOut(self.nodeSpinner, duration=0.2)
        animations.MorphVector2(self.node, 'scale', startVal=(1.0, 1.0), endVal=(2.0, 2.0), duration=0.15, sleep=True)
        animations.MorphVector2(self.node, 'scale', startVal=(2.0, 2.0), endVal=(0.5, 0.5), duration=0.1)
        animations.FadeOut(self.node, duration=0.15)
        blue.synchro.SleepWallclock(25)
        backdrop = Sprite(parent=self, align=uiconst.CENTER, state=uiconst.UI_DISABLED, width=48, height=48, texturePath='res:/UI/Texture/classes/ItemPacks/Hacking_NodeExploredBackground.png', opacity=0.0)
        animations.FadeIn(backdrop, duration=0.25, timeOffset=0.1)
        size = self.GetItemIconSize()
        isCopy = self.item.customInfo is not None and 'blueprintRun' in self.item.customInfo
        icon = Icon(parent=self, align=uiconst.CENTER, state=uiconst.UI_NORMAL, width=size, height=size, typeID=self.item.typeID, isCopy=isCopy, idx=0)
        icon.LoadTooltipPanel = self.LoadItemTooltipPanel
        animations.FadeTo(icon, duration=0.15)
        animations.MorphVector2(icon, 'scale', startVal=(4.0, 4.0), endVal=(0.9, 0.9), duration=0.15, sleep=True)
        animations.MorphVector2(icon, 'scale', startVal=(0.9, 0.9), endVal=(1.0, 1.0), duration=0.15)
        animations.SpGlowFadeOut(icon, duration=0.3)
        animations.MorphScalar(icon, 'glowExpand', startVal=0.5, endVal=10.0, duration=0.3)

    def GetItemIconSize(self):
        if IsBlueprint(self.item.typeID) or IsApparel(self.item.typeID):
            return 42
        else:
            return 64

    def OnClick(self):
        self.ClaimLoot()

    def OnMouseEnter(self):
        animations.SpColorMorphTo(self.frame, endColor=(1.0, 0.376, 0.208, 2.0), duration=0.15)
        animations.FadeTo(self.back, startVal=self.back.opacity, endVal=0.4, duration=0.3)

    def OnMouseExit(self):
        animations.SpColorMorphTo(self.frame, endColor=activeConnectionColor, duration=0.3)
        animations.FadeTo(self.back, startVal=self.back.opacity, endVal=0.1, duration=0.3)

    def LoadItemTooltipPanel(self, panel, owner):
        panel.columns = 2
        panel.margin = (1, 1, 1, 1)
        techIcon = Sprite(parent=panel, align=uiconst.TOPLEFT, state=uiconst.UI_HIDDEN, width=16, height=16)
        uix.GetTechLevelIcon(techIcon, typeID=self.item.typeID)
        if self.item.quantity > 1:
            text = localization.GetByLabel('UI/Crate/ItemNameAndQuantity', typeID=self.item.typeID, quantity=self.item.quantity)
        else:
            text = localization.GetByMessageID(evetypes.GetNameID(self.item.typeID))
        panel.AddLabelMedium(text=text, padding=(0, 4, 16, 4))


class Obstacle(Container):
    default_state = uiconst.UI_DISABLED
    default_clipChildren = False
    default_width = 1
    default_height = 1
    _obstacleTexturePaths = ['res:/UI/Texture/classes/hacking/defSoftAntiVirus.png',
     'res:/UI/Texture/classes/hacking/defSoftFirewall.png',
     'res:/UI/Texture/classes/hacking/defSoftHoneyPotHealing.png',
     'res:/UI/Texture/classes/hacking/defSoftHoneyPotStrength.png',
     'res:/UI/Texture/classes/hacking/defSoftIds.png']
    _noiseTexturePaths = ['res:/UI/Texture/classes/ItemPacks/Hacking_VirusNoise01.png',
     'res:/UI/Texture/classes/ItemPacks/Hacking_VirusNoise02.png',
     'res:/UI/Texture/classes/ItemPacks/Hacking_VirusNoise03.png',
     'res:/UI/Texture/classes/ItemPacks/Hacking_VirusNoise04.png']

    def ApplyAttributes(self, attributes):
        super(Obstacle, self).ApplyAttributes(attributes)
        self.Layout()

    def Layout(self):
        self.node = Sprite(parent=self, align=uiconst.CENTER, width=64, height=64, texturePath='res:/UI/Texture/classes/hacking/tileUnflipped.png', color=(0.3, 0.3, 0.3))
        self.virus = Sprite(parent=self, align=uiconst.CENTER, width=64, height=64, texturePath=random.choice(self._obstacleTexturePaths), color=activeConnectionColor, opacity=0.0)
        self.frame = Sprite(parent=self, align=uiconst.CENTER, width=64, height=64, texturePath='res:/UI/Texture/classes/hacking/tileIconFrame.png', color=activeConnectionColor, opacity=0.0)
        self.back = Sprite(parent=self, align=uiconst.CENTER, width=48, height=48, texturePath='res:/UI/Texture/classes/ItemPacks/hacking_NodeExploredBackground.png', opacity=0.0)
        self.noise = Sprite(parent=self, align=uiconst.CENTER, width=150, height=100, color=activeConnectionColor, opacity=0.25, textureSecondaryPath='res:/UI/Texture/classes/hacking/healRing1.png', spriteEffect=trinity.TR2_SFX_MASK, blendMode=trinity.TR2_SBM_ADD)

    def AnimReveal(self):
        animations.FadeOut(self.node, duration=0.2)
        animations.FadeIn(self.frame, endVal=0.5, duration=0.2)
        animations.FadeIn(self.back, duration=0.3)
        animations.SpGlowFadeOut(self.frame, duration=0.3, timeOffset=0.2)
        animations.MorphScalar(self.frame, 'glowExpand', startVal=0.5, endVal=10.0, duration=0.3, timeOffset=0.2)
        animations.BlinkIn(self.virus, sleep=True)
        animations.SpColorMorphTo(self.virus, endColor=(0.2, 0.2, 0.2, 1.0))
        animations.SpColorMorphTo(self.frame, endColor=(0.3, 0.3, 0.3, 0.3))
        uthread.new(self.AnimPulseNoise)

    def AnimPulseNoise(self):
        offset = 2.0 + random.random() * 12.0
        self.noise.SetTexturePath(random.choice(self._noiseTexturePaths))
        animations.MorphVector2(self.noise, 'scaleSecondary', startVal=(5.0, 5.0), endVal=(0.25, 0.25), duration=4.0, timeOffset=offset, sleep=True)
        if not self.destroyed:
            uthread.new(self.AnimPulseNoise)


class TitleLabel(EveStyleLabel):
    default_fontsize = 30
    default_bold = True
    default_fontStyle = fontConst.STYLE_HEADER


class HintTooltip(TooltipPersistentPanel):
    defaultPointer = uiconst.POINT_LEFT_2

    def ApplyAttributes(self, attributes):
        super(HintTooltip, self).ApplyAttributes(attributes)
        self.owner = attributes.get('owner')
        self.pickState = uiconst.TR2_SPS_ON
        uicore.uilib.RegisterForTriuiEvents(uiconst.UI_MOUSEMOVEDRAG, self.OnGlobalMouseMoveDrag)

    def LoadTooltip(self, panel, owner):
        self.AddLabelMedium(text=localization.GetByLabel('UI/Crate/HackingHint'), padding=(24, 8, 24, 8))

    def ShowPanel(self, owner):
        animations.FadeTo(self, duration=1.5)

    def OnClick(self, *args):
        FadeOutPanelAndClose(self)

    def OnGlobalMouseMoveDrag(self, *args):
        if not self.destroyed:
            RefreshPanelPosition(self)
            return True
        return False


def center(text):
    return u'<center>{}</center>'.format(text)


def __SakeReloadHook():
    try:
        instance = CrateWindow.GetIfOpen()
        if instance:
            CrateWindow.Reload(instance)
    except Exception:
        import log
        log.LogException()
