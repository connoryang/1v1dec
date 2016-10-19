#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\carbonui\primitives\sprite.py
from .base import Base
import carbonui.const as uiconst
import audio2
import blue
import logging
import remotefilecache
import trinity
import types
import weakref
import uthread
import videoplayer
try:
    import GameWorld
except:
    GameWorld = None

DEFAULTCOLOR = (1.0,
 1.0,
 1.0,
 1.0)

class VisibleBase(Base):
    __guid__ = 'uiprimitives.VisibleBase'
    __renderObject__ = None
    default_name = 'VisibleBase'
    default_left = 0
    default_top = 0
    default_color = DEFAULTCOLOR
    default_opacity = None
    default_blendMode = trinity.TR2_SBM_BLEND
    default_depth = 0.0
    _color = None

    def ApplyAttributes(self, attributes):
        Base.ApplyAttributes(self, attributes)
        color = attributes.get('color', self.default_color)
        if type(color) == types.TupleType and color != DEFAULTCOLOR:
            self.SetRGB(*color)
        self.blendMode = attributes.get('blendMode', self.default_blendMode)
        self.depth = attributes.get('depth', self.default_depth)
        opacity = attributes.get('opacity', self.default_opacity)
        if opacity is not None:
            self.opacity = opacity

    def Close(self):
        self._color = None
        Base.Close(self)

    @apply
    def blendMode():
        doc = '\n        Determines how the sprite blends with the background. Must be a \n        trinity.TR2_SBM_{X} constant'

        def fget(self):
            return self._blendMode

        def fset(self, value):
            self._blendMode = value
            ro = self.renderObject
            if ro:
                ro.blendMode = value

        return property(**locals())

    @apply
    def color():
        doc = 'Set color as (r,g,b,a) [0.0 - 1.0]'

        def fget(self):
            if self._color is None:
                self._color = PyColor(self)
            return self._color

        def fset(self, value):
            if type(value) == types.TupleType:
                self.SetRGB(*value)
            elif isinstance(value, PyColor):
                self._color = value
            ro = self.renderObject
            if ro:
                ro.color = self._color.GetRGBA()

        def fdel(self):
            self._color = None

        return property(**locals())

    @apply
    def opacity():
        doc = 'opacity [0.0 - 1.0]'

        def fget(self):
            return self.color.a

        def fset(self, value):
            self.color.a = value

        return property(**locals())

    @apply
    def depth():
        doc = 'z-axis offset. Only has meaning when using with 3d rendering'

        def fget(self):
            return self._depth

        def fset(self, value):
            self._depth = value
            ro = self.renderObject
            if ro:
                ro.depth = value

        return property(**locals())

    def SetRGB(self, *color):
        if type(color) != types.TupleType:
            return
        self.color.SetRGB(*color)

    SetRGBA = SetRGB

    def GetRGB(self):
        return self.color.GetRGB()

    def GetRGBA(self):
        return self.color.GetRGBA()

    def SetAlpha(self, alpha):
        self.color.SetAlpha(alpha)

    def GetAlpha(self):
        return self.color.GetAlpha()


class TexturedBase(VisibleBase):
    __guid__ = 'uiprimitives.TexturedBase'
    __renderObject__ = None
    default_noScale = 0
    default_texturePath = None
    default_textureSecondaryPath = None
    default_translationPrimary = (0.0, 0.0)
    default_translationSecodary = (0.0, 0.0)
    default_glowFactor = 0.0
    default_glowExpand = 0.0
    default_glowColor = (1, 1, 1, 1)
    default_shadowOffset = (0, 0)
    default_shadowColor = (0, 0, 0, 0.5)
    default_spriteEffect = trinity.TR2_SFX_COPY
    default_rotation = 0.0
    default_tileX = False
    default_tileY = False
    _textureSecondary = None

    def ApplyAttributes(self, attributes):
        VisibleBase.ApplyAttributes(self, attributes)
        self.texture = trinity.Tr2Sprite2dTexture()
        texturePath = attributes.get('texturePath', self.default_texturePath)
        if texturePath:
            self.SetTexturePath(texturePath)
        secondaryPath = attributes.get('textureSecondaryPath', self.default_textureSecondaryPath)
        if secondaryPath:
            self.SetSecondaryTexturePath(secondaryPath)
        self.glowFactor = attributes.get('glowFactor', self.default_glowFactor)
        self.glowExpand = attributes.get('glowExpand', self.default_glowExpand)
        self.glowColor = attributes.get('glowColor', self.default_glowColor)
        self.shadowOffset = attributes.get('shadowOffset', self.default_shadowOffset)
        self.shadowColor = attributes.get('shadowColor', self.default_shadowColor)
        rectLeft = attributes.rectLeft
        if rectLeft:
            self.rectLeft = rectLeft
        rectTop = attributes.rectTop
        if rectTop:
            self.rectLeft = rectTop
        rectWidth = attributes.rectWidth
        if rectWidth:
            self.rectWidth = rectWidth
        rectHeight = attributes.rectHeight
        if rectHeight:
            self.rectHeight = rectHeight
        self.translationPrimary = attributes.get('translationPrimary', self.default_translationPrimary)
        self.translationSecondary = attributes.get('translationSecondary', self.default_translationSecodary)
        self.spriteEffect = attributes.get('spriteEffect', self.default_spriteEffect)
        self.rotation = attributes.get('rotation', self.default_rotation)
        self.tileX = attributes.get('tileX', self.default_tileX)
        self.tileY = attributes.get('tileY', self.default_tileY)

    def Close(self):
        self._texture = None
        self._textureSecondary = None
        VisibleBase.Close(self)

    @apply
    def spriteEffect():
        doc = '\n        determines how the primary and secondary textures are blended together. Must be\n        a trinity.TR2_SFX_{X} constant'

        def fget(self):
            return self._spriteEffect

        def fset(self, value):
            self._spriteEffect = value
            ro = self.renderObject
            if ro and hasattr(ro, 'spriteEffect'):
                ro.spriteEffect = value

        return property(**locals())

    @apply
    def texture():
        doc = 'The primary texture. An instance of trinity.Tr2Sprite2dTexture'

        def fget(self):
            return self._texture

        def fset(self, value):
            self._texture = value
            ro = self.renderObject
            if ro:
                ro.texturePrimary = self._texture

        return property(**locals())

    @apply
    def textureSecondary():
        doc = 'The secondary texture. An instance of trinity.Tr2Sprite2dTexture'

        def fget(self):
            return self._textureSecondary

        def fset(self, value):
            self._textureSecondary = value
            ro = self.renderObject
            if ro and value is not None:
                ro.textureSecondary = value

        return property(**locals())

    @apply
    def rectLeft():
        doc = 'Manually set left edge of primary texture'

        def fget(self):
            return self._rectLeft

        def fset(self, value):
            self._rectLeft = value
            ro = self.renderObject
            if ro and ro.texturePrimary:
                ro.texturePrimary.srcX = value

        return property(**locals())

    @apply
    def rectTop():
        doc = 'Manually set top edge of primary texture'

        def fget(self):
            return self._rectTop

        def fset(self, value):
            self._rectTop = value
            ro = self.renderObject
            if ro and ro.texturePrimary:
                ro.texturePrimary.srcY = value

        return property(**locals())

    @apply
    def rectWidth():
        doc = 'Manually set width of primary texture'

        def fget(self):
            return self._rectWidth

        def fset(self, value):
            self._rectWidth = value
            ro = self.renderObject
            if ro and ro.texturePrimary:
                ro.texturePrimary.srcWidth = value

        return property(**locals())

    @apply
    def rectHeight():
        doc = 'Manually set height of primary texture'

        def fget(self):
            return self._rectHeight

        def fset(self, value):
            self._rectHeight = value
            ro = self.renderObject
            if ro and ro.texturePrimary:
                ro.texturePrimary.srcHeight = value

        return property(**locals())

    @apply
    def rectSecondary():
        doc = 'Manually set rect (srcX, srcY, srcWidth, srcHeight) of secondary texture'

        def fget(self):
            if self.textureSecondary:
                return (self.textureSecondary.srcX,
                 self.textureSecondary.srcY,
                 self.textureSecondary.srcWidth,
                 self.textureSecondary.srcHeight)

        def fset(self, value):
            if self.textureSecondary:
                self.textureSecondary.srcX, self.textureSecondary.srcY, self.textureSecondary.srcWidth, self.textureSecondary.srcHeight = value

        return property(**locals())

    @apply
    def translationPrimary():
        doc = 'Manually set translation of primary texture'

        def fget(self):
            if self.texture:
                return self.texture.translation

        def fset(self, value):
            if self.texture:
                self.texture.translation = value
                if value != (0, 0):
                    self.texture.useTransform = True
                    self._EnableStandAloneTexture(self.texture)

        return property(**locals())

    @apply
    def translationSecondary():
        doc = 'Manually set translation of secondary texture'

        def fget(self):
            if self.textureSecondary:
                return self.textureSecondary.translation

        def fset(self, value):
            if self.textureSecondary:
                self.textureSecondary.translation = value
                if value != (0, 0):
                    self.__EnableSecondaryTransform()

        return property(**locals())

    @apply
    def rotationSecondary():
        doc = 'Manually set rotation of secondary texture'

        def fget(self):
            if self.textureSecondary:
                return self.textureSecondary.rotation

        def fset(self, value):
            if self.textureSecondary:
                self.textureSecondary.rotation = value
                if value != 0.0:
                    self.__EnableSecondaryTransform()

        return property(**locals())

    @apply
    def scaleSecondary():
        doc = 'Manually set scale of secondary texture'

        def fget(self):
            if self.textureSecondary:
                return self.textureSecondary.scale

        def fset(self, value):
            if self.textureSecondary:
                self.textureSecondary.scale = value
                if value != (1.0, 1.0):
                    self.__EnableSecondaryTransform()

        return property(**locals())

    @apply
    def scalingCenterSecondary():
        doc = 'Manually set scale center of secondary texture'

        def fget(self):
            if self.textureSecondary:
                return self.textureSecondary.scalingCenter

        def fset(self, value):
            if self.textureSecondary:
                self.textureSecondary.scalingCenter = value

        return property(**locals())

    @apply
    def glowFactor():
        doc = 'Glow effect amount [0.0 - 1.0]'

        def fget(self):
            return self._glowFactor

        def fset(self, value):
            self._glowFactor = value
            ro = self.renderObject
            if ro:
                ro.glowFactor = value

        return property(**locals())

    @apply
    def glowExpand():
        doc = 'Glow effect expand [0.0 - inf]'

        def fget(self):
            return self._glowExpand

        def fset(self, value):
            self._glowExpand = value
            ro = self.renderObject
            if ro:
                ro.glowExpand = value

        return property(**locals())

    @apply
    def glowColor():
        doc = 'Glow effect color tuple (r,g,b,a) [0.0 - 1.0]'

        def fget(self):
            return self._glowColor

        def fset(self, value):
            self._glowColor = value
            ro = self.renderObject
            if ro:
                ro.glowColor = value

        return property(**locals())

    @apply
    def shadowOffset():
        doc = 'Shadow effect offset tuple (x,y) [0.0 - inf]'

        def fget(self):
            return self._shadowOffset

        def fset(self, value):
            self._shadowOffset = value
            ro = self.renderObject
            if ro:
                ro.shadowOffset = value

        return property(**locals())

    @apply
    def shadowColor():
        doc = 'Shadow effect color tuple (r,g,b,a) [0.0 - 1.0]'

        def fget(self):
            return self._shadowColor

        def fset(self, value):
            self._shadowColor = value
            ro = self.renderObject
            if ro:
                ro.shadowColor = value

        return property(**locals())

    @apply
    def rotation():
        doc = 'Set rotation of primary texture'

        def fget(self):
            if self.texture:
                return self.texture.rotation
            else:
                return 0

        def fset(self, value):
            if self.texture:
                self.texture.rotation = value
                if value != 0.0:
                    self.texture.useTransform = True
                    self._EnableStandAloneTexture(self.texture)

        return property(**locals())

    @apply
    def scale():
        doc = 'Manually set scaling of primary texture'

        def fget(self):
            if self.texture:
                return self.texture.scale

        def fset(self, value):
            if self.texture:
                self.texture.scale = value
                if value != (1.0, 1.0):
                    self.texture.useTransform = True
                    self._EnableStandAloneTexture(self.texture)

        return property(**locals())

    @apply
    def scalingCenter():
        doc = 'Manually set scale center of primary texture'

        def fget(self):
            if self.texture:
                return self.texture.scalingCenter

        def fset(self, value):
            if self.texture:
                self.texture.scalingCenter = value

        return property(**locals())

    @apply
    def tileX():
        doc = 'Set whether the texture should tile on X-axis'

        def fget(self):
            if self.texture:
                return self.texture.tileX

        def fset(self, value):
            if self.texture:
                self.texture.tileX = value
                if value:
                    self.texture.useTransform = True
                    self._EnableStandAloneTexture(self.texture)

        return property(**locals())

    @apply
    def tileY():
        doc = 'Set whether the texture should tile on Y-axis'

        def fget(self):
            if self.texture:
                return self.texture.tileY

        def fset(self, value):
            if self.texture:
                self.texture.tileY = value
                if value:
                    self.texture.useTransform = True
                    self._EnableStandAloneTexture(self.texture)

        return property(**locals())

    @apply
    def tileXSecondary():
        doc = 'Set whether the texture should tile on X-axis on secondary texture'

        def fget(self):
            if self.textureSecondary:
                return self.textureSecondary.tileX

        def fset(self, value):
            if self.textureSecondary:
                self.textureSecondary.tileX = value
                if value:
                    self.textureSecondary.useTransform = True
                    self._EnableStandAloneTexture(self.textureSecondary)

        return property(**locals())

    @apply
    def tileYSecondary():
        doc = 'Set whether the texture should tile on Y-axis on secondary texture'

        def fget(self):
            if self.textureSecondary:
                return self.textureSecondary.tileY

        def fset(self, value):
            if self.textureSecondary:
                self.textureSecondary.tileY = value
                if value:
                    self.textureSecondary.useTransform = True
                    self._EnableStandAloneTexture(self.textureSecondary)

        return property(**locals())

    def _EnableStandAloneTexture(self, texture):
        if getattr(texture, 'atlasTexture', None) is not None:
            texture.atlasTexture.isStandAlone = True

    def __EnableSecondaryTransform(self):
        self.textureSecondary.useTransform = True
        self._EnableStandAloneTexture(self.textureSecondary)

    def ReloadTexture(self):
        if self.texture:
            if self.texture.atlasTexture:
                self.texture.atlasTexture.Reload()

    def ReloadSecondaryTexture(self):
        if self.textureSecondary:
            if self.textureSecondary.atlasTexture:
                self.textureSecondary.atlasTexture.Reload()

    def SetTexturePath(self, texturePath):
        if self.texture:
            newPath = str(texturePath or '')
            if newPath != self.texture.resPath:
                self.texture.resPath = newPath

    LoadTexture = SetTexturePath

    def GetTexturePath(self):
        if self.texture:
            return self.texture.resPath

    texturePath = property(GetTexturePath, SetTexturePath)

    def SetSecondaryTexturePath(self, texturePath):
        if not self.textureSecondary:
            self.textureSecondary = trinity.Tr2Sprite2dTexture()
        self.textureSecondary.resPath = str(texturePath or '')

    def GetSecondaryTexturePath(self):
        if self.textureSecondary:
            return self.textureSecondary.resPath

    def SetRect(self, rectLeft, rectTop, rectWidth, rectHeight):
        self.rectLeft = rectLeft
        self.rectTop = rectTop
        self.rectWidth = rectWidth
        self.rectHeight = rectHeight

    def LoadIcon(self, iconNo, ignoreSize = False):
        if self.destroyed:
            return
        if iconNo.startswith('res:') or iconNo.startswith('cache:'):
            self.LoadTexture(iconNo)
            return
        if iconNo.startswith('ui_'):
            root, sheetNo, iconSize, icon = iconNo.split('_')
            resPath = 'res:/ui/texture/icons/%s_%s_%s.png' % (int(sheetNo), int(iconSize), int(icon))
            iconSize = int(iconSize)
            self.LoadTexture(resPath)
            if not ignoreSize and self.GetAlign() != uiconst.TOALL and self.texture.atlasTexture:
                self.width = iconSize
                self.height = iconSize
            return
        return iconNo


class Sprite(TexturedBase):
    __guid__ = 'uiprimitives.Sprite'
    __renderObject__ = trinity.Tr2Sprite2d
    isDragObject = True
    default_noScale = 0
    default_left = 0
    default_top = 0
    default_width = 0
    default_height = 0
    default_pickRadius = 0
    default_saturation = 1.0
    default_effectOpacity = 1.0
    default_useSizeFromTexture = False

    def ApplyAttributes(self, attributes):
        TexturedBase.ApplyAttributes(self, attributes)
        self.pickRadius = attributes.get('pickRadius', self.default_pickRadius)
        self.saturation = attributes.get('saturation', self.default_saturation)
        self.effectOpacity = attributes.get('effectOpacity', self.default_effectOpacity)
        self.renderObject.useSizeFromTexture = attributes.get('useSizeFromTexture', self.default_useSizeFromTexture)

    @apply
    def pickRadius():
        doc = 'Pick radius'

        def fget(self):
            return self._pickRadius

        def fset(self, value):
            self._pickRadius = value
            ro = self.renderObject
            if ro and hasattr(ro, 'pickRadius'):
                if value < 0:
                    ro.pickRadius = value
                else:
                    ro.pickRadius = uicore.ScaleDpi(value) or 0.0

        return property(**locals())

    @apply
    def useSizeFromTexture():
        doc = '\n            If set, displayWidth/Height are ignored and size of primary texture is used instead.\n            '

        def fget(self):
            return self._useSizeFromTexture

        def fset(self, value):
            self._useSizeFromTexture = value
            if self.renderObject:
                self.renderObject.useSizeFromTexture = value

        return property(**locals())

    @apply
    def saturation():
        doc = '\n        Saturation of texture when using TR2_SFX_COLOROVERLAY or TR2_SFX_SOFTLIGHT.\n        '

        def fget(self):
            return self._saturation

        def fset(self, value):
            self._saturation = value
            ro = self.renderObject
            if ro:
                ro.saturation = value or 0.0

        return property(**locals())

    @apply
    def effectOpacity():
        doc = '\n        Opacity of effect when using TR2_SFX_COLOROVERLAY or TR2_SFX_SOFTLIGHT.\n        '

        def fget(self):
            return self._effectOpacity

        def fset(self, value):
            self._effectOpacity = value
            ro = self.renderObject
            if ro:
                ro.effectOpacity = value or 0.0

        return property(**locals())


class StreamingVideoSprite(Sprite):
    __guid__ = 'uiprimitives.StreamingVideoSprite'
    __renderObject__ = trinity.Tr2Sprite2d
    __notifyevents__ = ['OnAudioActivated', 'OnAudioDeactivated']
    default_disableAudio = False
    default_videoPath = ''
    default_videoLoop = False
    default_videoAutoPlay = True
    default_muteAudio = False
    default_spriteEffect = trinity.TR2_SFX_NOALPHA

    def Close(self, *args, **kwds):
        self._DestroyVideo()
        Sprite.Close(self, *args, **kwds)

    def ApplyAttributes(self, attributes):
        Sprite.ApplyAttributes(self, attributes)
        sm.RegisterNotify(self)
        self.textureRes = trinity.TriTextureRes()
        self.texture = trinity.Tr2Sprite2dTexture()
        self.player = None
        self.path = None
        self.audioTrack = 0
        self.videoLoop = False
        self.emitter = None
        self._updateStep = None
        self._isFetchingFile = False
        RO = self.GetRenderObject()
        self.disableAudio = attributes.get('disableAudio', self.default_disableAudio)
        self._positionComponent = attributes.get('positionComponent', None)
        self.positionComponent = None
        if 'videoPath' in attributes and attributes['videoPath'] and attributes.get('videoAutoPlay', self.default_videoAutoPlay):
            self.SetVideoPath(attributes['videoPath'], attributes.get('audioTrack', 0), attributes.get('videoLoop', self.default_videoLoop))
        if 'pos' in attributes:
            pos = attributes.get('pos', (self.default_left,
             self.default_top,
             self.default_width,
             self.default_height))
            RO.displayX, RO.displayY, RO.displayWidth, RO.displayHeight = pos

    def OnVideoSizeAvailable(self, width, height):
        pass

    def OnVideoFinished(self):
        pass

    def _OnCreateTextures(self, player, width, height):
        try:
            self.textureRes = trinity.TriTextureRes(width, height, 1, trinity.PIXEL_FORMAT.B8G8R8A8_UNORM)
            player.bgra_texture = self.textureRes
            self.texture.atlasTexture = trinity.Tr2AtlasTexture()
            self.texture.atlasTexture.textureRes = self.textureRes
        except:
            logging.exception('Exception in VideoPlayer.on_create_textures')

    def _OnVideoStateChange(self, player):
        try:
            logging.debug('Video player state changed to %s', videoplayer.State.GetNameFromValue(player.state))
            if player.state == videoplayer.State.INITIAL_BUFFERING:
                info = self.player.get_video_info()
                self.OnVideoSizeAvailable(info['width'], info['height'])
            elif player.state == videoplayer.State.DONE:
                self.OnVideoFinished()
        except:
            logging.exception('Exception in VideoPlayer.on_state_change')

    def _OnVideoError(self):
        try:
            self.player.validate()
        except RuntimeError as e:
            logging.exception('Video player error')

    def _DestroyVideo(self):
        if self.positionComponent:
            self.positionComponent.UnRegisterPlacementObserverWrapper(self.positionObserver)
            self.positionComponent = None
            self.positionObserver = None
        self.emitter = None
        self.player = None
        self._updateStep = None
        self.textureRes = trinity.TriTextureRes()

    def OnAudioActivated(self):
        if self.path and not self._isFetchingFile:
            self.SetVideoPath(self.path, self.audioTrack, self.videoLoop)

    def OnAudioDeactivated(self):
        if self.path and not self._isFetchingFile:
            self.SetVideoPath(self.path, self.audioTrack, self.videoLoop)

    def SetPositionComponent(self, positionComponent):
        if self.emitter and positionComponent and GameWorld:
            self.positionObserver = GameWorld.PlacementObserverWrapper(self.emitter)
            positionComponent.RegisterPlacementObserverWrapper(self.positionObserver)
            return positionComponent

    def GetVideoSize(self):
        try:
            info = self.player.get_video_info()
            return (info['width'], info['height'])
        except (AttributeError, videoplayer.VideoPlayerError):
            pass

    def SetVideoPath(self, path, audioTrack = 0, videoLoop = False):
        self._DestroyVideo()
        self.path = path
        self.audioTrack = audioTrack
        self.videoLoop = videoLoop

        def prefetch():
            blue.paths.GetFileContentsWithYield(path)
            if self._isFetchingFile and path == self.path:
                self._isFetchingFile = False
                self.SetVideoPath(path, audioTrack, videoLoop)

        if path.lower().startswith('res:/'):
            if blue.remoteFileCache.FileExists(path):
                if not blue.paths.FileExistsLocally(path):
                    self._isFetchingFile = True
                    uthread.new(prefetch)
                    return
        if not self.disableAudio:
            is3D = self._positionComponent is not None
            self.emitter, outputChannel = uicore.audioHandler.GetAudioBus(is3D=is3D, rate=48000)
            self.positionComponent = self.SetPositionComponent(self._positionComponent)
        if path.lower().startswith('res:/') or path.find(':') < 2:
            stream = blue.paths.open(path)
        else:
            stream = blue.BlueNetworkStream(unicode(path).encode('utf-8'))
        if uicore.audioHandler.active and not self.disableAudio:
            sink = videoplayer.Audio2Sink(audio2.GetDirectSoundPtr(), audio2.GetStreamPositionPtr(), outputChannel)
        else:
            sink = None
        self.player = videoplayer.VideoPlayer(stream, sink, audioTrack, videoLoop)
        self.player.on_state_change = self._OnVideoStateChange
        self.player.on_create_textures = self._OnCreateTextures
        self.player.on_error = self._OnVideoError

    def Play(self):
        if self.player:
            self.player.resume()

    def Pause(self):
        if self.player:
            self.player.pause()

    def MuteAudio(self):
        try:
            self.player.audio_sink.volume = 0
        except AttributeError:
            pass

    def UnmuteAudio(self):
        try:
            self.player.audio_sink.volume = 1
        except AttributeError:
            pass

    def GetVolume(self):
        try:
            return self.player.audio_sink.volume
        except AttributeError:
            return 1

    def SetVolume(self, volume):
        try:
            self.player.audio_sink.volume = volume
        except AttributeError:
            pass

    def Seek(self, nanoseconds):
        try:
            self.player.seek(nanoseconds)
        except AttributeError:
            pass

    @apply
    def isMuted():
        doc = 'Is audio stream muted for this video'

        def fget(self):
            try:
                return self.player.audio_sink.volume == 0
            except AttributeError:
                return None

        return property(**locals())

    @apply
    def isPaused():
        doc = 'Is video paused'

        def fget(self):
            if self.player:
                return self.player.is_paused

        return property(**locals())

    @apply
    def isFinished():
        doc = 'Has video finished playing'

        def fget(self):
            if self.destroyed:
                return True
            if self._isFetchingFile:
                return False
            if self.player:
                return self.player.state == videoplayer.State.DONE

        return property(**locals())

    @apply
    def mediaTime():
        doc = 'Media playback time in nanoseconds'

        def fget(self):
            if self.player:
                return self.player.media_time

        return property(**locals())

    @apply
    def duration():
        doc = 'Total video duration in nanoseconds'

        def fget(self):
            if self.player:
                return self.player.duration

        return property(**locals())

    @apply
    def downloadedTime():
        doc = 'Media time downloaded from input stream in nanoseconds'

        def fget(self):
            if self.player:
                return self.player.downloaded_media_time

        return property(**locals())


class PyColor(object):

    def __init__(self, owner, r = 1.0, g = 1.0, b = 1.0, a = 1.0):
        self.owner = weakref.ref(owner)
        self._r = r
        self._g = g
        self._b = b
        self._a = a
        self.UpdateOwner()

    def UpdateOwner(self):
        owner = self.owner()
        if owner is not None:
            if owner.renderObject:
                owner.renderObject.color = (self._r,
                 self._g,
                 self._b,
                 self._a)

    @apply
    def r():
        doc = 'Red component of this color'

        def fget(self):
            return self._r

        def fset(self, value):
            self._r = value
            self.UpdateOwner()

        return property(**locals())

    @apply
    def g():
        doc = 'Green component of this color'

        def fget(self):
            return self._g

        def fset(self, value):
            self._g = value
            self.UpdateOwner()

        return property(**locals())

    @apply
    def b():
        doc = 'Blue component of this color'

        def fget(self):
            return self._b

        def fset(self, value):
            self._b = value
            self.UpdateOwner()

        return property(**locals())

    @apply
    def a():
        doc = 'Alpha component of this color'

        def fget(self):
            return self._a

        def fset(self, value):
            self._a = value
            self.UpdateOwner()

        return property(**locals())

    def SetRGB(self, r, g, b, a = 1.0):
        self.r = r
        self.g = g
        self.b = b
        self.a = a

    SetRGBA = SetRGB

    def GetRGB(self):
        return (self.r, self.g, self.b)

    def GetRGBA(self):
        return (self.r,
         self.g,
         self.b,
         self.a)

    def SetAlpha(self, a):
        self.a = a

    def GetAlpha(self):
        return self.a

    def GetHSV(self):
        return trinity.TriColor(*self.GetRGBA()).GetHSV()

    def SetHSV(self, h, s, v):
        c = trinity.TriColor()
        c.SetHSV(h, s, v)
        self.SetRGB(c.r, c.g, c.b)
