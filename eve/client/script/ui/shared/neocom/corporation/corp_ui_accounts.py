#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\neocom\corporation\corp_ui_accounts.py
import blue
import evetypes
import uiprimitives
import uicontrols
import uthread
import util
import uix
import listentry
import log
import carbonui.const as uiconst
import sys
import localization
from carbonui.control.menuLabel import MenuLabel
from contractutils import DoParseItemType
from carbon.common.script.sys.row import Row
from eve.client.script.ui.shared.assets.assetSafety import AssetSafetyCont
from eve.client.script.ui.shared.assets.assetSafetyControllers import SafetyControllerCorp
FLAGNAME_OFFICES = 'offices'
FLAGNAME_JUNK = 'junk'
FLAGNAME_PROPERTY = 'property'
FLAGNAME_DELIVERIES = 'deliveries'
FLAGNAME_IMPOUNDED = 'impounded'
KEYNAME_LOCKDOWN = 'lockdown'
KEYNAME_SAFETY = 'safety'
KEYNAME_SEARCH = 'search'
FLAG_OFFICES = 71
FLAG_JUNK = 72
FLAG_PROPERTY = 74
FLAG_DELIVERIES = 75
FLAG_TO_FLAGNAME = {FLAG_OFFICES: FLAGNAME_OFFICES,
 FLAG_JUNK: FLAGNAME_JUNK,
 FLAG_PROPERTY: FLAGNAME_PROPERTY,
 FLAG_DELIVERIES: FLAGNAME_DELIVERIES}
FLAGNAME_TO_FLAG = {FLAGNAME_OFFICES: FLAG_OFFICES,
 FLAGNAME_IMPOUNDED: FLAG_JUNK,
 FLAGNAME_JUNK: FLAG_JUNK,
 FLAGNAME_PROPERTY: FLAG_PROPERTY,
 FLAGNAME_DELIVERIES: FLAG_DELIVERIES}

class CorpAccounts(uiprimitives.Container):
    __guid__ = 'form.CorpAccounts'
    __nonpersistvars__ = ['assets']
    __notifyevents__ = ['OnCorpAssetChange', 'OnReloadCorpAssets']

    def ApplyAttributes(self, attributes):
        uiprimitives.Container.ApplyAttributes(self, attributes)
        self.sr.journalFromDate = blue.os.GetWallclockTime() - 24 * const.HOUR * 7 + const.HOUR
        self.sr.journalToDate = blue.os.GetWallclockTime() + const.HOUR
        self.sr.viewMode = 'details'
        self.key = None
        self.safetyCont = None
        self.sr.search_inited = 0
        sm.RegisterNotify(self)

    def OnReloadCorpAssets(self):
        if self.sr.tabs:
            self.sr.tabs.ReloadVisible()

    def OnCorpAssetChange(self, items, stationID):
        if items[0].locationID != stationID:
            id = ('corpofficeassets', (stationID, items[0].flagID))
            which = FLAGNAME_DELIVERIES
        else:
            id = ('corpassets', stationID)
            which = FLAGNAME_OFFICES
        if not self.sr.Get('inited', 0):
            return
        for node in self.sr.scroll.GetNodes():
            if node.Get('id', 0) == id:
                rows = sm.RemoteSvc('corpmgr').GetAssetInventory(eve.session.corpid, which)
                for row in rows:
                    if stationID == row.locationID:
                        node.data = self.GetLocationData(row, FLAG_OFFICES, scrollID=self.sr.scroll.sr.id)

                if node.panel:
                    node.panel.Load(node)
                self.sr.scroll.PrepareSubContent(node)
                pos = self.sr.scroll.GetScrollProportion()
                self.sr.scroll.ScrollToProportion(pos)

    def Load(self, key):
        sm.GetService('corpui').LoadTop('res:/ui/Texture/WindowIcons/assetscorp.png', localization.GetByLabel('UI/Corporations/Assets/CorpAssets'), localization.GetByLabel('UI/Corporations/Common/UpdateDelay'))
        if not self.sr.Get('inited', 0):
            self.sr.inited = 1
            self.sr.scroll = uicontrols.Scroll(parent=self, padding=(const.defaultPadding,
             const.defaultPadding,
             const.defaultPadding,
             const.defaultPadding))
            self.sr.scroll.adjustableColumns = 1
            self.sr.scroll.sr.id = 'CorporationAssets'
            self.sr.scroll.sr.minColumnWidth = {localization.GetByLabel('UI/Common/Name'): 44}
            self.sr.scroll.SetColumnsHiddenByDefault(uix.GetInvItemDefaultHiddenHeaders())
            self.sr.tabs = uicontrols.TabGroup(name='tabparent', parent=self, idx=0)
            tabs = [[localization.GetByLabel('UI/Corporations/Common/Offices'),
              self.sr.scroll,
              self,
              FLAGNAME_OFFICES],
             [localization.GetByLabel('UI/Corporations/Assets/Impounded'),
              self.sr.scroll,
              self,
              FLAGNAME_IMPOUNDED],
             [localization.GetByLabel('UI/Corporations/Assets/InSpace'),
              self.sr.scroll,
              self,
              FLAGNAME_PROPERTY],
             [localization.GetByLabel('UI/Corporations/Assets/Deliveries'),
              self.sr.scroll,
              self,
              FLAGNAME_DELIVERIES],
             [localization.GetByLabel('UI/Corporations/Assets/Lockdown'),
              self.sr.scroll,
              self,
              KEYNAME_LOCKDOWN],
             [localization.GetByLabel('UI/Common/Search'),
              self.sr.scroll,
              self,
              KEYNAME_SEARCH]]
            if self.IsDirector():
                self.safetyParent = uiprimitives.Container(parent=self)
                safetyTabInfo = [localization.GetByLabel('UI/Inventory/AssetSafety/Safety'),
                 self.safetyParent,
                 self,
                 KEYNAME_SAFETY]
                tabs.insert(-1, safetyTabInfo)
            self.sr.tabs.Startup(tabs, 'corpassetstab', autoselecttab=0)
        self.sr.scroll.Load(contentList=[], headers=uix.GetInvItemDefaultHeaders())
        self.sr.scroll.OnNewHeaders = self.OnNewHeadersSet
        self.sr.scroll.allowFilterColumns = 0
        if self.sr.Get('search_cont', None):
            self.sr.search_cont.state = uiconst.UI_HIDDEN
        if key == 'accounts':
            key = FLAGNAME_OFFICES
            self.sr.tabs.AutoSelect()
            return
        if key not in (KEYNAME_SEARCH, KEYNAME_SAFETY):
            if not getattr(self, 'filt_inited', False):
                self.InitAssetFilters()
            self.sr.filt_cont.state = uiconst.UI_PICKCHILDREN
        elif self.sr.Get('filt_cont', None):
            self.sr.filt_cont.state = uiconst.UI_HIDDEN
        if key in (KEYNAME_LOCKDOWN,):
            uthread.new(self.ShowLockdown, None, None)
        elif key == KEYNAME_SEARCH:
            self.sr.scroll.OnNewHeaders = self.Search
            uthread.new(self.ShowSearch)
        elif key == KEYNAME_SAFETY:
            if self.safetyCont is None or self.safetyCont.destroyed:
                self.safetyCont = AssetSafetyCont(parent=self.safetyParent, padding=4, controller=SafetyControllerCorp())
            self.safetyCont.display = True
            self.safetyCont.Load()
        else:
            uthread.new(self.ShowAssets, key, None, None)

    def InitAssetFilters(self):
        sortKey = settings.char.ui.Get('corpAssetsSortKey', None)
        self.sr.filt_cont = uiprimitives.Container(align=uiconst.TOTOP, height=37, parent=self, top=2, idx=1)
        self.sr.sortcombo = uicontrols.Combo(label=localization.GetByLabel('UI/Common/SortBy'), parent=self.sr.filt_cont, options=[], name='sortcombo', select=sortKey, callback=self.Filter, width=100, pos=(5, 16, 0, 0))
        l = self.sr.sortcombo.width + self.sr.sortcombo.left + const.defaultPadding
        self.sr.filtcombo = uicontrols.Combo(label=localization.GetByLabel('UI/Common/View'), parent=self.sr.filt_cont, options=[], name='filtcombo', select=None, callback=self.Filter, width=100, pos=(l,
         16,
         0,
         0))
        self.sr.filt_cont.height = self.sr.filtcombo.top + self.sr.filtcombo.height
        self.filt_inited = 1

    def UpdateSortOptions(self, currentlySelected, sortKey):
        sortOptions = [(localization.GetByLabel('UI/Common/Name'), 0), (localization.GetByLabel('UI/Common/NumberOfJumps'), 1)]
        if currentlySelected == FLAGNAME_DELIVERIES:
            sortOptions.append((localization.GetByLabel('UI/Common/NumberOfItems'), 2))
        self.sr.sortcombo.LoadOptions(sortOptions, None)
        if sortKey is None:
            sortKey = settings.char.ui.Get('corpAssetsSortKey', None)
        if sortKey is None or sortKey >= len(sortOptions):
            sortKey = 0
        self.sr.sortcombo.SelectItemByIndex(sortKey)
        settings.char.ui.Set('corpAssetsSortKey', sortKey)
        return sortKey

    def Filter(self, *args):
        flagName, regionKey = self.sr.filtcombo.GetValue()
        sortKey = self.sr.sortcombo.GetValue()
        if flagName == KEYNAME_LOCKDOWN:
            self.ShowLockdown(sortKey, regionKey)
        else:
            self.ShowAssets(flagName, sortKey, regionKey)

    def OnNewHeadersSet(self, *args):
        self.sr.tabs.ReloadVisible()

    def ShowAssets(self, flagName, sortKey, regionKey):
        if self is not None and not self.destroyed:
            sm.GetService('corpui').ShowLoad()
        else:
            return
        sortKey = self.UpdateSortOptions(flagName, sortKey)
        if regionKey is None:
            regionKey = settings.char.ui.Get('corpAssetsKeyID_%s' % flagName, 0)
        settings.char.ui.Set('corpAssetsKeyID_%s' % flagName, regionKey)
        flag = FLAGNAME_TO_FLAG[flagName]
        which = flagName
        if flagName == FLAGNAME_IMPOUNDED:
            which = FLAGNAME_JUNK
        rows = sm.RemoteSvc('corpmgr').GetAssetInventory(eve.session.corpid, which)
        options = self.GetFilterOptions(rows, flagName)
        try:
            self.sr.filtcombo.LoadOptions(options, None)
            if regionKey and regionKey not in (0, 1):
                label = localization.GetByLabel('UI/Common/LocationDynamic', location=regionKey)
                self.sr.filtcombo.SelectItemByLabel(label)
            else:
                self.sr.filtcombo.SelectItemByIndex(regionKey)
        except (Exception,) as e:
            sys.exc_clear()

        def CmpFunc(a, b):
            if sortKey == 0:
                return cmp(a.label, b.label)
            elif sortKey == 1:
                return cmp(a.jumps, b.jumps)
            else:
                return cmp(b.itemCount, a.itemCount)

        if (const.corpRoleAccountant | const.corpRoleJuniorAccountant) & eve.session.corprole == 0:
            self.SetHint(localization.GetByLabel('UI/Corporations/Assets/NeedAccountantOrJuniorRole'))
            sm.GetService('corpui').HideLoad()
            return
        self.sr.scroll.allowFilterColumns = 1
        data = []
        scrolllist = []
        for row in rows:
            data.append(self.GetLocationData(row, flag, scrollID=self.sr.scroll.sr.id))

        data.sort(lambda x, y: cmp(x['label'], y['label']))
        for row in data:
            if regionKey == 1:
                scrolllist.append(listentry.Get('Group', row))
            elif regionKey == 0:
                if row['regionID'] == eve.session.regionid:
                    scrolllist.append(listentry.Get('Group', row))
            elif row['regionID'] == regionKey:
                scrolllist.append(listentry.Get('Group', row))
            uicore.registry.SetListGroupOpenState(('corpassets', row['locationID']), 0)

        scrolllist.sort(CmpFunc)
        self.sr.scroll.Load(fixedEntryHeight=42, contentList=scrolllist, sortby='label', headers=uix.GetInvItemDefaultHeaders(), noContentHint=localization.GetByLabel('UI/Corporations/Assets/NoItemsFound'))
        sm.GetService('corpui').HideLoad()

    def GetFilterOptions(self, rows, flagName):
        filterOptions = self.GetRegions(rows, flagName)
        options = [(localization.GetByLabel('UI/Corporations/Assets/CurrentRegion'), (flagName, 0)), (localization.GetByLabel('UI/Corporations/Assets/AllRegions'), (flagName, 1))]
        opts = {}
        for r in filterOptions:
            if util.IsRegion(r):
                label = localization.GetByLabel('UI/Common/LocationDynamic', location=r)
                opts[label] = r

        keys = opts.keys()
        keys.sort()
        for k in keys:
            options.append((k, (flagName, opts[k])))

        return options

    def GetRegions(self, rows, flagName):
        mapSvc = sm.GetService('map')
        regionIDs = []
        for row in rows:
            if flagName == KEYNAME_LOCKDOWN:
                locationID = row
            else:
                locationID = row.locationID
            try:
                solarSystemID = sm.GetService('ui').GetStation(locationID).solarSystemID
            except:
                solarSystemID = locationID

            try:
                constellationID = mapSvc.GetParent(solarSystemID)
                regionID = mapSvc.GetParent(constellationID)
                regionIDs.append(regionID)
            except:
                log.LogException()

        return regionIDs

    def GetLocationData(self, row, flag, scrollID = None):
        jumps = -1
        solarSystemID = row.solarsystemID
        try:
            locationName = localization.GetByLabel('UI/Common/LocationDynamic', location=row.locationID)
            mapSvc = sm.GetService('map')
            constellationID = mapSvc.GetParent(solarSystemID)
            regionID = mapSvc.GetParent(constellationID)
            jumps = sm.GetService('clientPathfinderService').GetJumpCountFromCurrent(solarSystemID)
            label = localization.GetByLabel('UI/Corporations/Assets/LocationAndJumps', location=row.locationID, jumps=jumps)
        except:
            log.LogException()
            label = locationName

        numberOfItems = -1
        if hasattr(row, 'itemCount'):
            numberOfItems = row.itemCount
            label = localization.GetByLabel('UI/Inventory/AssetsWindow/LocationDataLabel', location=row.locationID, itemCount=numberOfItems, jumps=jumps)
        data = {'GetSubContent': self.GetSubContent,
         'label': label,
         'jumps': jumps,
         'itemCount': numberOfItems,
         'groupItems': None,
         'flag': flag,
         'id': ('corpassets', row.locationID),
         'tabs': [],
         'state': 'locked',
         'locationID': row.locationID,
         'showicon': 'hide',
         'MenuFunction': self.GetLocationMenu,
         'solarSystemID': solarSystemID,
         'regionID': regionID,
         'scrollID': scrollID,
         'locationTypeID': getattr(row, 'typeID', None)}
        return data

    def IsLocationStructure(self, node):
        locationTypeID = node.locationTypeID
        if not locationTypeID:
            return False
        categoryID = evetypes.GetCategoryID(locationTypeID)
        return categoryID == const.categoryStructure

    def GetLocationMenu(self, node):
        locationID = node.locationID
        if util.IsStation(locationID) or self.IsLocationStructure(node):
            if util.IsStation(locationID):
                stationInfo = sm.GetService('ui').GetStation(locationID)
                typeID = stationInfo.stationTypeID
            else:
                typeID = node.locationTypeID
            solarSystemID = node.solarSystemID
            menu = sm.GetService('menu').CelestialMenu(locationID, typeID=typeID, parentID=solarSystemID)
            checkIsDirector = self.IsDirector()
            if checkIsDirector:
                if node.flag == FLAG_JUNK:
                    menu.append((MenuLabel('UI/Corporations/Assets/TrashItemsAtLocation'), self.TrashJunkAtLocation, (locationID,)))
                if self.IsLocationStructure(node):
                    if util.IsWormholeSystem(solarSystemID):
                        label = MenuLabel('UI/Inventory/AssetSafety/MoveItemsToSpace')
                    else:
                        label = MenuLabel('UI/Inventory/AssetSafety/MoveItemsToSafety')
                    menu.append((label, self.MoveItemsToSafety, (solarSystemID, locationID)))
            return menu
        if util.IsSolarSystem(locationID):
            return sm.GetService('menu').CelestialMenu(locationID)
        return []

    def IsDirector(self):
        checkIsDirector = const.corpRoleDirector == session.corprole & const.corpRoleDirector
        return checkIsDirector

    def TrashJunkAtLocation(self, locationID):
        items = sm.RemoteSvc('corpmgr').GetAssetInventoryForLocation(eve.session.corpid, locationID, FLAGNAME_JUNK)
        sm.GetService('menu').TrashInvItems(items)

    def MoveItemsToSafety(self, solarSystemID, structureID):
        sm.GetService('assetSafety').MoveItemsInStructureToAssetSafetyForCorp(solarSystemID, structureID)

    def GetSubContent(self, nodedata, *args):
        which = FLAG_TO_FLAGNAME[nodedata.flag]
        items = sm.RemoteSvc('corpmgr').GetAssetInventoryForLocation(eve.session.corpid, nodedata.locationID, which)
        scrolllist = []
        if len(items) == 0:
            label = localization.GetByLabel('/Carbon/UI/Controls/Common/NoItem')
            if nodedata.flag == FLAG_OFFICES:
                label = localization.GetByLabel('UI/Corporations/Assets/UnusedCorpOffice')
            return [listentry.Get('Generic', {'label': label,
              'sublevel': nodedata.Get('sublevel', 0) + 1})]
        items.header.virtual = items.header.virtual + [('groupID', lambda row: evetypes.GetGroupID(row.typeID)), ('categoryID', lambda row: evetypes.GetCategoryID(row.typeID))]
        searchCondition = nodedata.Get('searchCondition', None)
        if which == FLAGNAME_OFFICES and searchCondition is None:
            divisionNames = sm.GetService('corp').GetDivisionNames()
            if util.IsStation(nodedata.locationID):
                divisionIdFromHangarFlag = {const.flagHangar: 1}
            else:
                divisionIdFromHangarFlag = {const.flagCorpSAG1: 1}
            divisionIdFromHangarFlag.update({const.flagCorpSAG2: 2,
             const.flagCorpSAG3: 3,
             const.flagCorpSAG4: 4,
             const.flagCorpSAG5: 5,
             const.flagCorpSAG6: 6,
             const.flagCorpSAG7: 7})
            for flag, divisionNumber in divisionIdFromHangarFlag.iteritems():
                label = divisionNames[divisionNumber]
                data = {'GetSubContent': self.GetSubContentDivision,
                 'label': label,
                 'groupItems': None,
                 'flag': flag,
                 'id': ('corpofficeassets', (nodedata.locationID, flag)),
                 'tabs': [],
                 'state': 'locked',
                 'locationID': nodedata.locationID,
                 'showicon': 'hide',
                 'sublevel': nodedata.Get('sublevel', 0) + 1,
                 'viewMode': self.sr.viewMode,
                 'scrollID': nodedata.scrollID}
                scrolllist.append(listentry.Get('Group', data))
                uicore.registry.SetListGroupOpenState(('corpofficeassets', (nodedata.locationID, flag)), 0)

        else:
            if nodedata.flag in (FLAG_OFFICES, FLAG_JUNK):
                sm.GetService('corp').GetLockedItemsByLocation(nodedata.locationID)
            for each in items:
                if searchCondition is not None:
                    if searchCondition.typeID is not None and searchCondition.typeID != each.typeID or searchCondition.groupID is not None and searchCondition.groupID != each.groupID or searchCondition.categoryID is not None and searchCondition.categoryID != each.categoryID or searchCondition.qty > each.stacksize:
                        continue
                data = uix.GetItemData(each, self.sr.viewMode, viewOnly=1, scrollID=nodedata.scrollID)
                data.id = each.itemID
                data.remote = True
                if nodedata.flag in (FLAG_OFFICES, FLAG_JUNK) and each.categoryID == const.categoryBlueprint:
                    data.locked = sm.GetService('corp').IsItemLocked(each)
                scrolllist.append(listentry.Get('InvItem', data=data))

        return scrolllist

    def GetSubContentDivision(self, nodedata, *args):
        items = sm.RemoteSvc('corpmgr').GetAssetInventoryForLocation(eve.session.corpid, nodedata.locationID, FLAGNAME_OFFICES)
        scrolllist = []
        if len(items) == 0:
            label = localization.GetByLabel('UI/Corporations/Assets/UnusedCorpOffice')
            data = util.KeyVal()
            data.label = label
            data.sublevel = nodedata.Get('sublevel', 1) + 1
            data.id = nodedata.flag
            return [listentry.Get('Generic', data=data)]
        if not set(['groupID', 'categoryID']) & {i[0] for i in items.header.virtual}:
            items.header.virtual = items.header.virtual + [('groupID', lambda row: evetypes.GetGroupID(row.typeID)), ('categoryID', lambda row: evetypes.GetCategoryID(row.typeID))]
        sm.GetService('corp').GetLockedItemsByLocation(nodedata.locationID)
        for each in items:
            if each.flagID != nodedata.flag:
                continue
            data = uix.GetItemData(each, nodedata.viewMode, viewOnly=1, scrollID=nodedata.scrollID)
            data.id = each.itemID
            data.remote = True
            data.sublevel = nodedata.Get('sublevel', 1) + 1
            if each.categoryID == const.categoryBlueprint:
                data.locked = sm.GetService('corp').IsItemLocked(each)
            scrolllist.append(listentry.Get('InvItemWithVolume', data=data))

        return scrolllist

    def OnGetEmptyMenu(self, *args):
        return []

    def ShowJournal(self, *args):
        if self is not None and not self.destroyed:
            sm.GetService('corpui').ShowLoad()
        else:
            return
        if (const.corpRoleAccountant | const.corpRoleJuniorAccountant) & eve.session.corprole == 0:
            self.SetHint(localization.GetByLabel('UI/Corporations/Assets/NeedAccountantRole'))
            self.sr.scroll.Clear()
            sm.GetService('corpui').HideLoad()
            return
        keymap = sm.GetService('account').GetKeyMap()
        scrolllist = []
        for row in keymap:
            label = '%s (%s - %s)' % (row.keyName.capitalize(), util.FmtDate(self.sr.journalFromDate, 'ls'), util.FmtDate(self.sr.journalToDate, 'ls'))
            data = {'GetSubContent': self.GetJournalSubContent,
             'label': label,
             'groupItems': None,
             'id': ('corpaccounts', row.keyName),
             'tabs': [],
             'state': 'locked',
             'accountKey': row.keyID,
             'showicon': 'hide',
             'fromDate': self.sr.journalFromDate}
            scrolllist.append(listentry.Get('Group', data))

        self.sr.scroll.Load(fixedEntryHeight=19, contentList=scrolllist, headers=[localization.GetByLabel('UI/Common/Date'),
         localization.GetByLabel('UI/Common/ID'),
         localization.GetByLabel('UI/Common/Amount'),
         localization.GetByLabel('UI/Common/Description'),
         localization.GetByLabel('UI/Common/Amount')])
        sm.GetService('corpui').HideLoad()

    def GetJournalSubContent(self, nodedata, *args):
        items = sm.GetService('account').GetJournal(nodedata.keyID, nodedata.fromDate, None, 1)
        scrolllist = []
        for row in items:
            if row.entryTypeID == const.refSkipLog:
                continue
            data = {}
            if row.entryTypeID in (const.refMarketEscrow, const.refTransactionTax, const.refBrokerfee):
                actor = cfg.eveowners.Get(row.ownerID1).name
            else:
                actor = ''
            data['label'] = '%s<t>%s<t>%s<t>%s<t>%s' % (util.FmtDate(row.transactionDate, 'ls'),
             row.transactionID,
             util.FmtCurrency(row.amount, currency=None, showFractionsAlways=0),
             util.FmtRef(row.entryTypeID, row.ownerID1, row.ownerID2, row.referenceID, amount=row.amount),
             actor)
            data['sort_%s' % localization.GetByLabel('UI/Common/Date')] = row.transactionDate
            data['sort_%s' % localization.GetByLabel('UI/Common/Amount')] = row.amount
            data['sort_%s' % localization.GetByLabel('UI/Common/ID')] = row.transactionID
            scrolllist.append(listentry.Get('Generic', data))

        return scrolllist

    def OnLockedItemChangeUI(self, itemID, ownerID, locationID, change):
        self.LogInfo(self.__class__.__name__, 'OnLockedItemChangeUI')
        if self.sr.tabs.GetSelectedArgs() == KEYNAME_LOCKDOWN:
            sortKey = settings.char.ui.Get('corpAssetsSortKey', None)
            regionKey = settings.char.ui.Get('corpAssetsKeyID_lockdown', 0)
            self.ShowLockdown(sortKey, regionKey)

    def ShowLockdown(self, sortKey, regionKey, *args):
        if self is not None and not self.destroyed:
            sm.GetService('corpui').ShowLoad()
        else:
            return
        if sortKey is None:
            sortKey = settings.char.ui.Get('corpAssetsSortKey', None)
        settings.char.ui.Set('corpAssetsSortKey', sortKey)
        if regionKey is None:
            regionKey = settings.char.ui.Get('corpAssetsKeyID_lockdown', 0)
        settings.char.ui.Set('corpAssetsKeyID_lockdown', regionKey)
        if (const.corpRoleAccountant | const.corpRoleJuniorAccountant) & eve.session.corprole == 0:
            self.SetHint(localization.GetByLabel('UI/Corporations/Assets/NeedAccountantRole'))
            self.sr.scroll.Clear()
            sm.GetService('corpui').HideLoad()
            return
        scrolllistTmp = []
        self.sr.scroll.allowFilterColumns = 1
        locationIDs = sm.GetService('corp').GetLockedItemLocations()
        options = self.GetFilterOptions(locationIDs, KEYNAME_LOCKDOWN)
        try:
            self.sr.filtcombo.LoadOptions(options, None)
            if regionKey and regionKey not in (0, 1):
                self.sr.filtcombo.SelectItemByLabel(cfg.evelocations.Get(regionKey).name)
            else:
                self.sr.filtcombo.SelectItemByIndex(regionKey)
        except (Exception,) as e:
            sys.exc_clear()

        def CmpFunc(a, b):
            if sortKey == 1:
                return cmp(a.jumps, b.jumps)
            else:
                return cmp(a.label, b.label)

        for locationID in locationIDs:
            try:
                solarSystemID = sm.GetService('ui').GetStation(locationID).solarSystemID
            except:
                solarSystemID = row.locationID

            try:
                mapSvc = sm.GetService('map')
                jumps = sm.GetService('clientPathfinderService').GetJumpCountFromCurrent(solarSystemID)
                locationName = localization.GetByLabel('UI/Common/LocationDynamic', location=locationID)
                constellationID = mapSvc.GetParent(solarSystemID)
                regionID = mapSvc.GetParent(constellationID)
                label = localization.GetByLabel('UI/Corporations/Assets/LocationAndJumps', location=locationID, jumps=jumps)
            except:
                log.LogException()
                label = locationName

            data = {'label': label,
             'jumps': jumps,
             'GetSubContent': self.ShowLockdownSubcontent,
             'locationID': locationID,
             'regionID': regionID,
             'groupItems': None,
             'id': ('itemlocking', locationID),
             'tabs': [],
             'state': 'locked',
             'showicon': 'hide',
             'scrollID': self.sr.scroll.sr.id}
            scrolllistTmp.append(listentry.Get('Group', data))

        scrolllistTmp.sort(lambda x, y: cmp(x['label'], y['label']))
        scrolllist = []
        for row in scrolllistTmp:
            if regionKey == 1:
                scrolllist.append(listentry.Get('Group', row))
            elif regionKey == 0:
                if row['regionID'] == eve.session.regionid:
                    scrolllist.append(listentry.Get('Group', row))
            elif row['regionID'] == regionKey:
                scrolllist.append(listentry.Get('Group', row))
            uicore.registry.SetListGroupOpenState(('corpassets', row['locationID']), 0)

        scrolllist.sort(CmpFunc)
        self.sr.scroll.Load(fixedEntryHeight=19, contentList=scrolllist, headers=uix.GetInvItemDefaultHeaders(), noContentHint=localization.GetByLabel('UI/Corporations/Assets/NoItemsFound'))
        sm.GetService('corpui').HideLoad()

    def ShowLockdownSubcontent(self, nodedata, *args):
        scrolllist = []
        items = sm.GetService('corp').GetLockedItemsByLocation(nodedata.locationID)
        locationID = nodedata.locationID
        offices = sm.GetService('corp').GetMyCorporationsOffices().SelectByUniqueColumnValues('locationID', [locationID])
        if offices and len(offices):
            for office in offices:
                if locationID == office.locationID:
                    locationID = office.officeID

        header = ['itemID',
         'typeID',
         'ownerID',
         'groupID',
         'categoryID',
         'quantity',
         'singleton',
         'stacksize',
         'locationID',
         'flagID']
        for it in items.itervalues():
            line = [it.itemID,
             it.typeID,
             eve.session.corpid,
             evetypes.GetGroupID(it.typeID),
             evetypes.GetCategoryID(it.typeID),
             1,
             const.singletonBlueprintOriginal,
             1,
             locationID,
             4]
            fakeItem = Row(header, line)
            data = uix.GetItemData(fakeItem, self.sr.viewMode, viewOnly=1, scrollID=nodedata.scrollID)
            data.GetMenu = self.OnGetEmptyMenu
            scrolllist.append(listentry.Get('InvItem', data))

        return scrolllist

    def SetHint(self, hintstr = None):
        if self.sr.scroll:
            self.sr.scroll.ShowHint(hintstr)

    def ShowSearch(self, *args):
        if not self.sr.search_inited:
            search_cont = uiprimitives.Container(name='search_cont', parent=self, height=36, align=uiconst.TOTOP, idx=1)
            self.sr.search_cont = search_cont
            catOptions = [(localization.GetByLabel('UI/Common/All'), None)]
            categories = []
            for categoryID in evetypes.IterateCategories():
                if categoryID > 0:
                    categories.append([evetypes.GetCategoryNameByCategory(categoryID), categoryID, evetypes.IsCategoryPublishedByCategory(categoryID)])

            categories.sort()
            for c in categories:
                if c[2]:
                    catOptions.append((c[0], c[1]))

            typeOptions = [(localization.GetByLabel('UI/Corporations/Common/StationOffices'), FLAGNAME_OFFICES),
             (localization.GetByLabel('UI/Corporations/Assets/Impounded'), FLAGNAME_JUNK),
             (localization.GetByLabel('UI/Corporations/Assets/InSpace'), FLAGNAME_PROPERTY),
             (localization.GetByLabel('UI/Corporations/Assets/StationDeliveries'), FLAGNAME_DELIVERIES)]
            left = 5
            top = 17
            self.sr.fltType = c = uicontrols.Combo(label=localization.GetByLabel('UI/Common/Where'), parent=search_cont, options=typeOptions, name='flt_type', select=settings.user.ui.Get('corp_assets_filter_type', None), callback=self.ComboChange, width=90, pos=(left,
             top,
             0,
             0))
            left += c.width + 4
            self.sr.fltCategories = c = uicontrols.Combo(label=localization.GetByLabel('UI/Corporations/Assets/ItemCategory'), parent=search_cont, options=catOptions, name='flt_category', select=settings.user.ui.Get('corp_assets_filter_categories', None), callback=self.ComboChange, width=90, pos=(left,
             top,
             0,
             0))
            left += c.width + 4
            grpOptions = [(localization.GetByLabel('UI/Common/All'), None)]
            self.sr.fltGroups = c = uicontrols.Combo(label=localization.GetByLabel('UI/Corporations/Assets/ItemGroup'), parent=search_cont, options=grpOptions, name='flt_group', select=settings.user.ui.Get('corp_assets_filter_groups', None), callback=self.ComboChange, width=90, pos=(left,
             top,
             0,
             0))
            left += c.width + 4
            self.sr.fltItemType = c = uicontrols.SinglelineEdit(name='flt_exacttype', parent=search_cont, label=localization.GetByLabel('UI/Corporations/Assets/ItemTypeExact'), setvalue=settings.user.ui.Get('corp_assets_filter_itemtype', ''), width=106, top=top, left=left, isTypeField=True)
            left += c.width + 4
            self.sr.fltQuantity = c = uicontrols.SinglelineEdit(name='flt_quantity', parent=search_cont, label=localization.GetByLabel('UI/Corporations/Assets/MinQuantity'), setvalue=str(settings.user.ui.Get('corp_assets_filter_quantity', '')), width=60, top=top, left=left)
            left += c.width + 4
            c = self.sr.fltSearch = uicontrols.Button(parent=search_cont, label=localization.GetByLabel('UI/Common/Search'), func=self.Search, pos=(left,
             top,
             0,
             0), btn_default=1)
            self.PopulateGroupCombo(isSel=True)
            self.sr.search_inited = 1
        self.sr.search_cont.state = uiconst.UI_PICKCHILDREN
        self.sr.scroll.Load(fixedEntryHeight=42, contentList=[], sortby='label', headers=uix.GetInvItemDefaultHeaders()[:], noContentHint=localization.GetByLabel('UI/Corporations/Assets/NoItemsFound'))
        self.Search()

    def ComboChange(self, wnd, *args):
        if wnd.name == 'flt_category':
            self.PopulateGroupCombo()

    def PopulateGroupCombo(self, isSel = False):
        categoryID = self.sr.fltCategories.GetValue()
        groups = [(localization.GetByLabel('UI/Common/All'), None)]
        if categoryID:
            if evetypes.CategoryExists(categoryID):
                for groupID in evetypes.GetGroupIDsByCategory(categoryID):
                    if evetypes.IsGroupPublishedByGroup(groupID):
                        groups.append((evetypes.GetGroupNameByGroup(groupID), groupID))

        sel = None
        if isSel:
            sel = settings.user.ui.Get('contracts_filter_groups', None)
        self.sr.fltGroups.LoadOptions(groups, sel)

    def ParseItemType(self, wnd, *args):
        if self.destroyed:
            return
        if not hasattr(self, 'parsingItemType'):
            self.parsingItemType = None
        typeID = DoParseItemType(wnd, self.parsingItemType)
        if typeID:
            self.parsingItemType = evetypes.GetName(typeID)
        return typeID

    def Search(self, *args):
        if self is None or self.destroyed:
            return
        sm.GetService('corpui').ShowLoad()
        self.sr.scroll.Load(fixedEntryHeight=42, contentList=[], sortby='label', headers=uix.GetInvItemDefaultHeaders()[:])
        self.SetHint(localization.GetByLabel('UI/Common/Searching'))
        scrolllist = []
        try:
            itemTypeID = None
            itemCategoryID = None
            itemGroupID = None
            txt = self.sr.fltItemType.GetValue()
            if txt != '':
                for t in sm.GetService('contracts').GetMarketTypes():
                    if txt == t.typeName:
                        itemTypeID = t.typeID
                        break

                if not itemTypeID:
                    itemTypeID = self.ParseItemType(self.sr.fltItemType)
            txt = self.sr.fltGroups.GetValue()
            txtc = self.sr.fltCategories.GetValue()
            if txt and int(txt) > 0:
                itemGroupID = int(txt)
            elif txtc and int(txtc) > 0:
                itemCategoryID = int(txtc)
            qty = self.sr.fltQuantity.GetValue() or None
            try:
                qty = int(qty)
                if qty < 0:
                    qty = 0
            except:
                qty = None

            which = self.sr.fltType.GetValue() or None
            settings.user.ui.Set('corp_assets_filter_type', which)
            settings.user.ui.Set('corp_assets_filter_categories', itemCategoryID)
            settings.user.ui.Set('corp_assets_filter_groups', itemGroupID)
            settings.user.ui.Set('corp_assets_filter_itemtype', self.sr.fltItemType.GetValue())
            settings.user.ui.Set('corp_assets_filter_quantity', qty)
            rows = sm.RemoteSvc('corpmgr').SearchAssets(which, itemCategoryID, itemGroupID, itemTypeID, qty)
            searchCond = util.KeyVal(categoryID=itemCategoryID, groupID=itemGroupID, typeID=itemTypeID, qty=qty)
            flag = FLAGNAME_TO_FLAG[which]
            self.SetHint(None)
            self.sr.scroll.allowFilterColumns = 1
            for row in rows:
                jumps = -1
                try:
                    solarSystemID = sm.GetService('ui').GetStation(row.locationID).solarSystemID
                except:
                    solarSystemID = row.locationID

                try:
                    jumps = sm.GetService('clientPathfinderService').GetJumpCountFromCurrent(solarSystemID)
                    locationName = cfg.evelocations.Get(row.locationID).locationName
                    label = localization.GetByLabel('UI/Corporations/Assets/LocationAndJumps', location=row.locationID, jumps=jumps)
                except:
                    log.LogException()
                    label = locationName

                data = {'GetSubContent': self.GetSubContent,
                 'label': label,
                 'groupItems': None,
                 'flag': flag,
                 'id': ('corpassets', row.locationID),
                 'tabs': [],
                 'state': 'locked',
                 'locationID': row.locationID,
                 'showicon': 'hide',
                 'MenuFunction': self.GetLocationMenu,
                 'searchCondition': searchCond,
                 'scrollID': self.sr.scroll.sr.id}
                scrolllist.append(listentry.Get('Group', data))
                uicore.registry.SetListGroupOpenState(('corpassets', row.locationID), 0)

            self.sr.scroll.Load(fixedEntryHeight=42, contentList=scrolllist, sortby='label', headers=uix.GetInvItemDefaultHeaders(), noContentHint=localization.GetByLabel('UI/Corporations/Assets/NoItemsFound'))
        finally:
            sm.GetService('corpui').HideLoad()
