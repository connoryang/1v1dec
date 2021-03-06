#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\util\uix.py
import math
import blue
from dogma.attributes.format import GetFormatAndValue
from eve.client.script.ui.control.themeColored import FillThemeColored, LineThemeColored
from eve.client.script.ui.shared.fitting.fittingUtil import FITKEYS
from inventorycommon.util import GetItemVolume
import util
import searchUtil
import uiprimitives
import uicontrols
import sys
import types
import log
from log import LogError, LogWarn
import util
import uiutil
import mathUtil
import carbonui.const as uiconst
import trinity
import localization
import fontConst
import telemetry
from spacecomponents.common.helper import HasDeployComponent, HasNpcPilotComponent
from .uix2 import SEL_FILES, SEL_BOTH, SEL_FOLDERS, RefreshHeight
import evetypes
advchannelsTutorial = 50
cloningTutorial = 42
cloningWhenPoddedTutorial = 27
podriskTutorial = 43
skillfittingTutorial = 51
insuranceTutorial = 41
tutorial = 109
tutorialAuraIntroduction = 5
tutorialBoarding = 6
tutorialCharacterSheet = 7
tutorialControlConsole = 18
tutorialItems = 8
tutorialNavigation = 19
tutorialOverview = 21
tutorialSelling = 10
tutorialShips = 6
tutorialSpace = 17
tutorialTargeting = 20
tutorialUndock = 16
tutorialWallet = 11
tutorialWarpingDC = 23
tutorialCombatChooseTheVenue = 103
tutorialCombatConcepts = 105
tutorialCombatKnowYourEquipment = 104
tutorialCombatStudyTheOpponent = 102
tutorialInformativeCareerPlanning = 99
tutorialInformativeCharacterSheetAdvancedInformation = 100
tutorialInformativeContracts = 54
tutorialInformativeCorporations = 33
tutorialInformativeCosmosComplexes = 101
tutorialInformativeCrimeAndPunishment = 97
tutorialInformativeDrones = 65
tutorialInformativeExploration = 124
tutorialInformativeFittingStationService = 13
tutorialInformativeHeat = 123
tutorialInformativeMap = 14
tutorialInformativeMarket = 12
tutorialInformativePeopleAndPlaces = 15
tutorialInformativePoliticsAndmanagement = 98
tutorialInformativeRepairshop = 46
tutorialInformativeReprocessingPlant = 9
tutorialInformativeSalvaging = 122
tutorialInformativeScanning = 63
tutorialInformativeScienceIndustry = 52
tutorialWorldspaceNavigation = 235
tutorialTutorials = 215
tutorialCertificates = 134
CLOSE = 4
OKCLOSE = 5
AUTOPOSCENTER = 17
TABMARGIN = 6
escapes = {'amp': '&',
 'lt': '<',
 'gt': '>'}

def TakeTime(label, func, *args, **kw):
    if eve.taketime:
        t = blue.pyos.taskletTimer.EnterTasklet(label)
        try:
            return func(*args, **kw)
        finally:
            blue.pyos.taskletTimer.ReturnFromTasklet(t)

    else:
        return func(*args, **kw)


def Click(*args):
    print 'UIXClickX', args


import re
tag = re.compile('<color=0x.*?>|<right>|<center>|<left>')

def DeTag(s):
    return tag.sub('', s)


def Flush(wnd):
    wnd.Flush()


def GetBuffersize(size):
    return uiutil.GetBuffersize(size)


@telemetry.ZONE_FUNCTION
def GetItemData(rec, viewMode, viewOnly = 0, container = None, scrollID = None, *args, **kw):
    attribs = {}
    for attribute in sm.GetService('godma').GetType(rec.typeID).displayAttributes:
        attribs[attribute.attributeID] = attribute.value

    sort_slotsize = 0
    for effect in cfg.dgmtypeeffects.get(rec.typeID, []):
        if effect.effectID in (const.effectHiPower, const.effectMedPower, const.effectLoPower):
            sort_slotsize = 1
            break

    data = uiutil.Bunch()
    data.__guid__ = 'listentry.InvItem'
    data.item = rec
    data.rec = rec
    data.itemID = rec.itemID
    data.godmaattribs = attribs
    data.invtype = rec.typeID
    data.container = container
    data.viewMode = viewMode
    data.viewOnly = viewOnly
    data.locked = rec.flagID == const.flagLocked
    if not data.locked and rec.flagID != const.flagUnlocked and container and container.invController.isLockable:
        if hasattr(container, 'invController'):
            containerItem = container.invController.GetInventoryItem()
            if containerItem.groupID in (const.groupAuditLogSecureContainer, const.groupStation) or containerItem.typeID == const.typeOffice:
                data.locked = sm.GetService('corp').IsItemLocked(rec)
    data.factionID = sm.GetService('faction').GetCurrentFactionID()
    if rec.singleton or rec.typeID in (const.typeBookmark,):
        data.Set('sort_%s' % localization.GetByLabel('UI/Common/Quantity'), 0)
    else:
        data.Set('sort_%s' % localization.GetByLabel('UI/Common/Quantity'), rec.stacksize)
    ml = data.godmaattribs.get(const.attributeMetaLevel, None)
    if not ml:
        metaLevel = ''
    else:
        metaLevel = util.FmtAmt(ml)
    data.metaLevel = metaLevel
    data.groupName = evetypes.GetGroupName(rec.typeID)
    data.categoryName = evetypes.GetCategoryName(rec.typeID)
    data.sort_ammosizeconstraints = attribs.has_key(const.attributeChargeSize)
    data.sort_slotsize = sort_slotsize
    data.Set('sort_%s' % localization.GetByLabel('UI/Common/Name'), GetItemName(rec, data).lower())
    data.Set('sort_%s' % localization.GetByLabel('UI/Common/Type'), GetCategoryGroupTypeStringForItem(rec).lower())
    data.Set('sort_%s' % localization.GetByLabel('UI/Inventory/ItemMetaLevel'), ml or 0.0)
    data.Set('sort_%s' % localization.GetByLabel('UI/Inventory/ItemGroup'), data.groupName.lower())
    data.Set('sort_%s' % localization.GetByLabel('UI/Inventory/ItemCategory'), data.categoryName.lower())
    if data.rec.typeID == const.typePlasticWrap:
        data.volume = ''
        data.Set('sort_%s' % localization.GetByLabel('UI/Inventory/ItemVolume'), 0)
    else:
        volume = GetItemVolume(rec)
        u = cfg.dgmunits.Get(const.unitVolume)
        unit = u.displayName
        decimalPlaces = 2 if abs(volume - int(volume)) > const.FLOAT_TOLERANCE else 0
        data.volume = localization.GetByLabel('UI/InfoWindow/ValueAndUnit', value=util.FmtAmt(volume, showFraction=decimalPlaces), unit=unit)
        data.Set('sort_%s' % localization.GetByLabel('UI/Inventory/ItemVolume'), volume)
    data.scrollID = scrollID
    return data


@telemetry.ZONE_FUNCTION
def GetItemLabel(rec, data, new = 0):
    if getattr(data, 'label', None) and data.viewMode == 'icons' and not new:
        return data.label
    name = GetItemName(rec, data)
    if data.viewMode in ('list', 'details'):
        pType = ''
        fType = ''
        attribs = getattr(data, 'godmaattribs', {})
        if attribs.has_key(const.attributeImplantness):
            kv = util.KeyVal(unitID=int, attributeID=const.attributeImplantness)
            v = attribs[const.attributeImplantness]
            fType = GetFormatAndValue(kv, v)
        elif attribs.has_key(const.attributeBoosterness):
            kv = util.KeyVal(unitID=int, attributeID=const.attributeBoosterness)
            v = attribs[const.attributeBoosterness]
            fType = GetFormatAndValue(kv, v)
        elif attribs.has_key(const.attributeChargeSize):
            kv = util.KeyVal(unitID=const.unitSizeclass, attributeID=const.attributeChargeSize)
            v = attribs[const.attributeChargeSize]
            pType = GetFormatAndValue(kv, v)
        techLevel = data.godmaattribs.get(const.attributeTechLevel, '')
        if techLevel:
            techLevel = util.FmtAmt(techLevel)
        for effect in cfg.dgmtypeeffects.get(rec.typeID, []):
            if effect.effectID in (const.effectRigSlot,
             const.effectHiPower,
             const.effectMedPower,
             const.effectLoPower):
                fType = {const.effectRigSlot: localization.GetByLabel('UI/Inventory/SlotRigs'),
                 const.effectHiPower: localization.GetByLabel('UI/Inventory/SlotHigh'),
                 const.effectMedPower: localization.GetByLabel('UI/Inventory/SlotMedium'),
                 const.effectLoPower: localization.GetByLabel('UI/Inventory/SlotLow')}.get(effect.effectID)
                continue

        stringDict = {localization.GetByLabel('UI/Common/Name'): name,
         localization.GetByLabel('UI/Common/Quantity'): '<right>%s' % GetItemQty(data, 'ln'),
         localization.GetByLabel('UI/Inventory/ItemGroup'): data.groupName,
         localization.GetByLabel('UI/Inventory/ItemCategory'): data.categoryName,
         localization.GetByLabel('UI/Inventory/ItemSize'): pType,
         localization.GetByLabel('UI/Inventory/ItemSlot'): fType,
         localization.GetByLabel('UI/Inventory/ItemVolume'): '<right>%s' % data.volume,
         localization.GetByLabel('UI/Inventory/ItemMetaLevel'): '<right>%s' % data.metaLevel,
         localization.GetByLabel('UI/Inventory/ItemTechLevel'): '<right>%s' % techLevel}
        headers = GetVisibleItemHeaders(data.scrollID)
        labelList = []
        for each in headers:
            string = stringDict.get(each, '')
            labelList.append(string)

        label = '<t>'.join(labelList)
        data.label = label
    else:
        data.label = '<center>%s' % name
    return data.label


def GetItemQty(data, fmt = 'ln'):
    ret = getattr(data, 'qty_%s' % fmt, None)
    if ret is not None and ret[0] == data.item.stacksize:
        return ret[1]
    ret = ''
    if not (data.item.singleton or data.item.typeID in (const.typeBookmark,)):
        import util
        ret = util.FmtAmt(data.item.stacksize, fmt)
    setattr(data, 'qty_%s' % fmt, (data.item.stacksize, ret))
    return ret


NAMEABLE_GROUPS = (const.groupWreck,
 const.groupCargoContainer,
 const.groupSecureCargoContainer,
 const.groupAuditLogSecureContainer,
 const.groupFreightContainer,
 const.groupBiomass)

def IsValidNamedItem(invItem):
    if not invItem.singleton:
        return False
    elif invItem.categoryID == const.categoryShip:
        return True
    elif invItem.groupID in NAMEABLE_GROUPS:
        return True
    elif HasDeployComponent(invItem.typeID):
        return True
    else:
        return False


def GetItemName(invItem, data = None):
    if data and getattr(data, 'name', None):
        return data.name
    name = evetypes.GetName(invItem.typeID)
    if invItem.categoryID == const.categoryStation and invItem.groupID == const.groupStation:
        try:
            name = localization.GetByLabel('UI/Station/StationInSolarSystem', station=invItem.itemID, solarsystem=invItem.locationID)
        except KeyError('RecordNotFound'):
            sys.exc_clear()

    elif invItem.groupID == const.groupVoucher:
        voucherName = sm.GetService('voucherCache').GetVoucherName(invItem.itemID)
        if voucherName:
            name = voucherName
        else:
            name = localization.GetByLabel('UI/Common/Bookmark')
    elif IsValidNamedItem(invItem):
        locationName = cfg.evelocations.Get(invItem.itemID).name
        if locationName:
            name = locationName
    if data:
        data.name = name
    return name


def GetCategoryGroupTypeStringForItem(invItem):
    try:
        return '%s %s %s' % (evetypes.GetCategoryNameByCategory(invItem.categoryID), evetypes.GetGroupNameByGroup(invItem.groupID), evetypes.GetName(invItem.typeID))
    except IndexError:
        if invItem is None:
            log.LogTraceback('None is not an invItem')
            sys.exc_clear()
            return 'Unknown Unknown Unknown'
        log.LogTraceback('InvalidItem Report')
        sys.exc_clear()
        LogError('--------------------------------------------------')
        LogError('Invalid Item Report')
        LogError('Item: ', invItem)
        reason = ''
        typeName = 'Unknown'
        groupName = 'Unknown'
        categoryName = 'Unknown'
        try:
            typeID = getattr(invItem, 'typeID', None)
        except IndexError:
            typeID = None
            sys.exc_clear()

        try:
            groupID = getattr(invItem, 'groupID', None)
        except IndexError:
            groupID = None
            sys.exc_clear()

        try:
            categoryID = getattr(invItem, 'categoryID', None)
        except IndexError:
            categoryID = None
            sys.exc_clear()

        if typeID is None:
            LogError('typeID is missing. Probably caused by a coding mistake.')
            reason += 'item attribute typeID is missing (Probably a coding mistake). '
        else:
            typeExists = evetypes.Exists(typeID)
            if not typeExists:
                LogError('THERE IS NO type info FOR typeID:', typeID)
                LogError('THE DATABASE REQUIRES CLEANUP FOR THIS TYPE')
                reason += 'The type %s no longer exists. Database requires cleanup. ' % typeID
        if groupID is None:
            LogError('groupID is missing. Probably caused by a coding mistake.')
            reason += 'item attribute groupID is missing (Probably a coding mistake?). '
            if typeExists:
                LogWarn('Extracting groupID from type')
                groupID = evetypes.GetGroupID(typeID)
        groupExists = evetypes.GroupExists(groupID)
        if groupID is not None:
            if not groupExists:
                LogError('THERE IS NO group info FOR groupID:', groupID)
                LogError('THE DATABASE REQUIRES CLEANUP FOR THIS GROUP')
                reason += 'The group %s no longer exists. Database requires cleanup. ' % groupID
        if categoryID is None:
            LogError('categoryID is missing. Probably caused by a coding mistake.')
            reason += 'item attribute categoryID is missing (Probably a coding mistake?). '
            if groupExists:
                LogWarn('Extracting categoryID from group')
                categoryID = evetypes.GetCategoryIDByGroup(groupID)
        if categoryID is not None:
            if not evetypes.CategoryExists(categoryID):
                LogError('THERE IS NO category info FOR categoryID:', categoryID)
                LogError('THE DATABASE REQUIRES CLEANUP FOR THIS CATEGORY')
                reason += 'The category %s no longer exists. Database requires cleanup. ' % categoryID
        if typeExists:
            typeName = evetypes.GetName(typeID)
        if groupExists:
            groupName = evetypes.GetGroupNameByGroup(groupID)
        if evetypes.CategoryExists(categoryID):
            categoryName = evetypes.GetCategoryNameByCategory(categoryID)
        LogError('--------------------------------------------------')
        eve.Message('CustomInfo', {'info': 'Invalid item detected:<br>Item:%s<br>CGT:%s %s %s<br>Reason: %s' % (invItem,
                  categoryName,
                  groupName,
                  typeName,
                  reason)})
        return '%s %s %s' % (categoryName, groupName, typeName)


def GetSlimItemName(slimItem):
    import util
    if slimItem.categoryID == const.categoryShip or HasNpcPilotComponent(slimItem.typeID):
        if not slimItem.charID or slimItem.charID == session.charid and slimItem.itemID != session.shipid:
            return evetypes.GetName(slimItem.typeID)
        if util.IsCharacter(slimItem.charID):
            return cfg.eveowners.Get(slimItem.charID).name
    else:
        if slimItem.groupID == const.groupHarvestableCloud:
            return localization.GetByLabel('UI/Inventory/SlimItemNames/SlimHarvestableCloud', cloudType=evetypes.GetName(slimItem.typeID))
        if slimItem.categoryID == const.categoryAsteroid:
            return localization.GetByLabel('UI/Inventory/SlimItemNames/SlimAsteroid', asteroidType=evetypes.GetName(slimItem.typeID))
        if slimItem.categoryID == const.categoryOrbital:
            return localization.GetByLabel('UI/Inventory/SlimItemNames/SlimOrbital', typeID=slimItem.typeID, planetID=slimItem.planetID, corpName=cfg.eveowners.Get(slimItem.ownerID).name)
    locationname = cfg.evelocations.Get(slimItem.itemID).name
    if locationname and locationname[0] != '@':
        if slimItem.groupID == const.groupBeacon:
            dungeonNameID = getattr(slimItem, 'dungeonNameID', None)
            if dungeonNameID:
                translatedName = localization.GetByMessageID(dungeonNameID)
                return translatedName
        return locationname
    else:
        return evetypes.GetName(slimItem.typeID)


def EditStationName(stationname, compact = 0, usename = 0):
    if compact:
        longForm = localization.GetByLabel('UI/Locations/LocationMoonLong') + ' '
        shortForm = localization.GetByLabel('UI/Locations/LocationMoonShort')
        stationname = stationname.replace(longForm, shortForm).replace(longForm.lower(), shortForm.lower())
    _stationname = stationname.split(' - ')
    if len(_stationname) >= 2 and usename:
        stationname = _stationname[-1]
    return stationname


def GetOrMakeChild(parent, name, make):
    ret = uiutil.FindChild(parent, name)
    if ret:
        return ret
    else:
        ret = make()
        ret.state = uiconst.UI_HIDDEN
        ret.name = name
        parent.children.insert(0, ret)
        return ret


def GetTextHeight(strng, width = 0, fontsize = fontConst.EVE_MEDIUM_FONTSIZE, linespace = None, hspace = 0, uppercase = 0, specialIndent = 0, getTextObj = 0, tabs = [], maxLines = None, **kwds):
    return uicore.font.GetTextHeight(strng, width=width, font=None, fontsize=fontsize, linespace=linespace, letterspace=hspace, uppercase=uppercase, specialIndent=specialIndent, getTextObj=getTextObj, tabs=tabs, maxLines=maxLines)


def GetTextWidth(strng, fontsize = fontConst.EVE_MEDIUM_FONTSIZE, hspace = 0, uppercase = 0):
    return uicore.font.GetTextWidth(strng, fontsize, hspace, uppercase)


def GetWindowAbove(fromItem):
    if fromItem == uicore.desktop:
        return None
    if getattr(fromItem, 'isDockWnd', 0) == 1:
        return fromItem
    if fromItem.parent and not fromItem.parent.destroyed:
        return GetWindowAbove(fromItem.parent)


def ShowMinDevice():
    for each in uicore.desktop.children[:]:
        if each.name == 'devicegrid':
            each.Close()

    sizes = [(1024, 768)]
    for w, h in sizes:
        p = uiprimitives.Container(name='devicegrid', parent=uicore.desktop, pos=(0,
         0,
         w,
         h), state=uiconst.UI_DISABLED, align=uiconst.CENTER)
        uicontrols.Frame(parent=p, color=(1.0, 1.0, 1.0, 0.25))


def GetStanding(standing, type = 0):
    if standing > 5:
        return localization.GetByLabel('UI/Standings/Excellent')
    elif standing > 0:
        return localization.GetByLabel('UI/Standings/Good')
    elif standing == 0:
        return localization.GetByLabel('UI/Standings/Neutral')
    elif standing < -5:
        return localization.GetByLabel('UI/Standings/Terrible')
    elif standing < 0:
        return localization.GetByLabel('UI/Standings/Bad')
    else:
        return localization.GetByLabel('UI/Standings/Unknown')


def GetMappedRankBase(rank, warFactionID, align):
    logo = uiprimitives.Sprite(align=align)
    if rank < 0:
        logo.texture = None
    else:
        iconNum = '%s_%s' % (rank / 4 + 1, rank % 4 + 1)
        MapLogo(iconNum, logo, root='res:/UI/Texture/Medals/Ranks/%s_' % warFactionID)
    if align != uiconst.TOALL:
        logo.width = logo.height = 128
    else:
        logo.width = logo.height = 0
    return logo


def MapLogo(iconNum, sprite, root = 'res:/UI/Texture/Corps/corps'):
    texpix, num = iconNum.split('_')
    while texpix.find('0') == 0:
        texpix = texpix[1:]

    sprite.texturePath = '%s%s%s.dds' % (root, ['', '0'][int(texpix) < 10], texpix)
    num = int(num)
    sprite.rectWidth = sprite.rectHeight = 128
    sprite.rectLeft = [0, 128][num in (2, 4)]
    sprite.rectTop = [0, 128][num > 2]


def GetTechLevelIconID(metaGroupID):
    if metaGroupID == const.metaGroupStoryline:
        return 'res:/UI/Texture/Icons/73_16_245.png'
    if metaGroupID == const.metaGroupFaction:
        return 'res:/UI/Texture/Icons/73_16_246.png'
    if metaGroupID == const.metaGroupOfficer:
        return 'res:/UI/Texture/Icons/73_16_248.png'
    if metaGroupID == const.metaGroupDeadspace:
        return 'res:/UI/Texture/Icons/73_16_247.png'


def GetTechLevelIconPathAndHint(typeID = None):
    if typeID is None:
        return (None, None)
    try:
        if evetypes.GetCategoryID(typeID) in (const.categoryBlueprint, const.categoryAncientRelic):
            ptID = cfg.blueprints.Get(typeID).productTypeID
            if ptID is not None:
                typeID = ptID
    except Exception:
        pass

    godmaSvc = sm.GetService('godma')
    structureVisualFlag = godmaSvc.GetTypeAttribute(typeID, const.attributeStructureItemVisualFlag)
    if structureVisualFlag:
        return ('res:/UI/Texture/Shared/structureOverlay.png', localization.GetByLabel('UI/Inventory/StructureModule'))
    techLevel = godmaSvc.GetTypeAttribute(typeID, const.attributeTechLevel)
    if techLevel:
        techLevel = int(techLevel)
    groupID = None
    metaGroupID = godmaSvc.GetTypeAttribute(typeID, const.attributeMetaGroupID)
    if metaGroupID:
        groupID = int(metaGroupID)
    icon = hint = None
    if groupID or techLevel in (2, 3):
        if groupID:
            icon = GetTechLevelIconID(groupID)
            hint = cfg.invmetagroups.Get(groupID).name
        else:
            icon, hint = {2: ('res:/UI/Texture/Icons/73_16_242.png', localization.GetByLabel('UI/Inventory/TechLevel2')),
             3: ('res:/UI/Texture/Icons/73_16_243.png', localization.GetByLabel('UI/Inventory/TechLevel3'))}.get(techLevel, None)
    return (icon, hint)


def GetTechLevelIcon(tlicon = None, offset = 0, typeID = None):
    icon, hint = GetTechLevelIconPathAndHint(typeID)
    if icon:
        if tlicon is None:
            tlicon = uicontrols.Icon(icon=icon, parent=None, width=16, height=16, align=uiconst.TOPLEFT, idx=0, hint=hint)
        else:
            uiutil.MapIcon(tlicon, icon)
            tlicon.hint = hint
        if offset:
            tlicon.top = offset
        tlicon.state = uiconst.UI_NORMAL
    elif tlicon:
        tlicon.state = uiconst.UI_HIDDEN
    return tlicon


def GetBigButton(size = 128, where = None, left = 0, top = 0, menu = 0, align = 0, iconMargin = 0, hint = '', width = None, height = None):
    import xtriui
    if width is None:
        width = size
    if height is None:
        height = size
    btn = xtriui.BigButton(parent=where, left=left, top=top, width=width, height=height, hint=hint, align=align)
    btn.Startup(width, height, iconMargin)
    return btn


def GetBallparkRecord(itemID):
    bp = sm.GetService('michelle').GetBallpark()
    if bp and hasattr(bp, 'GetInvItem'):
        return bp.GetInvItem(itemID)
    else:
        return None


def Close(owner, wndNames):
    for each in wndNames:
        if getattr(owner, each, None):
            wnd = getattr(owner, each, None)
            setattr(owner, each, None)
            if not wnd.destroyed:
                wnd.Close()


def GetDatePicker(where, setval = None, left = 0, top = 0, idx = None, withTime = False, timeparts = 4, startYear = None, yearRange = None):
    import xtriui
    picker = xtriui.DatePicker(name='datepicker', parent=where, align=uiconst.TOPLEFT, width=256, height=18, left=left, top=top)
    picker.Startup(setval, withTime, timeparts, startYear, yearRange)
    if idx is not None:
        uiutil.SetOrder(picker, idx)
    return picker


def GetContainerHeader(caption, where, bothlines = 1, xmargin = 0):
    container = uiprimitives.Container(name='headercontainer', parent=where, align=uiconst.TOTOP, height=18)
    par = uiprimitives.Container(name='headerparent', align=uiconst.TOALL, parent=container, padding=(xmargin,
     0,
     xmargin,
     0))
    FillThemeColored(parent=par, colorType=uiconst.COLORTYPE_UIHEADER, align=uiconst.TOALL, opacity=0.15)
    t = uicontrols.EveLabelMedium(text=caption, name='header1', parent=par, padding=(8, 1, 8, 2), align=uiconst.TOTOP, bold=True)
    container.height = t.textheight + 3
    return container


def GetSlider(name = 'slider', where = None, config = '', minval = None, maxval = None, header = '', hint = '', align = None, width = 0, height = 18, left = 0, top = 0, setlabelfunc = None, getvaluefunc = None, endsliderfunc = None, gethintfunc = None, increments = [], underlay = 1):
    if align is None:
        align = uiconst.TOTOP
    mainpar = uiprimitives.Container(name=config + '_slider', align=align, width=width, height=height, left=left, top=top, state=uiconst.UI_NORMAL, parent=where)
    slider = uicontrols.Slider(parent=mainpar, align=uiconst.TOPLEFT, top=6, state=uiconst.UI_NORMAL)
    lbl = uicontrols.EveLabelSmall(text='', parent=mainpar, left=7, top=-14, state=uiconst.UI_NORMAL)
    lbl.name = 'label'
    if getvaluefunc:
        slider.GetSliderValue = getvaluefunc
    if setlabelfunc:
        slider.SetSliderLabel = setlabelfunc
    if gethintfunc:
        slider.GetSliderHint = gethintfunc
    slider.Startup(config, minval, maxval, config, header, increments=increments)
    slider.name = name
    mainpar.hint = hint
    if endsliderfunc:
        slider.EndSetSliderValue = endsliderfunc
    return mainpar


def GetFileDialog(path = None, fileExtensions = None, multiSelect = False, selectionType = SEL_FILES):
    from eve.client.script.ui.control.fileDialog import FileDialog
    wnd = FileDialog.Open(path=path, fileExtensions=fileExtensions, multiSelect=multiSelect, selectionType=selectionType)
    wnd.width = 400
    wnd.height = 400
    if wnd.ShowModal() == 1:
        return wnd.result
    else:
        return None


def _PrimeSearchResultsInEveOwners(results):
    if results:
        cfg.eveowners.Prime(results)


def __Search(searchStr, groupID, exact, filterCorpID, hideNPC = False):
    import searchUtil
    result = []
    if groupID == const.groupCharacter:
        groupIDList = [const.searchResultCharacter]
        if not hideNPC:
            groupIDList.append(const.searchResultAgent)
        result = searchUtil.QuickSearch(searchStr, groupIDList, exact)
        _PrimeSearchResultsInEveOwners(result)
    elif groupID == const.groupCorporation:
        onlyAltName = False
        groupIDList = [const.searchResultCorporation]
        if exact == -1:
            onlyAltName = True
        elif filterCorpID == -1:
            hideNPC = True
        result = searchUtil.QuickSearch(searchStr, groupIDList, exact, hideNPC=hideNPC, onlyAltName=onlyAltName)
        _PrimeSearchResultsInEveOwners(result)
    elif groupID == const.groupAlliance:
        onlyAltName = False
        groupIDList = [const.searchResultAlliance]
        if exact == -1:
            onlyAltName = True
        result = searchUtil.QuickSearch(searchStr, groupIDList, exact, onlyAltName=onlyAltName)
        _PrimeSearchResultsInEveOwners(result)
    elif groupID == const.groupStation:
        result = searchUtil.QuickSearch(searchStr, [const.searchResultStation, const.searchResultStructure], exact)
    elif groupID == const.groupFaction:
        result = searchUtil.QuickSearch(searchStr, [const.searchResultFaction], exact)
    elif groupID == const.groupSolarSystem:
        result = searchUtil.QuickSearch(searchStr, [const.searchResultSolarSystem, const.searchResultWormHoles], exact)
    elif evetypes.GetCategoryIDByGroup(groupID) == const.categoryCelestial:
        result = sm.RemoteSvc('lookupSvc').LookupKnownLocationsByGroup(groupID, searchStr)
        result = [ each.itemID for each in result ]
        if result:
            cfg.evelocations.Prime(result)
    return result


def __ValidSearch(searchStr, getError, exact):
    searchStr = searchStr.replace('%', '').replace('?', '')
    if len(searchStr) < 1:
        sm.GetService('loading').StopCycle()
        if getError:
            return localization.GetByLabel('UI/Common/PleaseTypeSomething')
        eve.Message('LookupStringMinimum', {'minimum': 1})
        return None
    if len(searchStr) >= 100 or exact == -1 and len(searchStr) > 5:
        sm.GetService('loading').StopCycle()
        if getError:
            return localization.GetByLabel('UI/Common/SearchStringTooLong')
        eve.Message('CustomInfo', {'info': localization.GetByLabel('UI/Common/SearchStringTooLong')})
        return None
    return searchStr


def Search(searchStr, groupID, categoryID = None, modal = 1, exact = const.searchByPartialTerms, getError = 0, notifyOneMatch = 0, filterCorpID = None, hideNPC = 0, searchWndName = 'mySearch', getWindow = 1, listType = None, hideDustChars = False):
    searchStr = __ValidSearch(searchStr, getError, exact)
    if not searchStr:
        return
    attrGroupName = {const.groupCharacter: 'Character',
     const.groupCorporation: 'Corporation',
     const.groupFaction: 'Faction',
     const.groupStation: 'Station',
     const.groupAsteroidBelt: 'Asteroid Belt',
     const.groupSolarSystem: 'SolarSystem',
     const.groupConstellation: 'Constellation',
     const.groupRegion: 'Region',
     const.groupAlliance: 'Alliance'}.get(groupID, '')
    attrLocGroupNamePlural = {const.groupCharacter: 'UI/Common/Characters',
     const.groupCorporation: 'UI/Common/Corporations',
     const.groupFaction: 'UI/Common/Factions',
     const.groupStation: 'UI/Common/Stations',
     const.groupAsteroidBelt: 'UI/Common/AsteroidBelts',
     const.groupSolarSystem: 'UI/Common/SolarSystems',
     const.groupConstellation: 'UI/Common/Constellations',
     const.groupRegion: 'UI/Common/Regions',
     const.groupAlliance: 'UI/Common/Alliances'}.get(groupID, '')
    if categoryID:
        if categoryID == const.categoryOwner:
            groupIDList = [const.searchResultCharacter, const.searchResultCorporation]
            if not hideNPC:
                groupIDList.append(const.searchResultAgent)
            result = searchUtil.QuickSearch(searchStr, groupIDList, exact, hideNPC=hideNPC)
            _PrimeSearchResultsInEveOwners(result)
            displayGroupName = localization.GetByLabel('UI/Common/Owner')
            displayGroupNamePlural = localization.GetByLabel('UI/Common/Owners')
        elif categoryID == const.categoryStructure:
            groupIDList = [const.searchResultStructure, const.searchResultStation]
            result = searchUtil.QuickSearch(searchStr, groupIDList, exact)
            displayGroupName = localization.GetByLabel('UI/Common/Location')
            displayGroupNamePlural = localization.GetByLabel('UI/Common/Locations')
    else:
        displayGroupName = evetypes.GetGroupNameByGroup(groupID)
        if attrGroupName and attrLocGroupNamePlural:
            displayGroupNamePlural = localization.GetByLabel(attrLocGroupNamePlural)
        else:
            displayGroupNamePlural = displayGroupName
        result = __Search(searchStr, groupID, exact, filterCorpID, hideNPC)
    if not result:
        sm.GetService('loading').StopCycle()
        if searchStr[-1] == '*':
            searchStr = searchStr[:-1]
        if getError:
            return localization.GetByLabel('UI/Search/NoGroupFoundWith', groupName=displayGroupName, searchTerm=searchStr)
        if exact and groupID == const.groupCharacter:
            eve.Message('CustomInfo', {'info': localization.GetByLabel('UI/Search/NoCharacterFoundWith', searchTerm=searchStr)})
        else:
            eve.Message('CustomInfo', {'info': localization.GetByLabel('UI/Search/NoGroupFoundWith', groupName=displayGroupName, searchTerm=searchStr)})
        return
    if len(result) == 1:
        if groupID == const.groupCharacter and hideDustChars and util.IsDustCharacter(result[0]):
            if exact:
                eve.Message('CustomInfo', {'info': localization.GetByLabel('UI/Search/NoEVECharacterFoundWith', searchTerm=searchStr)})
            else:
                eve.Message('CustomInfo', {'info': localization.GetByLabel('UI/Search/NoEVEGroupFoundWith', groupName=displayGroupName, searchTerm=searchStr)})
            return
        if result[0] and modal:
            if notifyOneMatch:
                return (result[0], 1)
            return result[0]
        hint = localization.GetByLabel('UI/Search/OneGroupFoundWith', groupName=displayGroupName, searchTerm=searchStr)
    else:
        hint = localization.GetByLabel('UI/Search/ManyGroupsFoundWith', itemCount=len(result), groupNames=displayGroupNamePlural, searchTerm=searchStr)
    tmplist = []
    corpTickersToPrime = []
    for each in result:
        if categoryID == const.categoryOwner:
            ownerData = cfg.eveowners.Get(each)
            if ownerData.typeID == const.typeCorporation:
                groupID = const.groupCorporation
            elif ownerData.typeID == const.typeAlliance:
                groupID = const.groupAlliance
            else:
                groupID = const.groupCharacter
        if groupID == const.groupCorporation:
            corpTickersToPrime.append(each)
        if groupID == const.groupCharacter and util.IsNPC(each):
            agentInfo = sm.GetService('agents').GetAgentByID(each)
            if agentInfo is not None and agentInfo.agentTypeID == const.agentTypeAura:
                if each != sm.GetService('agents').GetAuraAgentID():
                    continue
        elif groupID == const.groupCharacter and hideDustChars and util.IsDustCharacter(each):
            continue
        if categoryID == const.categoryStructure and not util.IsStation(each):
            structureInfo = sm.GetService('structureDirectory').GetStructureInfo(each)
            if structureInfo is None:
                continue
            typeID = structureInfo.typeID
            name = structureInfo.itemName
        else:
            typeID = GetType(each, groupID)
            name = GetName(each, groupID)
        if each and name:
            tmplist.append((name, each, typeID or 0))

    cfg.corptickernames.Prime(corpTickersToPrime)
    sm.GetService('loading').StopCycle()
    if getWindow:
        selectionText = localization.GetByLabel('UI/Search/GenericSelection', groupName=displayGroupName)
        if listType is None:
            listType = attrGroupName.lower()
            if not listType:
                listType = 'Generic'
        chosen = ListWnd(tmplist, listType, [displayGroupNamePlural, selectionText][modal], hint, 1, minChoices=modal, isModal=modal, windowName=searchWndName, unstackable=1)
        if chosen:
            return chosen[1]
    else:
        return tmplist


def GetName(rec, groupID = None):
    if groupID in (const.groupCharacter,
     const.groupCorporation,
     const.groupFaction,
     const.groupAlliance):
        return cfg.eveowners.Get(rec).name
    if groupID in (const.groupStation,
     const.groupAsteroidBelt,
     const.groupSolarSystem,
     const.groupConstellation,
     const.groupRegion):
        return cfg.evelocations.Get(rec).name
    return ''


def GetType(rec, groupID = None):
    if groupID in (const.groupCharacter,
     const.groupCorporation,
     const.groupFaction,
     const.groupAlliance):
        return cfg.eveowners.Get(rec).typeID
    if groupID == const.groupStation:
        return cfg.stations.Get(rec).stationTypeID
    if groupID == const.groupSolarSystem:
        return const.typeSolarSystem
    if groupID == const.groupConstellation:
        return const.typeConstellation
    if groupID == const.groupRegion:
        return const.typeRegion
    if groupID == const.groupAsteroidBelt:
        return const.typeAsteroidBelt
    return 0


def SearchOwners(searchStr, groupIDs = None, exact = False, notifyOneMatch = False, hideNPC = False, getError = False, searchWndName = 'mySearch'):
    if type(groupIDs) == int:
        groupIDs = [groupIDs]
    elif groupIDs is None:
        groupIDs = [const.groupCharacter,
         const.groupCorporation,
         const.groupAlliance,
         const.groupFaction]
    groupNames = {const.groupCharacter: [localization.GetByLabel('UI/Common/Character'), localization.GetByLabel('UI/Common/Characters')],
     const.groupCorporation: [localization.GetByLabel('UI/Common/Corporation'), localization.GetByLabel('UI/Common/Corporations')],
     const.groupAlliance: [localization.GetByLabel('UI/Common/Alliance'), localization.GetByLabel('UI/Common/Alliances')],
     const.groupFaction: [localization.GetByLabel('UI/Common/Faction'), localization.GetByLabel('UI/Common/Factions')]}
    searchStr = searchStr.replace('%', '').replace('?', '')
    if len(searchStr) < 1:
        sm.GetService('loading').StopCycle()
        if getError:
            return localization.GetByLabel('UI/Common/PleaseTypeSomething')
        eve.Message('LookupStringMinimum', {'minimum': 1})
        return
    if len(searchStr) >= 100 or exact == -1 and len(searchStr) > 5:
        sm.GetService('loading').StopCycle()
        if getError:
            return localization.GetByLabel('UI/Common/SearchStringTooLong')
        eve.Message('CustomInfo', {'info': localization.GetByLabel('UI/Common/SearchStringTooLong')})
        return
    displayGroupName = ''
    displayGroupNamePlural = ''
    for g in groupNames:
        if g in groupIDs:
            displayGroupName += groupNames[g][0] + '/'
            displayGroupNamePlural += groupNames[g][1] + '/'

    displayGroupName = displayGroupName[:-1]
    displayGroupNamePlural = displayGroupNamePlural[:-1]
    if hideNPC:
        owners = sm.RemoteSvc('lookupSvc').LookupPCOwners(searchStr, exact)
    else:
        owners = sm.RemoteSvc('lookupSvc').LookupOwners(searchStr, exact)
    list = []
    for o in owners:
        if o.groupID in groupIDs:
            list.append(('%s %s' % (o.ownerName, groupNames[o.groupID][0]), o.ownerID, o.typeID))

    if not list:
        sm.GetService('loading').StopCycle()
        if getError:
            return localization.GetByLabel('UI/Search/NoGroupFoundWith', groupName=displayGroupName, searchTerm=searchStr)
        eve.Message('CustomInfo', {'info': localization.GetByLabel('UI/Search/NoGroupFoundWith', groupName=displayGroupName, searchTerm=searchStr)})
        return
    if len(list) == 1 and not notifyOneMatch:
        return list[0][1]
    hint = localization.GetByLabel('UI/Search/ManyGroupsFoundWith', itemCount=len(list), groupNames=displayGroupNamePlural, searchTerm=searchStr)
    chosen = ListWnd(lst=list, listtype='owner', caption=localization.GetByLabel('UI/Search/GenericSelection', groupName=displayGroupName), hint=hint, ordered=1, minChoices=1, windowName=searchWndName)
    if chosen:
        return chosen[1]


def ShowInfo(typeID, itemID, abstractinfo = None, *args):
    sm.GetService('info').ShowInfo(typeID=typeID, itemID=itemID, abstractinfo=abstractinfo)


def GetStationByName(searchstr, flag = 0):
    result = None
    try:
        result = sm.RemoteSvc('lookupSvc').LookupStations(searchstr)
    except:
        sys.exc_clear()
        return

    return result


def SearchStation(stationname, flag = 0):
    if len(stationname) < 1:
        sm.GetService('loading').StopCycle()
        eve.Message('CustomInfo', {'info': localization.GetByLabel('UI/Common/PleaseTypeSomething')})
        return
    stationinfo = GetStationByName(stationname.lower(), flag)
    if stationinfo is None or not len(stationinfo):
        sm.GetService('loading').StopCycle()
        eve.Message('CustomInfo', {'info': localization.GetByLabel('UI/Search/NoStationFoundWith', searchTerm=stationname)})
        return
    if len(stationinfo) > 20:
        sm.GetService('loading').StopCycle()
        eve.Message('CustomInfo', {'info': localization.GetByLabel('UI/Search/MoreThanLimitStationsFound', limit=20, searchTerm=stationname)})
        return
    if len(stationinfo) >= 1 and len(stationinfo) <= 20:
        if len(stationinfo) == 1:
            if stationinfo[0].stationName == stationname:
                return
            hint = localization.GetByLabel('UI/Search/OneStationFoundWith', searchTerm=stationname)
        elif len(stationinfo) <= 20:
            hint = localization.GetByLabel('UI/Search/ManyStationsFoundWith', itemCount=len(stationinfo), searchTerm=stationname)
        if len(stationinfo) == 1:
            return stationinfo[0].stationID
        tmplist = []
        for each in stationinfo:
            tmplist.append((each.stationName, each.stationID, 0))

        sm.GetService('loading').StopCycle()
        choosestation = ListWnd(tmplist, 'station', localization.GetByLabel('UI/Search/SelectStation'), hint, 1)
        if choosestation:
            return choosestation[1]


def FittingFlags():
    flags = []
    for key in FITKEYS:
        for i in range(8):
            flags.append(util.LookupConstValue('flag%sSlot%s' % (key, i)))

    return flags


def ListWnd(lst, listtype = None, caption = None, hint = None, ordered = 0, minw = 200, minh = 256, minChoices = 1, maxChoices = 1, initChoices = [], validator = None, isModal = 1, scrollHeaders = [], iconMargin = 0, windowName = 'listwindow', lstDataIsGrouped = 0, unstackable = 0, noContentHint = None):
    if caption is None:
        caption = localization.GetByLabel('UI/Search/SelectItem')
    from eve.client.script.ui.control.listwindow import ListWindow
    ListWindow.CloseIfOpen(windowID=windowName)
    wnd = ListWindow(windowID=windowName, lst=lst, listtype=listtype, ordered=ordered, minSize=(minw, minh), caption=caption, minChoices=minChoices, maxChoices=maxChoices, initChoices=initChoices, validator=validator, scrollHeaders=scrollHeaders, iconMargin=iconMargin, lstDataIsGrouped=lstDataIsGrouped, noContentHint=noContentHint)
    if hint:
        wnd.SetHint(['<center>', hint])
    if unstackable:
        wnd.MakeUnstackable()
    if isModal:
        wnd.DefineButtons(uiconst.OKCANCEL)
        if wnd.ShowModal() == uiconst.ID_OK:
            return wnd.result
        else:
            return
    else:
        wnd.DefineButtons(uiconst.CLOSE)
        wnd.Maximize()
        uiutil.SetOrder(wnd, 0)


def HybridWnd(format, caption, modal = 1, windowID = None, buttons = None, location = None, minW = 256, minH = 256, blockconfirm = 0, icon = None, unresizeAble = 0, ignoreCurrent = 1):
    if windowID is not None:
        wnd = uicontrols.Window.GetIfOpen(windowID=windowID)
        if wnd:
            return
    windowID = windowID or caption
    if buttons is None:
        buttons = uiconst.OK
    from eve.client.script.ui.control.hybridWindow import HybridWindow
    wnd = HybridWindow.Open(ignoreCurrent=ignoreCurrent, format=format, caption=caption, modal=modal, windowID=windowID, buttons=buttons, location=location, minW=minW, minH=minH, icon=icon, blockconfirm=blockconfirm)
    wnd.MakeUnstackable()
    if unresizeAble:
        wnd.MakeUnResizeable()
    import uthread
    uthread.new(wnd.OnScale_)
    if modal == 1:
        if wnd.ShowModal() == uiconst.ID_OK:
            return wnd.result
        else:
            return
    return wnd


def TextBox(header, txt, modal = 0, windowID = 'generictextbox2', tabs = [], preformatted = 0, scrolltotop = 1):
    wnd = uicontrols.Window.GetIfOpen(windowID=windowID)
    if wnd is None or wnd.destroyed or uicore.uilib.Key(uiconst.VK_SHIFT):
        format = [{'type': 'textedit',
          'readonly': 1,
          'label': '_hide',
          'key': 'text'}]
        wnd = HybridWnd(format, header, modal, windowID, uiconst.CLOSE, None, minW=256, minH=128)
        if wnd:
            wnd.form.align = uiconst.TOALL
            wnd.form.left = wnd.form.width = 3
            wnd.form.top = -2
            wnd.form.height = 6
            wnd.form.sr.text.parent.align = uiconst.TOALL
            wnd.form.sr.text.parent.left = wnd.form.sr.text.parent.top = wnd.form.sr.text.parent.width = wnd.form.sr.text.parent.height = 0
            wnd.form.sr.text.parent.children[0].height = 0
            wnd.form.sr.text.autoScrollToBottom = 0
    if wnd is not None:
        i = 1
        for t in tabs:
            setattr(wnd.form.sr.text.content.control, 'tabstop%s' % i, t)
            i = i + 1

        wnd.form.sr.text.SetValue(txt, scrolltotop=scrolltotop, preformatted=preformatted)
        if wnd.state == uiconst.UI_NORMAL:
            uiutil.SetOrder(wnd, 0)
        else:
            wnd.Maximize()


def NamePopupErrorCheck(ret):
    if not len(ret['name']) or len(ret['name']) and len(ret['name'].strip()) < 1:
        return localization.GetByLabel('UI/Common/PleaseTypeSomething')
    return ''


def QtyPopup(maxvalue = None, minvalue = 0, setvalue = '', hint = None, caption = None, label = '', digits = 0):
    if caption is None:
        caption = localization.GetByLabel('UI/Common/SetQuantity')
    if maxvalue is not None and hint is None:
        hint = localization.GetByLabel('UI/Common/SetQtyBetween', min=util.FmtAmt(minvalue), max=util.FmtAmt(maxvalue))
        if setvalue == 0:
            setvalue = maxvalue
    maxvalue = maxvalue or min(maxvalue, sys.maxint)
    format = []
    if hint is not None:
        format += [{'type': 'text',
          'text': hint,
          'frame': 0}]
    if label is not None:
        format += [{'type': 'labeltext',
          'label': label,
          'text': '',
          'frame': 0,
          'labelwidth': 180}]
    if digits:
        format += [{'type': 'edit',
          'setvalue': setvalue,
          'floatonly': [minvalue, maxvalue, digits],
          'key': 'qty',
          'label': '_hide',
          'required': 1,
          'frame': 0,
          'setfocus': 1,
          'selectall': 1}]
    else:
        format += [{'type': 'edit',
          'setvalue': setvalue,
          'intonly': [minvalue, maxvalue],
          'key': 'qty',
          'label': '_hide',
          'required': 1,
          'frame': 0,
          'setfocus': 1,
          'selectall': 1}]
    return HybridWnd(format, caption, 1, None, uiconst.OKCANCEL, None, minW=240, minH=80)


def GetInvItemDefaultHiddenHeaders():
    return [localization.GetByLabel('UI/Inventory/ItemMetaLevel'), localization.GetByLabel('UI/Inventory/ItemTechLevel'), localization.GetByLabel('UI/Inventory/ItemCategory')]


def GetInvItemDefaultHeaders():
    return [localization.GetByLabel('UI/Common/Name'),
     localization.GetByLabel('UI/Common/Quantity'),
     localization.GetByLabel('UI/Inventory/ItemGroup'),
     localization.GetByLabel('UI/Inventory/ItemCategory'),
     localization.GetByLabel('UI/Inventory/ItemSize'),
     localization.GetByLabel('UI/Inventory/ItemSlot'),
     localization.GetByLabel('UI/Inventory/ItemVolume'),
     localization.GetByLabel('UI/Inventory/ItemMetaLevel'),
     localization.GetByLabel('UI/Inventory/ItemTechLevel')]


def GetVisibleItemHeaders(scrollID):
    defaultHeaders = GetInvItemDefaultHeaders()
    hiddenColumns = settings.user.ui.Get('filteredColumns_%s' % uiconst.SCROLLVERSION, {}).get(scrollID, [])
    allHiddenColumns = hiddenColumns + settings.user.ui.Get('filteredColumnsByDefault_%s' % uiconst.SCROLLVERSION, {}).get((scrollID, session.languageID), [])
    filterColumns = filter(lambda x: x not in allHiddenColumns, defaultHeaders)
    return filterColumns


def CheckAudioFileForEnglish(audioPath):
    if settings.user.ui.Get('forceEnglishVoice', False):
        audioPath = audioPath[:-3] + 'EN.' + audioPath[-3:]
    return audioPath


def GetLightYearDistance(fromSystem, toSystem, fraction = True):
    for system in (fromSystem, toSystem):
        if type(system) not in (types.IntType, types.InstanceType, types.LongType):
            return None
        if util.IsWormholeSystem(system):
            return None

    def GetLoc(system):
        if type(system) in (types.IntType, types.LongType):
            return cfg.evelocations.Get(system)
        if type(system) == types.InstanceType:
            return system

    fromSystem = GetLoc(fromSystem)
    toSystem = GetLoc(toSystem)
    dist = math.sqrt((toSystem.x - fromSystem.x) ** 2 + (toSystem.y - fromSystem.y) ** 2 + (toSystem.z - fromSystem.z) ** 2) / const.LIGHTYEAR
    if fraction:
        dist = float(int(dist * 10)) / 10
    return dist


def HideButtonFromGroup(btns, label, button = None):
    if label:
        btn = uiutil.FindChild(btns, '%s_Btn' % label)
        if btn:
            btn.state = uiconst.UI_HIDDEN
    if button:
        btn.state = uiconst.UI_HIDDEN


def ShowButtonFromGroup(btns, label, button = None):
    if label:
        btn = uiutil.FindChild(btns, '%s_Btn' % label)
        if btn:
            btn.state = uiconst.UI_NORMAL
    if button:
        btn.state = uiconst.UI_NORMAL


def FadeCont(cont, fadeIn, after = 0, fadeTime = 500.0):
    if getattr(cont, 'fading', 0) == 1:
        return
    if fadeIn:
        current = cont.opacity
        end = 1.0
    else:
        current = cont.opacity
        end = 0.0
    setattr(cont, 'fading', 1)
    blue.pyos.synchro.SleepWallclock(after)
    start, ndt = blue.os.GetWallclockTime(), 0.0
    while ndt != 1.0:
        if not cont or cont.destroyed:
            break
        ndt = min(blue.os.TimeDiffInMs(start, blue.os.GetWallclockTime()) / fadeTime, 1.0)
        cont.opacity = mathUtil.Lerp(current, end, ndt)
        blue.pyos.synchro.Yield()

    if cont and not cont.destroyed:
        setattr(cont, 'fading', 0)


def FormatMedalData(data):
    import xtriui
    fdata = []
    for part in (1, 2):
        dpart = {1: xtriui.Ribbon,
         2: xtriui.Medal}.get(part, None)
        pdata = []
        for row in data.Filter('part').get(part):
            label, icon = row.graphic.split('.')
            color = row.color
            pdata.append((label, icon, color))

        fdata.append([dpart, pdata])

    return fdata


def GetFullscreenProjectionViewAndViewport():
    viewport = trinity.device.viewport
    camera = sm.GetService('sceneManager').GetActiveCamera()
    return (camera.projectionMatrix, camera.viewMatrix, viewport)


def GetOwnerLogo(parent, ownerID, size = 64, noServerCall = False):
    if util.IsCharacter(ownerID):
        logo = uicontrols.Icon(icon=None, parent=parent, pos=(0,
         0,
         size,
         size), ignoreSize=True)
        if size < 64:
            fetchSize = 64
        else:
            fetchSize = size
        sm.GetService('photo').GetPortrait(ownerID, fetchSize, logo)
    elif util.IsCorporation(ownerID) or util.IsAlliance(ownerID) or util.IsFaction(ownerID):
        uiutil.GetLogoIcon(itemID=ownerID, parent=parent, pos=(0,
         0,
         size,
         size), ignoreSize=True)
    else:
        raise RuntimeError('ownerID %d is not of an owner type!!' % ownerID)


def GetTiDiAdjustedAnimationTime(normalDuation, minTiDiValue = 0.1, minValue = None, *args):
    curFactor = blue.os.desiredSimDilation
    multiplier = max(curFactor, minTiDiValue)
    returnValue = multiplier * normalDuation
    if minValue is not None:
        returnValue = max(minValue, returnValue)
    return returnValue


def FindLocalStargate(destinationID, *args):
    if session.solarsystemid is None:
        return
    michelle = sm.GetService('michelle')
    solarSystemItems = cfg.GetLocationsLocalBySystem(session.solarsystemid, requireLocalizedTexts=False)
    for ssItem in solarSystemItems:
        if ssItem.groupID != const.groupStargate:
            continue
        slimItem = michelle.GetItem(ssItem.itemID)
        if not slimItem:
            continue
        if slimItem.jumps[0].locationID == destinationID:
            return slimItem


import carbon.common.script.util.autoexport as autoexport
exports = autoexport.AutoExports('uix', locals())
