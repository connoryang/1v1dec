#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\projectdiscovery\client\projects\subcellular\taskimages.py
import logging
import math
import os
import blue
import carbonui.const as uiconst
import localization
import uicontrols
import uiprimitives
from carbon.common.script.util.format import FmtAmt
from carbonui.primitives.base import ScaleDpi, ReverseScaleDpi
from carbonui.uianimations import animations
from eve.client.script.ui.control.eveLabel import EveCaptionSmall
from eve.client.script.ui.control.eveLoadingWheel import LoadingWheel
from eve.client.script.ui.services.evePhotosvc import NONE_PATH
from projectdiscovery.client import const
from projectdiscovery.client.util.eventlistener import eventlistener, on_event
logger = logging.getLogger(__name__)
PROCESSING_LABEL_DEFAULT_WIDTH = 225
PROCESSING_LABEL_HEIGHT = 20
PROCESSING_LABEL_FONT_SIZE = 18

@eventlistener()

class TaskImage(uiprimitives.Container):
    ORIGINAL_HEIGHT = 420
    ORIGINAL_WIDTH = 420

    def ApplyAttributes(self, attributes):
        super(TaskImage, self).ApplyAttributes(attributes)
        self.reset_color_channels()
        self.all_selected = False
        self.service = sm.RemoteSvc('ProjectDiscovery')
        self.photo_service = sm.GetService('photo')
        self.audio_service = sm.GetService('audio')
        self.is_zoom_fixed = False
        self.cacheID = None
        self.setup_layout()
        self.oldTranslationTop = self.expandTopContainer.translation
        self.oldTranslationBottom = self.expandBottomContainer.translation
        self.resize_to_scale(attributes.get('starting_scale'))

    def setup_layout(self):
        self.transmitting_container = uiprimitives.Container(name='transmitting_container', parent=self, align=uiconst.CENTER, width=self.width, height=70, top=-15, opacity=0, state=uiconst.UI_DISABLED)
        self._create_processing_label()
        self.expandTopContainer = uiprimitives.Container(name='expandTopContainer', parent=self.transmitting_container, width=364, height=8, align=uiconst.TOTOP)
        self.expandTop = uiprimitives.Sprite(name='expandTop', parent=self.expandTopContainer, texturePath='res:/UI/Texture/classes/ProjectDiscovery/expandTop.png', width=174, height=5, align=uiconst.CENTERTOP)
        self.original_expand_width = self.expandTop.width
        self.expandBracketTop = uiprimitives.Sprite(name='expandbracketsTop', parent=self.expandTopContainer, texturePath='res:/UI/Texture/classes/ProjectDiscovery/expandBrackets.png', width=364, height=3, align=uiconst.CENTERTOP, top=5)
        self.original_expand_bracket_width = self.expandBracketTop.width
        self.expandBottomContainer = uiprimitives.Transform(name='expandBottomContainer', parent=self.transmitting_container, width=364, height=8, align=uiconst.TOBOTTOM, rotation=math.pi)
        self.expandBracketBot = uiprimitives.Sprite(name='expandbracketBot', parent=self.expandBottomContainer, texturePath='res:/UI/Texture/classes/ProjectDiscovery/expandBrackets.png', width=364, height=3, align=uiconst.CENTERTOP, top=5)
        self.expandBot = uiprimitives.Sprite(name='expandBot', parent=self.expandBottomContainer, texturePath='res:/UI/Texture/classes/ProjectDiscovery/expandTop.png', width=174, height=5, align=uiconst.CENTERBOTTOM, top=3)
        self.expandGradient = uiprimitives.Sprite(parent=self.transmitting_container, align=uiconst.CENTER, width=364, height=64, texturePath='res:/UI/Texture/classes/ProjectDiscovery/expandGradient.png')
        self.colorFilterContainer = uiprimitives.Container(name='colorFilterContainer', parent=self, align=uiconst.TOBOTTOM_PROP, height=0.065)
        self.colorFilterButtonsContainer = uiprimitives.Container(name='colorFilterButtonsContainer', parent=self.colorFilterContainer, align=uiconst.CENTERTOP, width=120, height=24)
        self.colorCube = uicontrols.ButtonIcon(name='colorCube', parent=self.colorFilterButtonsContainer, align=uiconst.TOLEFT, width=30, height=24, opacity=2, texturePath='res:/UI/Texture/classes/ProjectDiscovery/colorFilterCube.png', func=self.toggle_all_channels)
        self.colorCube.icon.SetSize(30, 24)
        self.colorCubeSelectedSprite = uiprimitives.Sprite(name='selectedFilter', parent=self.colorFilterButtonsContainer, width=30, height=24, align=uiconst.TOPLEFT, texturePath='res:/UI/Texture/classes/ProjectDiscovery/colorFilterSelection.png')
        self.colorSwatchRed = uicontrols.ButtonIcon(parent=self.colorFilterButtonsContainer, align=uiconst.TOLEFT, width=30, height=24, texturePath='res:/UI/Texture/classes/ProjectDiscovery/colorFilterSwatch_R.png', func=self.toggle_red_channel)
        self.colorSwatchRed.icon.SetSize(30, 24)
        self.redSelectedSprite = uiprimitives.Sprite(name='selectedFilter', parent=self.colorFilterButtonsContainer, width=30, height=24, align=uiconst.TOPLEFT, texturePath='res:/UI/Texture/classes/ProjectDiscovery/colorFilterSelection.png', left=30, opacity=0)
        self.colorSwatchGreen = uicontrols.ButtonIcon(name='colorSwatchGreen', parent=self.colorFilterButtonsContainer, align=uiconst.TOLEFT, width=30, height=24, texturePath='res:/UI/Texture/classes/ProjectDiscovery/colorFilterSwatch_G.png', func=self.toggle_green_channel)
        self.colorSwatchGreen.icon.SetSize(30, 24)
        self.greenSelectedSprite = uiprimitives.Sprite(name='selectedFilter', parent=self.colorFilterButtonsContainer, width=30, height=24, align=uiconst.TOPLEFT, texturePath='res:/UI/Texture/classes/ProjectDiscovery/colorFilterSelection.png', left=60, opacity=0)
        self.colorSwatchBlue = uicontrols.ButtonIcon(parent=self.colorFilterButtonsContainer, align=uiconst.TOLEFT, width=30, height=24, iconSize=30, texturePath='res:/UI/Texture/classes/ProjectDiscovery/colorFilterSwatch_B.png', func=self.toggle_blue_channel)
        self.colorSwatchBlue.icon.SetSize(30, 24)
        self.blueSelectedSprite = uiprimitives.Sprite(name='selectedFilter', parent=self.colorFilterButtonsContainer, width=30, height=24, align=uiconst.TOPLEFT, texturePath='res:/UI/Texture/classes/ProjectDiscovery/colorFilterSelection.png', left=90, opacity=0)
        self.colorFilterBack = uiprimitives.Sprite(parent=self.colorFilterContainer, align=uiconst.CENTERTOP, width=187, height=32, texturePath='res:/UI/Texture/classes/ProjectDiscovery/colorFilterBack.png')
        self.images_container = uiprimitives.Container(name='ImagesContainer', parent=self, align=uiconst.TOPLEFT_PROP, clipChildren=True, width=self.ORIGINAL_WIDTH, height=self.ORIGINAL_HEIGHT)
        self.image_locked_sprite = uiprimitives.Sprite(name='lockImage', parent=self.images_container, texturePath='res:/UI/Texture/classes/ProjectDiscovery/magnifyLocked.png', width=54, height=64, align=uiconst.CENTER, opacity=0, state=uiconst.UI_DISABLED)
        self.image_unlocked_sprite = uiprimitives.Sprite(name='unlockImage', parent=self.images_container, texturePath='res:/UI/Texture/classes/ProjectDiscovery/magnifyUnlocked.png', width=108, height=64, align=uiconst.CENTER, opacity=0, state=uiconst.UI_DISABLED)
        self.image_container = uiprimitives.Container(name='mainImageContainer', parent=self.images_container, align=uiconst.TOALL, clipChildren=True)
        self.image_frame = uicontrols.Frame(name='imageFrame', bgParent=self.images_container, texturePath='res:/UI/Texture/classes/ProjectDiscovery/SampleBack.png', cornerSize=20)
        self.loading_wheel = LoadingWheel(name='SampleLoadingIndicator', parent=self.images_container, align=uiconst.CENTER, width=64, height=64)
        self.image_sprite = SubCellularSprite(name='mainImage', parent=self.image_container, align=uiconst.TOALL, opacity=1, pos=(10, 10, 10, 10))
        self.image_sprite.texture = None
        self.mini_map_container = uiprimitives.Container(name='miniMapContainer', parent=self.images_container, align=uiconst.BOTTOMRIGHT, width=100, height=100, top=12, left=12)
        self.mini_map_container_frame = uicontrols.Frame(name='zoomContainerFrame', parent=self.mini_map_container, state=uiconst.UI_HIDDEN)
        self.mini_map_frame_container = uiprimitives.Container(name='miniMapFrameContainer', parent=self.mini_map_container, align=uiconst.TOPLEFT, width=30, height=30)
        self.mini_map_frame = uicontrols.Frame(name='zoomFrame', parent=self.mini_map_frame_container, state=uiconst.UI_HIDDEN)
        self.mini_map_image_sprite = uiprimitives.Sprite(name='miniMapSprite', parent=self.mini_map_container, width=100, height=100)
        self.zoom_image_container = uiprimitives.Container(name='zoomContainer', parent=self.images_container, align=uiconst.TOALL, clipChildren=True, pos=(10, 10, 10, 10))
        self.zoom_image_sprite = uiprimitives.Sprite(name='zoomSprite', parent=self.zoom_image_container, align=uiconst.TOALL, opacity=0, pos=(0, 0, -1200, -1200))
        self.error_message = uicontrols.Label(parent=self.images_container, align=uiconst.CENTER, text=localization.GetByLabel('UI/ProjectDiscovery/NoImageErrorLabel'), opacity=0)

    def _create_processing_label(self):
        self.label_container = uiprimitives.Container(parent=self.transmitting_container, height=PROCESSING_LABEL_HEIGHT, align=uiconst.CENTER, fontsize=PROCESSING_LABEL_FONT_SIZE)
        self.processing_message_label = EveCaptionSmall(parent=self.label_container, align=uiconst.CENTERLEFT, text=localization.GetByLabel('UI/ProjectDiscovery/Subcellular/RewardsScreen/ProcessingLabel'))
        self.processing_percentage = EveCaptionSmall(parent=self.label_container, align=uiconst.CENTERRIGHT, text=str(FmtAmt(0)) + '%')
        self.label_container.width = self._get_processing_text_width()

    def _resize_processing_label(self):
        self.label_container.width = self._get_processing_text_width()

    def _get_processing_text_width(self):
        processing_message_text_width = self.processing_message_label.textwidth
        processing_percentage_text_width = self._get_processing_percentage_max_text_width()
        text_width = processing_message_text_width + processing_percentage_text_width
        if text_width > 0:
            return text_width
        return PROCESSING_LABEL_DEFAULT_WIDTH

    def _get_processing_percentage_max_text_width(self):
        max_percentage_text = str(FmtAmt(100)) + '%'
        return uicore.font.GetTextWidth(max_percentage_text, self.processing_percentage.fontsize, self.processing_percentage.letterspace, self.processing_percentage.uppercase)

    @on_event('OnWindowClosed')
    def on_window_closed(self, wndID, wndCaption, wndGUID):
        self.delete_previous_image()

    @on_event('OnProjectDiscoveryResized')
    def resize_to_scale(self, scale):
        if self.is_zoom_fixed:
            self.is_zoom_fixed = False
            self.show_main_image()
            self.fade_in_unlock()
        self.reset_animation()
        self.SetSize(self.ORIGINAL_WIDTH * scale, 445 * scale)
        self.images_container.SetSize(self.ORIGINAL_WIDTH * scale, self.ORIGINAL_HEIGHT * scale)
        self.transmitting_container.SetSize(self.width, self.transmitting_container.height)
        self._resize_processing_label()
        self.expandTop.width = self.original_expand_width * scale
        self.expandBot.width = self.expandTop.width
        self.expandBracketTop.width = self.original_expand_bracket_width * scale
        self.expandBracketBot.width = self.expandBracketTop.width

    def toggle_green_channel(self):
        if self.all_selected:
            self.all_selected = False
            self.red_channel = 0
            self.blue_channel = 0
        if self.green_channel == 1:
            self.green_channel = 0
            self.greenSelectedSprite.SetAlpha(0)
        else:
            self.green_channel = 1
            self.greenSelectedSprite.SetAlpha(1)
        self.set_color_channels()
        if self.is_zoom_fixed:
            self.hide_main_image()

    def toggle_blue_channel(self):
        if self.all_selected:
            self.all_selected = False
            self.green_channel = 0
            self.red_channel = 0
        if self.blue_channel == 1:
            self.blue_channel = 0
            self.blueSelectedSprite.SetAlpha(0)
        else:
            self.blue_channel = 1
            self.blueSelectedSprite.SetAlpha(1)
        self.set_color_channels()
        if self.is_zoom_fixed:
            self.hide_main_image()

    def toggle_red_channel(self):
        if self.all_selected:
            self.all_selected = False
            self.green_channel = 0
            self.blue_channel = 0
        if self.red_channel == 1:
            self.red_channel = 0
            self.redSelectedSprite.SetAlpha(0)
        else:
            self.red_channel = 1
            self.redSelectedSprite.SetAlpha(1)
        self.set_color_channels()
        if self.is_zoom_fixed:
            self.hide_main_image()

    def toggle_all_channels(self):
        self.reset_color_selection()
        self.reset_color_channels()
        self.image_sprite.SetRGB(1, 1, 1)
        self.zoom_image_sprite.SetRGB(1, 1, 1)
        self.mini_map_image_sprite.SetRGB(1, 1, 1)
        if self.is_zoom_fixed:
            self.hide_main_image()

    def reset_color_channels(self):
        self.red_channel = 0
        self.green_channel = 0
        self.blue_channel = 0

    def reset_color_selection(self):
        self.redSelectedSprite.SetAlpha(0)
        self.greenSelectedSprite.SetAlpha(0)
        self.blueSelectedSprite.SetAlpha(0)
        self.colorCubeSelectedSprite.SetAlpha(1)
        self.all_selected = True

    def hide_main_image(self):
        self.image_sprite.SetAlpha(0)

    def set_color_channels(self):
        self.colorCubeSelectedSprite.SetAlpha(0)
        self.audio_service.SendUIEvent(const.Sounds.ColorSelectPlay)
        self.image_sprite.SetRGB(self.red_channel, self.green_channel, self.blue_channel)
        self.zoom_image_sprite.SetRGB(self.red_channel, self.green_channel, self.blue_channel)
        self.mini_map_image_sprite.SetRGB(self.red_channel, self.green_channel, self.blue_channel)

    def load_image(self):
        self.hide_error_message()
        self.show_loading_wheel()
        self.stop_loop_sound_and_play_load_sound()
        self.image_sprite.texture = self.photo_service.GetTextureFromURL(self.image_url, dontcache=1, ignoreCache=1)[0]
        self.cacheID = self.image_sprite.texturePath.split('/')[-1:][0][:-5]
        self.zoom_image_sprite.texture = self.image_sprite.texture
        self.mini_map_image_sprite.texture = self.image_sprite.texture
        self.check_if_image_loaded()

    def delete_previous_image(self):
        if self.cacheID:
            file_path = '%sBrowser/Img/%s.%s' % (blue.paths.ResolvePath(u'cache:/'), self.cacheID, 'jpeg')
            try:
                os.remove(file_path)
            except WindowsError:
                pass

    def check_if_image_loaded(self):
        if self.image_sprite.texture.resPath == NONE_PATH or not self.image_sprite or not self.image_sprite.texture:
            logger.error('ProjectDiscovery::load_image: Image failed to load URL: %s' % self.image_url)
            self.hide_loading_wheel()
            self.show_error_message()
        else:
            self.hide_loading_wheel()
            self.stop_load_sound_and_play_open_and_loop_sound()
            sm.ScatterEvent(const.Events.MainImageLoaded)

    def stop_load_sound_and_play_open_and_loop_sound(self):
        if Audio.play_sound:
            self.audio_service.SendUIEvent(const.Sounds.MainImageLoadStop)
            self.audio_service.SendUIEvent(const.Sounds.MainImageOpenPlay)
            self.audio_service.SendUIEvent(const.Sounds.MainImageLoopPlay)

    def stop_loop_sound_and_play_load_sound(self):
        if Audio.play_sound:
            self.audio_service.SendUIEvent(const.Sounds.MainImageLoopStop)
            self.audio_service.SendUIEvent(const.Sounds.MainImageLoadPlay)

    def show_loading_wheel(self):
        self.loading_wheel.SetAlpha(1)

    def hide_loading_wheel(self):
        self.loading_wheel.SetAlpha(0)

    def show_error_message(self):
        self.error_message.SetAlpha(1)

    def hide_error_message(self):
        self.error_message.SetAlpha(0)

    def show_minimap_frames(self):
        self.mini_map_frame.state = uiconst.UI_NORMAL
        self.mini_map_container_frame.state = uiconst.UI_NORMAL

    def hide_minimap_frames(self):
        self.mini_map_container_frame.state = uiconst.UI_HIDDEN
        self.mini_map_frame.state = uiconst.UI_HIDDEN

    def remove_all_textures(self):
        self.image_sprite.texture = None
        self.zoom_image_sprite.texture = None
        self.mini_map_image_sprite.texture = None

    def show_retry_button(self):
        self.retry_button.SetState(uiconst.UI_NORMAL)

    def hide_retry_button(self):
        self.retry_button.SetState(uiconst.UI_HIDDEN)

    @on_event(const.Events.NewTask)
    def on_new_task(self, task):
        self.image_url = task['assets']['url']
        self.load_image()
        self.toggle_all_channels()
        self.image_sprite.SetAlpha(1)
        self.is_zoom_fixed = False

    def reset_image(self):
        if hasattr(self, 'image_sprite'):
            self.hide_error_message()
            self.remove_all_textures()
            self.delete_previous_image()
            self.hide_minimap_frames()
            self.image_frame.SetRGB(1, 1, 1, 0.5)
            self.show_loading_wheel()

    @on_event(const.Events.ClickMainImage)
    def fix_post(self):
        animations.FadeTo(self.image_frame, duration=0.3, endVal=2.0, startVal=1.0, curveType=uiconst.ANIM_BOUNCE)
        self.is_zoom_fixed = not self.is_zoom_fixed
        if self.is_zoom_fixed:
            self.fade_in_lock()
        else:
            self.fade_in_unlock()

    def fade_in_lock(self):
        animations.FadeIn(self.image_locked_sprite, duration=0.3, endVal=0.5, callback=self.fade_out_lock)

    def fade_out_lock(self):
        animations.FadeOut(self.image_locked_sprite, duration=0.5)

    def fade_in_unlock(self):
        animations.FadeIn(self.image_unlocked_sprite, duration=0.3, endVal=0.5, callback=self.fade_out_unlock)

    def fade_out_unlock(self):
        animations.FadeOut(self.image_unlocked_sprite, duration=0.5)

    @on_event(const.Events.HoverMainImage)
    def zoom_in(self):
        if not self.image_sprite.texture or self.image_sprite.texture.resPath.startswith('res:'):
            return
        if self.is_zoom_fixed:
            uicore.uilib.SetCursor(uiconst.UICURSOR_POINTER)
        else:
            self.show_zoom_image()
            self.hide_main_image()
            self.show_minimap_frames()
            uicore.uilib.SetCursor(uiconst.UICURSOR_MAGNIFIER)
            mouse_position = (uicore.uilib.x, uicore.uilib.y)
            img_position = self.image_sprite.GetAbsolutePosition()
            if self.is_mouse_out_of_bounds(mouse_position, img_position):
                return
            zoom_aspect_ratio = ScaleDpi(self.zoom_image_sprite._displayWidth) / float(self.image_sprite._displayWidth) - 1
            self.zoom_image_sprite.displayX = (img_position[0] - mouse_position[0]) * zoom_aspect_ratio
            self.zoom_image_sprite.displayY = (img_position[1] - mouse_position[1]) * zoom_aspect_ratio
            self.mini_map_frame_container.displayX = self.zoom_image_sprite.displayX / -17
            self.mini_map_frame_container.displayY = self.zoom_image_sprite.displayY / -17

    def is_mouse_out_of_bounds(self, mouse_position, img_position):
        if mouse_position[0] < img_position[0]:
            return True
        elif mouse_position[0] > img_position[0] + ReverseScaleDpi(self.image_sprite.displayWidth):
            return True
        elif mouse_position[1] < img_position[1]:
            return True
        elif mouse_position[1] > img_position[1] + ReverseScaleDpi(self.image_sprite.displayHeight):
            return True
        else:
            return False

    @on_event(const.Events.MouseExitMainImage)
    def on_mouse_exit_main_image(self):
        animations.FadeTo(self.image_frame, duration=0.3, endVal=0.5, startVal=1.0)
        self.hide_mini_map()
        if not self.is_zoom_fixed:
            self.hide_zoom_image()
            self.show_main_image()
            uicore.uilib.SetCursor(uiconst.UICURSOR_POINTER)

    def show_zoom_image(self):
        self.zoom_image_sprite.SetAlpha(1)

    def hide_zoom_image(self):
        self.zoom_image_sprite.SetAlpha(0)

    def show_main_image(self):
        self.image_sprite.SetAlpha(1)

    @on_event(const.Events.MouseEnterMainImage)
    def on_mouse_enter_main_image(self):
        self.show_mini_map()
        animations.FadeIn(self.image_frame, duration=0.3)

    def show_mini_map(self):
        self.mini_map_container.SetOpacity(1)

    def hide_mini_map(self):
        self.mini_map_container.SetOpacity(0)

    def reset_animation(self):
        self.expandTopContainer.translation = self.oldTranslationTop
        self.expandBottomContainer.translation = self.oldTranslationBottom
        self.expandGradient.height = 64

    @property
    def gradient_height(self):
        return self._gradient_height

    @gradient_height.setter
    def gradient_height(self, value):
        self._gradient_height = value
        self.expandGradient.SetSize(364, self._gradient_height)

    def gradient_height_callback(self):
        self.gradient_height = self.images_container.displayHeight
        animations.FadeOut(self.transmitting_container, callback=self.reset_animation)
        self.fade_in_active_image()
        sm.ScatterEvent(const.Events.TransmissionFinished)

    def fade_in_active_image(self):
        if self.is_zoom_fixed:
            animations.FadeIn(self.zoom_image_sprite)
        else:
            animations.FadeIn(self.image_sprite)

    @property
    def percentage(self):
        return self._percentage

    @percentage.setter
    def percentage(self, value):
        self._percentage = value
        self.processing_percentage.SetText(str(FmtAmt(self._percentage)) + '%')

    def percentage_callback(self):
        self.percentage = 100
        self.move_image_out()
        sm.ScatterEvent(const.Events.PercentageCountFinished)
        self.audio_service.SendUIEvent(const.Sounds.ProcessingStop)
        self.audio_service.SendUIEvent(const.Sounds.AnalysisDonePlay)

    def start_transmission_animation(self):
        self.reset_animation()
        self.audio_service.SendUIEvent(const.Sounds.ProcessingPlay)
        self.hide_mini_map()
        self.percentage = 0
        self.move_image_in()
        self.fade_out_active_image()
        animations.FadeIn(self.transmitting_container, duration=0.5)
        self.start_percentage_count()

    def fade_out_active_image(self):
        if self.is_zoom_fixed:
            animations.FadeTo(self.zoom_image_sprite, startVal=1.0, endVal=0.5)
            self.image_sprite.SetAlpha(0)
        else:
            animations.FadeTo(self.image_sprite, startVal=1.0, endVal=0.5)
            self.hide_zoom_image()

    def start_percentage_count(self):
        animations.MorphScalar(self, 'percentage', startVal=self.percentage, endVal=100, curveType=uiconst.ANIM_SMOOTH, duration=2.5, callback=self.percentage_callback)

    def expand_screen(self):
        self.oldTranslationTop = self.expandTopContainer.translation
        self.oldTranslationBottom = self.expandBottomContainer.translation
        translationtop = (self.expandTopContainer.displayX, -self.images_container.displayHeight / 2.5)
        translationbottom = (self.expandBottomContainer.displayX, -self.images_container.displayHeight / 2.5)
        self.image_frame.SetRGB(0.498, 0.627, 0.74, 0.5)
        animations.MoveTo(self.expandTopContainer, startPos=(0, 0), endPos=translationtop, duration=0.3, curveType=uiconst.ANIM_LINEAR)
        animations.MoveTo(self.expandBottomContainer, startPos=(0, 0), endPos=translationbottom, duration=0.3, curveType=uiconst.ANIM_LINEAR)
        animations.MorphScalar(self, 'gradient_height', startVal=48, endVal=self.images_container.displayHeight, curveType=uiconst.ANIM_LINEAR, duration=0.3, callback=self.gradient_height_callback)
        self.audio_service.SendUIEvent(const.Sounds.AnalysisWindowMovePlay)

    def move_image_in(self):
        animations.SpShadowAppear(self.image_sprite, duration=1, curveType=uiconst.ANIM_BOUNCE)
        end_pos = (self.parent.parent.parent.parent.displayWidth / 2 - self.width / 1.8, 20)
        animations.MoveTo(self.parent, startPos=(0, 20), endPos=end_pos, duration=1)

    def move_image_out(self):
        animations.SpShadowDisappear(self.image_sprite, duration=1, curveType=uiconst.ANIM_BOUNCE)
        start_pos = (self.parent.parent.parent.parent.displayWidth / 2 - self.width / 1.8, 20)
        animations.MoveTo(self.parent, startPos=start_pos, endPos=(0, 20), duration=1, timeOffset=0.8, callback=self.expand_screen)


class Audio():

    def __init__(self):
        _play_sound = True

    @property
    def play_sound(self):
        return self._play_sound

    @play_sound.setter
    def play_sound(self, val):
        self._play_sound = val


class SubCellularSprite(uiprimitives.Sprite):

    def OnMouseMove(self, *args):
        sm.ScatterEvent(const.Events.HoverMainImage)

    def OnMouseExit(self, *args):
        sm.ScatterEvent(const.Events.MouseExitMainImage)

    def OnMouseEnter(self, *args):
        sm.ScatterEvent(const.Events.MouseEnterMainImage)

    def OnMouseDownDrag(self, *args):
        sm.ScatterEvent(const.Events.ClickMainImage)
