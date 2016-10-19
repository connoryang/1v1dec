#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\devtools\script\form_viewer.py
import uiprimitives
import uicontrols
import uix
import blue
import base
import os
import uthread
import listentry
import carbonui.const as uiconst
from carbonui.primitives.sprite import StreamingVideoSprite
from carbonui.control.slider import Slider
from service import *
BTNSIZE = 16
ASPECT_X = 16
ASPECT_Y = 9

class BinkVideoViewer(uicontrols.Window):
    __guid__ = 'form.InsiderBinkVideoViewer'
    __neocommenuitem__ = (('Video Player', 'InsiderBinkVideoViewer'), True, ROLE_GML)

    def ApplyAttributes(self, attributes):
        uicontrols.Window.ApplyAttributes(self, attributes)
        w, h = (450, 230)
        self.HideMainIcon()
        self.SetTopparentHeight(0)
        self.SetMinSize([w, h])
        self.SetHeight(h)
        self.SetCaption('Video Player')
        margin = const.defaultPadding
        self.sr.innermain = uiprimitives.Container(name='inner', left=margin, top=margin, parent=self.sr.main)
        self.sr.bottomframe = uiprimitives.Container(name='bottom', align=uiconst.TOBOTTOM, parent=self.sr.innermain, height=BTNSIZE, left=margin, top=margin, clipChildren=1)
        self.sr.rightframe = uiprimitives.Container(name='right', align=uiconst.TORIGHT, parent=self.sr.innermain, width=150, left=margin, top=margin, clipChildren=1)
        self.sr.movieCont = uiprimitives.Container(name='movieCont', align=uiconst.TOALL, parent=self.sr.innermain, pos=(margin,
         margin,
         margin,
         margin))
        uicontrols.Frame(parent=self.sr.innermain, color=(1.0, 1.0, 1.0, 0.2), idx=0)
        uicontrols.Frame(parent=self.sr.movieCont, color=(1.0, 1.0, 1.0, 0.2), idx=0)
        self.videoDir = blue.paths.ResolvePath(u'res:/') + 'video'
        self.node = None
        self.playing = False
        self.movieWidth = ASPECT_X
        self.movieHeight = ASPECT_Y
        self.InitButtons()
        self.InitScroll()

    def CloseByUser(self, *args):
        if getattr(self, 'movie', None) and self.movie:
            self.movie.Close()
        self.Close()

    def OnResizeUpdate(self, *args):
        if self and not self.destroyed:
            self.sr.resizeTimer = base.AutoTimer(250, self.OnEndScale_)

    def OnEndScale_(self, *args):
        self.sr.resizeTimer = None
        dimWidth, dimHeight = self.GetSize(self.movieWidth, self.movieHeight)
        if getattr(self, 'movie', None) is not None:
            self.movie.width = dimWidth
            self.movie.height = dimHeight

    def InitButtons(self):
        buttons = [['Play', self.MoviePlay, 'ui_38_16_228'],
         ['Pause', self.MoviePause, 'ui_38_16_238'],
         ['Stop', self.MovieStop, 'ui_38_16_111'],
         ['Toggle Sound', self.MovieAudioToggle, 'ui_38_16_90'],
         ['Set Aspect', self.SetMovieAspect, 'ui_38_16_1']]
        for button in buttons:
            hint, function, iconID = button
            btn = uiprimitives.Container(name=hint, align=uiconst.TOLEFT, width=BTNSIZE, left=const.defaultPadding, parent=self.sr.bottomframe)
            uicontrols.Frame(parent=btn, color=(1.0, 1.0, 1.0, 0.125))
            icon = uicontrols.Icon(icon=iconID, parent=btn, size=BTNSIZE, align=uiconst.CENTER)
            icon.OnClick = function
            icon.hint = hint
            icon.OnMouseEnter = (self.ShowSelected, icon, 1)
            icon.OnMouseExit = (self.ShowSelected, icon, 0)
            icon.sr.hilite = uiprimitives.Fill(parent=btn, name='hilite', state=uiconst.UI_HIDDEN)

        textWidth = 353
        self.textBlock = uiprimitives.Container(parent=self.sr.bottomframe, align=uiconst.TOALL, left=const.defaultPadding)
        self.slider = Slider(name='mySlider', parent=self.textBlock, align=uiconst.TOLEFT, width=100, minValue=0.0, maxValue=100.0, startVal=0.0, endsliderfunc=self._OnSlider)
        self.textBtm = uicontrols.Label(text='', parent=self.textBlock, align=uiconst.TOALL, left=const.defaultPadding, height=0, top=1, fontsize=10, letterspace=1, linespace=9, uppercase=1, state=uiconst.UI_NORMAL)

    def _OnSlider(self, slider):
        if getattr(self, 'movie', None) is None or self.movie.duration is None:
            return
        self.movie.Seek(long(slider.GetValue() / 100.0 * self.movie.duration))

    def UpdateText(self):
        node = self.node
        if node is not None:
            btmText = 'Time: %s / %s' % (int(self.GetCurrentMovieTime()), int(self.GetDuration()))
            self.textBtm.text = btmText
            if not self.slider.dragging:
                if self.GetDuration():
                    self.slider.SetValue(self.GetCurrentMovieTime() / self.GetDuration() * 100.0, updateHandle=True)
                else:
                    self.slider.SetValue(0, updateHandle=True)

    def GetCurrentMovieTime(self):
        if getattr(self, 'movie', None) is None:
            return 0
        if self.movie.mediaTime is None:
            return 0
        return float(self.movie.mediaTime / 1000000) / 1000

    def GetDuration(self):
        if getattr(self, 'movie', None) is None:
            return 0
        if self.movie.duration is None:
            return 0
        return float(self.movie.duration / 1000000) / 1000

    def ShowSelected(self, btn, toggle, *args):
        btn.sr.hilite.state = [uiconst.UI_HIDDEN, uiconst.UI_DISABLED][toggle]

    def MoviePlay(self, btn = None, *args):
        if self.node is None:
            return
        if getattr(self, 'movie', None) is not None:
            self.movie.Play()
            uthread.new(self.MoviePlaying)
        else:
            self.Populate()
            self.MoviePlay()

    def MoviePause(self, btn = None, stop = False, *args):
        if stop:
            if getattr(self, 'movie', None) is not None:
                self.movie.Pause()
                self.playing = False
                return
        if getattr(self, 'movie', None) is not None and not self.movie.isFinished and not self.movie.isPaused:
            self.movie.Pause()
        elif getattr(self, 'movie', None) is not None and not self.movie.isFinished and self.movie.isPaused:
            self.MoviePlay()

    def MovieStop(self, btn = None, *args):
        if getattr(self, 'movie', None) is not None:
            self.movie.Pause()
            self.sr.movieCont.Flush()
            uicontrols.Frame(parent=self.sr.movieCont, color=(1.0, 1.0, 1.0, 0.2), idx=0)
            self.movie = None
            self.playing = False

    def MoviePlaying(self):
        while self and not self.destroyed:
            self.UpdateText()
            if getattr(self, 'movie', None) is not None:
                self.playing = True
                if self.movie.isFinished:
                    self.sr.movieCont.Flush()
                    uicontrols.Frame(parent=self.sr.movieCont, color=(1.0, 1.0, 1.0, 0.2), idx=0)
                    self.playing = False
                elif self.movie.isPaused:
                    self.playing = False
            blue.pyos.synchro.SleepWallclock(20)

    def MovieAudioToggle(self, btn = None, *args):
        if getattr(self, 'movie', None) is not None:
            if self.movie.isMuted:
                self.movie.UnmuteAudio()
            else:
                self.movie.MuteAudio()

    def SetMovieAspect(self, btn = None, *args):
        popup = ModifyAspectRatioPopup(caption='Set aspect ratio...', width=self.movieWidth, height=self.movieHeight)
        ret = popup.Wnd()
        if ret is not None:
            width = int(ret['width'])
            height = int(ret['height'])
            dimWidth, dimHeight = self.GetSize(width, height)
            if getattr(self, 'movie', None) is not None:
                self.movieWidth = width
                self.movieHeight = height
                self.movie.width = dimWidth
                self.movie.height = dimHeight

    def Populate(self, path = None):
        self.sr.movieCont.Flush()
        uicontrols.Frame(parent=self.sr.movieCont, color=(1.0, 1.0, 1.0, 0.2), idx=0)
        dimWidth, dimHeight = self.GetSize(self.movieWidth, self.movieHeight)
        if path is not None:
            moviePath = path
        else:
            moviePath = str(self.node.resPath)
        self.path = moviePath
        self.movie = StreamingVideoSprite(parent=self.sr.movieCont, width=dimWidth, height=dimHeight, align=uiconst.CENTER, state=uiconst.UI_DISABLED, videoPath=moviePath)

    def GetSize(self, vidWidth = ASPECT_X, vidHeight = ASPECT_Y):
        x, y, contWidth, contHeight = self.sr.movieCont.GetAbsolute()
        dimWidth, dimHeight = self.GetVideoDimensions(contWidth, contHeight, vidWidth, vidHeight)
        return (dimWidth, dimHeight)

    def GetVideoDimensions(self, contWidth, contHeight, vidResWidth, vidResHeight):
        margin = const.defaultPadding
        dimWidth = vidResWidth
        dimHeight = vidResHeight
        contFactor = float(contWidth) / float(contHeight)
        vidResFactor = float(vidResWidth) / float(vidResHeight)
        if vidResFactor > contFactor:
            widthFactor = float(contWidth) / float(vidResWidth)
            dimWidth *= widthFactor
            dimHeight *= widthFactor
        elif vidResFactor < contFactor:
            heightFactor = float(contHeight) / float(vidResHeight)
            dimWidth *= heightFactor
            dimHeight *= heightFactor
        else:
            dimWidth = contWidth
            dimHeight = contHeight
        return (int(dimWidth), int(dimHeight))

    def GetFileListFromDirectories(self, path):
        for root, dirs, files in os.walk(path):
            for filename in files:
                if filename.lower().endswith('.webm'):
                    yield root + '\\' + filename

    def InitScroll(self):
        self.scroll = uicontrols.Scroll(parent=self.sr.rightframe, padding=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding))
        self.scroll.sr.id = 'VideoList'
        videos = []
        for video in ['https://cdn1.eveonline.com/academy/001-EVEFA-YourPlaceinNewEden.webm'] + list(self.GetFileListFromDirectories(self.videoDir)):
            if video.startswith('https://'):
                fileName = video[video.rindex('/') + 1:]
                resPath = video
            else:
                normPath = os.path.normpath(video)
                fileName = os.path.basename(normPath)
                resPath = blue.paths.ResolvePathToRoot('res', normPath).replace(':', '')
            videos.append(listentry.Get('Generic', {'label': fileName,
             'hint': resPath,
             'resPath': resPath,
             'fileName': fileName,
             'OnClick': self.ScrollClick,
             'OnDblClick': self.ScrollDblClick}))

        self.scroll.Load(contentList=videos, headers=['Filename'], fixedEntryHeight=18)

    def ScrollClick(self, node, *args):
        if not self.playing:
            self.node = node.sr.node
            self.movie = None
            self.UpdateText()

    def ScrollDblClick(self, node, *args):
        if getattr(self, 'movie', None) is not None:
            self.MoviePause(stop=True)
        path = str(node.sr.node.resPath)
        self.node = node.sr.node
        self.Populate(path=path)
        self.MoviePlay()


class ModifyAspectRatioPopup():
    __wndname__ = 'ModifyAspectRatioPopup'

    def __init__(self, caption = None, width = ASPECT_X, height = ASPECT_Y):
        aspectPairs = [['width', width], ['height', height]]
        focus = 'width'
        if caption is None:
            caption = u'Type in name'
        format = [{'type': 'btline'}]
        for each in aspectPairs:
            key, val = each
            if key == focus:
                hasFocus = 1
            else:
                hasFocus = 0
            format += [{'type': 'edit',
              'setvalue': '%s' % val,
              'key': '%s' % key,
              'label': '%s' % key,
              'required': 1,
              'frame': 1,
              'setfocus': hasFocus,
              'selectall': hasFocus}]

        format += [{'type': 'bbline'}]
        OKCANCEL = 1
        self.popup = uix.HybridWnd(format, caption, 1, None, OKCANCEL, None, minW=240, minH=80)

    def __getitem__(self, *args):
        return args

    def Wnd(self, *args):
        return self.popup
