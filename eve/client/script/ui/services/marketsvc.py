#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\services\marketsvc.py
import functools
import itertools
import evetypes
import marketutil
import structures
from eve.common.script.sys.idCheckers import IsStation
from service import *
import util
import blue
import dbutil
import uiutil
import localization
import facwarCommon
import const
CACHE_INTERVAL = 300
jumpsPerSkillLevel = {0: -1,
 1: 0,
 2: 5,
 3: 10,
 4: 20,
 5: 50}

def SortAsks(x, y, headers):
    priceIdx = headers.index('price')
    if x[priceIdx] < y[priceIdx]:
        return -1
    elif x[priceIdx] > y[priceIdx]:
        return 1
    issuedIdx = headers.index('issueDate')
    if x[issuedIdx] < y[issuedIdx]:
        return -1
    elif x[issuedIdx] > y[issuedIdx]:
        return 1
    jmpIdx = headers.index('jumps')
    if x[jmpIdx] < y[jmpIdx]:
        return -1
    elif x[jmpIdx] > y[jmpIdx]:
        return 1
    orderIdx = headers.index('orderID')
    if x[orderIdx] < y[orderIdx]:
        return -1
    else:
        return 1


def SortBids(x, y, headers):
    priceIdx = headers.index('price')
    if x[priceIdx] < y[priceIdx]:
        return 1
    elif x[priceIdx] > y[priceIdx]:
        return -1
    issuedIdx = headers.index('issueDate')
    if x[issuedIdx] < y[issuedIdx]:
        return -1
    elif x[issuedIdx] > y[issuedIdx]:
        return 1
    jmpIdx = headers.index('jumps')
    rngIdx = headers.index('range')
    if x[jmpIdx] - max(0, x[rngIdx]) < y[jmpIdx] - max(0, y[rngIdx]):
        return -1
    elif x[jmpIdx] - x[rngIdx] > y[jmpIdx] - y[rngIdx]:
        return 1
    orderIdx = headers.index('orderID')
    if x[orderIdx] < y[orderIdx]:
        return -1
    else:
        return 1


class MarketQuote(Service):
    __exportedcalls__ = {'GetMyOrders': [ROLE_ANY],
     'GetCorporationOrders': [ROLE_ANY],
     'PlaceOrder': [ROLE_ANY],
     'BuyStuff': [ROLE_ANY],
     'SellMulti': [ROLE_ANY],
     'CancelOrder': [ROLE_ANY],
     'ModifyOrder': [ROLE_ANY],
     'GetSkillLimits': [ROLE_ANY],
     'BrokersFee': [ROLE_ANY],
     'GetPriceHistory': [ROLE_ANY],
     'GetAveragePrice': [ROLE_ANY],
     'GetStationAsks': [ROLE_ANY],
     'GetSystemAsks': [ROLE_ANY],
     'GetOrders': [ROLE_ANY],
     'GetOrder': [ROLE_ANY],
     'GetRegionBest': [ROLE_ANY],
     'RefreshAll': [ROLE_ANY],
     'ClearAll': [ROLE_ANY],
     'GetStationDistance': [ROLE_ANY],
     'CanTradeAtStation': [ROLE_ANY],
     'GetBestMatchableBid': [ROLE_ANY],
     'GetBestBid': [ROLE_ANY],
     'GetBestAverageAsk': [ROLE_ANY],
     'GetBestAskInRange': [ROLE_ANY],
     'GetBestBidInRange': [ROLE_ANY],
     'DumpQuotes': [ROLE_ANY],
     'DumpOrdersForType': [ROLE_ANY],
     'GetMarketProxy': []}
    __guid__ = 'svc.marketQuote'
    __servicename__ = 'marketquote'
    __displayname__ = 'Market Quote Service'
    __notifyevents__ = ['OnSessionChanged', 'OnSkillsChanged', 'OnOwnOrdersChanged']
    __dependencies__ = ['clientPathfinderService']
    __update_on_reload__ = 1

    def Run(self, ms):
        self.groupsQuotes = {}
        self.lastGotGroupsQuotes = {}
        self.lastGotGroupQuotes = {}
        self.groupQuotes = {}
        self.waitingFor = {}
        self.locks = {}
        self.orderCache = {}
        sm.FavourMe(self.OnOwnOrdersChanged)

    def OnOwnOrdersChanged(self, orders, reason, isCorp):
        sm.services['objectCaching'].InvalidateCachedMethodCall('marketProxy', 'GetCharOrders')
        if orders is not None:
            for order in orders:
                sm.services['objectCaching'].InvalidateCachedMethodCall('marketProxy', 'GetOrders', order.typeID)

        sm.services['objectCaching'].InvalidateCachedMethodCall('marketProxy', 'GetSystemAsks')
        sm.services['objectCaching'].InvalidateCachedMethodCall('marketProxy', 'GetStationAsks')

    def OnSkillsChanged(self, skillInfos):
        typeIDs = {const.typeRetail,
         const.typeTrade,
         const.typeWholesale,
         const.typeAccounting,
         const.typeBrokerRelations,
         const.typeTycoon,
         const.typeMarketing,
         const.typeProcurement,
         const.typeVisibility,
         const.typeDaytrading,
         const.typeMarginTrading}
        if len(typeIDs.intersection([ k for k in skillInfos.iterkeys() ])):
            sm.services['objectCaching'].InvalidateCachedMethodCall('marketProxy', 'GetCharSkillLimits')

    def OnSessionChanged(self, isRemote, session, change):
        if 'regionid' in change:
            self.LogInfo('MarketSvc: Region change, clearing internal cache')
            self.ClearAll()

    def BrokersFee(self, stationID, amount, commissionPercentage):
        if amount < 0.0:
            raise AttributeError('Amount must be positive')
        orderValue = float(amount)
        station = sm.GetService('ui').GetStation(stationID)
        stationOwnerID = None
        if station is not None:
            stationOwnerID = station.ownerID
        factionChar = 0
        corpChar = 0
        if stationOwnerID:
            if util.IsNPC(stationOwnerID):
                factionID = sm.GetService('faction').GetFaction(stationOwnerID)
                factionChar = sm.GetService('standing').GetStanding(factionID, eve.session.charid) or 0.0
            corpChar = sm.GetService('standing').GetStanding(stationOwnerID, eve.session.charid) or 0.0
        commissionPercentage = commissionPercentage - factionChar * 0.0003 - corpChar * 0.0002
        tax = util.KeyVal()
        tax.amt = commissionPercentage * orderValue
        tax.percentage = commissionPercentage
        if tax.amt <= const.mktMinimumFee:
            tax.amt = const.mktMinimumFee
            tax.percentage = -1.0
        return tax

    def CanTradeAtStation(self, bid, stationID, retList = None):
        limits = self.GetSkillLimits(stationID)
        if bid:
            jumps = self.GetStationDistance(stationID)
            if retList is not None:
                retList.append(jumps)
                retList.append(limits['bid'])
            if jumps <= limits['bid']:
                return True
        else:
            jumps = self.GetStationDistance(stationID)
            if retList is not None:
                retList.append(jumps)
                retList.append(limits['ask'])
            if jumps <= limits['ask']:
                return True
        return False

    def GetStationDistance(self, stationID, getFastestRoute = True):
        if stationID in (session.stationid, session.structureid):
            return -1
        solarSystemID = self.GetSolarSystemForMarketLocation(stationID)
        regionID = sm.GetService('map').GetRegionForSolarSystem(solarSystemID)
        if regionID != session.regionid:
            return const.rangeRegion
        if getFastestRoute:
            jumps = self.clientPathfinderService.GetJumpCountFromCurrent(solarSystemID)
        else:
            jumps = self.clientPathfinderService.GetAutopilotJumpCount(session.solarsystemid2, solarSystemID)
        if jumps >= 1:
            return jumps
        return 0

    def GetRegionBest(self):
        return self.GetMarketProxy().GetRegionBest()

    def GetBaseTax(self, stationID):
        if IsStation(stationID):
            return const.marketCommissionPercentage
        else:
            return self.GetMarketTaxAtStructure(stationID)

    @util.Memoized(2)
    def GetMarketTaxAtStructure(self, structureID):
        return sm.RemoteSvc('structureSettings').CharacterGetSetting(structureID, structures.SETTING_MARKET_TAX)

    def GetSkillLimits(self, stationID):
        return marketutil.GetSkillLimits(lambda : self.GetBaseTax(stationID), lambda typeIDs: self.GetMarketSkills(), self.GetBaseTax, IsStation(stationID))

    def GetMarketSkills(self):
        myskills = sm.GetService('skills').MySkillLevelsByID()
        skillLevels = util.KeyVal()
        skillLevels.retail = myskills.get(const.typeRetail, 0)
        skillLevels.trade = myskills.get(const.typeTrade, 0)
        skillLevels.wholeSale = myskills.get(const.typeWholesale, 0)
        skillLevels.accounting = myskills.get(const.typeAccounting, 0)
        skillLevels.broker = myskills.get(const.typeBrokerRelations, 0)
        skillLevels.tycoon = myskills.get(const.typeTycoon, 0)
        skillLevels.margin = myskills.get(const.typeMarginTrading, 0)
        skillLevels.marketing = myskills.get(const.typeMarketing, 0)
        skillLevels.procurement = myskills.get(const.typeProcurement, 0)
        skillLevels.visibility = myskills.get(const.typeVisibility, 0)
        skillLevels.daytrading = myskills.get(const.typeDaytrading, 0)
        return skillLevels

    def GetMarketProxy(self):
        return sm.ProxySvc('marketProxy')

    def BuyStuff(self, stationID, typeID, price, quantity, orderRange = None, minVolume = 1, duration = 0, useCorp = False):
        if orderRange is None:
            orderRange = const.rangeStation
        self.PlaceOrder(stationID, typeID, price, quantity, 1, orderRange, None, minVolume, duration, useCorp)

    def BuyMulti(self, stationID, itemList, useCorp):
        ordersCreated = self.GetMarketProxy().BuyMultipleItems(stationID, itemList, useCorp)
        return ordersCreated

    def SellMulti(self, itemList, useCorp, duration):
        self.GetMarketProxy().PlaceMultiSellOrder(itemList, useCorp, duration)

    def PlaceOrder(self, stationID, typeID, price, quantity, bid, orderRange, itemID = None, minVolume = 1, duration = 14, useCorp = False, located = None):
        price = round(price, 2)
        if price > 9223372036854.0:
            raise ValueError('Price can not exceed %s', 9223372036854.0)
        if quantity < 0:
            raise UserError('RepackageBeforeSelling', {'item': typeID})
        self.GetMarketProxy().PlaceBuyOrder(int(stationID), int(typeID), round(float(price), 2), int(quantity), int(orderRange), itemID, int(minVolume), int(duration), useCorp, located)

    def CancelOrder(self, orderID, regionID):
        self.GetMarketProxy().CancelCharOrder(orderID, regionID)

    def ModifyOrder(self, order, newPrice):
        if newPrice > 9223372036854.0:
            raise ValueError('Price can not exceed %s', 9223372036854.0)
        self.GetMarketProxy().ModifyCharOrder(order.orderID, newPrice, order.bid, order.stationID, order.solarSystemID, order.price, order.range, order.volRemaining, order.issueDate)

    def GetStationAsks(self):
        if session.stationid is None and session.structureid is None:
            raise AttributeError('Must be in station')
        return marketutil.ConvertTuplesToBestByOrders(self.GetMarketProxy().GetStationAsks())

    def GetSystemAsks(self):
        if session.solarsystemid2 is None:
            raise AttributeError('Must be in a solarsystem')
        return marketutil.ConvertTuplesToBestByOrders(self.GetMarketProxy().GetSystemAsks())

    def GetPriceHistory(self, typeID):
        old = self.GetMarketProxy().GetOldPriceHistory(typeID)
        new = self.GetMarketProxy().GetNewPriceHistory(typeID)
        history = dbutil.RowList((new.header, []))
        lastTime = blue.os.GetWallclockTimeNow()
        midnightToday = lastTime / const.DAY * const.DAY
        lastPrice = 0.0
        for entry in old:
            while lastTime + const.DAY < entry.historyDate:
                lastTime += const.DAY
                history.append(blue.DBRow(history.header, [lastTime,
                 lastPrice,
                 lastPrice,
                 lastPrice,
                 0,
                 0]))

            history.append(entry)
            lastTime = entry.historyDate
            lastPrice = entry.avgPrice

        while lastTime < midnightToday - const.DAY:
            lastTime += const.DAY
            history.append(blue.DBRow(history.header, [lastTime,
             lastPrice,
             lastPrice,
             lastPrice,
             0,
             0]))

        if len(new):
            history.extend(new)
        else:
            history.append(blue.DBRow(history.header, [blue.os.GetWallclockTimeNow(),
             lastPrice,
             lastPrice,
             lastPrice,
             0,
             0]))
        return history

    def GetAveragePrice(self, typeID, days = 7):
        history = self.GetPriceHistory(typeID)
        now = blue.os.GetWallclockTime()
        averagePrice = -1.0
        volume = 0
        priceVolume = 0.0
        for entry in history:
            if entry[0] < now - days * const.DAY:
                continue
            priceVolume += entry[3] * entry[4]
            volume += entry[4]

        if volume > 0:
            averagePrice = priceVolume / volume
        else:
            averagePrice = float(evetypes.GetBasePrice(typeID)) / evetypes.GetPortionSize(typeID)
            if averagePrice <= 0.0:
                averagePrice = 1.0
        return round(float(averagePrice), 2)

    def GetMyOrders(self):
        return self.GetMarketProxy().GetCharOrders()

    def GetCorporationOrders(self):
        return self.GetMarketProxy().GetCorporationOrders()

    def DumpQuotes(self, typeID, amount = 1):
        typeName = evetypes.GetName(typeID)
        print '\n\nCurrently in station %s in solarsystem %s in constellation %s\n' % (session.stationid, session.solarsystemid2, session.constellationid)
        print 'Trying to buy %s units of %s from current position' % (amount, typeName)
        ranges = {1: 'station',
         3: 'solarsystem',
         4: 'constellation',
         5: 'region'}
        for bidRange, name in ranges.iteritems():
            ask = self.GetBestAskInRange(typeID, bidRange, amount=amount)
            if ask is None:
                print '- In %15s' % name, ': No one selling %s based within %s' % (typeName, name)
            else:
                numJumps = self.clientPathfinderService.GetJumpCountFromCurrent(ask.solarSystemID)
                print '- In %15s' % name, ': Seller %s jumps away, selling %s units at %s ISK at station %s %s wide' % (numJumps,
                 ask.volRemaining,
                 ask.price,
                 ask.stationID,
                 ranges[ask.range])

        print '\nTrying to buy %s units of %s from current position' % (amount, typeName)
        for bidRange, name in ranges.iteritems():
            ask = self.GetBestAverageAsk(typeID, bidRange, amount=amount)
            if ask is None:
                print '- In %15s' % name, ': No one selling %s based within %s' % (typeName, name)
            else:
                numJumps = self.clientPathfinderService.GetJumpCountFromCurrent(ask[2])
                print '- In %15s' % name, ': %s units of %s available at the average price of %s ISK %s jumps away at station %s' % (amount,
                 typeName,
                 ask[0],
                 numJumps,
                 ask[1])

        print '\nTrying to sell %s units of %s from current position:' % (amount, typeName)
        for askRange, name in ranges.iteritems():
            bid = self.GetBestBidInRange(typeID, askRange, amount=amount)
            if bid is None:
                print '- In %15s' % name, ': No one buying %s within here' % typeName
            else:
                numJumps = self.clientPathfinderService.GetJumpCountFromCurrent(bid.solarSystemID)
                print '- In %15s' % name, ': Buyer buying %s units at %s ISK (located at %s %s jumps away)' % (bid.volRemaining,
                 bid.price,
                 bid.stationID,
                 numJumps)

    def GetBestBidWithStationID(self, item, locationID):
        stationID = sm.GetService('invCache').GetStationIDOfItem(item)
        return self.GetBestBid(item.typeID, locationID, stationID)

    def GetBestBid(self, typeID, locationID, stationID = None):
        self.RefreshOrderCache(typeID)
        self.RefreshJumps(typeID, locationID=locationID)
        bids = self.orderCache[typeID][1]
        for bid in bids:
            if self.SkipBidDueToStructureRestrictions(bid, stationID):
                continue
            return bid

    def GetSellCountEstimate(self, typeID, stationID, price, maxToSell):
        estimate = 0
        leftToSell = maxToSell
        bids = self.GetMatchableBids(typeID, stationID, maxToSell)
        for b in bids:
            if b.price < price or estimate > maxToSell or b.minVolume > leftToSell:
                break
            estimate += b.volRemaining
            leftToSell -= b.volRemaining

        return min(estimate, maxToSell)

    def GetMatchableBids(self, typeID, stationID, amount, solarSystemID = None):
        if solarSystemID is None:
            solarSystemID = self.GetSolarSystemForMarketLocation(stationID)
        self.RefreshOrderCache(typeID)
        self.RefreshJumps(typeID, locationID=solarSystemID)
        bids = self.orderCache[typeID][1]
        if len(bids) == 0:
            return bids
        candidates = dbutil.RowList([], bids.columns)
        jmpIdx = bids.columns.index('jumps')
        rngIdx = bids.columns.index('range')
        minIdx = bids.columns.index('minVolume')
        volIdx = bids.columns.index('volRemaining')
        staIdx = bids.columns.index('stationID')
        for x in bids:
            bidJumps = x[jmpIdx]
            bidRange = x[rngIdx]
            bidStationID = x[staIdx]
            bidIsInRange = bidJumps <= bidRange or bidRange == const.rangeStation and bidStationID == stationID
            bidMinAmount = x[minIdx]
            bidVolRemaining = x[volIdx]
            bidAmountIsOk = bidMinAmount <= amount or bidVolRemaining < bidMinAmount and amount >= bidVolRemaining
            isGoodCandidate = bidIsInRange and bidAmountIsOk
            if isGoodCandidate and not self.SkipBidDueToStructureRestrictions(x, stationID):
                candidates.append(x)

        return candidates

    def SkipBidDueToStructureRestrictions(self, bid, itemStationID):
        if util.IsStation(itemStationID) and util.IsStation(bid.stationID):
            return False
        inStructure = itemStationID and not util.IsStation(itemStationID)
        if inStructure and bid.stationID != itemStationID:
            return True
        return False

    def GetSolarSystemForMarketLocation(self, stationID):
        if util.IsStation(stationID):
            station = sm.GetService('ui').GetStation(stationID)
            return station.solarSystemID
        else:
            structureInfo = sm.GetService('structureDirectory').GetStructureInfo(stationID)
            return structureInfo.solarSystemID

    def GetBestMatchableBid(self, typeID, stationID, amount = 1, solarSystemID = None):
        bids = self.GetMatchableBids(typeID, stationID, amount, solarSystemID=solarSystemID)
        try:
            return bids[0]
        except IndexError:
            return None

    def GetBestPrice(self, typeID, item, stacksize, solarSystemID):
        stationID = sm.GetService('invCache').GetStationIDOfItem(item)
        bestMatchableBid = self.GetBestMatchableBid(typeID, stationID, stacksize, solarSystemID=solarSystemID)
        if bestMatchableBid:
            return bestMatchableBid.price
        return self.GetAveragePrice(typeID)

    def GetOfficeFolderInfo(self, item):
        self.stationID, officeFolderID, officeID = sm.GetService('invCache').GetStationIDOfficeFolderIDOfficeIDOfItem(item)
        if officeFolderID is not None:
            return [officeFolderID, officeID]

    def GetBestAverageAsk(self, typeID, bidRange = None, amount = 1, locationID = None):
        self.RefreshOrderCache(typeID)
        self.RefreshJumps(typeID, locationID=locationID)
        if bidRange is None:
            bidRange = const.rangeRegion
        self.LogInfo('[GetBestAverageAsk]', 'typeID:', typeID, 'range:', bidRange, 'amount:', amount)
        self.RefreshOrderCache(typeID)
        saveAmount = amount
        amount = 1
        asks = self.orderCache[typeID][0]
        if len(asks) == 0:
            return
        candidates = {}
        if bidRange == const.rangeRegion:
            for x in asks:
                if x.volRemaining >= amount:
                    if x.stationID in candidates:
                        candidates[x.stationID].append(x)
                    else:
                        candidates[x.stationID] = [x]

        elif bidRange == const.rangeConstellation:
            for x in asks:
                if x.volRemaining >= amount and x.constellationID == session.constellationid:
                    if x.stationID in candidates:
                        candidates[x.stationID].append(x)
                    else:
                        candidates[x.stationID] = [x]

        elif bidRange == const.rangeSolarSystem or session.stationid is None:
            for x in asks:
                if x.volRemaining >= amount and x.solarSystemID == session.solarsystemid2:
                    if x.stationID in candidates:
                        candidates[x.stationID].append(x)
                    else:
                        candidates[x.stationID] = [x]

        else:
            for x in asks:
                if x.volRemaining >= amount and x.stationID == session.stationid:
                    if x.stationID in candidates:
                        candidates[x.stationID].append(x)
                    else:
                        candidates[x.stationID] = [x]

        resultList = []
        amount = saveAmount
        for stationID, askList in candidates.iteritems():
            saveAmount = amount
            averagePrice = 0.0
            cumulatedVolume = 0
            for ask in askList:
                solarsystemID = ask.solarSystemID
                available = min(ask.volRemaining, saveAmount)
                cumulatedVolume += available
                saveAmount -= available
                averagePrice += available * ask.price
                if saveAmount == 0:
                    break

            if cumulatedVolume < amount:
                continue
            averagePrice = averagePrice / cumulatedVolume
            resultList.append([averagePrice, stationID, solarsystemID])

        if len(resultList) == 0:
            return
        resultList.sort()
        return resultList[0]

    def GetBestAskInRange(self, typeID, stationID, bidRange = None, amount = 1):
        if bidRange is None:
            bidRange = const.rangeRegion
        self.LogInfo('[GetBestAskInRange]', 'typeID:', typeID, 'range:', bidRange, 'amount:', amount)
        solarSystemID = self.GetSolarSystemForMarketLocation(stationID)
        self.RefreshOrderCache(typeID)
        self.RefreshJumps(typeID, locationID=solarSystemID)
        asks = self.orderCache[typeID][0]
        for x in asks:
            if x.jumps == 0 and x.stationID == stationID:
                jumps = -1
            else:
                jumps = x.jumps
            if jumps <= bidRange and x.volRemaining >= amount:
                return x

    def GetBestAskPriceInStationAndNumberOrders(self, typeID, stationID, amount = 1):
        self.RefreshOrderCache(typeID)
        asks = self.orderCache[typeID][0]
        asksInStation = filter(lambda x: x.stationID == stationID, asks)
        asksInStation = sorted(asksInStation, key=lambda x: x.price)
        totalQty = 0
        numOrders = 0
        for eachOrder in asksInStation:
            totalQty += eachOrder.volRemaining
            numOrders += 1
            if totalQty >= amount:
                return (eachOrder.price, numOrders)

        return (None, None)

    def GetBestBidInRange(self, typeID, askRange = None, locationID = None, amount = 1):
        if askRange is None:
            askRange = const.rangeRegion
        if locationID is None:
            if askRange == const.rangeStation:
                locationID = session.stationid
                if locationID is None:
                    return
            elif askRange == const.rangeSolarSystem:
                locationID = session.solarsystemid2
            elif askRange == const.rangeConstellation:
                locationID = session.constellationid
        self.LogInfo('[GetBestBidInRange]', 'typeID:', typeID, 'locationID:', locationID, 'range:', askRange, 'amount:', amount)
        self.RefreshOrderCache(typeID)
        bids = self.orderCache[typeID][1]
        if len(bids) == 0:
            return
        if askRange == const.rangeStation:
            stationID = locationID
            solarsystemID = sm.RemoteSvc('map').GetStationExtraInfo()[0].Index('stationID')[stationID].solarSystemID
            constellationID = sm.GetService('map').GetItem(solarsystemID).locationID
        elif askRange == const.rangeSolarSystem:
            solarsystemID = locationID
            constellationID = sm.GetService('map').GetItem(solarsystemID).locationID
        elif askRange == const.rangeConstellation:
            constellationID = locationID
        stationIdx = bids.columns.index('stationID')
        rangeIdx = bids.columns.index('range')
        solIdx = bids.columns.index('solarSystemID')
        conIdx = bids.columns.index('constellationID')
        minIdx = bids.columns.index('minVolume')
        found = 0
        i = 0
        for x in bids:
            bidRange = x[rangeIdx]
            if askRange == const.rangeStation and amount >= x[minIdx] and (x[stationIdx] == stationID or bidRange == const.rangeSolarSystem and x[solIdx] == solarsystemID or bidRange == const.rangeConstellation and x[conIdx] == constellationID or bidRange == const.rangeRegion):
                found = 1
                break
            elif askRange == const.rangeSolarSystem and amount >= x[minIdx] and (bidRange in [const.rangeStation, const.rangeSolarSystem] and x[solIdx] == solarsystemID or bidRange == const.rangeConstellation and x[conIdx] == constellationID or bidRange == const.rangeRegion):
                found = 1
                break
            elif askRange == const.rangeConstellation and amount >= x[minIdx] and (bidRange in [const.rangeStation, const.rangeSolarSystem, const.rangeConstellation] and x[conIdx] == constellationID or bidRange == const.rangeRegion):
                found = 1
                break
            elif askRange == const.rangeRegion and amount >= x[minIdx]:
                found = 1
                break
            i += 1

        if not found:
            return
        self.LogInfo('[GetBestBidInRange] found:', bids[i])
        return bids[i]

    def GetOrders(self, typeID):
        self.RefreshOrderCache(typeID)
        self.RefreshJumps(typeID)
        return [[self.orderCache[typeID][0], [['price', 1], ['jumps', 1]]], [self.orderCache[typeID][1], [['price', -1], ['jumps', 1]]]]

    def DumpOrdersForType(self, typeID):
        orders = self.GetOrders(typeID)
        sells = orders[0][0]
        buys = orders[1][0]
        if len(sells) > 0:
            dateIdx = sells[0].__columns__.index('issueDate')
        elif len(buys) > 0:
            dateIdx = buys[0].__columns__.index('issueDate')
        else:
            eve.Message('CustomInfo', {'info': localization.GetByLabel('UI/Market/MarketWindow/ExportNoData')})
            return
        date = util.FmtDate(blue.os.GetWallclockTime())
        f = blue.classes.CreateInstance('blue.ResFile')
        typeName = evetypes.GetName(typeID)
        fileTypeName = localization.CleanImportantMarkup(typeName)
        fileTypeName = fileTypeName.replace('"', '')
        fileRegionName = localization.CleanImportantMarkup(cfg.evelocations.Get(session.regionid).name)
        directory = blue.sysinfo.GetUserDocumentsDirectory() + '/EVE/logs/Marketlogs/'
        sanitizedFileTypeName = uiutil.SanitizeFilename(fileTypeName)
        filename = '%s-%s-%s.txt' % (fileRegionName, sanitizedFileTypeName, util.FmtDateEng(blue.os.GetWallclockTime()).replace(':', ''))
        if not f.Open(directory + filename, 0):
            f.Create(directory + filename)
        first = 1
        for order in sells:
            if first:
                for key in order.__columns__:
                    f.Write('%s,' % key)

                f.Write('\r\n')
                first = 0
            for i in range(len(order)):
                first = 0
                if i == dateIdx:
                    f.Write('%s,' % util.FmtDateEng(order[i], 'el').replace('T', ' '))
                else:
                    f.Write('%s,' % order[i])

            f.Write('\r\n')

        for order in buys:
            if first:
                for key in order.__columns__:
                    f.Write('%s,' % key)

                f.Write('\r\n')
                first = 0
            for i in range(len(order)):
                if i == dateIdx:
                    f.Write('%s,' % util.FmtDateEng(order[i], 'el').replace('T', ' '))
                else:
                    f.Write('%s,' % order[i])

            f.Write('\r\n')

        f.Close()
        eve.Message('MarketExportInfo', {'sell': len(sells),
         'buy': len(buys),
         'typename': evetypes.GetName(typeID),
         'filename': localization.GetByLabel('UI/Map/StarMap/lblBoldName', name=filename),
         'directory': localization.GetByLabel('UI/Map/StarMap/lblBoldName', name=directory)})

    def GetOrder(self, orderID, typeID = None):
        if typeID is not None:
            self.RefreshOrderCache(typeID)
            self.RefreshJumps(typeID)
        for asksAndBids in self.orderCache.values():
            asks, bids, stamp = asksAndBids
            for order in asks:
                if order.orderID == orderID:
                    return order

            for order in bids:
                if order.orderID == orderID:
                    return order

    def RefreshJumps(self, typeID, refreshOrders = 0, locationID = None):
        if refreshOrders:
            self.RefreshOrderCache(typeID)
        asks = self.orderCache[typeID][0]
        bids = self.orderCache[typeID][1]
        if locationID is None:
            getJumpCountFunc = self.clientPathfinderService.GetJumpCountFromCurrent
        else:
            getJumpCountFunc = functools.partial(self.clientPathfinderService.GetJumpCount, locationID)
        for row in itertools.chain(asks, bids):
            row.jumps = getJumpCountFunc(row.solarSystemID)

        asks.sort(lambda x, y, headers = asks.columns: SortAsks(x, y, headers))
        bids.sort(lambda x, y, headers = bids.columns: SortBids(x, y, headers))

    def ClearAll(self):
        self.orderCache = {}

    def RefreshAll(self):
        for typeID in self.orderCache.iterkeys():
            self.RefreshOrderCache(typeID)
            self.RefreshJumps(typeID)

    def RefreshOrderCache(self, typeID, forceUpdate = 0):
        self.LogInfo('[RefreshOrderCache] Refreshing', typeID)
        orders = self.GetMarketProxy().GetOrders(typeID)
        version = sm.GetService('objectCaching').GetCachedMethodCallVersion(None, 'marketProxy', 'GetOrders', (typeID,))
        if typeID in self.orderCache:
            if self.orderCache[typeID][2] == version:
                return
        asks, bids = orders[0], orders[1]
        self.orderCache[typeID] = [asks, bids, version]
        self.LogInfo('[RefreshOrderCache] Refresh done:', len(orders[0]), 'asks and', len(orders[1]), 'bids')
