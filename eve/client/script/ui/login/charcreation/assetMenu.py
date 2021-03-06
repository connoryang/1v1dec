#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\login\charcreation\assetMenu.py
import uicontrols
import carbonui.const as uiconst
import uicls
import random
import uiprimitives
import uthread
import uiutil
import charactercreator.const as ccConst
import ccUtil
import blue
import types
import base
import service
import localization
import evegraphics.settings as gfxsettings
HAIRDARKNESS = 'hari_darkness'
HAIRSATURATION = 'hari_saturation'
GROUPNAMES = {ccConst.SKINGROUP: 'UI/Login/CharacterCreation/AssetMenu/Groups/Complexion',
 ccConst.HAIRGROUP: 'UI/Login/CharacterCreation/AssetMenu/Groups/Hair',
 ccConst.EYESGROUP: 'UI/Login/CharacterCreation/AssetMenu/Groups/Eyes',
 ccConst.MAKEUPGROUP: 'UI/Login/CharacterCreation/AssetMenu/Groups/Makeup',
 ccConst.SKINDETAILSGROUP: 'UI/Login/CharacterCreation/AssetMenu/Groups/SkinDetails',
 ccConst.CLOTHESGROUP: 'UI/Login/CharacterCreation/AssetMenu/Groups/Clothes',
 ccConst.BODYGROUP: 'UI/Login/CharacterCreation/AssetMenu/Groups/Shape',
 ccConst.BACKGROUNDGROUP: 'UI/Login/CharacterCreation/AssetMenu/Groups/Backgrounds',
 ccConst.POSESGROUP: 'UI/Login/CharacterCreation/AssetMenu/Groups/Poses',
 ccConst.LIGHTSGROUP: 'UI/Login/CharacterCreation/AssetMenu/Groups/Lights',
 ccConst.PIERCINGGROUP: 'UI/Login/CharacterCreation/AssetMenu/Groups/Piercings',
 ccConst.TATTOOGROUP: 'UI/Login/CharacterCreation/AssetMenu/Groups/Tattoos',
 ccConst.SCARSGROUP: 'UI/Login/CharacterCreation/AssetMenu/Groups/Scars',
 ccConst.PROSTHETICS: 'UI/Login/CharacterCreation/AssetMenu/Groups/Prosthetics',
 ccConst.AUGMENTATIONS: 'UI/Login/CharacterCreation/AssetMenu/Groups/Augmentations'}
commonModifiersDisplayNames = {ccConst.eyes: 'UI/Login/CharacterCreation/AssetMenu/ModifierNames/Eyes',
 ccConst.hair: 'UI/Login/CharacterCreation/AssetMenu/ModifierNames/HairStyle',
 ccConst.eyebrows: 'UI/Login/CharacterCreation/AssetMenu/ModifierNames/Eyebrows',
 ccConst.skintone: 'UI/Login/CharacterCreation/AssetMenu/ModifierNames/SkinTone',
 ccConst.skinaging: 'UI/Login/CharacterCreation/AssetMenu/ModifierNames/Aging',
 ccConst.scarring: 'UI/Login/CharacterCreation/AssetMenu/ModifierNames/Scarring',
 ccConst.freckles: 'UI/Login/CharacterCreation/AssetMenu/ModifierNames/Freckles',
 ccConst.glasses: 'UI/Login/CharacterCreation/AssetMenu/ModifierNames/Clothing/Glasses',
 ccConst.muscle: 'UI/Login/CharacterCreation/AssetMenu/ModifierNames/Muscularity',
 ccConst.weight: 'UI/Login/CharacterCreation/AssetMenu/ModifierNames/Weight',
 ccConst.topmiddle: 'UI/Login/CharacterCreation/AssetMenu/ModifierNames/Clothing/TopMiddleLayer',
 ccConst.topouter: 'UI/Login/CharacterCreation/AssetMenu/ModifierNames/Clothing/TopOuterLayer',
 ccConst.bottomouter: 'UI/Login/CharacterCreation/AssetMenu/ModifierNames/Clothing/BottomOuterLayer',
 ccConst.outer: 'UI/Login/CharacterCreation/AssetMenu/ModifierNames/Clothing/OuterLayer',
 ccConst.bottommiddle: 'UI/Login/CharacterCreation/AssetMenu/ModifierNames/Clothing/BottomMiddleLayer',
 ccConst.feet: 'UI/Login/CharacterCreation/AssetMenu/ModifierNames/Clothing/FeetLayer',
 ccConst.p_earslow: 'UI/Login/CharacterCreation/AssetMenu/ModifierNames/Piercings/EarsLow',
 ccConst.p_earshigh: 'UI/Login/CharacterCreation/AssetMenu/ModifierNames/Piercings/EarsHigh',
 ccConst.p_nose: 'UI/Login/CharacterCreation/AssetMenu/ModifierNames/Piercings/Nose',
 ccConst.p_nostril: 'UI/Login/CharacterCreation/AssetMenu/ModifierNames/Piercings/Nostril',
 ccConst.p_brow: 'UI/Login/CharacterCreation/AssetMenu/ModifierNames/Piercings/Eyebrows',
 ccConst.p_lips: 'UI/Login/CharacterCreation/AssetMenu/ModifierNames/Piercings/Lips',
 ccConst.p_chin: 'UI/Login/CharacterCreation/AssetMenu/ModifierNames/Piercings/Chin',
 ccConst.t_head: 'UI/Login/CharacterCreation/AssetMenu/ModifierNames/Tattoos/Head',
 ccConst.t_armleft: 'UI/Login/CharacterCreation/AssetMenu/ModifierNames/Tattoos/ArmLeft',
 ccConst.t_armright: 'UI/Login/CharacterCreation/AssetMenu/ModifierNames/Tattoos/ArmRight',
 ccConst.s_head: 'UI/Login/CharacterCreation/AssetMenu/ModifierNames/Scars/Head',
 ccConst.skintype: 'UI/Login/CharacterCreation/AssetMenu/ModifierNames/Skintype',
 ccConst.pr_armleft: 'UI/Login/CharacterCreation/AssetMenu/ModifierNames/Prosthetics/ArmLeft',
 ccConst.pr_armright: 'UI/Login/CharacterCreation/AssetMenu/ModifierNames/Prosthetics/ArmRight',
 ccConst.augm_face: 'UI/Login/CharacterCreation/AssetMenu/ModifierNames/Augmentations/Face'}
maleModifierDisplayNames = {ccConst.eyeshadow: 'UI/Login/CharacterCreation/AssetMenu/ModifierNames/EyeDetails',
 ccConst.eyeliner: 'UI/Login/CharacterCreation/AssetMenu/ModifierNames/LashThickness',
 ccConst.lipstick: 'UI/Login/CharacterCreation/AssetMenu/ModifierNames/LipTone',
 ccConst.blush: 'UI/Login/CharacterCreation/AssetMenu/ModifierNames/CheekColor',
 ccConst.beard: 'UI/Login/CharacterCreation/AssetMenu/ModifierNames/FacialHair'}
maleModifierDisplayNames.update(commonModifiersDisplayNames)
femaleModifierDisplayNames = {ccConst.eyeshadow: 'UI/Login/CharacterCreation/AssetMenu/ModifierNames/EyeShadow',
 ccConst.eyeliner: 'UI/Login/CharacterCreation/AssetMenu/ModifierNames/Eyeliner',
 ccConst.lipstick: 'UI/Login/CharacterCreation/AssetMenu/ModifierNames/Lipstick',
 ccConst.blush: 'UI/Login/CharacterCreation/AssetMenu/ModifierNames/Blush'}
femaleModifierDisplayNames.update(commonModifiersDisplayNames)

class CharCreationAssetMenu(uiprimitives.Container):
    __guid__ = 'uicls.CharCreationAssetMenu'

    def ApplyAttributes(self, attributes):
        uiprimitives.Container.ApplyAttributes(self, attributes)
        self.name = attributes.menuType or 'CharCreationAssetMenu'
        sm.GetService('cc').LogInfo('CharCreationAssetMenu::ApplyAttributes:: name = ', self.name)
        if attributes.genderID == 0:
            modifierNames = femaleModifierDisplayNames
        else:
            modifierNames = maleModifierDisplayNames
        self.sr.mainCont = uiprimitives.Container(parent=self, name='mainAssetMenuCont', align=uiconst.TOTOP, state=uiconst.UI_PICKCHILDREN, height=self.height)
        self.sr.mainCont.clipChildren = 1
        self.togglerIdx = None
        self.toggleFunc = attributes.toggleFunc
        if self.toggleFunc:
            self.togglerIdx = idx = attributes.get('togglerIdx', -1)
            if idx == -1:
                padTop = 16
                padBottom = 4
            else:
                padTop = 4
                padBottom = 16
            self.sr.menuToggler = uicls.CharCreationMenuToggler(parent=self.sr.mainCont, caption=localization.GetByLabel('UI/Login/CharacterCreation/AssetMenu/BodyModifications'), padTop=padTop, padBottom=padBottom, menuType=attributes.menuType, func=self.ToggleMenu, idx=idx)
        for groupID, modifiers in attributes.groups:
            if type(groupID) == types.IntType:
                caption = localization.GetByLabel(GROUPNAMES.get(groupID, 'UI/Login/CharacterCreation/AssetMenu/MissingCaption'))
            else:
                caption = localization.GetByLabel(modifierNames.get(groupID, 'UI/Login/CharacterCreation/AssetMenu/MissingCaption'))
            group = uicls.CharCreationAssetPicker(parent=self.sr.mainCont, modifier=groupID, caption=caption, padTop=4, padBottom=4, genderID=attributes.genderID, bloodlineID=attributes.bloodlineID, charID=attributes.charID, isSubmenu=False, groupID=groupID)
            for modifier in modifiers:
                if type(modifier) is not types.IntType:
                    itemTypes, activeIndex = uicore.layer.charactercreation.GetAvailableStyles(modifier)
                    if not itemTypes:
                        continue
                caption = localization.GetByLabel(modifierNames.get(modifier, 'UI/Login/CharacterCreation/AssetMenu/MissingCaption'))
                picker = uicls.CharCreationAssetPicker(parent=self.sr.mainCont, modifier=modifier, caption=caption, padTop=-2, padBottom=4, genderID=attributes.genderID, bloodlineID=attributes.bloodlineID, isSubmenu=True, groupID=groupID)

        menuState = settings.user.ui.Get('assetMenuState', {ccConst.BODYGROUP: True})
        for pickerContainer in self.sr.mainCont.children:
            if isinstance(pickerContainer, uicls.CharCreationMenuToggler):
                continue
            key = pickerContainer.modifier or 'group_%s' % getattr(pickerContainer, 'groupID', '')
            if not pickerContainer.isSubmenu and menuState.get(key, 0):
                pickerContainer.Expand(initing=True)

        if self.togglerIdx and self.sr.menuToggler:
            uiutil.SetOrder(self.sr.menuToggler, self.togglerIdx)

    def ToggleMenu(self, *args):
        if self.toggleFunc:
            if self.togglerIdx == -1:
                top = self.sr.menuToggler.absoluteTop - self.absoluteTop + self.sr.menuToggler.height + self.sr.menuToggler.padBottom + 10
                self.sr.mainCont.height = top
            self.toggleFunc()

    def CheckIfOversize(self, currentPicker = None):
        canCollapse = []
        totalExpandedHeight = 0
        for each in self.sr.mainCont.children:
            if not isinstance(each, uicls.CharCreationAssetPicker):
                continue
            if each.state == uiconst.UI_HIDDEN:
                continue
            if each.IsExpanded():
                if not each.isSubmenu:
                    subs = each.GetMySubmenus()
                    totalExpandedHeight += each.padTop + each.GetExpandedHeight() + each.padBottom
                    someSubExpanded = False
                    for sub in subs:
                        if sub.IsExpanded():
                            someSubExpanded = True
                            break

                    if not someSubExpanded:
                        canCollapse.append((each._expandTime, each))
                else:
                    totalExpandedHeight += each.padTop + each.GetExpandedHeight() + each.padBottom
                if each is not currentPicker and each.isSubmenu:
                    canCollapse.append((each._expandTime, each))
            else:
                totalExpandedHeight += each.padTop + each.GetCollapsedHeight() + each.padBottom

        canCollapse.sort()
        availableSpace = uicore.desktop.height - 130
        if totalExpandedHeight > availableSpace:
            diff = totalExpandedHeight - availableSpace
            for expandTime, each in canCollapse:
                if each.IsExpanded():
                    uthread.new(each.Collapse)
                    diff -= each.GetExpandedHeight() - each.GetCollapsedHeight()
                if diff <= 0:
                    break

    def ChangeHeight(self, newHeight):
        self.height = newHeight
        self.sr.mainCont.height = newHeight


class CCColorPalette(uicontrols.ContainerAutoSize):
    __guid__ = 'uicls.CCColorPalette'
    default_state = uiconst.UI_NORMAL
    default_opacity = 0.0
    default_left = 6
    default_top = 22
    SIDEMARGIN = 6
    TOPMARGIN = 6
    COLORSIZE = 14
    MINCOLORSIZE = 10
    COLORGAP = 0
    COLORMARGIN = 1
    COLORPALETTEWIDTH = 124

    def ApplyAttributes(self, attributes):
        uiprimitives.Container.ApplyAttributes(self, attributes)
        self.modifier = attributes.modifier
        self.primaryColors = None
        self.secondaryColors = None
        self.OnSetValue = attributes.OnSetValue
        self.maxHeight = attributes.maxHeight or 200
        self.maxWidth = attributes.maxWidth
        self.startingWidth = self.width
        self.currentNumColorAreas = None
        self.browseFunction = attributes.browseFunction
        self.browseText = attributes.browseText
        self.isLights = attributes.isLights
        self._expanded = False
        self.sr.fadeInThread = None
        self.sr.fadeOutThread = None
        self.PrepareControls()

    def Close(self):
        if self.sr.mouseOverTimer:
            self.sr.mouseOverTimer.KillTimer()
        uiprimitives.Container.Close(self)

    def PrepareControls(self, reloading = None, *args):
        info = uicore.layer.charactercreation.GetInfo()
        charSvc = sm.GetService('character')
        sliders = []
        if info.genderID == ccConst.GENDERID_FEMALE:
            facialHairText = localization.GetByLabel('UI/Login/CharacterCreation/AssetMenu/EyebrowsColor')
        else:
            facialHairText = localization.GetByLabel('UI/Login/CharacterCreation/AssetMenu/FacialHairColor')
        if ccUtil.HasUserDefinedWeight(self.modifier):
            sliders += [('intensity', localization.GetByLabel('UI/Login/CharacterCreation/AssetMenu/MakeupOpacity'), charSvc.GetWeightByCategory(info.charID, self.modifier))]
        if info.genderID == ccConst.GENDERID_FEMALE and ccUtil.HasUserDefinedSpecularity(self.modifier):
            sliders += [('specularity', localization.GetByLabel('UI/Login/CharacterCreation/AssetMenu/LipGloss'), charSvc.GetColorSpecularityByCategory(info.charID, self.modifier))]
        if self.modifier == ccConst.hair:
            sliders += [(HAIRDARKNESS, facialHairText, charSvc.GetHairDarkness(info.charID))]
        elif self.isLights:
            if not uicore.layer.charactercreation.IsSlowMachine():
                sliders += [('lights', localization.GetByLabel('UI/Login/CharacterCreation/AssetMenu/Intensity'), uicore.layer.charactercreation.GetLightIntensity())]
        self.Flush()
        self.height = 0
        self.width = self.startingWidth
        self.currentColorSize = self.COLORSIZE
        self.PrepareTuckControls()
        for referenceName, label, currentValue in sliders:
            extraParameters = {}
            if referenceName == 'intensity':
                sliderClass = uicls.GradientSlider
                extraParameters = {'alphaValues': (0, 0)}
            elif referenceName == HAIRDARKNESS:
                sliderClass = uicls.GradientSlider
            else:
                sliderClass = uicls.BitSlider
            modifier = self.modifier or 'NotReallyModifier'
            slider = sliderClass(parent=self, name=(modifier + '_slider'), padTop=20, padLeft=6, align=uiconst.TOTOP, setvalue=currentValue, OnSetValue=self.SetSliderValue, sliderWidth=(self.COLORPALETTEWIDTH - self.SIDEMARGIN * 2 + 1), bitHeight=6, idx=0, left=self.SIDEMARGIN, **extraParameters)
            slider.modifier = modifier
            slider.sliderType = referenceName
            self.sr.Set(referenceName, slider)
            label = uicls.CCLabel(parent=slider, uppercase=1, shadowOffset=(0, 0), fontsize=9, letterspace=2, text=label, width=slider.width, color=ccConst.COLOR50)
            label.top = -label.textheight - 1

        self.previousWidth = self.width
        self.activePrimary = None
        self.activeSecondary = None
        if self.modifier in ccConst.COLORMAPPING:
            if reloading == 'oldColors':
                self.LoadColors(self.primaryColors, self.secondaryColors)
            else:
                self.PrepareCategoryColorOptions()
        self.SetGradientsColor()
        self.SetSizeAutomatically()
        self.sr.mouseOverTimer = base.AutoTimer(50, self.CheckMouseOver)

    def SetSizeAutomatically(self):
        uicontrols.ContainerAutoSize.SetSizeAutomatically(self)
        if self.height > 0:
            self.padBottom = -8
        else:
            self.padBottom = 0

    def PrepareTuckControls(self, *args):
        self.sr.tuckParent = uiprimitives.Container(parent=self, name='tuckParent', align=uiconst.TOTOP, top=8, height=56, state=uiconst.UI_HIDDEN, padLeft=self.SIDEMARGIN, padRight=self.SIDEMARGIN)
        if self.isLights:
            browseText = localization.GetByLabel('UI/Login/CharacterCreation/AssetMenu/BrowseLightColors')
        else:
            browseText = localization.GetByLabel('UI/Login/CharacterCreation/AssetMenu/Tucking')
        label = uicls.CCLabel(parent=self.sr.tuckParent, uppercase=1, shadowOffset=(0, 0), fontsize=9, letterspace=2, text=browseText, top=0, left=0, color=ccConst.COLOR50, idx=0)
        self.sr.tuckParent.sr.countLabel = uicls.CCLabel(parent=self.sr.tuckParent, uppercase=1, shadowOffset=(0, 0), fontsize=9, letterspace=2, text='', top=16, left=0, color=ccConst.COLOR50, idx=0)
        tuckingCont = self.sr.tuckParent
        buttonWidth = int((self.width - 16) / 2.0)
        backButton = uicls.CharCreationButton(parent=tuckingCont, name='leftBtn', align=uiconst.TOPLEFT, top=32, func=self.OnTuckButtonClicked)
        backButton.icon = uicontrols.Icon(name='BackIcon', icon=ccConst.ICON_BACK, parent=backButton, state=uiconst.UI_PICKCHILDREN, align=uiconst.CENTER)
        nextButton = uicls.CharCreationButton(parent=tuckingCont, name='rightBtn', align=uiconst.TOPRIGHT, top=32, func=self.OnTuckButtonClicked)
        nextButton.icon = uicontrols.Icon(name='NextIcon', icon=ccConst.ICON_NEXT, parent=nextButton, state=uiconst.UI_PICKCHILDREN, align=uiconst.CENTER)
        backButton.width = nextButton.width = buttonWidth

    def SetTuckingCounter(self, current = 0, total = 0):
        self.sr.tuckParent.sr.countLabel.text = '%s/%s' % (current, total)

    def OnTuckButtonClicked(self, btn):
        if self.browseFunction is not None:
            self.browseFunction(btn)

    def SetGradientsColor(self, displayColor = None):
        slidersToColor = []
        if self.activePrimary is None:
            return
        for slider in [getattr(self.sr, HAIRDARKNESS, None), getattr(self.sr, 'intensity', None)]:
            if slider is None:
                continue
            if displayColor is None:
                displayColor = self.activePrimary.displayColor
            slidersToColor.append(slider)

        if displayColor is None:
            return
        gradientColor = (1.0, displayColor[:3])
        for slider in slidersToColor:
            slider.ChangeGradientColor(secondColor=gradientColor)

    def CheckMouseOver(self, *args):
        if uicore.uilib.leftbtn or uicore.uilib.rightbtn:
            return
        if self.parent is None:
            return
        grandParent = self.parent.parent
        if uicore.uilib.mouseOver is self or uicore.uilib.mouseOver is grandParent or uiutil.IsUnder(uicore.uilib.mouseOver, grandParent):
            if grandParent.sr.browser and grandParent.IsExpanded():
                activeData = grandParent.sr.browser.GetActiveData()
                if not activeData:
                    return
                self.ExpandPalette()
                return
        if self._expanded:
            self.CollapsePalette()

    def ExpandPalette(self, *args):
        if self.sr.fadeOutThread:
            self.sr.fadeOutThread.kill()
            self.sr.fadeOutThread = None
        if self.sr.fadeInThread:
            return
        self._expanded = True
        self.left = 0
        self.sr.fadeInThread = uthread.new(self.ShowPalette_thread)

    def ShowPalette_thread(self, *args):
        if self and not self.destroyed:
            self.state = uiconst.UI_NORMAL
        uicore.effect.CombineEffects(self, opacity=1.0, time=500.0)

    def CollapsePalette(self, push = False, *args):
        if self.sr.fadeInThread:
            self.sr.fadeInThread.kill()
            self.sr.fadeInThread = None
        if self.sr.fadeOutThread:
            return
        self._expanded = False
        if push:
            uicore.effect.CombineEffects(self, left=-self.COLORPALETTEWIDTH, opacity=0.0, time=150.0)
        else:
            self.sr.fadeOutThread = uthread.new(self.HidePalette_thread)

    def HidePalette_thread(self, *args):
        uicore.effect.CombineEffects(self, opacity=0.0, time=750.0)
        if self and not self.destroyed:
            self.state = uiconst.UI_HIDDEN

    def PrepareCategoryColorOptions(self):
        info = uicore.layer.charactercreation.GetInfo()
        categoryColors = sm.GetService('character').GetAvailableColorsForCategory(self.modifier, info.genderID, info.bloodlineID)
        if not categoryColors:
            return
        primary, secondary = categoryColors
        self.hasSecondary = bool(secondary)
        uicore.layer.charactercreation.ValidateColors(self.modifier)
        self.LoadColors(primary, secondary)
        self.primaryColors = primary
        self.secondaryColors = secondary

    def UpdatePalette(self):
        self.HiliteActive()

    def HiliteActive(self):
        info = uicore.layer.charactercreation.GetInfo()
        charSvc = sm.GetService('character')
        currentPrimaryName, currentSecondaryName = charSvc.GetTypeColors(info.charID, self.modifier)
        if not currentPrimaryName:
            return
        if getattr(self, 'colorControlsCont', None) is None:
            return
        for each in self.colorControlsCont.children:
            if not getattr(each, 'colorValue', None):
                continue
            each.sr.activeFrame.state = uiconst.UI_HIDDEN
            if not self.hasSecondary:
                if each.colorName == currentPrimaryName:
                    each.sr.activeFrame.state = uiconst.UI_DISABLED
                    self.activePrimary = each
                continue
            if each.colorName == currentPrimaryName:
                each.sr.activeFrame.state = uiconst.UI_DISABLED
                self.activePrimary = each
            elif each.colorName == currentSecondaryName:
                each.sr.activeFrame.state = uiconst.UI_DISABLED
                self.activeSecondary = each

    def GetNumColorAreas(self, *args):
        info = uicore.layer.charactercreation.GetInfo()
        activeMod = sm.GetService('character').GetModifierByCategory(info.charID, self.modifier)
        if activeMod:
            return activeMod.metaData.numColorAreas

    def TryReloadColors(self, *args):
        numColorAreas = self.GetNumColorAreas()
        if numColorAreas is not None and self.currentNumColorAreas != numColorAreas:
            self.PrepareControls(reloading='oldColors')

    def LoadColors(self, primary, secondary):
        for each in self.children[:]:
            if each.name == 'colorPar':
                each.Close()

        if self.modifier == ccConst.hair:
            firstColourCaption = localization.GetByLabel('UI/Login/CharacterCreation/AssetMenu/HairRootColor')
            secondColourCaption = localization.GetByLabel('UI/Login/CharacterCreation/AssetMenu/HairColor')
        else:
            firstColourCaption = localization.GetByLabel('UI/Login/CharacterCreation/AssetMenu/NonHairColor')
            secondColourCaption = localization.GetByLabel('UI/Login/CharacterCreation/AssetMenu/NonHairSecondaryColor')
        numColorAreas = self.GetNumColorAreas()
        self.currentNumColorAreas = numColorAreas
        if numColorAreas is not None:
            if numColorAreas < 2:
                secondary = []
                if self.modifier == ccConst.hair:
                    firstColourCaption = localization.GetByLabel('UI/Login/CharacterCreation/AssetMenu/HairColor')
            if numColorAreas < 1:
                primary = []
        if not (primary or secondary):
            return
        top = 0
        left = self.SIDEMARGIN
        gapAndSize = self.currentColorSize + self.COLORGAP
        self.colorControlsCont = uiprimitives.Container(parent=self, align=uiconst.TOTOP, idx=0)
        for colors in [primary, secondary]:
            if colors:
                top += 20
                inRow = self.width / gapAndSize
                rows = len(colors) / inRow + bool(len(colors) % inRow)
                colorHeight = top + rows * gapAndSize
                top = colorHeight
                self.SetSizeAutomatically()
                if self.height + colorHeight > self.maxHeight:
                    if self.width > self.maxWidth:
                        if self.currentColorSize > self.MINCOLORSIZE:
                            self.currentColorSize = self.currentColorSize - 1
                            self.width = self.startingWidth
                            return self.LoadColors(primary, secondary)
                    else:
                        self.width += gapAndSize
                        return self.LoadColors(primary, secondary)
                top += self.currentColorSize

        top = 0
        colorHeight = 0
        for colors, caption in ((primary, firstColourCaption), (secondary, secondColourCaption)):
            if not colors:
                continue
            left = self.SIDEMARGIN
            top += 4
            label = uicls.CCLabel(parent=self.colorControlsCont, uppercase=1, shadowOffset=(0, 0), fontsize=9, letterspace=2, text=caption, top=top, left=left, color=ccConst.COLOR50, idx=0)
            top += label.textheight + 3
            for data in colors:
                colorName, displayColor, colorValue = data
                colorPar = uiprimitives.Container(parent=self.colorControlsCont, pos=(left,
                 top,
                 self.currentColorSize,
                 self.currentColorSize), align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL, name='colorPar', idx=0)
                colorPar.OnClick = (self.OnColorPicked, colorPar)
                colorPar.OnMouseEnter = (self.OnMouseEnterColor, colorPar)
                colorPar.OnMouseExit = (self.OnMouseExitColor, colorPar)
                colorPar.colorName = colorName
                colorPar.displayColor = displayColor
                colorPar.colorValue = colorValue
                colorPar.modifier = self.modifier
                colorPar.sr.activeFrame = uicontrols.Frame(parent=colorPar, name='activeFrame', state=uiconst.UI_HIDDEN, frameConst=(ccConst.ICON_FOCUSFRAME, 15, -11), color=(1.0, 1.0, 1.0, 1.0))
                colorPar.sr.hiliteFrame = uicontrols.Frame(parent=colorPar, name='hiliteFrame', state=uiconst.UI_HIDDEN, frameConst=(ccConst.ICON_FOCUSFRAME, 15, -11), color=(1.0, 1.0, 1.0, 0.25))
                f = uicontrols.Frame(parent=colorPar, color=(1.0, 1.0, 1.0, 0.05), padding=self.COLORMARGIN - 2)
                uiprimitives.Fill(parent=colorPar, color=displayColor, padding=self.COLORMARGIN)
                colorHeight = top + self.currentColorSize
                left += self.currentColorSize + self.COLORGAP
                if left + self.currentColorSize > self.width:
                    top += self.currentColorSize + self.COLORGAP
                    left = self.SIDEMARGIN

            top += self.currentColorSize

        self.colorControlsCont.height = colorHeight
        self.HiliteActive()
        if self.width > self.previousWidth:
            sm.ScatterEvent('OnColorPaletteChanged', self.width)
        self.previousWidth = self.width

    def OnColorPicked(self, colorObj, *args):
        var1 = None
        var2 = None
        if self.hasSecondary:
            charID = uicore.layer.charactercreation.GetInfo().charID
            currentPrimaryName, currentSecondaryName = sm.GetService('character').GetTypeColors(charID, self.modifier)
            if colorObj.colorName.lower().endswith('_bc'):
                var2 = (colorObj.colorName, colorObj.colorValue)
                for each in self.colorControlsCont.children:
                    if not getattr(each, 'colorValue', None):
                        continue
                    if each.colorName == currentPrimaryName:
                        var1 = (each.colorName, each.colorValue)

                if var1 is None:
                    return
            else:
                var1 = (colorObj.colorName, colorObj.colorValue)
                if currentSecondaryName:
                    for each in self.colorControlsCont.children:
                        if not getattr(each, 'colorValue', None):
                            continue
                        if each.colorName == currentSecondaryName:
                            var2 = (each.colorName, each.colorValue)

        else:
            var1 = (colorObj.colorName, colorObj.colorValue)
        if not colorObj.colorName.lower().endswith('_bc'):
            displayColor = colorObj.displayColor
            gradientColor = (1.0, displayColor[:3])
            self.SetGradientsColor(displayColor=displayColor)
        uicore.layer.charactercreation.SetColorValue(self.modifier, var1, var2)

    def SetSliderValue(self, slider):
        value = slider.GetValue()
        if slider.sliderType == 'lights':
            intensity = slider.GetValue()
            uicore.layer.charactercreation.SetLightIntensity(intensity)
        elif slider.sliderType == 'intensity':
            info = uicore.layer.charactercreation.GetInfo()
            value = sm.GetService('character').GetTrueWeight(info.charID, slider.modifier, value)
            uicore.layer.charactercreation.SetIntensity(slider.modifier, value)
        elif slider.sliderType == 'specularity':
            uicore.layer.charactercreation.SetColorSpecularity(slider.modifier, value)
        elif slider.sliderType == HAIRDARKNESS:
            uicore.layer.charactercreation.SetHairDarkness(value)

    def OnMouseWheel(self, *args):
        pass

    def OnMouseEnterColor(self, colorPar, *args):
        colorPar.sr.hiliteFrame.state = uiconst.UI_DISABLED

    def OnMouseExitColor(self, colorPar, *args):
        colorPar.sr.hiliteFrame.state = uiconst.UI_HIDDEN


class CharCreationAssetPicker(uiprimitives.Container):
    __guid__ = 'uicls.CharCreationAssetPicker'
    __notifyevents__ = ['OnDollUpdated', 'OnColorPaletteChanged', 'OnPortraitPicked']
    FULLHEIGHT = 190
    COLLAPSEHEIGHT = 22
    default_align = uiconst.TOTOP
    default_left = 0
    default_top = 0
    default_width = 0
    default_height = COLLAPSEHEIGHT
    default_name = 'CharCreationAssetPicker'
    default_state = uiconst.UI_PICKCHILDREN

    def ApplyAttributes(self, attributes):
        sm.GetService('cc').LogInfo('CharCreationAssetPicker::ApplyAttributes:: modifier = ', attributes.modifier)
        for each in uicore.layer.main.children:
            if each.name == self.default_name:
                each.Close()

        info = uicore.layer.charactercreation.GetInfo()
        if attributes.isSubmenu:
            self.COLLAPSEHEIGHT = 18
            attributes.heght = 18
        uiprimitives.Container.ApplyAttributes(self, attributes)
        if attributes.parent is None:
            uicore.layer.main.children.append(self)
        self._expandTime = None
        self._expanded = False
        self._didRandomize = None
        self.sr.colorPaletteParent = uiprimitives.Container(parent=self, align=uiconst.TOLEFT, width=uicls.CCColorPalette.COLORPALETTEWIDTH, name='colorPaletteParent', state=uiconst.UI_PICKCHILDREN)
        self.sr.captionParent = uiprimitives.Container(parent=self, align=uiconst.TOTOP, height=self.COLLAPSEHEIGHT, name='captionParent', state=uiconst.UI_NORMAL)
        self.sr.captionParent.OnClick = self.Toggle
        self.sr.captionParent.OnMouseEnter = self.OnCaptionEnter
        self.sr.captionParent.OnMouseExit = self.OnCaptionExit
        self.sr.captionParent.modifier = attributes.modifier
        self.sr.caption = uicls.CCLabel(parent=self.sr.captionParent, align=uiconst.CENTERLEFT, left=10, letterspace=3, shadowOffset=(0, 0), text=attributes.caption, uppercase=1, color=ccConst.COLOR, fontsize=13)
        self.sr.caption.SetAlpha(0.5)
        self.sr.expanderIcon = uicontrols.Icon(name='expanderIcon', icon=[ccConst.ICON_EXPANDED, ccConst.ICON_EXPANDEDSINGLE][attributes.isSubmenu], parent=self.sr.captionParent, state=uiconst.UI_DISABLED, align=uiconst.CENTERRIGHT, color=ccConst.COLOR50)
        if attributes.isSubmenu:
            uiprimitives.Fill(parent=self.sr.captionParent, color=(0.2, 0.2, 0.2, 0.4))
            self.sr.caption.fontsize = 12
            bevelAlpha = 0.1
        else:
            randomButton = uiprimitives.Transform(parent=self.sr.colorPaletteParent, pos=(0, 0, 22, 22), state=uiconst.UI_NORMAL, align=uiconst.TOPRIGHT, hint=localization.GetByLabel('UI/Login/CharacterCreation/AssetMenu/RandomizeGroup'), idx=0)
            randomButton.OnClick = (self.RandomizeGroup, randomButton)
            randomButton.OnMouseEnter = (self.OnGenericMouseEnter, randomButton)
            randomButton.OnMouseExit = (self.OnGenericMouseExit, randomButton)
            randomButton.groupID = attributes.groupID
            randIcon = uicontrols.Icon(parent=randomButton, icon=ccConst.ICON_RANDOMSMALL, state=uiconst.UI_DISABLED, align=uiconst.CENTER, color=ccConst.COLOR50)
            randomButton.sr.icon = randIcon
            uicontrols.Frame(parent=self.sr.captionParent, frameConst=ccConst.MAINFRAME_INV)
            uiprimitives.Fill(parent=self.sr.captionParent, color=(0.0, 0.0, 0.0, 0.5))
            bevelAlpha = 0.2
        self.sr.bevel = bevel = uicontrols.Frame(parent=self.sr.captionParent, color=(1.0,
         1.0,
         1.0,
         bevelAlpha), frameConst=ccConst.FILL_BEVEL, state=uiconst.UI_HIDDEN)
        frame = uicontrols.Frame(parent=self.sr.captionParent, frameConst=ccConst.FRAME_SOFTSHADE)
        frame.padding = (-12, -5, -12, -15)
        self.sr.mainParent = uiprimitives.Container(parent=self, align=uiconst.TOALL, name='mainParent')
        if attributes.modifier in ccConst.REMOVEABLE:
            self.sr.removeParent = uiprimitives.Container(parent=self.sr.mainParent, align=uiconst.TOPRIGHT, name='removeParent', pickRadius=-1, state=uiconst.UI_HIDDEN, hint=localization.GetByLabel('UI/Login/CharacterCreation/AssetMenu/RemoveCharacterPart'), pos=(2, 2, 20, 20), opacity=0.75, idx=0)
            self.sr.removeParent.OnClick = (self.RemoveAsset, self.sr.removeParent)
            self.sr.removeParent.OnMouseEnter = (self.OnGenericMouseEnter, self.sr.removeParent)
            self.sr.removeParent.OnMouseExit = (self.OnGenericMouseExit, self.sr.removeParent)
            self.sr.removeParent.modifier = attributes.modifier
            self.sr.removeParent.sr.icon = uicontrols.Icon(name='removeIcon', icon=ccConst.ICON_CLOSE, parent=self.sr.removeParent, state=uiconst.UI_DISABLED, align=uiconst.CENTERLEFT, color=ccConst.COLOR50, left=-10)
        modifier = attributes.modifier
        if modifier == ccConst.EYESGROUP:
            modifier = ccConst.eyes
        elif modifier == ccConst.HAIRGROUP:
            modifier = ccConst.hair
        uicontrols.Frame(parent=self.sr.mainParent, frameConst=ccConst.MAINFRAME, color=(1.0, 1.0, 1.0, 0.5))
        self.sr.assetParent = uiprimitives.Container(parent=self.sr.mainParent, align=uiconst.TOALL, name='assetParent', clipChildren=True, padding=(1, 1, 1, 1))
        self.modifier = modifier
        self.isSubmenu = attributes.isSubmenu
        self.groupID = attributes.groupID
        genderID = attributes.genderID
        if modifier is not None:
            if modifier == ccConst.BACKGROUNDGROUP:
                self.FULLHEIGHT = 170
                self.PrepareBackgrounds()
            elif modifier == ccConst.POSESGROUP:
                self.FULLHEIGHT = 170
                self.PreparePoses()
            elif modifier == ccConst.LIGHTSGROUP:
                self.PrepareLights()
            elif modifier == ccConst.SKINGROUP:
                self.FULLHEIGHT = 150
                self.PrepareSkinTone()
            elif modifier == ccConst.BODYGROUP:
                self.FULLHEIGHT = 70
                self.PrepareBodyShape()
            elif modifier == ccConst.hair:
                self.PrepareHair()
            elif type(modifier) is not types.IntType:
                self.FULLHEIGHT = 150
                if modifier == ccConst.eyeshadow:
                    self.FULLHEIGHT = 180
                itemTypes, activeIndex = uicore.layer.charactercreation.GetAvailableStyles(modifier)
                svc = sm.GetService('character')
                categoryName = modifier.replace('/', '_')
                assetData = []
                numSpecialItems = 0
                for itemType in itemTypes:
                    path = ''
                    if itemType[2] is not None:
                        numSpecialItems += 1
                    path = self.GetAssetThumbnailPath(itemType, genderID, categoryName, info.bloodlineID)
                    assetData.append((path, itemType, ''))

                self.sr.browser = uicls.ImagePicker(parent=self.sr.assetParent, align=uiconst.CENTER, imageWidth=96, imageHeight=96, zoomFactor=3.0, radius=150.0, images=assetData, numSpecialItems=numSpecialItems, OnSetValue=self.OnStylePicked)
                self.sr.browser.assetCategory = modifier
            else:
                self.FULLHEIGHT = self.COLLAPSEHEIGHT
        uiprimitives.Fill(parent=self.sr.mainParent, color=(0.25, 0.25, 0.25, 0.25))
        self.sr.mainParent.SetOpacity(0.0)
        self.height = self.sr.captionParent.height
        self.sr.expanderIcon.LoadIcon([ccConst.ICON_COLLAPSED, ccConst.ICON_COLLAPSEDSINGLE][self.isSubmenu])
        if not attributes.isSubmenu:
            self.state = uiconst.UI_PICKCHILDREN
        else:
            self.state = uiconst.UI_HIDDEN
        sm.RegisterNotify(self)

    def GetAssetThumbnailPath(self, itemType, genderID, categoryName, bloodlineID):
        path = ''
        if itemType[2] is not None:
            if genderID == 0:
                genderText = 'Female'
            else:
                genderText = 'Male'
            assetResPath = cfg.paperdollResources.Get(itemType[0]).resPath
            assetResPath = assetResPath.replace('/', '_').replace('.type', '')
            tempPath = 'res:/UI/Asset/mannequin/%s/%s_%s_%s.png' % (categoryName,
             itemType[2],
             genderText,
             assetResPath)
            if blue.paths.exists(tempPath):
                path = tempPath
        if not path:
            path = 'res:/UI/Asset/%s_g%s_b%s.png' % ('_'.join(list(itemType[1])).replace('/', '_'), genderID, bloodlineID)
        return path

    def RandomizeGroup(self, randomButton, *args):
        if uicore.layer.charactercreation.doll.busyUpdating:
            raise UserError('uiwarning01')
        uthread.new(self.RandomizeRotation_thread, randomButton)
        uicore.layer.charactercreation.LockNavigation()
        doUpdate = False
        svc = sm.GetService('character')
        info = uicore.layer.charactercreation.GetInfo()
        if info.genderID == ccConst.GENDERID_FEMALE:
            itemDict = ccConst.femaleRandomizeItems
        else:
            itemDict = ccConst.maleRandomizeItems
        groupID = randomButton.groupID
        if groupID in (ccConst.BACKGROUNDGROUP, ccConst.POSESGROUP, ccConst.LIGHTSGROUP):
            randomPick = random.choice(self.sr.browser.images)
            _some, value, _some2 = randomPick
            self.sr.browser.SetActiveData(randomPick)
        elif groupID == ccConst.BODYGROUP:
            svc.RandomizeCharacterSculpting(info.charID, doUpdate=False)
            self.UpdateControls('OnDollUpdated', setFocusOnActive=True)
            svc.UpdateTattoos(info.charID, doUpdate=True)
            uicore.layer.charactercreation.TryStoreDna(False, 'Sculpting', force=True)
        else:
            groupList = []
            for key, value in itemDict.iteritems():
                if value == groupID:
                    groupList.append(key)
                    doUpdate = True

            if len(groupList) > 0:
                svc.RandomizeCharacterGroups(info.charID, groupList, doUpdate=True)
            for cat in groupList:
                if cat in ccConst.COLORMAPPING:
                    uicore.layer.charactercreation.UpdateColorSelectionFromDoll(cat)

        if groupID == ccConst.CLOTHESGROUP:
            uicore.layer.charactercreation.ToggleClothes(forcedValue=0)
        self._didRandomize = [groupID]
        uicore.layer.charactercreation.UnlockNavigation()

    def RandomizeRotation_thread(self, randomButton, *args):
        randomButton.StartRotationCycle(cycleTime=500.0, cycles=2)
        if randomButton and not randomButton.destroyed:
            randomButton.SetRotation(0)

    def GetAssetBloodlineID(self, fromBloodlineID):
        if fromBloodlineID in (1, 8, 7, 3, 2, 5, 6):
            assetBloodlineID = 1
        elif fromBloodlineID in (4,):
            assetBloodlineID = 4
        elif fromBloodlineID in (14, 12, 11, 13):
            assetBloodlineID = 14
        else:
            assetBloodlineID = 1
        return assetBloodlineID

    def OnDollUpdated(self, charID, redundantUpdate, *args):
        info = uicore.layer.charactercreation.GetInfo()
        if charID == info.charID and self and not self.destroyed:
            self.UpdateControls('OnDollUpdated', setFocusOnActive=True)

    def OnPortraitPicked(self, *args):
        pickerType = getattr(self, 'pickerType', None)
        if pickerType is None:
            return
        if pickerType == 'backgrounds':
            activeBackdrop = uicore.layer.charactercreation.GetBackdrop()
            if activeBackdrop:
                self.sr.browser.SetActiveDataFromValue(activeBackdrop, focusOnSlot=True, doCallbacks=False, doYield=False)
        elif pickerType == 'poses':
            poseID = uicore.layer.charactercreation.GetPoseId()
            self.sr.browser.SetActiveDataFromValue(poseID, focusOnSlot=True, doCallbacks=False, doYield=False)
        elif pickerType == 'lights':
            currentLight = uicore.layer.charactercreation.GetLight()
            self.sr.browser.SetActiveDataFromValue(currentLight, focusOnSlot=True, doCallbacks=False, doYield=False)
            if uicore.layer.charactercreation.IsSlowMachine():
                return
            self.BrowseLightColors(None)
            if self.sr.colorPalette:
                intensitySlider = self.sr.colorPalette.sr.lights
                intensitySlider.SetValue(uicore.layer.charactercreation.GetLightIntensity())

    def OnGenericMouseEnter(self, btn, *args):
        btn.sr.icon.SetAlpha(1.0)
        if btn.sr.label:
            btn.sr.label.SetAlpha(1.0)

    def OnGenericMouseExit(self, btn, *args):
        btn.sr.icon.SetAlpha(0.5)
        if btn.sr.label:
            btn.sr.label.SetAlpha(0.5)

    def OnGenericMouseDown(self, btn, *args):
        btn.sr.icon.top += 1

    def OnGenericMouseUp(self, btn, *args):
        btn.sr.icon.top -= 1

    def OnTuckBrowse(self, btn, *args):
        if getattr(self.sr.colorPalette.sr.tuckParent, 'tuckOptions', None) is None:
            return
        tuckOptions = self.sr.colorPalette.sr.tuckParent.tuckOptions
        currentIndex = self.sr.colorPalette.sr.tuckParent.tuckIndex
        if btn.name == 'leftBtn':
            if currentIndex == 0:
                currentIndex = len(tuckOptions) - 1
            else:
                currentIndex = currentIndex - 1
        elif currentIndex == len(tuckOptions) - 1:
            currentIndex = 0
        else:
            currentIndex = currentIndex + 1
        uicore.layer.charactercreation.SetStyle(self.sr.colorPalette.sr.tuckParent.tuckPath, self.sr.colorPalette.sr.tuckParent.tuckStyle, tuckOptions[currentIndex])

    def PrepareHair(self):
        self.FULLHEIGHT = 170
        svc = sm.GetService('character')
        info = uicore.layer.charactercreation.GetInfo()
        itemTypes, activeIndex = uicore.layer.charactercreation.GetAvailableStyles(ccConst.hair)
        assetData = []
        for itemType in itemTypes:
            path = self.GetAssetThumbnailPath(itemType, info.genderID, ccConst.hair, info.bloodlineID)
            assetData.append((path, itemType, ''))

        subPar = uiprimitives.Container(parent=self.sr.assetParent, align=uiconst.TOTOP, height=130)
        self.sr.browser = uicls.ImagePicker(parent=subPar, align=uiconst.CENTER, imageWidth=96, imageHeight=96, zoomFactor=3.0, radius=150.0, images=assetData, OnSetValue=self.OnStylePicked)
        self.sr.browser.assetCategory = ccConst.hair
        uiprimitives.Line(parent=self.sr.assetParent, align=uiconst.TOTOP, padding=(6, 0, 6, 0), color=(1.0, 1.0, 1.0, 0.1))
        itemTypes, activeIndex = uicore.layer.charactercreation.GetAvailableStyles(ccConst.eyebrows)
        assetData = []
        for itemType in itemTypes:
            assetData.append(('res:/UI/Asset/%s_g%s_b%s.png' % ('_'.join(list(itemType[1])).replace('/', '_'), info.genderID, info.bloodlineID), itemType, ''))

        subPar = uiprimitives.Container(parent=self.sr.assetParent, align=uiconst.TOTOP, height=92)
        removeParent = uiprimitives.Container(parent=subPar, align=uiconst.TOPRIGHT, name='removeParent', pickRadius=-1, state=uiconst.UI_NORMAL, hint=localization.GetByLabel('UI/Login/CharacterCreation/AssetMenu/RemoveCharacterPart'), pos=(2, 2, 20, 20), opacity=0.75, idx=0)
        removeParent.OnMouseEnter = (self.OnGenericMouseEnter, removeParent)
        removeParent.OnMouseExit = (self.OnGenericMouseExit, removeParent)
        removeParent.modifier = ccConst.eyebrows
        removeParent.sr.icon = uicontrols.Icon(name='removeIcon', icon=ccConst.ICON_CLOSE, parent=removeParent, state=uiconst.UI_DISABLED, align=uiconst.CENTERLEFT, color=ccConst.COLOR50, left=-9)
        self.sr.altbrowser = uicls.ImagePicker(parent=subPar, align=uiconst.CENTER, imageWidth=64, imageHeight=64, zoomFactor=3.0, radius=150.0, images=assetData, OnSetValue=self.OnStylePicked)
        self.sr.altbrowser.sr.removeParent = removeParent
        removeParent.OnClick = (self.RemoveHairAsset, removeParent, self.sr.altbrowser)
        self.sr.altbrowser.assetCategory = ccConst.eyebrows
        self.FULLHEIGHT += 80
        if info.genderID == 1:
            uiprimitives.Line(parent=self.sr.assetParent, align=uiconst.TOTOP, padding=(6, 0, 6, 0), color=(1.0, 1.0, 1.0, 0.1))
            itemTypes, activeIndex = uicore.layer.charactercreation.GetAvailableStyles(ccConst.beard)
            assetData = []
            for itemType in itemTypes:
                assetData.append(('res:/UI/Asset/%s_g%s_b%s.png' % ('_'.join(list(itemType[1])).replace('/', '_'), info.genderID, info.bloodlineID), itemType, ''))

            subPar = uiprimitives.Container(parent=self.sr.assetParent, align=uiconst.TOTOP, height=92)
            removeParent = uiprimitives.Container(parent=subPar, align=uiconst.TOPRIGHT, name='removeParent', pickRadius=-1, state=uiconst.UI_NORMAL, hint=localization.GetByLabel('UI/Login/CharacterCreation/AssetMenu/RemoveCharacterPart'), pos=(2, 2, 20, 20), opacity=0.75, idx=0)
            removeParent.OnMouseEnter = (self.OnGenericMouseEnter, removeParent)
            removeParent.OnMouseExit = (self.OnGenericMouseExit, removeParent)
            removeParent.modifier = ccConst.beard
            removeParent.sr.icon = uicontrols.Icon(name='removeIcon', icon=ccConst.ICON_CLOSE, parent=removeParent, state=uiconst.UI_DISABLED, align=uiconst.CENTERLEFT, color=ccConst.COLOR50, left=-9)
            self.sr.beardbrowser = uicls.ImagePicker(parent=subPar, align=uiconst.CENTER, imageWidth=64, imageHeight=64, zoomFactor=3.0, radius=150.0, images=assetData, OnSetValue=self.OnStylePicked)
            self.sr.beardbrowser.sr.removeParent = removeParent
            removeParent.OnClick = (self.RemoveHairAsset, removeParent, self.sr.beardbrowser)
            self.sr.beardbrowser.assetCategory = ccConst.beard
            self.FULLHEIGHT += 90

    def PrepareBodyShape(self):
        l, t, w, h = self.sr.assetParent.GetAbsolute()
        sliderWidth = (w - 30) / 2
        left = 10
        for sModifier in (ccConst.muscle, ccConst.weight):
            slider = uicls.BitSlider(parent=self.sr.assetParent, name=sModifier + '_slider', align=uiconst.CENTERLEFT, OnSetValue=self.OnSetSliderValue, sliderWidth=sliderWidth, left=left, top=7)
            left += sliderWidth + 10
            label = uicls.CCLabel(parent=slider, text=localization.GetByLabel(maleModifierDisplayNames.get(sModifier, 'UI/Login/CharacterCreation/AssetMenu/MissingCaption')), top=-18, color=ccConst.COLOR50)
            slider.modifier = sModifier

    def PrepareBackgrounds(self):
        self.modifier = None
        self.pickerType = 'backgrounds'
        images = []
        greenscreenOptions = []
        activeBackdrop = uicore.layer.charactercreation.GetBackdrop()
        if gfxsettings.Get(gfxsettings.UI_NCC_GREEN_SCREEN):
            greenscreenOptions = ccConst.greenscreenBackgroundOptions
        elif activeBackdrop is not None and uicore.layer.charactercreation.GetBackgroundID() > const.NCC_MAX_NORMAL_BACKGROUND_ID:
            activeBackdrop = None
        for background in greenscreenOptions + ccConst.backgroundOptions:
            images.append((background.replace('.dds', '_thumb.dds'), ('background', background), None))

        if activeBackdrop is None:
            activeBackdrop = random.choice(images)
            self.OnSetBackground(activeBackdrop[1][1])
            activeBackdrop = activeBackdrop[0]
        self.sr.browser = uicls.ImagePicker(parent=self.sr.assetParent, align=uiconst.CENTERTOP, top=-10, imageWidth=110, imageHeight=110, zoomFactor=3.0, radius=150.0, images=images, OnSetValue=self.OnAltSetAsset)
        if activeBackdrop:
            self.sr.browser.SetActiveDataFromValue(activeBackdrop, focusOnSlot=True, doCallbacks=False, doYield=False)

    def PreparePoses(self):
        info = uicore.layer.charactercreation.GetInfo()
        self.modifier = None
        self.pickerType = 'poses'
        posesData = []
        assetBloodlineID = self.GetAssetBloodlineID(info.bloodlineID)
        for i in range(ccConst.POSERANGE):
            posesData.append(('res:/UI/Asset/%s_g%s_b%s.png' % ('pose_%s' % i, info.genderID, assetBloodlineID), ('pose', i), None))

        self.sr.browser = uicls.ImagePicker(parent=self.sr.assetParent, align=uiconst.CENTERTOP, top=-10, imageWidth=110, imageHeight=110, zoomFactor=3.0, radius=150.0, images=posesData, OnSetValue=self.OnAltSetAsset)
        activePose = int(uicore.layer.charactercreation.GetPoseId())
        if activePose:
            pose = posesData[activePose]
        else:
            pose = random.choice(posesData)
        self.OnAltSetAsset(pose)
        self.sr.browser.SetActiveDataFromValue(pose[1][1], focusOnSlot=True, doCallbacks=False, doYield=False)

    def PrepareLights(self):
        info = uicore.layer.charactercreation.GetInfo()
        self.modifier = None
        self.pickerType = 'lights'
        currentLight = uicore.layer.charactercreation.GetLight()
        currentLightColor = uicore.layer.charactercreation.GetLightColor()
        lightingList = ccConst.LIGHT_SETTINGS_ID
        lightingColorList = ccConst.LIGHT_COLOR_SETTINGS_ID
        currentIndex = lightingColorList.index(currentLightColor)
        defaultThumbnailColor = lightingColorList[0]
        lightStyles = []
        assetBloodlineID = self.GetAssetBloodlineID(info.bloodlineID)
        for each in lightingList:
            lightStyles.append(('res:/UI/Asset/%s_g%s_b%s.png' % ('light_%s_%s' % (each, defaultThumbnailColor), info.genderID, assetBloodlineID), ('light', each), None))

        self.sr.browser = uicls.ImagePicker(parent=self.sr.assetParent, align=uiconst.CENTERTOP, top=-10, imageWidth=110, imageHeight=110, zoomFactor=3.0, radius=150.0, images=lightStyles, OnSetValue=self.OnAltSetAsset)
        if self.sr.colorPalette is None:
            self.CreateColorPallette(isLights=True)
        self.sr.colorPalette.sr.tuckParent.display = True
        self.sr.browser.SetActiveDataFromValue(currentLight, focusOnSlot=True, doCallbacks=False, doYield=False)
        self.sr.colorPalette.SetTuckingCounter(currentIndex + 1, len(lightingColorList))

    def BrowseLightColors(self, btn, *args):
        currentLightColor = uicore.layer.charactercreation.GetLightColor()
        lightingColorList = ccConst.LIGHT_COLOR_SETTINGS_ID
        currentIndex = lightingColorList.index(currentLightColor)
        if btn:
            if btn.name == 'leftBtn':
                currentIndex -= 1
                if currentIndex == -1:
                    currentIndex = len(lightingColorList) - 1
            else:
                currentIndex += 1
                if currentIndex == len(lightingColorList):
                    currentIndex = 0
        uicore.layer.charactercreation.SetLightColor(lightingColorList[currentIndex])
        self.sr.colorPalette.SetTuckingCounter(currentIndex + 1, len(lightingColorList))

    def OnAltSetAsset(self, assetData, *args):
        if assetData:
            thumb, assetData, hiliteResPath = assetData
            k, v = assetData
            if k == 'background':
                uicore.layer.charactercreation.SetBackdrop(v)
                uicore.layer.charactercreation.UpdateBackdrop()
            elif k == 'light':
                uicore.layer.charactercreation.SetLights(v)
            elif k == 'pose':
                uicore.layer.charactercreation.SetPoseID(assetData[1])
                info = uicore.layer.charactercreation.GetInfo()
                sm.GetService('character').ChangePose(v, info.charID)
                if uicore.layer.charactercreation.camera is not None:
                    uicore.layer.charactercreation.camera.UpdatePortraitInfo()
            self.UpdateControls('OnAltSetAsset')

    def OnSetBackground(self, bgPath, *args):
        uicore.layer.charactercreation.SetBackdrop(bgPath)
        uicore.layer.charactercreation.UpdateBackdrop()

    def OnColorPaletteChanged(self, width):
        self.sr.colorPaletteParent.width = width

    def PrepareSkinTone(self):
        itemTypes, activeIndex = uicore.layer.charactercreation.GetAvailableStyles(ccConst.skintype)
        itemsWithDisplayColor = []
        for i, each in enumerate(itemTypes):
            itemsWithDisplayColor.append(('colorName', ccConst.SKINTYPECOLORS.get(str(each[1][2]), (1, 1, 1, 1)), each))

        colorPicker = uicls.CharCreationColorPicker(parent=self.sr.assetParent, align=uiconst.CENTERLEFT, colors=itemsWithDisplayColor, OnSetValue=self.OnSkinTypePicked, activeColorIndex=activeIndex)
        colorPicker.modifier = ccConst.skintype
        l, t, w, h = self.sr.assetParent.GetAbsolute()
        sliderWidth = w - 130 - 10
        left = 10
        top = -32
        for sModifier in (ccConst.skinaging, ccConst.freckles, ccConst.scarring):
            itemTypes, activeIdx = uicore.layer.charactercreation.GetAvailableStyles(sModifier)
            bitAmount = len(itemTypes)
            slider = uicls.BitSlider(parent=self.sr.assetParent, name=sModifier + '_slider', align=uiconst.CENTERLEFT, OnSetValue=self.OnSetSliderValue, bitAmount=bitAmount, sliderWidth=sliderWidth, left=130, top=top)
            top += 32
            label = uicls.CCLabel(parent=slider, text=localization.GetByLabel(maleModifierDisplayNames.get(sModifier, 'UI/Login/CharacterCreation/AssetMenu/MissingCaption')), top=-18, color=ccConst.COLOR50)
            slider.modifier = sModifier

    def OnSetSliderValue(self, slider):
        value = slider.GetValue()
        if slider.modifier in (ccConst.skinaging, ccConst.freckles, ccConst.scarring):
            itemTypes, activeIdx = uicore.layer.charactercreation.GetAvailableStyles(slider.modifier)
            styleRange = 1.0 / len(itemTypes)
            portionalIndex = int(len(itemTypes) * (value + styleRange / 2))
            if portionalIndex == 0:
                uicore.layer.charactercreation.ClearCategory(slider.modifier)
            else:
                uicore.layer.charactercreation.SetItemType(itemTypes[portionalIndex - 1])
        else:
            uicore.layer.charactercreation.SetIntensity(slider.modifier, value)

    def ShowActiveItem(self, *args):
        if self.sr.browser:
            active = self.sr.browser.GetActiveData()
            if active:
                self.sr.browser.SetActiveData(active)

    def RemoveAsset(self, button, *args):
        uicore.layer.charactercreation.ClearCategory(button.modifier)
        if self.sr.browser:
            self.sr.browser.SetActiveData(None, focusOnSlot=False)
            self.CollapseColorPalette()

    def RemoveHairAsset(self, button, browser, *args):
        info = uicore.layer.charactercreation.GetInfo()
        modifiers = sm.GetService('character').GetModifierByCategory(info.charID, button.modifier, getAll=True)
        for each in modifiers:
            uicore.layer.charactercreation.ClearCategory(button.modifier)

    def OnCaptionEnter(self, *args):
        uicore.layer.charactercreation.SetHintText(self.sr.captionParent.modifier)
        sm.StartService('audio').SendUIEvent(unicode('wise:/ui_icc_menu_mouse_over_play'))
        self.sr.caption.SetAlpha(1.0)
        self.sr.expanderIcon.SetAlpha(1.0)
        if self.sr.bevel:
            self.sr.bevel.state = uiconst.UI_DISABLED

    def OnCaptionExit(self, *args):
        uicore.layer.charactercreation.SetHintText(None)
        if not self.IsExpanded():
            self.sr.caption.SetAlpha(0.5)
            self.sr.expanderIcon.SetAlpha(0.5)
        if self.sr.bevel:
            self.sr.bevel.state = uiconst.UI_HIDDEN

    def Toggle(self, *args):
        sm.StartService('audio').SendUIEvent(unicode('wise:/ui_icc_button_mouse_down_play'))
        if self._expanded:
            self.Collapse()
        else:
            self.Expand()

    def IsExpanded(self):
        return self._expanded

    def UpdateControls(self, trigger = None, setFocusOnActive = False):
        subMenus = self.GetMySubmenus()
        if not self.IsExpanded() or subMenus:
            if subMenus and self._didRandomize and self.groupID in self._didRandomize:
                self._didRandomize = None
                for each in subMenus:
                    each.UpdateControls('UpdateControls', setFocusOnActive=True)

            return
        try:
            if self.sr.colorPalette:
                uicore.layer.charactercreation.ValidateColors(self.modifier)
                self.sr.colorPalette.UpdatePalette()
        except Exception:
            if not self or self.destroyed:
                return
            raise

        info = uicore.layer.charactercreation.GetInfo()
        charSvc = sm.GetService('character')
        containers = [ w for w in self.Find('trinity.Tr2Sprite2dContainer') ]
        browsersAndModifiers = [(self.sr.browser, self.modifier)]
        if self.modifier == ccConst.hair:
            browsersAndModifiers.append((self.sr.altbrowser, ccConst.eyebrows))
            browsersAndModifiers.append((self.sr.beardbrowser, ccConst.beard))
        for browser, modifier in browsersAndModifiers:
            if browser and modifier is not None:
                if modifier == ccConst.beard:
                    activeMod = None
                    activeMods = charSvc.GetModifierByCategory(info.charID, modifier, getAll=True)
                    if activeMods:
                        if len(activeMods) == 1:
                            activeMod = activeMods[0]
                        else:
                            for a in activeMods:
                                if a.respath == ccConst.BASEBEARD:
                                    continue
                                activeMod = a
                                break
                            else:
                                activeMod = activeMods[0]

                else:
                    activeMod = charSvc.GetModifierByCategory(info.charID, modifier)
                    if activeMod and activeMod.name in ccConst.invisibleModifiers:
                        activeMod = None
                    if not activeMod and modifier in uicore.layer.charactercreation.clothesStorage:
                        activeMod = uicore.layer.charactercreation.clothesStorage.get(modifier, None)
                if activeMod:
                    uthread.new(self.SetActiveData_thread, browser, activeMod, setFocusOnActive)
                else:
                    browser.SetActiveData(None, focusOnSlot=False, doCallbacks=False)

        self.LoadTuckOptions()
        self.LoadRemoveOptions()
        colorPickers = [ each for each in containers if isinstance(each, uicls.CharCreationColorPicker) ]
        for colorPicker in colorPickers:
            if not getattr(colorPicker, 'modifier', None):
                continue
            itemTypes, activeIndex = uicore.layer.charactercreation.GetAvailableStyles(colorPicker.modifier)
            if activeIndex is None:
                colorPicker.SetActiveColor(None, initing=True)
            else:
                activeColor = itemTypes[activeIndex]
                colorPicker.SetActiveColor(activeColor, initing=True)

        sliders = [ each for each in containers if isinstance(each, uicls.BitSlider) ]
        for slider in sliders:
            if not getattr(slider, 'modifier', None):
                continue
            if slider.modifier in (ccConst.skinaging, ccConst.freckles, ccConst.scarring):
                itemTypes, activeIndex = uicore.layer.charactercreation.GetAvailableStyles(slider.modifier)
                if not itemTypes:
                    continue
                if activeIndex is None:
                    activeIndex = 0
                else:
                    activeIndex = activeIndex + 1
                value = 1.0 / float(len(itemTypes)) * activeIndex
                slider.SetValue(value, doCallback=False)
            elif slider.modifier in ccConst.weight:
                weight = charSvc.GetCharacterWeight(info.charID)
                slider.SetValue(weight, doCallback=False)
            elif slider.modifier == ccConst.muscle:
                muscularity = charSvc.GetCharacterMuscularity(info.charID)
                slider.SetValue(muscularity, doCallback=False)
            elif slider.modifier == ccConst.hair:
                slider.SetValue(charSvc.GetHairDarkness(info.charID), doCallback=False)
            else:
                activeMod = charSvc.GetModifierByCategory(info.charID, slider.modifier)
                if activeMod:
                    if slider.sliderType == 'intensity':
                        slider.SetValue(charSvc.GetWeightByCategory(info.charID, slider.modifier))
                    elif slider.sliderType == 'specularity':
                        slider.SetValue(charSvc.GetColorSpecularityByCategory(info.charID, slider.modifier))

    def SetActiveData_thread(self, browser, activeMod, setFocusOnActive):
        typeData = activeMod.GetTypeData()
        if typeData[0].startswith(('makeup', 'beard')) and typeData[2] in ('default', 'none'):
            typeData = (typeData[0], typeData[1], '')
        if browser and hasattr(browser, 'SetActiveDataFromValue'):
            browser.SetActiveDataFromValue(typeData, doCallbacks=False, focusOnSlot=setFocusOnActive, doYield=False)
            if self.sr.colorPalette:
                self.sr.colorPalette.TryReloadColors()
            self.LoadTuckOptions()
            self.LoadRemoveOptions()

    def DebugRoleCheck(self):
        mask = service.ROLE_CONTENT | service.ROLE_QA | service.ROLE_PROGRAMMER | service.ROLE_GMH
        if eve.session.role & mask and not prefs.GetValue('CCHideAssetDebugText', False):
            return True
        else:
            return False

    def UpdatePrefs(self, state):
        currentMenuState = settings.user.ui.Get('assetMenuState', {ccConst.BODYGROUP: 1})
        key = self.modifier or 'group_%s' % getattr(self, 'groupID', '')
        currentMenuState[key] = state
        settings.user.ui.Set('assetMenuState', currentMenuState)

    def Expand(self, initing = False):
        if self._expanded:
            return
        self._expanded = True
        self._expandTime = blue.os.GetWallclockTime()
        self.sr.caption.SetAlpha(1.0)
        self.sr.expanderIcon.SetAlpha(1.0)
        self.CheckIfOversize()
        if self.isSubmenu or not self.GetMySubmenus():
            self.height = self.GetCollapsedHeight()
            uthread.new(uicore.effect.CombineEffects, self.sr.mainParent, opacity=1.0, time=50.0)
            uicore.effect.MorphUIMassSpringDamper(self, 'height', self.GetExpandedHeight(), newthread=True, float=False, frequency=15.0, dampRatio=0.75)
            self.Show()
        else:
            mySubs = self.GetMySubmenus()
            menuState = settings.user.ui.Get('assetMenuState', {ccConst.BODYGROUP: True})
            for subMenu in mySubs:
                key = subMenu.modifier or 'group_%s' % getattr(subMenu, 'groupID', '')
                if menuState.get(key, False):
                    subMenu.Expand(True)
                else:
                    subMenu.height = 0
                    subMenu.Show()
                    uicore.effect.MorphUIMassSpringDamper(subMenu, 'height', subMenu.GetCollapsedHeight(), newthread=True, float=False, frequency=15.0, dampRatio=0.75)

        self.CheckIfOversize()
        if self.modifier in ccConst.COLORMAPPING or self.modifier in ccConst.TUCKMAPPING:
            uthread.new(self.ExpandColorPalette)
        self.UpdateControls('Expand', setFocusOnActive=True)
        self.UpdatePrefs(True)
        self.sr.expanderIcon.LoadIcon([ccConst.ICON_EXPANDED, ccConst.ICON_EXPANDEDSINGLE][self.isSubmenu])

    def ExpandColorPalette(self, initing = False, *args):
        blue.pyos.synchro.SleepWallclock(500)
        if hasattr(self, 'sr'):
            self.CreateColorPallette()
        if self.sr.browser and self.IsExpanded():
            info = uicore.layer.charactercreation.GetInfo()
            activeMod = sm.GetService('character').GetModifierByCategory(info.charID, self.modifier)
            if activeMod and (uicore.uilib.mouseOver is self or uiutil.IsUnder(uicore.uilib.mouseOver, self)):
                self.sr.colorPalette.ExpandPalette()

    def CreateColorPallette(self, isLights = False, *args):
        if self.sr.colorPalette is None:
            maxPaletteWidth = int(uicore.desktop.width / 8)
            if isLights:
                browseFunction = self.BrowseLightColors
            else:
                browseFunction = self.OnTuckBrowse
            self.sr.colorPalette = uicls.CCColorPalette(name='CCColorPalette', parent=self.sr.colorPaletteParent, align=uiconst.TOPRIGHT, pos=(0,
             self.GetCollapsedHeight(),
             uicls.CCColorPalette.COLORPALETTEWIDTH,
             0), modifier=self.modifier, state=uiconst.UI_HIDDEN, maxHeight=self.GetExpandedHeight(), maxWidth=maxPaletteWidth, browseFunction=browseFunction, bgColor=(0.0, 0.0, 0.0, 0.25), isLights=isLights)

    def CheckIfOversize(self, *args):
        self.parent.parent.CheckIfOversize(currentPicker=self)

    def GetCollapsedHeight(self):
        return self.sr.captionParent.height

    def GetExpandedHeight(self):
        return self.FULLHEIGHT

    def Collapse(self):
        self._expanded = False
        self.CollapseColorPalette()
        if self._expanded:
            return
        uthread.new(uicore.effect.CombineEffects, self.sr.mainParent, opacity=0.0, time=150.0)
        if self.isSubmenu or not self.GetMySubmenus():
            uicore.effect.MorphUIMassSpringDamper(self, 'height', self.sr.captionParent.height, newthread=1, float=False, frequency=15.0, dampRatio=1.0)
        else:
            mySubs = self.GetMySubmenus()
            hideHeight = 0
            for subMenu in mySubs:
                if subMenu.IsExpanded():
                    subMenu.Collapse()

            for subMenu in mySubs:
                subMenu.Hide()

        self.sr.expanderIcon.LoadIcon([ccConst.ICON_COLLAPSED, ccConst.ICON_COLLAPSEDSINGLE][self.isSubmenu])
        if uicore.uilib.mouseOver is not self.sr.captionParent:
            self.OnCaptionExit()
        self.UpdatePrefs(False)

    def CollapseColorPalette(self, *args):
        if self.sr.colorPalette:
            self.sr.colorPalette.CollapsePalette(push=True)

    def GetMySubmenus(self):
        ret = []
        if self.isSubmenu:
            return []
        for each in self.parent.children:
            if not hasattr(each, 'groupID'):
                continue
            if each is not self and each.groupID == self.groupID and getattr(each, 'isSubmenu', False):
                ret.append(each)

        return ret

    def GetCurrentModifierValue(self, modifierPath):
        info = uicore.layer.charactercreation.GetInfo()
        modifier = sm.GetService('character').GetModifiersByCategory(info.charID, modifierPath)
        if modifier:
            return modifier[0].weight
        return 0.0

    def OnStylePicked(self, assetData, *args):
        if assetData:
            info = uicore.layer.charactercreation.GetInfo()
            thumb, itemType, hiliteResPath = assetData
            weight = 1.0
            if self.sr.colorIntensitySlider:
                weight = self.sr.colorIntensitySlider.GetValue()
            uicore.layer.charactercreation.SetItemType(itemType, weight=weight)
            uthread.new(self.UpdateControls, 'OnStylePicked')

    def OnSkinTypePicked(self, itemType, *args):
        if itemType:
            info = uicore.layer.charactercreation.GetInfo()
            uicore.layer.charactercreation.ClearCategory(ccConst.skintone, doUpdate=False)
            sm.GetService('character').characterMetadata[info.charID].typeColors.pop(ccConst.skintone, None)
            uicore.layer.charactercreation.SetItemType(itemType)
            uthread.new(self.UpdateControls, 'OnSkinTypePicked')

    def LoadRemoveOptions(self, *args):
        if self.modifier == ccConst.hair:
            return self.LoadRemoveHairOptions()
        if not self.sr.browser or not self.IsExpanded() or self.state == uiconst.UI_HIDDEN or self.modifier not in ccConst.REMOVEABLE:
            return
        self.SetRemoveIcon(self.modifier, self.sr.removeParent)

    def SetRemoveIcon(self, modifier, icon):
        info = uicore.layer.charactercreation.GetInfo()
        currentModifier = sm.GetService('character').GetModifierByCategory(info.charID, modifier)
        if not currentModifier or getattr(currentModifier, 'name', None) in ccConst.invisibleModifiers:
            if icon:
                icon.Hide()
        elif icon:
            icon.Show()

    def LoadRemoveHairOptions(self, *args):
        if not self.IsExpanded() or self.state == uiconst.UI_HIDDEN:
            return
        if self.sr.altbrowser:
            self.SetRemoveIcon(ccConst.eyebrows, self.sr.altbrowser.sr.removeParent)
        if self.sr.beardbrowser:
            self.SetRemoveIcon(ccConst.beard, self.sr.beardbrowser.sr.removeParent)

    def LoadTuckOptions(self, *args):
        if not self.sr.browser or not self.IsExpanded() or self.state == uiconst.UI_HIDDEN or self.modifier not in ccConst.TUCKMAPPING:
            if getattr(self, 'pickerType', None) == 'lights' and uicore.layer.charactercreation.IsSlowMachine():
                self.sr.colorPalette.sr.tuckParent.display = False
            return
        if self.sr.colorPalette is None:
            self.CreateColorPallette()
        if self.sr.colorPalette is None:
            return
        info = uicore.layer.charactercreation.GetInfo()
        currentModifier = sm.GetService('character').GetModifierByCategory(info.charID, self.modifier)
        activeData = None
        if self.sr.browser and self.IsExpanded():
            activeData = self.sr.browser.GetActiveData()
        hideTuck = True
        if activeData and currentModifier:
            tuckPath, requiredModifiers, subKey = ccConst.TUCKMAPPING[self.modifier]
            if requiredModifiers:
                haveRequired = False
                for each in requiredModifiers:
                    haveRequired = bool(sm.GetService('character').GetModifierByCategory(info.charID, each))
                    if haveRequired:
                        break

            else:
                haveRequired = True
            resPath, itemType, hiliteResPath = activeData
            if haveRequired:
                tuckModifier = sm.GetService('character').GetModifierByCategory(info.charID, tuckPath)
                if tuckModifier:
                    tuckVariations = tuckModifier.GetVariations()
                    if tuckVariations:
                        currentTuckVariation = tuckModifier.currentVariation
                        tuckStyle = tuckModifier.GetResPath().split('/')[-1]
                        if currentTuckVariation in tuckVariations:
                            tuckIndex = tuckVariations.index(currentTuckVariation)
                        else:
                            tuckIndex = 0
                        tuckParent = self.sr.colorPalette.sr.tuckParent
                        tuckParent.tuckOptions = tuckVariations
                        tuckParent.tuckIndex = tuckIndex
                        tuckParent.tuckPath = tuckPath
                        tuckParent.tuckStyle = tuckStyle
                        tuckParent.tuckResPath = tuckModifier.GetResPath()
                        self.sr.colorPalette.SetTuckingCounter(tuckIndex + 1, len(tuckVariations))
                        hideTuck = False
        if hideTuck:
            if self.sr.colorPalette.sr.tuckParent.display == True:
                self.sr.colorPalette.sr.tuckParent.display = False
                uthread.new(uicore.effect.CombineEffects, self.sr.colorPalette.sr.tuckParent, opacity=0.0, time=125.0)
        else:
            self.sr.colorPalette.sr.tuckParent.display = True
            uthread.new(uicore.effect.CombineEffects, self.sr.colorPalette.sr.tuckParent, opacity=1.0, time=125.0)

    def OnColorPickedFromWheel(self, colorPicker, color, name):
        uicore.layer.charactercreation.SetColorValue(colorPicker.modifier, (name, tuple(color)))


class CharCreationMenuToggler(uiprimitives.Container):
    __guid__ = 'uicls.CharCreationMenuToggler'
    __notifyevents__ = ['OnColorPaletteChanged']
    FULLHEIGHT = 22
    COLLAPSEHEIGHT = 22
    default_align = uiconst.TOTOP
    default_left = 0
    default_top = 0
    default_width = 0
    default_height = COLLAPSEHEIGHT
    default_pos = None
    default_name = 'CharCreationMenuToggler'
    default_state = uiconst.UI_PICKCHILDREN

    def ApplyAttributes(self, attributes):
        for each in uicore.layer.main.children:
            if each.name == self.default_name:
                each.Close()

        info = uicore.layer.charactercreation.GetInfo()
        uiprimitives.Container.ApplyAttributes(self, attributes)
        if attributes.parent is None:
            uicore.layer.main.children.append(self)
        self.sr.colorPaletteParent = uiprimitives.Container(parent=self, align=uiconst.TOLEFT, width=uicls.CCColorPalette.COLORPALETTEWIDTH, name='colorPaletteParent', state=uiconst.UI_DISABLED)
        self.sr.captionParent = uiprimitives.Container(parent=self, align=uiconst.TOTOP, height=self.COLLAPSEHEIGHT, name='captionParent', state=uiconst.UI_NORMAL)
        self.func = attributes.func
        self.sr.captionParent.OnClick = self.Toggle
        self.sr.captionParent.OnMouseEnter = self.OnCaptionEnter
        self.sr.captionParent.OnMouseExit = self.OnCaptionExit
        self.menuType = attributes.menuType
        self.sr.caption = uicls.CCLabel(parent=self.sr.captionParent, align=uiconst.CENTERLEFT, left=10, letterspace=3, shadowOffset=(0, 0), text=attributes.caption, uppercase=1, color=ccConst.COLOR, fontsize=13)
        if self.menuType != 'tattooMenu':
            self.sr.caption.SetAlpha(0.5)
        self.keepColor = 0
        self.AddRadioButton()
        uiprimitives.Fill(parent=self.sr.captionParent, color=(0.4, 0.4, 0.4, 0.5))
        self.sr.bevel = bevel = uicontrols.Frame(parent=self.sr.captionParent, color=(1.0, 1.0, 1.0, 0.2), frameConst=ccConst.FILL_BEVEL, state=uiconst.UI_HIDDEN)
        frame = uicontrols.Frame(parent=self.sr.captionParent, frameConst=ccConst.FRAME_SOFTSHADE)
        frame.padding = (-12, -5, -12, -15)
        self.height = self.sr.captionParent.height
        sm.RegisterNotify(self)

    def AddRadioButton(self, *args):
        self.sr.shadowIcon = uiprimitives.Sprite(parent=self.sr.captionParent, name='shadowIcon', align=uiconst.CENTERRIGHT, state=uiconst.UI_DISABLED, pos=(0, 0, 32, 32), texturePath='res:/UI/Texture/CharacterCreation/radiobuttonShadow.dds', color=(0.4, 0.4, 0.4, 0.6))
        self.sr.backIcon = uiprimitives.Sprite(parent=self.sr.captionParent, name='backIcon', align=uiconst.CENTERRIGHT, state=uiconst.UI_DISABLED, pos=(0, 0, 32, 32), texturePath='res:/UI/Texture/CharacterCreation/radiobuttonBack.dds')
        self.sr.radioBtnFill = uiprimitives.Container(parent=self.sr.captionParent, state=uiconst.UI_HIDDEN, align=uiconst.CENTERRIGHT, pos=(0, 0, 32, 32), idx=0)
        self.sr.radioBtnHilite = uiprimitives.Sprite(parent=self.sr.radioBtnFill, name='radioBtnHilite', align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, pos=(0, 0, 32, 32), texturePath='res:/UI/Texture/CharacterCreation/radiobuttonWhite.dds')
        self.sr.radioBtnColor = uiprimitives.Sprite(parent=self.sr.radioBtnFill, name='radioBtnColor', align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, pos=(0, 0, 32, 32), texturePath='res:/UI/Texture/CharacterCreation/radiobuttonColor.dds')
        if self.menuType == 'tattooMenu':
            self.SetRadioBtnColor(color='green')

    def OnCaptionEnter(self, *args):
        uicore.layer.charactercreation.SetHintText(None, localization.GetByLabel('UI/Login/CharacterCreation/AssetMenu/BodyModHelp'))
        sm.StartService('audio').SendUIEvent(unicode('wise:/ui_icc_menu_mouse_over_play'))
        if not self.keepColor:
            self.sr.caption.SetAlpha(1.0)
            if self.menuType == 'tattooMenu':
                self.SetRadioBtnColor(color='red')
            elif self.menuType == 'assetMenu':
                self.SetRadioBtnColor(color='green')
        if self.sr.bevel:
            self.sr.bevel.state = uiconst.UI_DISABLED

    def OnCaptionExit(self, *args):
        uicore.layer.charactercreation.SetHintText(None)
        if self.menuType != 'tattooMenu':
            self.sr.caption.SetAlpha(0.5)
        if not self.keepColor:
            if self.menuType == 'tattooMenu':
                self.SetRadioBtnColor(color='green')
            else:
                self.sr.radioBtnFill.state = uiconst.UI_HIDDEN
            if self.sr.bevel:
                self.sr.bevel.state = uiconst.UI_HIDDEN

    def Toggle(self, *args):
        sm.StartService('audio').SendUIEvent(unicode('wise:/ui_icc_button_mouse_down_play'))
        self.keepColor = 1
        if self.func:
            self.func()
            self.ResetRadioButton()

    def ResetRadioButton(self, *args):
        self.keepColor = 0
        if self.menuType != 'tattooMenu':
            self.sr.caption.SetAlpha(0.5)
        if self.menuType == 'tattooMenu':
            self.SetRadioBtnColor(color='green')
        else:
            self.sr.radioBtnFill.state = uiconst.UI_HIDDEN

    def OnColorPaletteChanged(self, width):
        self.sr.colorPaletteParent.width = width

    def SetRadioBtnColor(self, color = 'green', *args):
        if color == 'green':
            self.sr.radioBtnFill.state = uiconst.UI_DISABLED
            self.sr.radioBtnColor.SetRGB(0, 1, 0)
            self.sr.radioBtnHilite.SetAlpha(0.7)
        elif color == 'red':
            self.sr.radioBtnFill.state = uiconst.UI_DISABLED
            self.sr.radioBtnColor.SetRGB(1, 0, 0)
            self.sr.radioBtnHilite.SetAlpha(0.3)
