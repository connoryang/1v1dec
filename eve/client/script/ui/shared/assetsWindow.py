#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\assetsWindow.py
import dbutil
from carbonui.control.menuLabel import MenuLabel
from eve.client.script.ui.shared.assets.assetSafetyControllers import SafetyControllerCharacter
from eve.client.script.ui.shared.assetsSearch import SearchBox
from eveAssets.assetSearchUtil import SearchNamesHelper, AssetKeywordSearch, IsPartOfText, ParseString
import carbonui.const as uiconst
from eve.client.script.ui.shared.inventory.invWindow import Inventory as InventoryWindow
from eve.client.script.ui.util.uix import IsValidNamedItem
from eve.client.script.ui.shared.assets.assetSafety import AssetSafetyCont
from eveAssets.assetSearching import GetSearchResults, GetFakeRowset
import evetypes
import localization
import uiprimitives
import uicontrols
import uix
import uthread
import blue
import util
from eve.client.script.ui.control import entries as listentry
import sys
from collections import defaultdict
from eve.client.script.ui.control.entries import LocationGroup
import log

class AssetsWindow(uicontrols.Window):
    __guid__ = 'form.AssetsWindow'
    __notifyevents__ = ['OnDestinationSet']
    default_width = 550
    default_height = 450
    default_minSize = (395, 256)
    default_windowID = 'assets'
    default_captionLabelPath = 'Tooltips/Neocom/PersonalAssets'
    default_descriptionLabelPath = 'Tooltips/Neocom/PersonalAssets_description'
    default_iconNum = 'res:/ui/Texture/WindowIcons/assets.png'

    def ApplyAttributes(self, attributes):
        uicontrols.Window.ApplyAttributes(self, attributes)
        self.pathfinder = sm.GetService('clientPathfinderService')
        self.key = None
        self.invalidateOpenState_regitems = 1
        self.invalidateOpenState_allitems = 1
        self.invalidateOpenState_conitems = 1
        self.invalidateOpenState_sysitems = 1
        self.safetyCont = None
        self.searchlist = None
        self.pending = None
        self.loading = 0
        self.SetScope('station_inflight')
        self.SetWndIcon('res:/ui/Texture/WindowIcons/assets.png', mainTop=-6)
        self.SetMainIconSize(64)
        self.sr.topParent.state = uiconst.UI_DISABLED
        self.sortOptions = [(localization.GetByLabel('UI/Common/Name'), 0), (localization.GetByLabel('UI/Common/NumberOfJumps'), 1), (localization.GetByLabel('UI/Common/NumberOfItems'), 2)]
        uicontrols.WndCaptionLabel(text=localization.GetByLabel('UI/Inventory/AssetsWindow/PersonalAssets'), subcaption=localization.GetByLabel('UI/Inventory/AssetsWindow/DelayedFiveMinutes'), parent=self.sr.topParent, align=uiconst.RELATIVE)
        self.nameHelper = SearchNamesHelper(sm.GetService('ui'))
        self.assetKeywordSearch = AssetKeywordSearch(self.nameHelper, sm.GetService('ui'), sm.GetService('map'), sm.GetService('godma'), localization, cfg)
        self.searchKeywords = self.assetKeywordSearch.GetSearchKeywords()
        self.searchText = None
        self.scrollPosition = defaultdict(float)
        self.Refresh()

    def OnDestinationSet(self, destinationID = None):
        self.Refresh()

    def ReloadTabs(self, *args):
        self.sr.maintabs.ReloadVisible()

    def Refresh(self, *args):
        self.station_inited = 0
        self.search_inited = 0
        self.filt_inited = 0
        try:
            self.scrollPosition[self.key] = self.sr.scroll.GetScrollProportion()
        except:
            self.scrollPosition[self.key] = 0.0

        self._RecoverSearchText()
        uix.Flush(self.sr.main)
        self.sr.scroll = uicontrols.Scroll(parent=self.sr.main, padding=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding))
        self.sr.scroll.sr.id = 'assets'
        self.sr.scroll.sr.minColumnWidth = {localization.GetByLabel('UI/Common/Name'): 44}
        self.sr.scroll.allowFilterColumns = 1
        self.sr.scroll.OnNewHeaders = self.ReloadTabs
        self.sr.scroll.sortGroups = True
        self.sr.scroll.SetColumnsHiddenByDefault(uix.GetInvItemDefaultHiddenHeaders())
        tabs = [[localization.GetByLabel('UI/Inventory/AssetsWindow/AllItems'),
          self.sr.scroll,
          self,
          'allitems'],
         [localization.GetByLabel('UI/Common/LocationTypes/Region'),
          self.sr.scroll,
          self,
          'regitems'],
         [localization.GetByLabel('UI/Common/LocationTypes/Constellation'),
          self.sr.scroll,
          self,
          'conitems'],
         [localization.GetByLabel('UI/Common/LocationTypes/SolarSystem'),
          self.sr.scroll,
          self,
          'sysitems'],
         [localization.GetByLabel('UI/Inventory/AssetSearch/SearchInStations'),
          self.sr.scroll,
          self,
          'search'],
         [localization.GetByLabel('UI/Inventory/AssetSafety/Safety'),
          self.sr.scroll,
          self,
          'safety']]
        if eve.session.stationid:
            tabs.insert(4, [localization.GetByLabel('UI/Common/LocationTypes/Station'),
             self.sr.scroll,
             self,
             'station'])
        self.sr.maintabs = uicontrols.TabGroup(name='tabparent', parent=self.sr.main, idx=0, tabs=tabs, groupID='assetspanel', silently=True)

    def _RecoverSearchText(self):
        assetSearchBox = self.sr.searchtype
        if assetSearchBox:
            self.searchText = assetSearchBox.GetValue()

    def Load(self, key, reloadStationID = None):
        if self.loading:
            self.pending = (key, reloadStationID)
            return
        uthread.new(self._Load, key, reloadStationID)

    def _Load(self, key, reloadStationID = None):
        self.loading = 1
        self.pending = None
        if key != self.key:
            self.scrollPosition[self.key] = self.sr.scroll.GetScrollProportion()
        self.key = key
        if self.safetyCont:
            self.safetyCont.display = False
        if key == 'safety':

            def Hide(cont):
                if cont:
                    cont.display = False

            Hide(self.sr.scroll)
            Hide(self.sr.search_cont)
            Hide(self.sr.filt_cont)
            Hide(self.sr.station_tabs)
            if self.safetyCont is None or self.safetyCont.destroyed:
                self.safetyCont = AssetSafetyCont(parent=self.sr.main, padding=4, controller=SafetyControllerCharacter())
            self.safetyCont.display = True
            self.safetyCont.Load()
        if key[:7] == 'station':
            if not self.station_inited:
                idx = self.sr.main.children.index(self.sr.maintabs)
                self.sr.station_tabs = uicontrols.TabGroup(name='tabparent2', parent=self.sr.main, idx=idx + 1)
                tabs = [[localization.GetByLabel('UI/Common/ItemTypes/Ships'),
                  self.sr.scroll,
                  self,
                  '%sships' % key],
                 [localization.GetByLabel('UI/Common/ItemTypes/Modules'),
                  self.sr.scroll,
                  self,
                  '%smodules' % key],
                 [localization.GetByLabel('UI/Common/ItemTypes/Charges'),
                  self.sr.scroll,
                  self,
                  '%scharges' % key],
                 [localization.GetByLabel('UI/Common/ItemTypes/Minerals'),
                  self.sr.scroll,
                  self,
                  '%sminerals' % key],
                 [localization.GetByLabel('UI/Common/Other'),
                  self.sr.scroll,
                  self,
                  '%sother' % key]]
                self.station_inited = 1
                self.sr.station_tabs.Startup(tabs, 'assetsatstation', silently=True)
            if self.sr.Get('filt_cont', None):
                self.sr.filt_cont.state = uiconst.UI_HIDDEN
            self.sr.station_tabs.state = uiconst.UI_NORMAL
            if self.sr.Get('search_cont', None):
                self.sr.search_cont.state = uiconst.UI_HIDDEN
            if key != 'station':
                self.ShowStationItems(key[7:])
            else:
                self.sr.station_tabs.AutoSelect(1)
        elif key in ('allitems', 'regitems', 'conitems', 'sysitems'):
            if not getattr(self, 'filt_inited', False):
                self.sr.filt_cont = uiprimitives.Container(align=uiconst.TOTOP, height=67, parent=self.sr.main, top=2, idx=1)
                self.sr.sortcombo = uicontrols.Combo(label=localization.GetByLabel('UI/Common/SortBy'), parent=self.sr.filt_cont, options=self.sortOptions, name='sortcombo', select=None, callback=self.Filter, width=115, pos=(5, 16, 0, 0))
                l = self.sr.sortcombo.width + self.sr.sortcombo.left + const.defaultPadding
                self.sr.filtcombo = uicontrols.Combo(label=localization.GetByLabel('UI/Common/View'), parent=self.sr.filt_cont, options=[], name='filtcombo', select=None, callback=self.Filter, width=115, pos=(l,
                 16,
                 0,
                 0))
                self.sr.filt_cont.height = self.sr.filtcombo.top + self.sr.filtcombo.height
                self.filt_inited = 1
            self.sr.filt_cont.state = uiconst.UI_PICKCHILDREN
            if key in ('regitems', 'conitems', 'sysitems'):
                self.sr.filtcombo.state = uiconst.UI_NORMAL
            else:
                self.sr.filtcombo.state = uiconst.UI_HIDDEN
            if self.sr.Get('station_tabs', None):
                self.sr.station_tabs.state = uiconst.UI_HIDDEN
            if self.sr.Get('search_cont', None):
                self.sr.search_cont.state = uiconst.UI_HIDDEN
            self.ShowAll(key, None, None)
        elif key == 'search':
            if self.sr.Get('station_tabs', None):
                self.sr.station_tabs.state = uiconst.UI_HIDDEN
            if not self.search_inited:
                self.sr.search_cont = uiprimitives.Container(align=uiconst.TOTOP, height=37, parent=self.sr.main, idx=1)
                uiprimitives.Container(name='comboCont', align=uiconst.TOLEFT, parent=self.sr.search_cont, width=100 + const.defaultPadding)
                top = const.defaultPadding + 14
                self.sr.sortcombosearch = uicontrols.Combo(label=localization.GetByLabel('UI/Common/SortBy'), parent=self.sr.search_cont, options=self.sortOptions, name='sortcombosearch', select=None, callback=self.Search, width=100, pos=(const.defaultPadding,
                 top,
                 0,
                 0))
                buttonCont = uiprimitives.Container(name='bottonCont', align=uiconst.TORIGHT, parent=self.sr.search_cont)
                sprite = uiprimitives.Sprite(name='questionMarkSprite', parent=buttonCont, align=uiconst.TOPRIGHT, pos=(const.defaultPadding,
                 top,
                 20,
                 20), state=uiconst.UI_NORMAL, texturePath='res:/UI/Texture/Icons/105_32_32.png', opacity=0.75)
                sprite.LoadTooltipPanel = self.LoadInfoTooltip
                button = uicontrols.Button(parent=buttonCont, label=localization.GetByLabel('UI/Common/Buttons/Search'), left=sprite.left + sprite.width + const.defaultPadding, top=top, func=self.Search, align=uiconst.TOPRIGHT)
                buttonCont.width = button.width + const.defaultPadding * 3 + sprite.width
                self.sr.searchtype = SearchBox(name='assetssearchtype', parent=self.sr.search_cont, left=const.defaultPadding, padBottom=1, width=0, top=top, label=localization.GetByLabel('UI/Common/SearchText'), maxLength=100, OnReturn=self.Search, align=uiconst.TOALL, keywords=self.searchKeywords, isTypeField=True)
                self._RestoreSearchText()
                self.search_inited = 1
            if self.sr.Get('filt_cont', None):
                self.sr.filt_cont.state = uiconst.UI_HIDDEN
            self.sr.search_cont.state = uiconst.UI_PICKCHILDREN
            sortKeySearch = settings.char.ui.Get('assetsSearchSortKey', None)
            self.ShowSearch(sortKeySearch)
            self.Search()
        self.loading = 0
        if self.pending:
            self.Load(*self.pending)

    def _RestoreSearchText(self):
        if self.searchText:
            searchBox = self.sr.searchtype
            if searchBox:
                searchBox.SetValue(self.searchText)

    def Filter(self, *args):
        key, keyID = self.sr.filtcombo.GetValue()
        sortKey = self.sr.sortcombo.GetValue()
        self.ShowAll(key, keyID, sortKey)

    def GetConditions(self, advancedMatches):
        conditions = []
        for word, value in advancedMatches:
            try:
                for kw in self.searchKeywords:
                    if IsPartOfText(kw.keyword, word):
                        kw.matchFunction(conditions, value)
                        break

            except:
                import log
                log.LogException()
                sm.GetService('assets').LogInfo('Failed parsing keyword', word, 'value', value, 'and happily ignoring it')

        return conditions

    def Search(self, *args):
        uthread.new(self.Search_thread)

    def Search_thread(self, *args):
        self.ShowLoad()
        if self.sr.maintabs.GetSelectedArgs() == 'search':
            self.sr.scroll.Load(contentList=[], noContentHint=localization.GetByLabel('UI/Common/GettingData'))
        blue.pyos.synchro.Yield()
        log.LogNotice('Asset Search - fetch items')
        invContainer = sm.GetService('invCache').GetInventory(const.containerGlobal)
        allitems = invContainer.ListIncludingContainers()
        log.LogNotice('Asset Search - items fetched =', len(allitems))
        itemRowset = GetFakeRowset(allitems)
        log.LogNotice('Asset Search - fake rows created')
        uiSvc = sm.StartService('ui')
        blue.pyos.synchro.Yield()
        if self.sr.maintabs.GetSelectedArgs() == 'search':
            self.sr.scroll.Load(contentList=[], noContentHint=localization.GetByLabel('UI/Common/Searching'))
        blue.pyos.synchro.Yield()
        searchtype = unicode(self.sr.searchtype.GetValue() or '').lower()
        searchtype, advancedMatches = ParseString(searchtype)
        conditions = self.GetConditions(advancedMatches)
        self.assetKeywordSearch.ResetPerRunDicts()
        allContainersByItemIDs, itemsByContainerID, stations = GetSearchResults(conditions, itemRowset, searchtype)
        containersInfoByStations = defaultdict(lambda : defaultdict(tuple))
        for containerID, itemsInContainer in itemsByContainerID.iteritems():
            containerItem = allContainersByItemIDs.get(containerID)
            if containerItem and containerItem.typeID == const.typePlasticWrap:
                continue
            if containerItem:
                containersInfoByStations[containerItem.locationID][containerID] = (containerItem, itemsInContainer)

        for stationID in containersInfoByStations.iterkeys():
            stations[stationID].extend([])

        sortlocations = []
        for stationID, stationItems in stations.iteritems():
            stationData = uiSvc.GetStation(stationID)
            if stationData is None:
                continue
            stationsContainersInfo = containersInfoByStations.get(stationID, {})
            sortlocations.append((stationData.solarSystemID,
             stationID,
             stationItems,
             stationsContainersInfo))

        sortlocations.sort()
        sortlocations = sortlocations
        self.searchlist = sortlocations
        sortKey = self.sr.sortcombosearch.GetValue()
        self.ShowSearch(sortKey)

    def ShowAll(self, key, keyID, sortKey, *args):
        if keyID is None:
            keyID = settings.char.ui.Get('assetsKeyID_%s' % key, None)
        oldSortKey = settings.char.ui.Get('assetsSortKey', None)
        if sortKey is not None:
            if oldSortKey != sortKey:
                for k in self.scrollPosition.keys():
                    self.scrollPosition[k] = 0.0

        else:
            sortKey = oldSortKey
        settings.char.ui.Set('assetsKeyID_%s' % key, keyID)
        settings.char.ui.Set('assetsSortKey', sortKey)
        self.ShowLoad()
        self.SetHint()
        closed = [0, 1][getattr(self, 'invalidateOpenState_%s' % key, 0)]
        sortlocations = sm.StartService('assets').GetAll(key, keyID=keyID, sortKey=sortKey)
        options = [(localization.GetByLabel('UI/Common/Current'), (key, 0))]
        opts = {}
        for r in sm.StartService('assets').locationCache.iterkeys():
            if key == 'regitems' and util.IsRegion(r) or key == 'conitems' and util.IsConstellation(r) or key == 'sysitems' and util.IsSolarSystem(r):
                opts[cfg.evelocations.Get(r).name] = r

        keys = opts.keys()
        keys.sort()
        for k in keys:
            options.append((k, (key, opts[k])))

        try:
            self.sr.filtcombo.LoadOptions(options, None)
            if keyID:
                self.sr.filtcombo.SelectItemByLabel(cfg.evelocations.Get(keyID).name)
            if sortKey:
                self.sr.sortcombo.SelectItemByIndex(sortKey)
        except (Exception,):
            sys.exc_clear()

        destPathList = sm.GetService('starmap').GetDestinationPath()
        scrolllist = []
        for solarsystemID, station in sortlocations:
            data = self.GetLocationData(solarsystemID, station, key, forceClosed=closed, scrollID=self.sr.scroll.sr.id, sortKey=sortKey, path=destPathList)
            scrolllist.append(listentry.Get(entryType=None, data=data, decoClass=LocationGroup))

        if self.destroyed:
            return
        setattr(self, 'invalidateOpenState_%s' % key, 0)
        locText = {'allitems': localization.GetByLabel('UI/Inventory/AssetsWindow/NoAssetsAtStation'),
         'regitems': localization.GetByLabel('UI/Inventory/AssetsWindow/NoAssetsInRegion'),
         'conitems': localization.GetByLabel('UI/Inventory/AssetsWindow/NoAssetsInConstellation'),
         'sysitems': localization.GetByLabel('UI/Inventory/AssetsWindow/NoAssetsInSolarSystem')}
        scrollPosition = self.scrollPosition[key]
        self.sr.scroll.Load(contentList=scrolllist, headers=uix.GetInvItemDefaultHeaders(), noContentHint=locText[key], scrollTo=scrollPosition)
        self.HideLoad()

    def ShowStationItems(self, key):
        self.ShowLoad()
        hangarInv = sm.GetService('invCache').GetInventory(const.containerHangar)
        items = hangarInv.List(const.flagHangar)
        if not len(items):
            self.SetHint(localization.GetByLabel('UI/Inventory/AssetsWindow/NoAssets'))
            return
        assetsList = []
        self.sr.scroll.Load(fixedEntryHeight=42, contentList=[], headers=uix.GetInvItemDefaultHeaders())
        itemname = ' ' + key
        itemSet = set()
        for each in items:
            if each.flagID not in (const.flagHangar, const.flagWallet):
                continue
            if key == 'ships':
                if each.categoryID != const.categoryShip:
                    continue
            elif key == 'modules':
                if not evetypes.IsCategoryHardwareByCategory(evetypes.GetCategoryID(each.typeID)):
                    continue
            elif key == 'minerals':
                if each.groupID != const.groupMineral:
                    continue
            elif key == 'charges':
                if each.categoryID != const.categoryCharge:
                    continue
            else:
                itemname = None
                if each.categoryID == const.categoryShip or evetypes.IsCategoryHardwareByCategory(evetypes.GetCategoryID(each.typeID)) or each.groupID == const.groupMineral or each.categoryID == const.categoryCharge:
                    continue
            itemSet.add(each)

        self.PrimeLocationNames(itemSet)
        for eachItem in itemSet:
            assetsList.append(listentry.Get('InvAssetItem', data=uix.GetItemData(eachItem, 'details', scrollID=self.sr.scroll.sr.id)))

        locText = {'ships': localization.GetByLabel('UI/Inventory/AssetsWindow/NoShipsAtStation'),
         'modules': localization.GetByLabel('UI/Inventory/AssetsWindow/NoModulesAtStation'),
         'minerals': localization.GetByLabel('UI/Inventory/AssetsWindow/NoMineralsAtStation'),
         'charges': localization.GetByLabel('UI/Inventory/AssetsWindow/NoChargesAtStation')}
        if not assetsList:
            if not itemname:
                self.SetHint(localization.GetByLabel('UI/Inventory/AssetsWindow/NoAssetsInCategoryAtStation'))
            else:
                self.SetHint(locText[key])
        else:
            self.SetHint()
        self.sr.scroll.Load(contentList=assetsList, sortby='label', headers=uix.GetInvItemDefaultHeaders())
        self.HideLoad()

    def GetLocationData(self, solarsystemID, station, key, forceClosed = 0, scrollID = None, sortKey = None, fakeItems = None, path = ()):
        location = cfg.evelocations.Get(station.stationID)
        if forceClosed:
            uicore.registry.SetListGroupOpenState(('assetslocations_%s' % key, location.locationID), 0)
        autopilotNumJumps = self.pathfinder.GetAutopilotJumpCount(session.solarsystemid2, solarsystemID)
        itemCount = fakeItems or station.itemCount
        if key is not 'sysitems':
            label = localization.GetByLabel('UI/Inventory/AssetsWindow/LocationDataLabel', location=location.locationID, itemCount=itemCount, jumps=autopilotNumJumps)
        else:
            label = localization.GetByLabel('UI/Inventory/AssetsWindow/LocationDataLabelNoJump', location=location.locationID, itemCount=itemCount)
        if sortKey == 1:
            sortVal = (autopilotNumJumps, location.name, itemCount)
        elif sortKey == 2:
            sortVal = (-itemCount, location.name, autopilotNumJumps)
        else:
            sortVal = (location.name, itemCount, autopilotNumJumps)
        data = {'GetSubContent': self.GetSubContent,
         'DragEnterCallback': self.OnGroupDragEnter,
         'DeleteCallback': self.OnGroupDeleted,
         'MenuFunction': self.GetMenuLocationMenu,
         'GetDragDataFunc': self.GetLocationDragData,
         'label': label,
         'jumps': autopilotNumJumps,
         'itemCount': station.itemCount,
         'groupItems': [],
         'id': ('assetslocations_%s' % key, location.locationID),
         'tabs': [],
         'state': 'locked',
         'location': location,
         'showicon': 'hide',
         'showlen': 0,
         'key': key,
         'scrollID': scrollID,
         'inMyPath': solarsystemID in path,
         'itemID': station.stationID}
        headers = uix.GetInvItemDefaultHeaders()
        for each in headers:
            data['sort_%s' % each] = sortVal

        return data

    def GetLocationDragData(self, node):
        solarSystemID, stationTypeID = self.GetStationSolarSystemIDAndTypeID(node)
        stationInfo = sm.StartService('ui').GetStation(node.itemID)
        if stationInfo:
            node['typeID'] = stationInfo.stationTypeID
            node['genericDisplayLabel'] = cfg.stations.Get(node.itemID).stationName
        elif stationTypeID:
            node['typeID'] = stationTypeID
            node['genericDisplayLabel'] = cfg.evelocations.Get(node.itemID).name
        return [node]

    def GetContainerSubContent(self, nodedata, *args):
        scrollList = []
        self.PrimeLocationNames(nodedata.groupItems)
        for each in nodedata.groupItems:
            data = uix.GetItemData(each, 'details', scrollID=nodedata.scrollID)
            data.sublevel = nodedata.sublevel
            scrollList.append(listentry.Get('InvAssetItem', data=data))

        return scrollList

    def GetContainerMenu(self, node):
        return sm.GetService('menu').InvItemMenu(node.item)

    def OnDblClickContainer(self, groupEntry):
        nodedata = groupEntry.sr.node
        if sm.StartService('menu').CheckSameLocation(nodedata.item):
            invID = ('StationContainer', nodedata.itemID)
            InventoryWindow.OpenOrShow(invID=invID, openFromWnd=self)

    def GetContainerGroupEntries(self, containersInfo, scrollID):
        scrollList = []
        cfg.evelocations.Prime(containersInfo.keys())
        for containerID, infoOnContainer in containersInfo.iteritems():
            containerItem, itemsInContainer = infoOnContainer
            containerName = uix.GetItemName(containerItem)
            containerData = {'GetSubContent': self.GetContainerSubContent,
             'label': containerName,
             'MenuFunction': self.GetContainerMenu,
             'groupItems': itemsInContainer,
             'id': ('assetslocations_%s' % containerID, containerID),
             'state': 'locked',
             'showicon': 'hide',
             'showlen': 1,
             'itemID': containerID,
             'item': containerItem,
             'sublevel': 1,
             'scrollID': scrollID,
             'OnDblClick': self.OnDblClickContainer}
            scrollList.append(listentry.Get('Group', data=containerData))

        return scrollList

    def GetSubContent(self, data, *args):
        if data.key == 'search':
            scrolllist = []
            items = []
            containersInfo = {}
            for solarsystemID, stationID, stationItems, stationsContainersInfo in self.searchlist:
                if stationID == data.location.locationID:
                    items = stationItems
                    containersInfo = stationsContainersInfo
                    break

            self.PrimeVoucherNames(items)
            self.PrimeLocationNames(items)
            groupEntries = self.GetContainerGroupEntries(containersInfo, data.scrollID)
            scrolllist.extend(groupEntries)
            for each in items:
                if each.flagID not in (const.flagHangar, const.flagWallet, const.flagAssetSafety):
                    continue
                scrolllist.append(listentry.Get('InvAssetItem', data=uix.GetItemData(each, 'details', scrollID=data.scrollID)))

            return scrolllist
        if session.stationid and data.location.locationID in (session.stationid, session.structureid):
            hangarInv = sm.GetService('invCache').GetInventory(const.containerHangar)
            items = hangarInv.List()
            scrolllist = []
            self.PrimeVoucherNames(items)
            self.PrimeLocationNames(items)
            for each in items:
                if each.flagID not in (const.flagHangar, const.flagWallet, const.flagAssetSafety):
                    continue
                scrolllist.append(listentry.Get('InvAssetItem', data=uix.GetItemData(each, 'details', scrollID=data.scrollID)))

            return scrolllist
        items = sm.GetService('invCache').GetInventory(const.containerGlobal).ListStationItems(data.location.locationID)
        badLocations = [const.locationTemp, const.locationSystem, eve.session.charid]
        scrolllist = []
        self.PrimeVoucherNames(items)
        self.PrimeLocationNames(items)
        for each in items:
            if util.IsJunkLocation(each.locationID) or each.locationID in badLocations:
                continue
            if each.stacksize == 0:
                continue
            data = uix.GetItemData(each, 'details', scrollID=data.scrollID)
            if util.IsStation(each.locationID):
                station = sm.GetService('map').GetStation(each.locationID)
                if station:
                    data.factionID = sm.StartService('faction').GetFactionOfSolarSystem(station.solarSystemID)
            scrolllist.append(listentry.Get('InvAssetItem', data=data))

        return scrolllist

    def PrimeVoucherNames(self, items):
        vouchers = [ item.itemID for item in items if item.typeID == const.typeBookmark ]
        if vouchers:
            sm.GetService('voucherCache').PrimeVoucherNames(vouchers)

    def PrimeLocationNames(self, items):
        itemLocationToPrime = set()
        for each in items:
            if IsValidNamedItem(each):
                itemLocationToPrime.add(each.itemID)

        cfg.evelocations.Prime(itemLocationToPrime)

    def UpdateLite(self, stationID, key, fromID):
        if not self or self.destroyed:
            return
        self.ShowLoad()
        destPathList = sm.GetService('starmap').GetDestinationPath()
        assetStations = sm.StartService('assets').GetStations().Index('stationID')
        searchKey = 'assetslocations_%s' % key
        affectedNodes = [ node for node in self.sr.scroll.GetNodes() if node.Get('id', None) in ((searchKey, stationID), (searchKey, fromID)) ]
        for node in affectedNodes:
            locationID = node.Get('id')[1]
            station = assetStations[locationID]
            node.data = self.GetLocationData(station.solarSystemID, station, key, scrollID=self.sr.scroll.sr.id, path=destPathList)
            if node.panel:
                node.panel.Load(node)
            self.sr.scroll.PrepareSubContent(node)
            self.sr.scroll.ScrollToProportion(self.sr.scroll.GetScrollProportion())

        self.Refresh()
        self.HideLoad()

    def ShowSearch(self, sortKey = None, *args):
        if sortKey is None:
            sortKey = settings.char.ui.Get('assetsSearchSortKey', None)
        settings.char.ui.Set('assetsSearchSortKey', sortKey)
        if sortKey:
            self.sr.sortcombosearch.SelectItemByIndex(sortKey)
        self.SetHint()
        scrolllist = []
        searchlist = getattr(self, 'searchlist', []) or []
        sortedList = []
        for solarsystemID, stationID, items, stationsContainersInfo in searchlist:
            numContainerItems = sum([ len(y) for x, y in stationsContainersInfo.values() ])
            station = util.KeyVal()
            station.stationID = stationID
            station.solarsystemID = solarsystemID
            station.stationName = cfg.evelocations.Get(stationID).name
            station.itemCount = len(items) + numContainerItems
            sortedList.append(station)

        destPathList = sm.GetService('starmap').GetDestinationPath()
        for station in sortedList:
            data = self.GetLocationData(station.solarsystemID, station, 'search', scrollID=self.sr.scroll.sr.id, sortKey=sortKey, path=destPathList)
            scrolllist.append(listentry.Get(entryType=None, data=data, decoClass=LocationGroup))

        if self.sr.maintabs.GetSelectedArgs() == 'search':
            scrollPosition = self.scrollPosition.get('search', 0)
            self.sr.scroll.Load(contentList=scrolllist, headers=uix.GetInvItemDefaultHeaders(), noContentHint=localization.GetByLabel('UI/Common/NothingFound'), scrollTo=scrollPosition)
        self.HideLoad()

    def GetMenuLocationMenu(self, node):
        locationID = node.location.locationID
        solarSystemID, stationTypeID = self.GetStationSolarSystemIDAndTypeID(node)
        menu = sm.StartService('menu').CelestialMenu(node.location.locationID, typeID=stationTypeID, parentID=solarSystemID)
        if not util.IsStation(locationID):
            if session.structureid != locationID:
                if util.IsWormholeSystem(solarSystemID):
                    label = MenuLabel('UI/Inventory/AssetSafety/MoveItemsToSpace')
                else:
                    label = MenuLabel('UI/Inventory/AssetSafety/MoveItemsToSafety')
                menu.append((label, self.MoveItemsInStructureToAssetSafety, (solarSystemID, locationID)))
        return menu

    def GetStationSolarSystemIDAndTypeID(self, node):
        locationID = node.location.locationID
        solarSystemID = stationTypeID = None
        if util.IsStation(locationID):
            stationInfo = sm.StartService('ui').GetStation(locationID)
            stationTypeID = stationInfo.stationTypeID
            solarSystemID = stationInfo.solarSystemID
        else:
            stations = sm.GetService('invCache').GetInventory(const.containerGlobal).ListStations()
            for station in stations:
                if station.stationID == locationID:
                    stationTypeID = station.typeID
                    solarSystemID = station.solarSystemID
                    break

        return (solarSystemID, stationTypeID)

    def MoveItemsInStructureToAssetSafety(self, solarSystemID, structureID):
        sm.GetService('assetSafety').MoveItemsInStructureToAssetSafetyForCharacter(solarSystemID, structureID)

    def SetHint(self, hintstr = None):
        if self.sr.scroll:
            self.sr.scroll.ShowHint(hintstr)

    def OnGroupDeleted(self, ids):
        pass

    def OnGroupDragEnter(self, group, drag):
        pass

    def LoadInfoTooltip(self, tooltipPanel, *args):
        tooltipPanel.LoadGeneric2ColumnTemplate()
        tooltipPanel.cellSpacing = 1
        tooltipPanel.AddLabelLarge(text=localization.GetByLabel('UI/Inventory/AssetsWindow/AdvancedSearch'), colSpan=2)
        tooltipPanel.AddLabelMedium(text='<b>%s' % localization.GetByLabel('UI/Inventory/AssetsWindow/AdvancedSearchKeywords'))
        tooltipPanel.AddLabelMedium(wrapWidth=200, text='<b>%s' % localization.GetByLabel('UI/Inventory/AssetsWindow/AdvancedSearchHints'), padLeft=20)
        for keywordOption in self.searchKeywords:
            tooltipPanel.AddLabelSmall(text='<b>%s:</b>' % keywordOption.keyword, opacity=0.85)
            tooltipPanel.AddLabelSmall(wrapWidth=200, text=keywordOption.optionDescription, padLeft=20, opacity=0.75)

        tooltipPanel.AddSpacer(width=0, height=10, colSpan=3)
        tooltipPanel.AddLabelMedium(text='<b>%s:' % localization.GetByLabel('UI/Inventory/AssetsWindow/AdvancedSearchExamples'), colSpan=3)
        text = '%s:%s' % (localization.GetByLabel('UI/Inventory/AssetSearch/KeywordType'), evetypes.GetName(1230)[:5])
        tooltipPanel.AddLabelSmall(text=text, opacity=0.75, colSpan=3, padLeft=10)
        text = '%s:%s %s:2 %s:9 %s:0.9' % (localization.GetByLabel('UI/Inventory/AssetSearch/KeywordCategory'),
         evetypes.GetCategoryNameByCategory(const.categoryShip),
         localization.GetByLabel('UI/Inventory/AssetSearch/KeywordTechLevel'),
         localization.GetByLabel('UI/Inventory/AssetSearch/KeywordMetalevel'),
         localization.GetByLabel('UI/Inventory/AssetSearch/KeywordMinSecurityLevel'))
        tooltipPanel.AddLabelSmall(text=text, opacity=0.75, colSpan=2, padLeft=10)
