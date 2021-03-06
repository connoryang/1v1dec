#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\market\quote.py
import blue
import evetypes
import form
import structures
import uiprimitives
import uicontrols
import uix
import uiutil
import util
import uthread
import sys
import service
import log
import carbonui.const as uiconst
import localization
from carbon.common.script.sys.row import Row
MINSCROLLHEIGHT = 64
LEFTSIDEWIDTH = 80
LABELWIDTH = 100

class MarketUtils(service.Service):
    __exportedcalls__ = {'Buy': [],
     'ModifyOrder': [],
     'GetMarketGroups': [],
     'GetMarketTypes': [],
     'GetJumps': [],
     'GetPrice': [],
     'GetType': [],
     'GetLocation': [],
     'GetExpiresIn': [],
     'GetQuantity': [],
     'GetMarketRange': [],
     'GetQuantitySlashVolume': [],
     'GetMinVolume': [],
     'GetSolarsystem': [],
     'GetRegion': [],
     'GetConstellation': [],
     'GetRange': [],
     'GetBestMatchText': [],
     'BuyStationAsk': [service.ROLE_IGB],
     'ShowMarketDetails': [service.ROLE_IGB],
     'MatchOrder': [service.ROLE_IGB],
     'ProcessRequest': [service.ROLE_IGB],
     'StartupCheck': {'role': service.ROLE_ANY,
                      'preargs': ['regionid'],
                      'caching': {'versionCheck': ('1 minute', None, None),
                                  'sessionInfo': 'regionid'},
                      'callhandlerargs': {'PreCall_CachedMethodCall.retainMachoVersion': 1}}}
    __guid__ = 'svc.marketutils'
    __servicename__ = 'Market Utils'
    __displayname__ = 'Market Utils'
    __notifyevents__ = ['ProcessUIRefresh']
    __dependencies__ = []

    def __init__(self):
        service.Service.__init__(self)
        self.marketgroups = None
        self.allgroups = None
        self.regionUpAt = None

    def Run(self, memStream = None):
        self.Reset()

    def Reset(self):
        self.marketgroups = None
        self.allgroups = None
        self.regionUpAt = None

    def ProcessUIRefresh(self):
        self.Reset()

    def StartupCheck(self):
        now = blue.os.GetWallclockTime()
        if self.regionUpAt is not None:
            if self.regionUpAt.time < now - 2 * const.MIN:
                return
            raise UserError(self.regionUpAt.msg, self.regionUpAt.dict)
        try:
            sm.ProxySvc('marketProxy').StartupCheck()
        except UserError as e:
            if eve.session.role & service.ROLE_GMH == 0:
                self.regionUpAt = Row(['time', 'msg', 'dict'], [now, e.msg, e.dict])
            sys.exc_clear()
            raise UserError(e.msg, e.dict)

    def GetMarketRange(self):
        if session.stationid or session.structureid:
            r = settings.user.ui.Get('marketRangeFilterStation', const.rangeStation)
        else:
            r = settings.user.ui.Get('marketRangeFilterSpace', const.rangeRegion)
        return r

    def SetMarketRange(self, value):
        if eve.session.stationid or session.structureid:
            r = settings.user.ui.Set('marketRangeFilterStation', value)
        else:
            r = settings.user.ui.Set('marketRangeFilterSpace', value)
        return r

    def BuyStationAsk(self, typeID):
        if eve.session.stationid:
            asks = sm.GetService('marketQuote').GetStationAsks()
            for ask in asks.itervalues():
                if ask.typeID == typeID:
                    self.Buy(typeID, ask)
                    return

    def FindMarketGroup(self, typeID, groupInfo = None, trace = None):
        groupInfo = groupInfo or self.GetMarketGroups()[None]
        trace = trace or ''
        for _groupInfo in groupInfo:
            if typeID in _groupInfo.types:
                trace += _groupInfo.marketGroupName.strip() + ' / '
                if not _groupInfo.hasTypes:
                    return self.FindMarketGroup(typeID, self.GetMarketGroups()[_groupInfo.marketGroupID], trace)
                else:
                    return (_groupInfo, trace)

        return (None, trace)

    def ProcessRequest(self, subMethod, typeID = None, orderID = None):
        if subMethod == 'Buy':
            self.Buy(typeID, orderID)
        elif subMethod == 'ShowMarketDetails':
            self.ShowMarketDetails(typeID, orderID)
        else:
            raise RuntimeError('Unsupported subMethod call. Possible h4x0r attempt.')

    def MatchOrder(self, typeID, orderID):
        order = None
        if orderID:
            order = sm.GetService('marketQuote').GetOrder(orderID, typeID)
        self.Buy(typeID, order, placeOrder=order is None)

    def ShowMarketDetails(self, typeID, orderID, silently = False):
        marketWnd = form.RegionalMarket.GetIfOpen()
        if marketWnd and not marketWnd.destroyed:
            stack = marketWnd.GetStack()
            if not silently or stack and stack.GetActiveWindow() != marketWnd or marketWnd.IsMinimized():
                marketWnd.Maximize()
        else:
            uicore.cmd.OpenMarket()
        marketWnd = form.RegionalMarket.GetIfOpen()
        if marketWnd:
            marketWnd.LoadTypeID_Ext(typeID)

    def AddTypesToMarketGroups(self):
        typeIDsByMktGrp = {}

        def ExtractTypes(marketGroups, groupID):
            sum = {}
            if groupID not in marketGroups:
                return {}
            for gr in marketGroups[groupID]:
                explicits = {}
                for typeID in evetypes.GetTypeIDsByMarketGroup(gr.marketGroupID):
                    blue.pyos.BeNice()
                    if evetypes.IsPublished(typeID):
                        explicits[typeID] = 1

                subids = ExtractTypes(marketGroups, gr.marketGroupID)
                subids.update(explicits)
                gr.types = subids.keys()
                typeIDsByMktGrp[gr.marketGroupID] = explicits.keys()
                sum.update(subids)

            return sum

        try:
            ExtractTypes(self.marketgroups, None)
        finally:
            ExtractTypes = None

    def GetMarketGroups(self, getall = 0):
        if self.marketgroups is None:
            marketgroups = sm.GetService('marketQuote').GetMarketProxy().GetMarketGroups()
            cols = marketgroups.header.Keys()
            self.marketgroups = {}
            for parentMarketGroupID in marketgroups:
                groups = marketgroups[parentMarketGroupID]
                theseMarketGroups = []
                for grp in groups:
                    marketGroup = util.KeyVal()
                    for c in cols:
                        setattr(marketGroup, c, getattr(grp, c))

                    marketGroup.marketGroupName = localization.GetImportantByMessageID(marketGroup.marketGroupNameID)
                    marketGroup.description = localization.GetByMessageID(marketGroup.descriptionID)
                    theseMarketGroups.append(marketGroup)

                self.marketgroups[parentMarketGroupID] = theseMarketGroups

            self.AddTypesToMarketGroups()
        return self.marketgroups

    def GetMarketTypes(self):
        t = []
        for each in self.GetMarketGroups()[None]:
            t += each.types

        return t

    def GetMarketGroup(self, findMarketGroupID):
        all = self.GetMarketGroups(1)
        return all.get(findMarketGroupID, None)

    def AllowTrade(self, order = None, locationID = None):
        limits = sm.GetService('marketQuote').GetSkillLimits(None)
        bidLimit = limits['bid']
        if session.structureid or session.stationid:
            if locationID != session.solarsystemid2:
                pass
            return True
        if bidLimit == const.rangeStation and order is None:
            raise UserError('CustomError', {'error': localization.GetByLabel('UI/Market/MarketQuote/OutOfRange')})

    def Buy(self, typeID, order = None, duration = 1, placeOrder = 0, prePickedLocationID = None, ignoreAdvanced = False, quantity = 1):
        locationID = None
        self.AllowTrade(order)
        if order is None:
            if prePickedLocationID:
                locationID = prePickedLocationID
            elif eve.session.stationid:
                locationID = session.stationid
            elif session.structureid:
                if not sm.GetService('structureServices').IsServiceAvailable(structures.SERVICE_MARKET):
                    raise UserError(structures.GetAccessErrorLabel(structures.SERVICE_MARKET), {'structureName': cfg.evelocations.Get(session.structureid).locationName})
                locationID = session.structureid
            else:
                stationData = sm.GetService('marketutils').PickStation()
                if stationData:
                    locationID = stationData
            if locationID is None:
                return
        sm.GetService('marketutils').StartupCheck()
        if locationID == None and order.stationID != None:
            locationID = order.stationID
        wnd = form.MarketActionWindow.Open()
        advancedBuyWnd = settings.char.ui.Get('advancedBuyWnd', 0)
        if uicore.uilib.Key(uiconst.VK_SHIFT) or placeOrder or advancedBuyWnd and not ignoreAdvanced:
            wnd.LoadBuy_Detailed(typeID, order, duration, locationID, forceRange=True, quantity=quantity)
        else:
            if locationID is not None:
                sm.GetService('marketQuote').RefreshJumps(typeID, locationID)
            wnd.TradeSimple(typeID=typeID, order=order, locationID=locationID, ignoreAdvanced=ignoreAdvanced, quantity=quantity)
        uicore.registry.SetFocus(wnd)

    def ModifyOrder(self, order):
        wnd = form.MarketActionWindow.Open(windowID='marketmodifyaction')
        wnd.LoadModify(order)

    def CancelOffer(self, order):
        if eve.Message('CancelMarketOrder', {}, uiconst.YESNO, suppress=uiconst.ID_YES) != uiconst.ID_YES:
            return
        sm.GetService('marketQuote').CancelOrder(order.orderID, order.regionID)

    def PickStation(self):
        if not session.solarsystemid2:
            return
        stations = sm.RemoteSvc('stationSvc').GetStationsByRegion(eve.session.regionid)
        quote = sm.GetService('marketQuote')
        limits = quote.GetSkillLimits(None)
        bidDistance = limits['bid']
        stationsToList = [ (each, quote.GetStationDistance(each.stationID)) for each in stations if quote.GetStationDistance(each.stationID) <= bidDistance ]
        if len(stationsToList) == 0:
            return
        for each, distance in stationsToList:
            itemID = each.stationID
            if itemID not in cfg.evelocations:
                staData = [itemID,
                 each.stationName,
                 each.solarSystemID,
                 each.x,
                 each.y,
                 each.z,
                 None]
                cfg.evelocations.Hint(itemID, staData)

        headers = [localization.GetByLabel('UI/Common/LocationTypes/Station'), localization.GetByLabel('UI/Market/Marketbase/Jumps')]
        stationLst = []
        for station, distance in stationsToList:
            data = util.KeyVal()
            data.label = '%s<t>%s' % (cfg.evelocations.Get(station.stationID).name, distance)
            data.listvalue = station.stationID
            data.showinfo = 1
            data.typeID = station.stationTypeID
            data.itemID = station.stationID
            data.Set('sort_' + headers[1], distance)
            stationLst.append(data)

        station = uix.ListWnd(stationLst, 'pickStation', localization.GetByLabel('UI/Search/SelectStation'), hint=localization.GetByLabel('UI/Market/MarketQuote/ChouseStation'), isModal=1, ordered=0, scrollHeaders=headers, minw=450)
        if station:
            return station

    def PickItem(self, typeID, quantity = None):
        stations = sm.GetService('invCache').GetInventory(const.containerGlobal).ListStations()
        primeloc = []
        for station in stations:
            primeloc.append(station.stationID)

        if len(primeloc):
            cfg.evelocations.Prime(primeloc)
        else:
            return None
        stationLst = [ (cfg.evelocations.Get(station.stationID).name + ' (' + str(station.itemCount) + ' items)', station.stationID) for station in stations ]
        station = uix.ListWnd(stationLst, 'generic', localization.GetByLabel('UI/Search/SelectStation'), hint=localization.GetByLabel('UI/Market/MarketQuote/SellFromStations'), isModal=1)
        if station:
            items = sm.GetService('invCache').GetInventory(const.containerGlobal).ListStationItems(station[1])
            badLocations = [const.locationTemp, const.locationSystem, eve.session.charid]
            valid = []
            for each in items:
                if each.typeID != typeID:
                    continue
                if util.IsJunkLocation(each.locationID) or each.locationID in badLocations:
                    continue
                if each.stacksize == 0 or each.stacksize < quantity:
                    continue
                valid.append(each)

            if len(valid) == 1:
                return valid[0]
            scrolllist = []
            for each in valid:
                scrolllist.append(('%s<t>%s' % (evetypes.GetName(each.typeID), util.FmtAmt(each.stacksize)), each))

            if not scrolllist:
                if eve.Message('CustomQuestion', {'header': localization.GetByLabel('UI/Market/MarketQuote/headerTryAnotherStation'),
                 'question': localization.GetByLabel('UI/Market/MarketQuote/NoItemsAtStations', typeID=typeID, stationName=station[0])}, uiconst.YESNO) == uiconst.ID_YES:
                    return self.PickItem(typeID, quantity)
                return None
            item = uix.ListWnd(scrolllist, 'generic', localization.GetByLabel('UI/Search/SelectItem'), hint=localization.GetByLabel('UI/Market/MarketQuote/SelectItemsToSell'), isModal=1, scrollHeaders=[localization.GetByLabel('UI/Common/Type'), localization.GetByLabel('UI/Common/Quantity')])
            if item:
                return item[1]

    def GetFuncMaps(self):
        return {uiutil.StripTags(localization.GetByLabel('UI/Common/Type'), stripOnly=['localized']): 'GetType',
         uiutil.StripTags(localization.GetByLabel('UI/Common/Quantity'), stripOnly=['localized']): 'GetQuantity',
         uiutil.StripTags(localization.GetByLabel('UI/Market/MarketQuote/headerPrice'), stripOnly=['localized']): 'GetPrice',
         uiutil.StripTags(localization.GetByLabel('UI/Common/Location'), stripOnly=['localized']): 'GetLocation',
         uiutil.StripTags(localization.GetByLabel('UI/Common/Station'), stripOnly=['localized']): 'GetStation',
         uiutil.StripTags(localization.GetByLabel('UI/Common/LocationTypes/Region'), stripOnly=['localized']): 'GetRegion',
         uiutil.StripTags(localization.GetByLabel('UI/Common/Range'), stripOnly=['localized']): 'GetRange',
         uiutil.StripTags(localization.GetByLabel('UI/Market/MarketQuote/HeaderMinVolumn'), stripOnly=['localized']): 'GetMinVolume',
         uiutil.StripTags(localization.GetByLabel('UI/Market/Marketbase/ExpiresIn'), stripOnly=['localized']): 'GetExpiresIn',
         uiutil.StripTags(localization.GetByLabel('UI/Market/MarketQuote/headerIssuedBy'), stripOnly=['localized']): 'GetIssuedBy',
         uiutil.StripTags(localization.GetByLabel('UI/Market/Marketbase/Jumps'), stripOnly=['localized']): 'GetJumps',
         uiutil.StripTags(localization.GetByLabel('UI/Market/MarketQuote/headerWalletDivision'), stripOnly=['localized']): 'GetWalletDivision'}

    def GetJumps(self, record, data):
        sortJumps = record.jumps
        if record.jumps == 0:
            if record.stationID in (session.stationid, session.structureid):
                data.label += '%s<t>' % localization.GetByLabel('UI/Common/LocationTypes/Station')
                sortJumps = -1
            else:
                data.label += '%s<t>' % localization.GetByLabel('UI/Common/LocationTypes/System')
        elif record.jumps == 1000000:
            data.label += '%s<t>' % localization.GetByLabel('UI/Common/LocationTypes/Unreachable')
        else:
            data.label += '<right>%i<t>' % record.jumps
        data.Set('sort_%s' % localization.GetByLabel('UI/Market/Marketbase/Jumps'), sortJumps)

    def GetWalletDivision(self, record, data):
        data.label += '%s <t>' % sm.GetService('corp').GetDivisionNames()[record.keyID - 1000 + 8]

    def GetPrice(self, record, data):
        data.label += '<right>%s<t>' % util.FmtISK(record.price)
        data.Set('sort_%s' % localization.GetByLabel('UI/Market/MarketQuote/headerPrice'), record.price)

    def GetType(self, record, data):
        name = evetypes.GetNameOrNone(record.typeID)
        if name is not None:
            data.label += name + '<t>'
            data.Set('sort_%s' % localization.GetByLabel('UI/Common/Type'), name.lower())
        else:
            data.label += localization.GetByLabel('UI/Market/MarketQuote/UnknowenTypeError', typeIDText=str(record.typeID)) + '<t>'
            data.Set('sort_%s' % localization.GetByLabel('UI/Common/Type'), localization.GetByLabel('UI/Market/MarketQuote/UnknowenTypeError', typeIDText=str(record.typeID)))

    def GetLocation(self, record, data):
        locationName = cfg.evelocations.Get(record.stationID).name
        data.label += locationName + '<t>'
        data.Set('sort_%s' % localization.GetByLabel('UI/Common/Location'), locationName.lower())

    def GetStation(self, record, data):
        locationName = cfg.evelocations.Get(record.stationID).name
        data.label += locationName + '<t>'
        data.Set('sort_%s' % localization.GetByLabel('UI/Common/Station'), locationName.lower())

    def GetRegion(self, record, data):
        regionID = cfg.evelocations.Get(60014926).Station().regionID
        regionName = cfg.evelocations.Get(regionID).name
        data.Set('sort_%s' % localization.GetByLabel('UI/Common/LocationTypes/Region'), regionName.lower())

    def GetExpiresIn(self, record, data):
        exp = record.issueDate + record.duration * DAY - blue.os.GetWallclockTime()
        if exp < 0:
            data.label += '%s<t>' % localization.GetByLabel('UI/Market/MarketQuote/Expired')
        else:
            data.label += util.FmtDate(exp, 'ss') + '<t>'
        data.Set('sort_%s' % localization.GetByLabel('UI/Market/Marketbase/ExpiresIn'), record.issueDate + record.duration * const.DAY)

    def GetQuantity(self, record, data):
        data.label += '<right>%s<t>' % util.FmtAmt(int(record.volRemaining))
        data.Set('sort_%s' % localization.GetByLabel('UI/Common/Quantity'), int(record.volRemaining))

    def GetQuantitySlashVolume(self, record, data):
        data.label += '<right>%s/%s<t>' % (util.FmtAmt(int(record.volRemaining)), util.FmtAmt(int(record.volEntered)))
        data.Set('sort_%s' % localization.GetByLabel('UI/Common/Quantity'), (int(record.volRemaining), record.volEntered))

    def GetMinVolume(self, record, data):
        vol = int(min(record.volRemaining, record.minVolume))
        data.label += '<right>%s<t>' % util.FmtAmt(vol)
        data.Set('sort_%s' % localization.GetByLabel('UI/Market/MarketQuote/HeaderMinVolumn'), vol)

    def GetSolarsystem(self, record, data):
        solarsystemName = cfg.evelocations.Get(record.solarSystemID).name
        data.label += solarsystemName + '<t>'
        data.Set('sort_%s' % localization.GetByLabel('UI/Common/LocationTypes/SolarSystem'), solarsystemName.lower())

    def GetRegion(self, record, data):
        regionName = cfg.evelocations.Get(record.regionID).name
        data.label += regionName + '<t>'
        data.Set('sort_%s' % localization.GetByLabel('UI/Common/LocationTypes/Region'), regionName.lower())

    def GetConstellation(self, record, data):
        constellationName = cfg.evelocations.Get(record.constellationID).name
        data.label += constellationName + '<t>'
        data.Set('sort_%s' % localization.GetByLabel('UI/Common/LocationTypes/Constellation'), constellationName.lower())

    def GetRange(self, record, data):
        if record.range == const.rangeStation:
            rangeText = localization.GetByLabel('UI/Common/LocationTypes/Station')
            sortval = 0
        elif record.range == const.rangeSolarSystem:
            rangeText = localization.GetByLabel('UI/Common/LocationTypes/SolarSystem')
            sortval = 0.5
        elif record.range == const.rangeRegion:
            rangeText = localization.GetByLabel('UI/Common/LocationTypes/Region')
            sortval = sys.maxint
        else:
            rangeText = localization.GetByLabel('UI/Market/MarketQuote/NumberOfJumps', num=record.range)
            sortval = record.range
        data.label += rangeText + '<t>'
        data.Set('sort_%s' % localization.GetByLabel('UI/Common/Range'), sortval)

    def GetIssuedBy(self, record, data):
        name = cfg.eveowners.Get(record.charID).name
        data.label += name + '<t>'
        data.Set('sort_%s' % localization.GetByLabel('UI/Market/MarketQuote/headerIssuedBy'), name.lower())

    def GetFilterops(self, marketGroupID):
        mg = self.GetMarketGroups()
        ret = []
        for level1 in mg[marketGroupID]:
            ret.append((level1.marketGroupName, level1.marketGroupID))

        ret.sort()
        ret.insert(0, (localization.GetByLabel('UI/Market/MarketQuote/All'), None))
        return ret

    def GetTypeFilterIDs(self, marketGroupID, checkcategory = 1):
        c = []
        mg = self.GetMarketGroups()[marketGroupID]
        if mg:
            for each in mg:
                for typeID in each.types:
                    groupID = evetypes.GetGroupID(typeID)
                    if checkcategory:
                        categoryID = evetypes.GetCategoryID(typeID)
                        if categoryID not in c:
                            c.append(categoryID)
                    elif groupID not in c:
                        c.append(groupID)

        else:
            typeIDs = evetypes.GetTypeIDsByMarketGroup(marketGroupID)
            for typeID in typeIDs:
                if checkcategory:
                    categoryID = evetypes.GetCategoryID(typeID)
                    if categoryID not in c:
                        c.append(categoryID)
                groupID = evetypes.GetGroupID(typeID)
                if not checkcategory and groupID not in c:
                    c.append(groupID)

        return c

    def GetProducableGroups(self, lineGroups, lineCategs):
        valid = [ group.groupID for group in lineGroups ]
        validcategs = [ categ.categoryID for categ in lineCategs ]
        return (valid, validcategs)

    def GetProducableCategories(self, lineGroups, lineCategs):
        valid = [ categ.categoryID for categ in lineCategs ]
        for group in lineGroups:
            categoryID = evetypes.GetCategoryIDByGroup(group.groupID)
            if categoryID not in valid:
                valid.append(categoryID)

        return valid

    def GetBestMatchText(self, price, averagePrice, percentage):
        if price < averagePrice:
            aboveBelow = 'UI/Market/MarketQuote/PercentBelow'
            color = '<color=0xff00ff00>'
        else:
            aboveBelow = 'UI/Market/MarketQuote/PercentAbove'
            color = '<color=0xffff5050>'
        p = {'colorText': color,
         'percentage': round(100 * percentage, 2),
         'aboveBelow': localization.GetByLabel(aboveBelow),
         'colorTextEnd': '</color>'}
        return localization.GetByLabel('UI/Market/MarketQuote/BuyQuantity', **p)

    def AddTypeToQuickBar(self, typeID, parentID = 0, fromMarket = False, extraText = ''):
        if typeID is None:
            return
        self.AddToQuickBar(typeID, parentID, fromMarket=fromMarket, extraText=extraText)

    def AddToQuickBar(self, typeID, parent = 0, fromMarket = False, scatter = True, extraText = ''):
        evetypes.RaiseIFNotExists(typeID)
        current = settings.user.ui.Get('quickbar', {})
        lastid = settings.user.ui.Get('quickbar_lastid', 0)
        for id, data in current.items():
            if data.parent == parent and data.label == typeID:
                return None

        n = util.KeyVal()
        n.parent = parent
        n.id = lastid + 1
        n.label = typeID
        n.extraText = extraText
        lastid += 1
        settings.user.ui.Set('quickbar_lastid', lastid)
        current[n.id] = n
        settings.user.ui.Set('quickbar', current)
        if scatter:
            sm.ScatterEvent('OnMarketQuickbarChange', fromMarket=fromMarket)


class MarketActionWindow(uicontrols.Window):
    __guid__ = 'form.MarketActionWindow'
    default_windowID = 'marketbuyaction'

    def ApplyAttributes(self, attributes):
        uicontrols.Window.ApplyAttributes(self, attributes)
        self.clipChildren = 1
        self.scope = 'station_inflight'
        self.sr.currentOrder = None
        self.sr.stationID = None
        self.quantity = None
        self.remoteBuyLocation = None
        self.bestAskDict = {}
        self.bestMatchableAskDict = {}
        self.bestBidDict = {}
        self.durations = [[localization.GetByLabel('UI/Market/MarketQuote/Immediate'), 0],
         [localization.GetByLabel('UI/Common/DateWords/Day'), 1],
         [localization.GetByLabel('UI/Market/MarketQuote/ThreeDays'), 3],
         [localization.GetByLabel('UI/Common/DateWords/Week'), 7],
         [localization.GetByLabel('UI/Market/MarketQuote/TwoWeeks'), 14],
         [localization.GetByLabel('UI/Common/DateWords/Month'), 30],
         [localization.GetByLabel('UI/Market/MarketQuote/ThreeMonths'), 90]]
        self.ranges = [[localization.GetByLabel('UI/Common/LocationTypes/Station'), const.rangeStation],
         [localization.GetByLabel('UI/Common/LocationTypes/SolarSystem'), const.rangeSolarSystem],
         [localization.GetByLabel('UI/Common/LocationTypes/Region'), const.rangeRegion],
         [localization.GetByLabel('UI/Market/MarketQuote/NumberOfJumps', num=1), 1],
         [localization.GetByLabel('UI/Market/MarketQuote/NumberOfJumps', num=2), 2],
         [localization.GetByLabel('UI/Market/MarketQuote/NumberOfJumps', num=3), 3],
         [localization.GetByLabel('UI/Market/MarketQuote/NumberOfJumps', num=4), 4],
         [localization.GetByLabel('UI/Market/MarketQuote/NumberOfJumps', num=5), 5],
         [localization.GetByLabel('UI/Market/MarketQuote/NumberOfJumps', num=10), 10],
         [localization.GetByLabel('UI/Market/MarketQuote/NumberOfJumps', num=20), 20],
         [localization.GetByLabel('UI/Market/MarketQuote/NumberOfJumps', num=30), 30],
         [localization.GetByLabel('UI/Market/MarketQuote/NumberOfJumps', num=40), 40]]
        self.SetWndIcon()
        self.SetTopparentHeight(0)
        self.SetMinSize([480, 310], 1)
        self.NoSeeThrough()
        self.MakeUnResizeable()
        self.MakeUncollapseable()
        uiprimitives.Container(name='push', parent=self.sr.main, align=uiconst.TOTOP, height=const.defaultPadding)
        uiprimitives.Container(name='push', parent=self.sr.main, align=uiconst.TOLEFT, width=const.defaultPadding * 2)
        uiprimitives.Container(name='push', parent=self.sr.main, align=uiconst.TORIGHT, width=const.defaultPadding)
        self.bidprice = None
        self.qty = None
        self.min = None
        self.duration = None
        self.range = None
        self.useCorp = None

    def FlushMain(self, fromObject):
        uiutil.FlushList(self.sr.main.children[fromObject:])

    def LoadBuy_Detailed(self, typeID, order = None, duration = 1, locationID = None, forceRange = False, quantity = 1):
        settings.char.ui.Set('advancedBuyWnd', 1)
        self.remoteBuyLocation = None
        if locationID:
            self.remoteBuyLocation = locationID
            location = cfg.evelocations.Get(locationID)
        elif order:
            location = cfg.evelocations.Get(order.stationID)
        setattr(self, 'order', order)
        if location is None:
            return
        self.sr.stationID = location.locationID
        self.loading = 'buy'
        self.ready = False
        self.FlushMain(4)
        quote = sm.GetService('marketQuote')
        averagePrice = quote.GetAveragePrice(typeID)
        bestMatchableAsk = quote.GetBestAskInRange(typeID, self.sr.stationID, const.rangeStation, 1)
        if bestMatchableAsk:
            self.sr.hasMatch = True
        else:
            self.sr.hasMatch = False
        self.typeID = typeID
        self.DefineButtons(uiconst.OKCANCEL, okLabel=localization.GetByLabel('UI/Market/MarketQuote/CommandBuy'), okFunc=self.Buy, cancelFunc=self.Cancel)
        self.SetCaption(localization.GetByLabel('UI/Market/MarketQuote/BuyItem', typeID=typeID))
        self.AddSpace(where=self.sr.main)
        self.AddBigText(None, evetypes.GetName(typeID), typeID=typeID)
        self.sr.isBuy = True
        strippedName = uiutil.StripTags(location.name)
        fullName = location.name
        shortName = strippedName
        if len(shortName) > 64:
            shortName = shortName[:61] + '...'
        if fullName == strippedName:
            name = strippedName
        else:
            name = fullName.replace(strippedName, shortName)
        locationText = self.AddText(localization.GetByLabel('UI/Common/Location'), '&gt;&gt; <color=0xffffbb00>%s</color> &lt;&lt;' % name)
        lt = locationText.children[1]
        lt.GetMenu = self.GetLocationMenu
        lt.expandOnLeft = 1
        lt.hint = localization.GetByLabel('UI/Search/SelectStation')
        lt.height += 1
        self.AddSpace(where=self.sr.main)
        if order:
            price = self.bidprice if self.bidprice is not None else order.price
            self.AddEdit(localization.GetByLabel('UI/Market/MarketQuote/labelBidPrice'), price, floats=(0.01, 9223372036854.0, 2), refName='price', rightText='')
        else:
            if bestMatchableAsk:
                bestPrice = bestMatchableAsk.price
            else:
                bestPrice = averagePrice
            price = self.bidprice if self.bidprice is not None else bestPrice
            self.AddEdit(localization.GetByLabel('UI/Market/MarketQuote/labelBidPrice'), price, floats=(0.01, 9223372036854.0, 2), refName='price', rightText='')
        self.AddSpace(where=self.sr.main)
        self.AddText(localization.GetByLabel('UI/Market/MarketQuote/RegionalAdverage'), util.FmtISK(averagePrice), height=14)
        self.AddText(localization.GetByLabel('UI/Market/MarketQuote/BestRegional'), '', 'quoteText', height=14)
        self.AddText(localization.GetByLabel('UI/Market/MarketQuote/BestMatchable'), '', refName='matchText', height=14)
        self.AddSpace(where=self.sr.main)
        quantity = self.qty if self.qty is not None else quantity
        self.AddEdit(localization.GetByLabel('UI/Common/Quantity'), quantity, ints=(1, sys.maxint), refName='quantity', showMin=1)
        buySettings = settings.user.ui.Get('buydefault', {})
        if buySettings and buySettings.has_key('duration'):
            duration = buySettings['duration']
        limits = quote.GetSkillLimits(self.sr.stationID)
        dist = quote.GetStationDistance(self.sr.stationID)
        canRemoteTrade = False
        if dist <= limits['bid']:
            canRemoteTrade = True
        duration2 = self.duration if self.duration is not None else duration
        if canRemoteTrade:
            self.AddCombo(localization.GetByLabel('UI/Market/MarketQuote/Duration'), self.durations, duration2, 'duration', refName='duration')
        else:
            self.AddCombo(localization.GetByLabel('UI/Market/MarketQuote/Duration'), self.durations[0:1], 0, 'duration', refName='duration')
        ranges = self._GetAvailableRanges(canRemoteTrade, locationID, forceRange, limits, order)
        firstRange = const.rangeStation
        buySettings = settings.user.ui.Get('buydefault', {})
        if buySettings and buySettings.has_key('range'):
            firstRange = buySettings['range']
        range = self.range if self.range is not None else firstRange
        combo = self.AddCombo(localization.GetByLabel('UI/Common/Range'), ranges, range, 'duration', refName='range')
        self.OnComboChange(combo, localization.GetByLabel('UI/Common/LocationTypes/Station'), const.rangeStation)
        self.AddSpace(where=self.sr.main)
        self.AddText(localization.GetByLabel('UI/Market/MarketQuote/BrokersFee'), '-', 'fee')
        self.AddBigText(localization.GetByLabel('UI/Generic/Total'), '-', 'totalOrder')
        self.MakeCorpCheckboxMaybe()
        self.AddSpace(where=self.sr.main)
        cont = uiprimitives.Container(name='cont', parent=self.sr.main, align=uiconst.TOTOP, height=20)
        self.sr.rememberBuySettings = uicontrols.Checkbox(text=localization.GetByLabel('UI/Market/MarketQuote/RememberSettings'), parent=cont, configName='rememberBuySettings', retval=None, align=uiconst.TOPLEFT, pos=(0, 0, 350, 0))
        btn = uix.GetBigButton(32, self.sr.main, left=10, top=10, iconMargin=2)
        btn.OnClick = (self.ViewDetails, typeID)
        btn.hint = localization.GetByLabel('UI/Market/MarketQuote/hintClickForDetails')
        btn.SetAlign(uiconst.BOTTOMRIGHT)
        uiutil.SetOrder(btn, 0)
        btn.sr.icon.LoadIcon('res:/UI/Texture/WindowIcons/searchmarket.png')
        self.sr.currentOrder = order
        self.ready = True
        mainBtnPar = uiutil.GetChild(self, 'btnsmainparent')
        btn = uicontrols.Button(parent=mainBtnPar, label=localization.GetByLabel('UI/Market/MarketQuote/SimpleOrder'), func=self.GoPlaceBuyOrder, args=(typeID,
         order,
         1,
         locationID), align=uiconst.TOPRIGHT, pos=(5, 2, 0, 0), hint=localization.GetByLabel('Tooltips/Market/MarketBuySimpleButton'))
        self.UpdateTotals()

    def _GetAvailableRanges(self, canRemoteTrade, locationID, forceRange, limits, order):
        atSelectedLocation = session.stationid == locationID or session.structureid == locationID
        if atSelectedLocation:
            return self.ranges
        notDocked = session.stationid is None and session.structureid is None
        if order or notDocked or forceRange:
            ranges = [self.ranges[0]]
            if canRemoteTrade:
                for range in self.ranges[1:]:
                    if range[1] <= limits['vis'] or limits['vis'] > self.ranges[-1][1]:
                        ranges.append(range)

        else:
            ranges = self.ranges
        return ranges

    def MakeCorpCheckboxMaybe(self):
        if session.corprole & (const.corpRoleAccountant | const.corpRoleTrader):
            n = sm.GetService('corp').GetMyCorpAccountName()
            if n is not None:
                useCorpWallet = False
                buySettings = settings.user.ui.Get('buydefault', {})
                if buySettings and buySettings.has_key('useCorpWallet'):
                    useCorpWallet = buySettings['useCorpWallet']
                useCorpWallet2 = self.useCorp if self.useCorp is not None else useCorpWallet
                cont = uiprimitives.Container(name='cont', parent=self.sr.main, align=uiconst.TOTOP, height=20)
                self.sr.usecorp = uicontrols.Checkbox(text=localization.GetByLabel('UI/Market/MarketQuote/UseCorpAccount', accountName=n), parent=cont, configName='usecorp', retval=None, checked=useCorpWallet2, align=uiconst.TOPLEFT, pos=(0, 0, 350, 0))

    def TradeSimple(self, typeID = None, order = None, locationID = None, ignoreAdvanced = False, quantity = 1):
        if not ignoreAdvanced:
            settings.char.ui.Set('advancedBuyWnd', 0)
        self.remoteBuyLocation = None
        self.SetMinSize([400, 220], 1)
        quote = sm.GetService('marketQuote')
        averagePrice = quote.GetAveragePrice(typeID)
        marketRange = sm.GetService('marketutils').GetMarketRange()
        self.typeID = typeID
        if locationID:
            self.remoteBuyLocation = locationID
            location = cfg.evelocations.Get(locationID)
        elif order:
            location = cfg.evelocations.Get(order.stationID)
        if location is None:
            return
        self.sr.stationID = location.locationID
        if order is None and not eve.session.stationid:
            marketRange = const.rangeStation
            order = quote.GetBestAskInRange(typeID, self.sr.stationID, const.rangeStation, 1)
            if order:
                order.jumps = quote.GetStationDistance(self.sr.stationID, False)
        else:
            order = order or quote.GetBestAskInRange(typeID, self.sr.stationID, marketRange, 1)
        if order is not None:
            location = cfg.evelocations.Get(order.stationID)
            locationID = location.locationID
            self.remoteBuyLocation = locationID
            self.sr.stationID = locationID
        self.SetCaption(localization.GetByLabel('UI/Market/MarketQuote/BuyType', typeID=typeID))
        self.loading = 'buy'
        self.ready = False
        self.FlushMain(4)
        self.AddSpace(where=self.sr.main)
        self.AddBigText(None, evetypes.GetName(typeID), typeID=typeID)
        if order:
            locationText = self.AddText(localization.GetByLabel('UI/Common/Location'), '&gt;&gt; %s &lt;&lt;' % location.name)
            self.sr.isBuy = False
            lt = locationText.children[1]
            lt.GetMenu = self.GetLocationMenu
            lt.height += 1
            if session.stationid and order.stationID != session.stationid:
                if order.jumps == 0:
                    self.AddText(localization.GetByLabel('UI/Market/MarketQuote/headerWarrning'), localization.GetByLabel('UI/Market/MarketQuote/InDifferentStationInSystem'), color=(1.0, 0.0, 0.0, 1.0))
                else:
                    self.AddText(localization.GetByLabel('UI/Market/MarketQuote/headerWarrning'), localization.GetByLabel('UI/Market/MarketQuote/InDifferentStationInDifferntSystem', jumps=order.jumps), color=(1.0, 0.0, 0.0, 1.0))
            elif session.solarsystemid and order.jumps > 0:
                self.AddText(localization.GetByLabel('UI/Market/MarketQuote/headerWarrning'), localization.GetByLabel('UI/Market/MarketQuote/InDifferentStationInDifferntSystem', jumps=order.jumps), color=(1.0, 0.0, 0.0, 1.0))
        self.AddSpace(where=self.sr.main)
        if order:
            colors = ['<color=0xff00ff00>', '<color=0xffff5050>']
            if order.bid:
                colors.reverse()
            self.sr.percentage = (order.price - averagePrice) / averagePrice
            p = {'price': order.price,
             'percentage': round(100 * self.sr.percentage, 2),
             'aboveBelow': localization.GetByLabel('UI/Market/MarketQuote/PercentBelow') if order.price < averagePrice else localization.GetByLabel('UI/Market/MarketQuote/PercentAbove'),
             'colorFormat': colors[order.price >= averagePrice],
             'colorFormatEnd': '</color>'}
            self.AddText(localization.GetByLabel('UI/Market/MarketQuote/headerPrice'), localization.GetByLabel('UI/Market/MarketQuote/PriceDisplay', **p))
        else:
            msg = 'UI/Market/MarketQuote/NoOneIsSellingHere'
            p = {'typeID': typeID}
            if marketRange == const.rangeStation:
                p['location'] = localization.GetByLabel('UI/Common/LocationTypes/Station')
            elif marketRange == const.rangeSolarSystem:
                p['location'] = localization.GetByLabel('UI/Common/LocationTypes/SolarSystem')
            elif marketRange == const.rangeRegion:
                p['location'] = localization.GetByLabel('UI/Common/LocationTypes/Region')
            self.AddText('hide', localization.GetByLabel(msg, **p))
        if order:
            self.AddSpace(where=self.sr.main)
            editBox = self.AddEdit(localization.GetByLabel('UI/Common/Quantity'), quantity, ints=(1, order.volRemaining), refName='quantity', rightText=localization.GetByLabel('UI/Market/MarketQuote/SimpleOrderQuantity', qty=order.volRemaining), autoselect=True)
            uicore.registry.SetFocus(editBox)
        if order:
            self.AddBigText(localization.GetByLabel('UI/Generic/Total'), '-', 'totalOrder')
        if order:
            self.MakeCorpCheckboxMaybe()
        if order:
            self.DefineButtons(uiconst.OKCANCEL, okLabel=localization.GetByLabel('UI/Market/MarketQuote/CommandBuy'), okFunc=self.Buy, cancelFunc=self.Cancel)
        else:
            self.DefineButtons(uiconst.CLOSE)
        btn = uix.GetBigButton(32, self.sr.main, left=10, top=10, iconMargin=2)
        btn.OnClick = (self.ViewDetails, typeID)
        btn.hint = localization.GetByLabel('UI/Market/MarketQuote/hintClickForDetails')
        btn.SetAlign(uiconst.BOTTOMRIGHT)
        uiutil.SetOrder(btn, 0)
        btn.sr.icon.LoadIcon('res:/UI/Texture/WindowIcons/searchmarket.png')
        mainBtnPar = uiutil.GetChild(self, 'btnsmainparent')
        btn = uicontrols.Button(parent=mainBtnPar, label=localization.GetByLabel('UI/Market/MarketQuote/btnAdvancedOrder'), func=self.GoPlaceBuyOrder, args=(typeID,
         order,
         0,
         locationID), align=uiconst.TOPRIGHT, pos=(5, 2, 0, 0), hint=localization.GetByLabel('Tooltips/Market/MarketBuyAdvancedButton'))
        self.sr.currentOrder = order
        self.ready = True
        self.UpdateTotals()
        self.HideLoad()

    def GetLocationMenu(self):
        m = [(uiutil.MenuLabel('UI/Search/SelectStation'), self.SelectStation)]
        if self.sr.stationID:
            m += sm.GetService('menu').MapMenu([self.sr.stationID])
        return m

    def SelectStation(self):
        format = []
        format.append({'type': 'header',
         'text': localization.GetByLabel('UI/Market/MarketQuote/SelectStationForBuyOrder'),
         'frame': 1})
        format.append({'type': 'edit',
         'labelwidth': 60,
         'label': localization.GetByLabel('UI/Common/LocationTypes/Station'),
         'key': 'station',
         'required': 0,
         'frame': 1,
         'group': 'avail',
         'setvalue': '',
         'setfocus': 1})
        format.append({'type': 'btline'})
        format.append({'type': 'push'})
        left = uicore.desktop.width / 2 - 500 / 2
        top = uicore.desktop.height / 2 - 400 / 2
        retval = uix.HybridWnd(format, localization.GetByLabel('UI/Search/SelectStation'), 1, None, uiconst.OKCANCEL, [left, top], 300, 100, unresizeAble=1, icon='res:/UI/Texture/WindowIcons/searchmarket.png')
        if retval:
            name = retval['station']
            if name:
                stationID = uix.Search(name.lower(), const.groupStation, categoryID=const.categoryStructure, searchWndName='marketQuoteSelectStationSearch')
                if stationID:
                    retList = []
                    if not sm.GetService('marketQuote').CanTradeAtStation(self.sr.Get('isBuy', False), stationID, retList):
                        jumps = retList[0]
                        limit = retList[1]
                        if jumps == const.rangeRegion:
                            raise UserError('MktInvalidRegion')
                        else:
                            jumpText = localization.GetByLabel('UI/Market/MarketQuote/JumpDistance', jumps=jumps)
                            limitText = localization.GetByLabel('UI/Market/MarketQuote/JumpDistance', jumps=limit)
                            if limit >= 0:
                                raise UserError('MktCantSellItem2', {'numJumps': jumps,
                                 'jumpText1': jumpText,
                                 'numLimit': limit,
                                 'jumpText2': limitText})
                            else:
                                raise UserError('MktCantSellItemOutsideStation', {'numJumps': jumps,
                                 'jumpText': jumpText})
                    if self.sr.Get('price'):
                        self.bidprice = self.sr.price.GetValue()
                    if self.sr.Get('quantity'):
                        self.qty = self.sr.quantity.GetValue()
                    if self.sr.Get('duration'):
                        self.duration = self.sr.duration.GetValue()
                    if self.sr.Get('range'):
                        self.range = self.sr.range.GetValue()
                    if self.sr.Get('quantityMin', None):
                        self.min = self.sr.quantityMin.GetValue()
                    if util.GetAttrs(self, 'sr', 'usecorp') is not None:
                        self.useCorp = self.sr.usecorp.GetValue()
                    else:
                        self.useCorp = False
                    self.LoadBuy_Detailed(self.typeID, order=getattr(self, 'order', None), locationID=stationID, forceRange=True)

    def RemeberBuySettings(self, *args):
        duration = 0
        if not self.destroyed and hasattr(self, 'sr') and self.sr.Get('duration') and not self.sr.duration.destroyed:
            duration = long(self.sr.duration.GetValue())
        useCorp = 0
        if not self.destroyed and hasattr(self, 'sr') and self.sr.Get('usecorp') and not self.sr.usecorp.destroyed:
            useCorp = self.sr.usecorp.GetValue()
        range = const.rangeStation
        if not self.destroyed and hasattr(self, 'sr') and self.sr.Get('range') and not self.sr.range.destroyed:
            range = self.sr.range.GetValue()
        settings.user.ui.Set('buydefault', {'duration': duration,
         'useCorpWallet': useCorp,
         'range': range})

    def RemeberSellSettings(self, *args):
        duration = 0
        if not self.destroyed and hasattr(self, 'sr') and self.sr.Get('duration') and not self.sr.duration.destroyed:
            duration = long(self.sr.duration.GetValue())
        useCorp = 0
        if not self.destroyed and hasattr(self, 'sr') and self.sr.Get('usecorp') and not self.sr.usecorp.destroyed:
            useCorp = self.sr.usecorp.GetValue()
        settings.user.ui.Set('selldefault', {'duration': duration,
         'useCorpWallet': useCorp})

    def ViewDetails(self, typeID, simple = 0, *args):
        uthread.new(self.ViewDetails_, typeID, simple)

    def ViewDetails_(self, typeID, simple = 0, *args):
        sm.GetService('marketutils').ShowMarketDetails(typeID, None)
        uiutil.SetOrder(self, 0)

    def GoPlaceSellOrder(self, invItem, simple = 0, *args):
        settings.char.ui.Set('advancedSellWnd', not simple)
        uthread.new(sm.GetService('marketutils').Sell, invItem.typeID, invItem, not simple)
        self.Close()

    def GoPlaceBuyOrder(self, typeID, order = None, simple = 0, prePickedLocationID = None, *args):
        settings.char.ui.Set('advancedBuyWnd', not simple)
        uthread.new(sm.GetService('marketutils').Buy, typeID, order=order, placeOrder=not simple, prePickedLocationID=prePickedLocationID)
        self.Close()

    def LoadModify(self, order):
        if order is None:
            return
        self.loading = 'modify'
        self.ready = False
        self.FlushMain(3)
        self.ShowLoad()
        self.sr.stationID = order.stationID
        self.typeID = order.typeID
        location = cfg.evelocations.Get(order.stationID)
        self.DefineButtons(uiconst.OKCANCEL, okFunc=self.Modify, cancelFunc=self.Cancel)
        self.SetCaption(localization.GetByLabel('UI/Market/MarketQuote/labelModifyOrder'))
        self.AddText(localization.GetByLabel('UI/Common/Type'), evetypes.GetName(self.typeID))
        self.AddText(localization.GetByLabel('UI/Common/Location'), location.name)
        uiprimitives.Container(name='push', parent=self.sr.main, align=uiconst.TOTOP, height=const.defaultPadding)
        self.AddText([localization.GetByLabel('UI/Market/MarketQuote/labelOldSellPrice'), localization.GetByLabel('UI/Market/MarketQuote/labelOldBuyPrice')][order.bid], util.FmtISK(order.price))
        self.AddText(localization.GetByLabel('UI/Market/MarketQuote/labelQuantityRemaining'), util.FmtAmt(order.volRemaining))
        self.quantity = order.volRemaining
        edit = self.AddEdit([localization.GetByLabel('UI/Market/MarketQuote/NewSellPrice'), localization.GetByLabel('UI/Market/MarketQuote/NewBuyPrice')][order.bid], '%.2f' % order.price, floats=(0.01, 9223372036854.0, 2), refName='price', rightText='', autoselect=True)
        uicore.registry.SetFocus(edit)
        uiprimitives.Container(name='push', parent=self.sr.main, align=uiconst.TOTOP, height=const.defaultPadding)
        self.AddText(localization.GetByLabel('UI/Market/MarketQuote/labelTotalChange'), '-', 'totalOrder')
        self.AddText(localization.GetByLabel('UI/Market/MarketQuote/BrokersFee'), '-', 'fee')
        btn = uix.GetBigButton(32, self.sr.main, left=10, top=10, iconMargin=2)
        btn.OnClick = (self.ViewDetails, order.typeID)
        btn.hint = localization.GetByLabel('UI/Market/MarketQuote/hintClickForDetails')
        btn.SetAlign(uiconst.BOTTOMRIGHT)
        uiutil.SetOrder(btn, 0)
        btn.sr.icon.LoadIcon('res:/UI/Texture/WindowIcons/searchmarket.png')
        self.sr.currentOrder = order
        self.ready = True
        self.UpdateTotals()
        self.HideLoad()

    def AddSpace(self, where, height = 6):
        uiprimitives.Container(name='space', parent=where, height=height, align=uiconst.TOTOP)

    def Cancel(self, *args):
        self.Close()

    def Modify(self, *args):
        if self.sr.currentOrder is None:
            return
        price = self.sr.price.GetValue()
        order = self.sr.currentOrder
        if self.sr.percentage < -0.5 or self.sr.percentage > 1.0:
            percentage = round(100 * abs(self.sr.percentage), 2)
            label = 'UI/Market/MarketQuote/PercentAboveWithQuantity'
            if self.sr.percentage < 0.0:
                label = 'UI/Market/MarketQuote/PercentBelowWithQuantity'
            ret = eve.Message('MktConfirmTrade', {'amount': localization.GetByLabel(label, amount=percentage)}, uiconst.YESNO, default=uiconst.ID_NO)
            if ret != uiconst.ID_YES:
                return
        self.Close()
        sm.GetService('marketQuote').ModifyOrder(order, price)

    def Buy(self, *args):
        if self.typeID is None:
            return
        typeID = self.typeID
        quantity = self.sr.quantity.GetValue()
        duration = 0
        brokersFee = 0
        if self.sr.Get('fee') and not self.sr.fee.destroyed and self.sr.fee.text != '-' and eve.Message('ConfirmMarketOrder', {'isk': self.sr.fee.text}, uiconst.YESNO, suppress=uiconst.ID_YES) != uiconst.ID_YES:
            return
        if self.sr.Get('price') and not self.sr.price.destroyed:
            price = self.sr.price.GetValue()
        elif self.sr.currentOrder is not None:
            price = self.sr.currentOrder.price
        if self.sr.Get('duration') and not self.sr.duration.destroyed:
            duration = self.sr.duration.GetValue()
        orderRange = const.rangeStation
        if self.sr.Get('range') and not self.sr.range.destroyed:
            orderRange = self.sr.range.GetValue()
        if self.remoteBuyLocation or not eve.session.stationid:
            stationID = self.remoteBuyLocation
        else:
            stationID = self.sr.currentOrder.stationID
        minVolume = 1
        if self.sr.Get('quantityMin', None) and not self.sr.quantityMin.destroyed:
            minVolume = self.sr.quantityMin.GetValue()
        if util.GetAttrs(self, 'sr', 'usecorp') is not None and not self.sr.usecorp.destroyed:
            useCorp = self.sr.usecorp.GetValue()
        else:
            useCorp = False
        if self.sr.percentage > 1.0:
            amount = round(100 * abs(self.sr.percentage), 2)
            ret = eve.Message('MktConfirmTrade', {'amount': localization.GetByLabel('UI/Market/MarketQuote/PercentAboveWithQuantity', amount=amount)}, uiconst.YESNO, default=uiconst.ID_NO)
            if ret != uiconst.ID_YES:
                return
        if self.sr.Get('rememberBuySettings') and not self.sr.rememberBuySettings.destroyed and self.sr.rememberBuySettings.checked:
            self.RemeberBuySettings()
        self.Close()
        sm.GetService('marketQuote').BuyStuff(stationID, typeID, price, quantity, orderRange, minVolume, duration, useCorp)

    def AddText(self, label, text, refName = None, height = 20, color = None):
        par = uiprimitives.Container(name='text', parent=self.sr.main, align=uiconst.TOTOP, height=height)
        left = LABELWIDTH
        if label == 'hide':
            left = 0
        elif label:
            uicontrols.EveLabelSmall(text=label, parent=par, width=LABELWIDTH, left=0, top=6, color=color, state=uiconst.UI_NORMAL)
        t = uicontrols.EveLabelMedium(text=text, parent=par, width=self.Width() - LABELWIDTH - 16, left=left, top=4, color=color, state=uiconst.UI_NORMAL)
        par.height = max(20, t.textheight)
        if refName:
            setattr(self.sr, refName, t)
        return par

    def AddBigText(self, label, text, refName = None, height = 28, typeID = None):
        par = uiprimitives.Container(name='text', parent=self.sr.main, align=uiconst.TOTOP, height=height)
        left = 0
        if label:
            uicontrols.EveLabelSmall(text=label, parent=par, width=LABELWIDTH, left=0, top=13, color=None, state=uiconst.UI_NORMAL)
            left = LABELWIDTH
        offset = 0
        if typeID:
            offset = 36
            icon = uicontrols.Icon(parent=par, pos=(left,
             -4,
             32,
             32), typeID=typeID, align=uiconst.TOPLEFT)
            icon.SetSize(32, 32)
        t = uicontrols.EveCaptionMedium(text=text, parent=par, align=uiconst.TOTOP, width=self.Width() - left + offset - 16, padLeft=left + offset)
        if refName:
            setattr(self.sr, refName, t)
        par.height = t.textheight + 4

    def AddEdit(self, label, setvalue, ints = None, floats = None, width = 95, showMin = 0, refName = None, rightText = None, left = LABELWIDTH, autoselect = False):
        minHeight = 20
        parent = uiprimitives.Container(name=label, parent=self.sr.main, height=20, align=uiconst.TOTOP)
        edit = uicontrols.SinglelineEdit(name=label, parent=parent, pos=(LABELWIDTH,
         1,
         width,
         0), align=uiconst.TOPLEFT, autoselect=autoselect)
        if refName == 'quantity':
            edit.OnChange = self.OnChanged_quantity
        else:
            edit.OnChange = self.OnEditChange
        edit.OnFocusLost = self.OnEditChange
        if ints:
            edit.IntMode(*ints)
            edit.AutoFitToText(util.FmtAmt(ints[1]), minWidth=width)
        elif floats:
            edit.FloatMode(*floats)
            edit.AutoFitToText(util.FmtAmt(floats[1], showFraction=floats[2]), minWidth=width)
        if showMin:
            min = 1
            if refName == 'quantity':
                min = self.min if self.min is not None else min
            minLabel = uicontrols.EveLabelSmall(text=localization.GetByLabel('UI/Generic/Minimum'), parent=parent, left=edit.left + edit.width + 6, align=uiconst.CENTERLEFT, state=uiconst.UI_NORMAL)
            minedit = uicontrols.SinglelineEdit(name=label, parent=parent, setvalue=min, ints=(1, sys.maxint), width=40, left=minLabel.left + minLabel.width + 6, top=1, align=uiconst.TOPLEFT)
            minedit.OnChange = self.OnEditChange
            minedit.AutoFitToText(util.FmtAmt(sys.maxint), minWidth=40)
            if refName:
                setattr(self.sr, refName + 'Min', minedit)
        if setvalue:
            edit.SetValue(setvalue)
        _label = uicontrols.EveLabelSmall(text=label, parent=parent, width=LABELWIDTH, left=0, top=[6, -1][label.find('<br>') >= 0], state=uiconst.UI_NORMAL)
        if rightText is not None:
            rightTextLeft = edit.left + edit.width + 6
            _rightText = uicontrols.EveLabelMedium(text=rightText, parent=parent, width=self.Width() - rightTextLeft - 6, left=rightTextLeft, top=4, state=uiconst.UI_NORMAL)
            minHeight = max(minHeight, _rightText.textheight + 8)
            if refName:
                setattr(self.sr, refName + '_rightText', _rightText)
            parent.height = minHeight
        if refName:
            setattr(self.sr, refName, edit)
        return edit

    def AddCombo(self, label, options, setvalue, configname, width = 95, refName = None):
        parent = uiprimitives.Container(name=configname, parent=self.sr.main, height=20, align=uiconst.TOTOP)
        combo = uicontrols.Combo(label='', parent=parent, options=options, name=configname, callback=self.OnComboChange, width=width, pos=(LABELWIDTH,
         2,
         0,
         0))
        _label = uicontrols.EveLabelSmall(text=label, parent=parent, width=LABELWIDTH, left=0, top=[7, -1][label.find('<br>') >= 0], state=uiconst.UI_NORMAL)
        combo.sr.label = _label
        if setvalue is not None:
            combo.SelectItemByValue(setvalue)
        if refName:
            setattr(self.sr, refName, combo)
        return combo

    def OnChanged_quantity(self, quantity):
        if not self.ready:
            return
        uthread.pool('MarketActionWindow::OnChanged_quantity', self.OnChanged_quantityThread, quantity)

    def OnChanged_quantityThread(self, quantity):
        try:
            self.UpdateTotals()
        except:
            log.LogException()
            sys.exc_clear()

    def OnEditChange(self, *args):
        if not self or self.destroyed:
            return
        uthread.pool('MarketActionWindow::OnEditChange', self.OnEditChangeThread, *args)

    def OnEditChangeThread(self, *args):
        self.UpdateTotals()

    def OnComboChange(self, combo, header, value, *args):
        uthread.pool('MarketActionWindow::OnComboChange', self.OnComboChangeThread, combo, header, value, *args)

    def OnComboChangeThread(self, combo, header, value, *args):
        self.UpdateTotals()

    def UpdateTotals(self):
        if self.destroyed:
            return
        if not self.ready:
            return
        if not self.typeID:
            return
        if not hasattr(self, 'sr'):
            return
        quote = sm.GetService('marketQuote')
        limits = quote.GetSkillLimits(self.sr.stationID)
        averagePrice = quote.GetAveragePrice(self.typeID)
        colors = ['<color=0xff00ff00>', '<color=0xffff5050>']
        if not self or self.destroyed or not hasattr(self, 'sr'):
            return
        self.sr.percentage = 0
        price = 0
        duration = 0
        if not self.destroyed and hasattr(self, 'sr') and self.sr.Get('duration') and not self.sr.duration.destroyed:
            duration = long(self.sr.duration.GetValue())
        if not self.destroyed and hasattr(self, 'sr') and self.sr.Get('price') and not self.sr.price.destroyed:
            price = self.sr.price.GetValue()
        elif self.sr.currentOrder is not None:
            price = self.sr.currentOrder.price
        if self.loading == 'modify':
            quantity = self.sr.currentOrder.volRemaining
        else:
            quantity = 1
            if not self.destroyed and hasattr(self, 'sr') and self.sr.Get('quantity') and not self.sr.quantity.destroyed:
                quantity = self.sr.quantity.GetValue(refreshDigits=0) or 0
            elif self.sr.currentOrder is not None:
                quantity = self.sr.currentOrder.volRemaining
        quantity = max(1, quantity)
        quantityMin = 1
        if not self.destroyed and hasattr(self, 'sr') and self.sr.Get('quantityMin') and not self.sr.quantityMin.destroyed:
            quantityMin = self.sr.quantityMin.GetValue()
        range = const.rangeStation
        if not self.destroyed and hasattr(self, 'sr') and self.sr.Get('range') and not self.sr.range.destroyed:
            range = self.sr.range.GetValue()
        fee = 0.0
        if not self.destroyed and hasattr(self, 'sr') and self.sr.Get('fee') and not self.sr.fee.destroyed:
            if duration > 0:
                _fee = quote.BrokersFee(self.sr.stationID, price * quantity, limits.GetBrokersFeeForLocation(self.sr.stationID))
                fee = _fee.amt
                if _fee.percentage < 0:
                    p = localization.GetByLabel('UI/Generic/Minimum')
                else:
                    p = '%s%%' % round(_fee.percentage * 100, 2)
                self.sr.fee.text = localization.GetByLabel('UI/Market/MarketQuote/MarketFee', percentage=p, price=fee)
            else:
                self.sr.fee.text = '-'
            self.CheckHeights(self.sr.fee, 'fee')
        tax = 0.0
        if not self.destroyed and hasattr(self, 'sr') and self.sr.Get('transactionTax') and not self.sr.transactionTax.destroyed:
            tax = price * quantity * limits['acc']
            self.sr.transactionTax.text = localization.GetByLabel('UI/Market/MarketQuote/MarketTax', percentage=limits['acc'] * 100.0, price=tax)
            self.CheckHeights(self.sr.transactionTax, 'transactionTax')
        if not self.destroyed and hasattr(self, 'sr') and self.sr.Get('totalOrder') and not self.sr.totalOrder.destroyed:
            if self.loading == 'buy':
                sumTotal = -price * quantity
            else:
                sumTotal = price * quantity
            color = 'green'
            if sumTotal - tax - fee < 0.0:
                if sm.GetService('experimentClientSvc').IsMinorImprovementsEnabled():
                    color = 'white'
                else:
                    color = 'red'
            self.sr.totalOrder.text = '<color=%s>' % color + util.FmtISK(abs(sumTotal - tax - fee))
            self.CheckHeights(self.sr.totalOrder, 'totalOrder')
        if self.loading == 'buy':
            colors.reverse()
            if not self.destroyed and hasattr(self, 'sr') and self.sr.Get('matchText') and not self.sr.matchText.destroyed:
                bestMatchableAskKey = (self.typeID,
                 self.sr.stationID,
                 const.rangeRegion,
                 quantityMin)
                bestMatchableAsk = self.bestMatchableAskDict.get(bestMatchableAskKey, -1)
                if bestMatchableAsk == -1:
                    bestMatchableAsk = quote.GetBestAskInRange(self.typeID, self.sr.stationID, range, amount=quantityMin)
                    self.ManageBestMatchableAskDict(key=bestMatchableAskKey, value=bestMatchableAsk)
                if bestMatchableAsk:
                    jumps = int(bestMatchableAsk.jumps)
                    if jumps == 0 and bestMatchableAsk.stationID == self.sr.stationID:
                        jumps = localization.GetByLabel('UI/Market/MarketQuote/InSameStation')
                    else:
                        jumps = localization.GetByLabel('UI/Market/MarketQuote/JumpsAway', jumps=jumps)
                    p = {'price': bestMatchableAsk.price,
                     'percentage': round(100 * (bestMatchableAsk.price - averagePrice) / averagePrice, 2),
                     'aboveBelow': localization.GetByLabel('UI/Market/MarketQuote/PercentBelow') if bestMatchableAsk.price < averagePrice else localization.GetByLabel('UI/Market/MarketQuote/PercentAbove'),
                     'volRemaining': int(bestMatchableAsk.volRemaining),
                     'jumps': jumps}
                    matchText = localization.GetByLabel('UI/Market/MarketQuote/BestAskDisplay', **p)
                else:
                    matchText = localization.GetByLabel('UI/Market/MarketQuote/NoMatchesAsk')
                self.sr.matchText.text = matchText
                self.CheckHeights(self.sr.matchText, 'matchText')
            if not self.destroyed and hasattr(self, 'sr') and self.sr.Get('quoteText') and not self.sr.quoteText.destroyed:
                bestAskKey = (self.typeID, self.sr.stationID, const.rangeRegion)
                bestAsk = self.bestAskDict.get(bestAskKey, -1)
                if bestAsk == -1:
                    bestAsk = quote.GetBestAskInRange(self.typeID, self.sr.stationID, const.rangeRegion)
                    self.bestAskDict[bestAskKey] = bestAsk
                if bestAsk:
                    jumps = int(bestAsk.jumps)
                    if jumps == 0 and bestAsk.stationID == self.sr.stationID:
                        jumps = localization.GetByLabel('UI/Market/MarketQuote/InSameStation')
                    else:
                        jumps = localization.GetByLabel('UI/Market/MarketQuote/JumpsAway', jumps=jumps)
                    p = {'price': bestAsk.price,
                     'percentage': round(100 * (bestAsk.price - averagePrice) / averagePrice, 2),
                     'aboveBelow': localization.GetByLabel('UI/Market/MarketQuote/PercentBelow') if bestAsk.price < averagePrice else localization.GetByLabel('UI/Market/MarketQuote/PercentAbove'),
                     'volRemaining': int(bestAsk.volRemaining),
                     'jumps': jumps}
                    quoteText = localization.GetByLabel('UI/Market/MarketQuote/BestAskDisplay', **p)
                else:
                    quoteText = localization.GetByLabel('UI/Market/MarketQuote/NoMatchesAsk')
                self.sr.quoteText.text = quoteText
                self.CheckHeights(self.sr.quoteText, 'quoteText')
            self.sr.percentage = (price - averagePrice) / averagePrice
            if not self.destroyed and hasattr(self, 'sr') and self.sr.Get('price_rightText') and not self.sr.price_rightText.destroyed:
                bestMatchText = sm.GetService('marketutils').GetBestMatchText(price, averagePrice, self.sr.percentage)
                self.sr.price_rightText.text = bestMatchText
                self.CheckHeights(self.sr.price_rightText, 'price_rightText')
        elif self.loading == 'sell':
            log.LogException('TRYING TO USE OLD SELL WINDOW!!!')
        elif self.loading == 'modify':
            if self.sr.currentOrder.bid:
                colors.reverse()
            oldPrice = self.sr.currentOrder.price
            self.sr.totalOrder.text = util.FmtISK((price - oldPrice) * quantity)
            self.CheckHeights(self.sr.totalOrder, 'totalOrder')
            if price - oldPrice < 0:
                self.sr.fee.text = util.FmtISK(const.mktMinimumFee)
            else:
                brokersFee = quote.BrokersFee(self.sr.stationID, (price - oldPrice) * quantity, limits.GetBrokersFeeForLocation(self.sr.currentOrder.stationID)).amt
                self.sr.fee.text = util.FmtISK(max(const.mktMinimumFee, brokersFee))
            self.CheckHeights(self.sr.fee, 'fee')
            if not self.destroyed and hasattr(self, 'sr') and self.sr.Get('price_rightText') and not self.sr.price_rightText.destroyed:
                self.sr.percentage = (price - averagePrice) / averagePrice
                p = {'colorText': colors[price < averagePrice],
                 'percentage': round(100 * self.sr.percentage, 2),
                 'aboveBelow': localization.GetByLabel('UI/Market/MarketQuote/PercentAbove')}
                if price < averagePrice:
                    p['aboveBelow'] = localization.GetByLabel('UI/Market/MarketQuote/PercentBelow')
                self.sr.price_rightText.text = localization.GetByLabel('UI/Market/MarketQuote/MarketModifyPrice', **p)
                self.CheckHeights(self.sr.price_rightText, 'price_rightText')

    def ManageBestMatchableAskDict(self, key, value):
        if len(self.bestMatchableAskDict) > 15:
            self.bestMatchableAskDict = {}
        else:
            self.bestMatchableAskDict[key] = value

    def CheckHeights(self, t, what = None):
        t.parent.height = t.textheight + t.top * 2
        theight = sum([ each.height for each in t.parent.parent.children if each.align == uiconst.TOTOP ])
        self.SetMinSize([self.width, theight + 56], 1)
