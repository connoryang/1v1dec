#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\projectdiscovery\client\projects\subcellular\categoryselector.py
import blue
import carbonui.const as uiconst
import localization
import trinity
import uicontrols
import uiprimitives
from carbonui.primitives.flowcontainer import FlowContainer
from carbonui.uianimations import animations
from eve.client.script.ui.control import themeColored
from eve.client.script.ui.control import tooltips
from eve.client.script.ui.tooltips.tooltipUtil import SetTooltipHeaderAndDescription
from eve.client.script.ui.tooltips.tooltipsWrappers import TooltipBaseWrapper
from projectdiscovery.client import const
from projectdiscovery.client.util.eventlistener import eventlistener, on_event
tooltips.SLEEPTIME_TIMETOLIVE_EDITABLE = 50

@eventlistener()

class CategorySelector(FlowContainer):
    default_name = 'CategorySelector'
    default_align = uiconst.TOPLEFT
    default_width = 405
    default_height = 405
    default_left = 31
    default_top = 65

    def ApplyAttributes(self, attributes):
        super(CategorySelector, self).ApplyAttributes(attributes)
        self.categories = attributes.get('categories')
        self.starting_scale = attributes.get('starting_scale')
        self.super_categories = []
        self.create_category_selector()
        self.resize_to_scale(self.starting_scale)
        self.cascade_categories_in()

    @on_event('OnProjectDiscoveryResized')
    def resize_to_scale(self, scale):
        self.SetSize(self.default_width * scale, self.default_height * scale)
        self.left = self.default_left * (1 / scale)

    def create_category_selector(self):
        for n, (key, supercategory) in enumerate(self.categories.iteritems()):
            self.super_categories.append(CategoryGroup(category=supercategory, parent=self, align=uiconst.NOALIGN, number=n, starting_scale=self.starting_scale))

    def cascade_categories_in(self):
        for super_cat in self.super_categories:
            animations.FadeIn(super_cat.category_group_hex, duration=0.5, curveType=uiconst.ANIM_OVERSHOT2)
            animations.FadeIn(super_cat.label, duration=0.5, curveType=uiconst.ANIM_OVERSHOT2)
            for sub_cat in super_cat.sub_categories:
                animations.SpGlowFadeIn(sub_cat.hexagon_outline, glowExpand=2)
                animations.SpGlowFadeOut(sub_cat.hexagon_outline, glowExpand=2)
                if sub_cat.unavailable:
                    animations.FadeIn(sub_cat, duration=0.5, curveType=uiconst.ANIM_OVERSHOT2, endVal=0.5)
                else:
                    animations.FadeIn(sub_cat, duration=0.5, curveType=uiconst.ANIM_OVERSHOT2)
                blue.synchro.Sleep(15)

    def cascade_categories_out(self):
        for super_cat in self.super_categories:
            animations.FadeOut(super_cat.category_group_hex, duration=0.5, curveType=uiconst.ANIM_OVERSHOT2)
            animations.FadeOut(super_cat.label, duration=0.5, curveType=uiconst.ANIM_OVERSHOT2)
            for sub_cat in super_cat.sub_categories:
                animations.FadeOut(sub_cat, duration=0.5, curveType=uiconst.ANIM_OVERSHOT2)
                blue.synchro.Sleep(15)

    def reset_categories(self):
        for super_cat in self.super_categories:
            for sub_cat in super_cat.sub_categories:
                sub_cat.reset()


@eventlistener()

class CategoryGroup(uiprimitives.Container):
    default_state = uiconst.UI_NORMAL
    default_height = 135
    MIN_WIDTH = 80
    HEX_WIDTH = 52
    HEX_HEIGHT = 46
    HEX_SPACING = 38.9
    CHAIN_TOP_OFFSET = 22
    TOP_OFFSET = {1: HEX_HEIGHT / 2,
     2: 0,
     0: HEX_HEIGHT}

    def ApplyAttributes(self, attributes):
        super(CategoryGroup, self).ApplyAttributes(attributes)
        category = attributes.get('category')
        number = attributes.get('number')
        self.starting_scale = attributes.get('starting_scale')
        self.sub_categories = []
        self.label = uicontrols.Label(name='categorygrouplabel', text=category['name'].upper(), parent=self, color=(1, 1, 1, 0.5), top=4, left=self.HEX_WIDTH, opacity=0, fontSize=20)
        self.original_label_fontsize = self.label.fontsize
        self.original_label_left = self.label.left
        self.original_label_top = self.label.top
        SetTooltipHeaderAndDescription(targetObject=self, headerText=category['name'], descriptionText=category['description'])
        self.category_group_hex = CategoryGroupHexagon(parent=self, category=category, number=number, top=0, left=0, width=self.HEX_WIDTH, height=self.HEX_HEIGHT, opacity=0, starting_scale=self.starting_scale)
        count = 1
        left = -self.HEX_SPACING
        self.width = self.HEX_WIDTH
        for subcat in category['children']:
            for cat in subcat['children']:
                pos = count % 3
                count += 1
                if pos is not 0:
                    left += self.HEX_SPACING
                    self.width += self.HEX_WIDTH
                self.sub_categories.append(CategoryHexagon(parent=self, category=cat, top=self.TOP_OFFSET[pos] + self.CHAIN_TOP_OFFSET, left=left, width=self.HEX_WIDTH, height=self.HEX_HEIGHT, opacity=0, starting_scale=self.starting_scale))

        if number == 3:
            self.width = 78
        else:
            self.width = self.width if self.width >= self.MIN_WIDTH else self.MIN_WIDTH
        self.default_width = self.width
        self.resize_to_scale(self.starting_scale)

    @on_event('OnProjectDiscoveryResized')
    def resize_to_scale(self, scale):
        self.label.left = self.original_label_left * scale
        self.label.top = self.original_label_top * scale
        self.label.fontsize = self.original_label_fontsize * scale
        self.SetSize(self.default_width * scale, self.default_height * scale)


class Hexagon(uiprimitives.Container):
    default_align = uiconst.TOPLEFT
    default_state = uiconst.UI_NORMAL
    default_pickRadius = -1

    def ApplyAttributes(self, attributes):
        super(Hexagon, self).ApplyAttributes(attributes)
        self.hexagon_outline = uiprimitives.Sprite(parent=self, texturePath='res:/UI/Texture/classes/ProjectDiscovery/hexOutline.png', align=uiconst.TOALL, state=uiconst.UI_DISABLED, color=(0.32, 0.32, 0.32, 1))


@eventlistener()

class CategoryGroupHexagon(Hexagon):
    default_state = uiconst.UI_DISABLED

    def ApplyAttributes(self, attributes):
        super(CategoryGroupHexagon, self).ApplyAttributes(attributes)
        self.original_width = attributes.get('width')
        self.original_height = attributes.get('height')
        self.starting_scale = attributes.get('starting_scale')
        self.originalFontSize = 20
        self.groupLabel = uicontrols.Label(name='groupLabel', text=str(attributes.get('number') + 1), parent=self, fontsize=self.originalFontSize, align=uiconst.CENTER, color=(1, 1, 1, 0.25))
        self.groupHexImage = uiprimitives.Sprite(parent=self, align=uiconst.TOALL, texturePath='res:/UI/Texture/classes/ProjectDiscovery/hexMask.png', state=uiconst.UI_DISABLED, color=(0.2, 0.2, 0.2, 1))
        self.resize_to_scale(self.starting_scale)

    @on_event('OnProjectDiscoveryResized')
    def resize_to_scale(self, scale):
        self.groupLabel.fontsize = self.originalFontSize * scale
        self.SetSize(self.original_width * scale, self.original_height * scale)


@eventlistener()

class CategoryHexagon(Hexagon):
    GLOW_ANIMATION = {'duration': 0.3,
     'curveType': uiconst.ANIM_OVERSHOT2}
    MIN_COLOR_VALUE = (0.5, 0.22, 0.17)
    MAX_COLOR_VALUE = (0.33, 0.49, 0.26)

    def ApplyAttributes(self, attributes):
        super(CategoryHexagon, self).ApplyAttributes(attributes)
        self.category = attributes.get('category')
        self.attributes = attributes
        self.id = self.category['id']
        self.excludes = self.category['excludes']
        self.reselect = False
        self.unavailable = False
        self.unclickable = False
        self.original_width = attributes.get('width')
        self.original_height = attributes.get('height')
        self.original_top = attributes.get('top')
        self.original_left = attributes.get('left')
        self.starting_scale = attributes.get('starting_scale')
        attributes['tooltipHeader'] = self.category['name']
        attributes['tooltipText'] = self.category.get('descriptionIdentification', self.category['description'])
        self.consensus_percentage = uicontrols.Label(parent=self, align=uiconst.CENTER, text='0', fontsize=16, state=uiconst.UI_HIDDEN)
        self.exclude_texture = uiprimitives.Sprite(parent=self, texturePath='res:/UI/Texture/classes/ProjectDiscovery/categoryUnavailable.png', state=uiconst.UI_HIDDEN, align=uiconst.TOALL)
        self.selected_texture = uiprimitives.Sprite(name='selected_texture', parent=self, texturePath='res:/UI/Texture/classes/ProjectDiscovery/categorySelected.png', align=uiconst.TOALL, opacity=0, idx=0, state=uiconst.UI_DISABLED, padding=(-8, -8, -8, -8))
        self.correct_texture = uiprimitives.Sprite(parent=self, texturePath='res:/UI/Texture/classes/ProjectDiscovery/categoryMatch.png', opacity=0, idx=0, state=uiconst.UI_DISABLED, align=uiconst.TOALL, padding=(-8, -8, -8, -8))
        self.unmatched_texture = uiprimitives.Sprite(parent=self, texturePath='res:/UI/Texture/classes/ProjectDiscovery/categoryWrong.png', align=uiconst.TOALL, padding=(-8, -8, -8, -8), opacity=0, idx=0, state=uiconst.UI_DISABLED)
        self.missed_texture = uiprimitives.Sprite(parent=self, texturePath='res:/UI/Texture/classes/ProjectDiscovery/categoryMissed.png', align=uiconst.TOALL, padding=(-8, -8, -8, -8), opacity=0, idx=0, state=uiconst.UI_DISABLED)
        self.color_overlay = uiprimitives.Sprite(parent=self, align=uiconst.TOALL, texturePath='res:/UI/Texture/classes/ProjectDiscovery/hexMask.png', textureSecondaryPath='res:/UI/Texture/classes/ProjectDiscovery/hexMask.png', spriteEffect=trinity.TR2_SFX_MASK, state=uiconst.UI_DISABLED, opacity=0, padding=(5, 5, 5, 5))
        self.image = uiprimitives.Sprite(name='image', parent=self, align=uiconst.TOALL, texturePath='res:/UI/Texture/classes/ProjectDiscovery/subcellular/' + self.category['url'][:-4] + '_NA.png', textureSecondaryPath='res:/UI/Texture/classes/ProjectDiscovery/hexMask.png', spriteEffect=trinity.TR2_SFX_MASK, state=uiconst.UI_DISABLED)
        self.tooltipPanelClassInfo = CategoryTooltipWrapper(header=attributes['tooltipHeader'], description=attributes['tooltipText'], imagePath='res:/UI/Texture/classes/ProjectDiscovery/subcellular/' + self.category['url'][:-4] + '_NA.png', category=self.category)
        self.resize_to_scale(self.starting_scale)

    @on_event('OnProjectDiscoveryResized')
    def resize_to_scale(self, scale):
        self.SetSize(self.original_width * scale, self.original_height * scale)
        self.top = self.original_top * scale
        self.left = self.original_left * scale
        self.selected_texture.padding = (-8 * scale,
         -8 * scale,
         -8 * scale,
         -8 * scale)
        self.unmatched_texture.padding = (-8 * scale,
         -8 * scale,
         -8 * scale,
         -8 * scale)
        self.missed_texture.padding = (-8 * scale,
         -8 * scale,
         -8 * scale,
         -8 * scale)
        self.correct_texture.padding = (-8 * scale,
         -8 * scale,
         -8 * scale,
         -8 * scale)

    def OnMouseEnter(self, *args):
        if not self.unavailable:
            animations.SpGlowFadeIn(self.hexagon_outline, glowExpand=2, duration=0.3)

    def OnMouseExit(self, *args):
        if not self.unavailable:
            animations.SpGlowFadeOut(self.hexagon_outline, glowExpand=2, duration=0.3)

    def set_percentage(self, percentage):
        self.consensus_percentage.state = uiconst.UI_DISABLED
        self.consensus_percentage.SetText(percentage + '%')

    def hide_percentage_and_color_overlay(self):
        self.consensus_percentage.SetAlpha(0)
        self.color_overlay.SetAlpha(0)

    def show_percentage_and_color_overlay(self):
        self.consensus_percentage.SetAlpha(1)
        if not self.consensus_percentage.text == '0%':
            self.color_overlay.SetAlpha(1)

    def set_unavailable(self):
        self.unavailable = True
        self.image.SetTexturePath('res:/UI/Texture/classes/ProjectDiscovery/subcellular/gray_' + self.category['url'])
        self.tooltipPanelClassInfo = None

    def set_available(self):
        self.unavailable = False
        self.image.SetTexturePath('res:/UI/Texture/classes/ProjectDiscovery/subcellular/' + self.category['url'][:-4] + '_NA.png')
        self.tooltipPanelClassInfo = CategoryTooltipWrapper(header=self.attributes['tooltipHeader'], description=self.attributes['tooltipText'], imagePath='res:/UI/Texture/classes/ProjectDiscovery/subcellular/' + self.category['url'][:-4] + '_NA.png', category=self.category)

    def set_selected(self):
        self.category['selected'] = True
        animations.FadeIn(self.selected_texture, **self.GLOW_ANIMATION)

    def set_unselected(self):
        self.category['selected'] = False
        animations.FadeOut(self.selected_texture, **self.GLOW_ANIMATION)

    def set_unclickable(self):
        self.unclickable = True

    def set_clickable(self):
        self.unclickable = False

    def lerp(self, value, maximum, start_point, end_point):
        return start_point + (end_point - start_point) * value / maximum

    def lerp_color(self, value, maximum, start_point = MIN_COLOR_VALUE, end_point = MAX_COLOR_VALUE):
        r = self.lerp(value, maximum, start_point[0], end_point[0])
        g = self.lerp(value, maximum, start_point[1], end_point[1])
        b = self.lerp(value, maximum, start_point[2], end_point[2])
        return (r,
         g,
         b,
         1)

    def OnClick(self, *args):
        if self.exclude_texture.state is not uiconst.UI_HIDDEN or self.unclickable is True:
            return
        sm.GetService('audio').SendUIEvent(const.Sounds.CategorySelectPlay)
        self.category['selected'] = not self.category['selected']
        if self.category['selected']:
            animations.FadeIn(self.selected_texture, **self.GLOW_ANIMATION)
        else:
            animations.FadeOut(self.selected_texture, **self.GLOW_ANIMATION)
        sm.ScatterEvent(const.Events.CategoryChanged, self)

    def GetTooltipPosition(self, *args):
        return self.GetAbsolute()

    @on_event(const.Events.ExcludeCategories)
    def on_exclude_categories(self, excluder, excluded):
        cat_id = self.category['id']
        if excluder is cat_id:
            self.category['excluded'] = False
            return
        if '*' in excluded or cat_id in excluded:
            self.category['excluded'] = True
            self.exclude_texture.state = uiconst.UI_DISABLED
            self.selected_texture.opacity = 0
        else:
            self.category['excluded'] = False
            self.exclude_texture.state = uiconst.UI_HIDDEN
            if self.category['selected']:
                self.selected_texture.opacity = 1

    @on_event(const.Events.ContinueFromTrainingResult)
    def reset(self):
        self.category['selected'] = False
        self.category['excluded'] = False
        self.correct_texture.opacity = 0
        self.unmatched_texture.opacity = 0
        self.missed_texture.opacity = 0
        self.selected_texture.opacity = 0
        self.exclude_texture.state = uiconst.UI_HIDDEN


@eventlistener()

class CategoryTooltipWrapper(TooltipBaseWrapper):
    IMAGE_SIZE = 300

    def __init__(self, header, description, imagePath, category, *args, **kwargs):
        self._headerText = header
        self._descriptionText = description
        self._imagePath = imagePath
        self.category = category

    def CreateTooltip(self, parent, owner, idx):
        self.tooltipPanel = tooltips.TooltipPanel(parent=parent, owner=owner, idx=idx)
        self.tooltipPanel.LoadGeneric1ColumnTemplate()
        self.tooltipPanel.SetState(uiconst.UI_NORMAL)
        self.add_description_label()
        self.add_main_image_container()
        self.add_example_images()
        animations.FadeIn(self.imageOverlaySprite, timeOffset=0.1, duration=2, curveType=uiconst.ANIM_OVERSHOT5)
        return self.tooltipPanel

    def get_image_paths_for_category(self):
        image_paths = []
        for imageFileName in blue.paths.listdir('res:/UI/Texture/classes/ProjectDiscovery/subcellular/' + str(self.category['id'])):
            path = 'res:/UI/Texture/classes/ProjectDiscovery/subcellular/%s/%s' % (str(self.category['id']), imageFileName)
            image_paths.append(path)

        return image_paths

    def add_example_images(self):
        image_paths = self.get_image_paths_for_category()
        self.tooltipPanel.AddLabelMedium(text=localization.GetByLabel('UI/ProjectDiscovery/TooltipExamplesLabel'), bold=True, cellPadding=(0, 5, 0, 5), wrapWidth=300)
        image_icon_container = uiprimitives.Container(width=self.IMAGE_SIZE, height=75, align=uiconst.TOPLEFT)
        themeColored.FrameThemeColored(bgParent=image_icon_container, colorType=uiconst.COLORTYPE_UIHILIGHT)
        for imagePath in image_paths:
            TooltipExampleSprite(name='TooltipExampleSprite', parent=uiprimitives.Container(parent=image_icon_container, width=self.IMAGE_SIZE / len(image_paths), align=uiconst.TOLEFT), align=uiconst.TOALL, padding=(5, 5, 5, 5), texturePath=imagePath, originalPath=self._imagePath)

        self.tooltipPanel.AddCell(image_icon_container, cellPadding=(0, 5, 0, 5))

    def add_main_image_container(self):
        image_container = uiprimitives.Container(width=self.IMAGE_SIZE, height=self.IMAGE_SIZE, align=uiconst.TOPLEFT)
        themeColored.FrameThemeColored(bgParent=image_container, colorType=uiconst.COLORTYPE_UIHILIGHT)
        self.imageOverlaySprite = uiprimitives.Sprite(parent=image_container, width=self.IMAGE_SIZE - 2, height=self.IMAGE_SIZE - 2, texturePath='res:/UI/Texture/classes/ProjectDiscovery/subcellular/' + self.category['url'][:-4] + '_A.png', align=uiconst.CENTER, opacity=0)
        self.imageSprite = uiprimitives.Sprite(parent=image_container, width=self.IMAGE_SIZE - 2, height=self.IMAGE_SIZE - 2, texturePath=self._imagePath, align=uiconst.CENTER)
        self.tooltipPanel.AddCell(image_container, cellPadding=(0, 5, 0, 5))

    def add_description_label(self):
        self.tooltipPanel.AddLabelMedium(text=self._headerText, bold=True, cellPadding=(0, 5, 0, 5), wrapWidth=300)
        self.tooltipPanel.AddLabelMedium(text=self._descriptionText, align=uiconst.TOPLEFT, wrapWidth=300, color=(0.6, 0.6, 0.6, 1))

    @on_event(const.Events.TooltipTextureChanged)
    def switch_main_tooltip_image(self, path):
        if hasattr(self, 'imageSprite'):
            self.fade_out_tooltip_image(path)
            self.fade_out_annotation()

    def fade_out_tooltip_image(self, path):
        animations.FadeOut(self.imageSprite, duration=0.15, callback=lambda : self.set_image_path(path))

    def set_image_path(self, path):
        self.imageSprite.SetTexturePath(path)
        animations.FadeIn(self.imageSprite, duration=0.15)
        if path == self._imagePath:
            self.fade_in_annotation()

    def fade_in_annotation(self):
        animations.FadeIn(self.imageOverlaySprite, timeOffset=0.1, duration=2, curveType=uiconst.ANIM_OVERSHOT5)

    def fade_out_annotation(self):
        animations.FadeOut(self.imageOverlaySprite, duration=0.15)


class TooltipExampleSprite(uiprimitives.Sprite):

    def ApplyAttributes(self, attributes):
        super(TooltipExampleSprite, self).ApplyAttributes(attributes)
        self.frame = themeColored.FrameThemeColored(bgParent=self.parent, colorType=uiconst.COLORTYPE_UIHILIGHT)
        self.frame.SetAlpha(0)
        self.path = attributes.get('texturePath')
        self.original_path = attributes.get('originalPath')

    def OnMouseEnter(self, *args):
        sm.ScatterEvent(const.Events.TooltipTextureChanged, self.path)
        self.frame.SetAlpha(1)

    def OnMouseExit(self, *args):
        sm.ScatterEvent(const.Events.TooltipTextureChanged, self.original_path)
        self.frame.SetAlpha(0)
