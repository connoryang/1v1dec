#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\neocom\contracts\contracts.py
import blue
import carbonui.const as uiconst
from eve.client.script.ui.shared.neocom.contracts.contractsDetailsWnd import ContractDetailsWindow
from eve.client.script.ui.shared.neocom.contracts.contractsWnd import ContractsWindow
from eve.client.script.ui.shared.neocom.contracts.createContractWnd import CreateContractWnd
from eve.client.script.ui.shared.neocom.contracts.ignoreListWnd import IgnoreListWindow
import eve.common.script.util.notificationconst as notificationConst
import evetypes
import localization
import service
import uiutil
import uix
import uthread
import util
import structures
import moniker
from contractutils import *
from eve.client.script.ui.shared.monetization.trialPopup import ORIGIN_CONTRACTS
from notifications.common.formatters.contractAssigned import ContractAssignedFormatter
from notifications.common.formatters.contractAttention import ContractNeedsAttentionFormatter
MAX_IGNORED = 1000
CACHE_TIME = 10

def GetSecurityClassText(securityClass):
    txt = {const.securityClassZeroSec: '<color=0xffbb0000>%s</color>' % localization.GetByLabel('UI/Common/NullSec'),
     const.securityClassLowSec: '<color=0xffbbbb00>%s</color>' % localization.GetByLabel('UI/Common/LowSec'),
     const.securityClassHighSec: '<color=0xff00bb00>%s</color>' % localization.GetByLabel('UI/Common/HighSec')}.get(securityClass, localization.GetByLabel('UI/Contracts/ContractsWindow/UnknownSystem'))
    return txt


class ContractsSvc(service.Service):
    __exportedcalls__ = {'GetContract': {},
     'AcceptContract': {},
     'DeleteContract': {},
     'CompleteContract': {},
     'FailContract': {},
     'RejectContract': {},
     'CreateContract': {},
     'PlaceBid': {},
     'FinishAuction': {},
     'GetMarketTypes': {},
     'NumOutstandingContracts': {},
     'GetSolarSystemIDForStationOrStructure': {},
     'GetItemsInContainer': {},
     'GetItemsInStation': {},
     'DeleteNotification': {},
     'CollectMyPageInfo': {},
     'ClearCache': {},
     'OpenJournal': [service.ROLE_IGB | service.ROLE_ANY],
     'OpenCreateContract': [service.ROLE_IGB | service.ROLE_ANY],
     'OpenAvailableTab': [service.ROLE_IGB | service.ROLE_ANY],
     'OpenAssignedToMe': [service.ROLE_IGB | service.ROLE_ANY],
     'AddIgnore': {},
     'OpenIgnoreList': [service.ROLE_IGB],
     'GetMessages': {},
     'DeliverCourierContractFromItemID': {},
     'FindCourierContractFromItemID': {}}
    __guid__ = 'svc.contracts'
    __notifyevents__ = ['ProcessSessionChange',
     'OnContractAssigned',
     'OnContractCompleted',
     'OnContractAccepted',
     'OnContractRejected',
     'OnContractFailed',
     'OnContractOutbid',
     'OnContractBuyout']
    __servicename__ = 'Contracts'
    __displayname__ = 'Contracts Service'
    __dependencies__ = []
    __update_on_reload__ = 0

    def __init__(self):
        service.Service.__init__(self)
        self.detailsByRegionByTypeFlag = {}
        self.contractID = None
        self.markettypes = None
        self.contracts = {}
        self.myPageInfo = None
        self.myExpiredContractList = None
        self.contractsInProgress = {}
        self.messages = []
        self.inited = False

    def Run(self, memStream = None):
        self.contractProxySvc = sm.ProxySvc('contractProxy')
        self.Init()

    def Stop(self, memStream = None):
        ContractsWindow.CloseIfOpen()

    def Init(self):
        if session.charid and not self.inited:
            uthread.new(self.NeocomBlink)
            self.inited = True

    def GetContractsInProgress(self):
        return self.contractsInProgress

    def GetContractsBookmarkMenu(self):
        contractsMenu = []
        stationsPickup = set()
        stationsDropoff = set()
        for contractID, contract in self.contractsInProgress.iteritems():
            if contract[-1] < blue.os.GetWallclockTime():
                continue
            if cfg.evelocations.Get(contract[0]).solarSystemID == session.solarsystemid2:
                stationsPickup.add(contract[0])
            if cfg.evelocations.Get(contract[1]).solarSystemID == session.solarsystemid2:
                stationsDropoff.add(contract[1])

        for stationID in stationsPickup:
            pickupLabel = localization.GetByLabel('UI/Contracts/ContractsService/CourierPickup', station=stationID)
            contractsMenu.append((pickupLabel, ('isDynamic', sm.GetService('menu').CelestialMenu, (stationID,
               None,
               None,
               0,
               None,
               None,
               None))))

        for stationID in stationsDropoff:
            dropoffLabel = localization.GetByLabel('UI/Contracts/ContractsService/CourierDelivery', station=stationID)
            contractsMenu.append((dropoffLabel, ('isDynamic', sm.GetService('menu').CelestialMenu, (stationID,
               None,
               None,
               0,
               None,
               None,
               None))))

        return contractsMenu

    def FindRelated(self, typeID, groupID, categoryID, issuerID, locationID, endLocationID, contractType = None, reset = True, *args):
        if contractType != const.conTypeCourier:
            contractType = CONTYPE_AUCTIONANDITEMECHANGE
        self.OpenSearchTab(typeID, groupID, categoryID, issuerID, locationID, endLocationID, const.conAvailPublic, contractType, reset)

    def OpenAssignedToMe(self, contractType = CONTYPE_AUCTIONANDITEMECHANGE, isCorp = False):
        self.Show()
        wnd = ContractsWindow.GetIfOpen()
        if wnd is not None:
            wnd = ContractsWindow.Open()
            blue.pyos.synchro.SleepWallclock(10)
            wnd.sr.maintabs.SelectByIdx(2)
            wnd.sr.contractSearchContent.FindMyContracts(contractType, isCorp)

    def GetRelatedMenu(self, contract, typeID, reset = True):
        m = []
        startConstellationID = sm.GetService('map').GetItem(contract.startSolarSystemID).locationID
        if typeID and contract.type != const.conTypeCourier:
            m += [(uiutil.MenuLabel('UI/Contracts/ContractsWindow/SameType'), self.FindRelated, (typeID,
               None,
               None,
               None,
               None,
               None,
               contract.type,
               reset))]
            m += [(uiutil.MenuLabel('UI/Contracts/ContractsWindow/SameGroup'), self.FindRelated, (None,
               evetypes.GetGroupID(typeID),
               None,
               None,
               None,
               None,
               contract.type,
               reset))]
            m += [(uiutil.MenuLabel('UI/Contracts/ContractsWindow/SameCategory'), self.FindRelated, (None,
               None,
               evetypes.GetCategoryID(typeID),
               None,
               None,
               None,
               contract.type,
               reset))]
            m += [None]
        m += [(uiutil.MenuLabel('UI/Contracts/ContractsWindow/FromSameIssuer'), self.FindRelated, (None,
           None,
           None,
           contract.issuerCorpID if contract.forCorp else contract.issuerID,
           None,
           None,
           contract.type,
           reset))]
        m += [None]
        m += [(uiutil.MenuLabel('UI/Contracts/ContractsWindow/FromSameSolarSystem'), self.FindRelated, (None,
           None,
           None,
           None,
           contract.startSolarSystemID,
           None,
           contract.type,
           reset))]
        m += [(uiutil.MenuLabel('UI/Contracts/ContractsWindow/FromSameConstellation'), self.FindRelated, (None,
           None,
           None,
           None,
           startConstellationID,
           None,
           contract.type,
           reset))]
        m += [(uiutil.MenuLabel('UI/Contracts/ContractsWindow/FromSameRegion'), self.FindRelated, (None,
           None,
           None,
           None,
           contract.startRegionID,
           None,
           contract.type,
           reset))]
        if contract.type == const.conTypeCourier:
            endConstellationID = sm.GetService('map').GetItem(contract.endSolarSystemID).locationID
            m += [None]
            m += [(uiutil.MenuLabel('UI/Contracts/ContractsWindow/ToSameSolarSystem'), self.FindRelated, (None,
               None,
               None,
               None,
               None,
               contract.endSolarSystemID,
               contract.type,
               reset))]
            m += [(uiutil.MenuLabel('UI/Contracts/ContractsWindow/ToSameConstellation'), self.FindRelated, (None,
               None,
               None,
               None,
               None,
               endConstellationID,
               contract.type,
               reset))]
            m += [(uiutil.MenuLabel('UI/Contracts/ContractsWindow/ToSameRegion'), self.FindRelated, (None,
               None,
               None,
               None,
               None,
               contract.endRegionID,
               contract.type,
               reset))]
        return m

    def DispatchAssignedNotification(self, assignedToMe):
        if len(assignedToMe) > 0:
            firstContractID = assignedToMe[0]
            data = ContractAssignedFormatter.MakeData(contractCountAssignedToMe=len(assignedToMe), firstContractID=firstContractID)
            sm.GetService('notificationSvc').MakeAndScatterNotification(notificationConst.notificationTypeContractAssigned, data)

    def DispatchAttentionNotification(self, needsAttention):
        if len(needsAttention) > 0:
            firstContractInfo = needsAttention[0]
            data = ContractNeedsAttentionFormatter.MakeData(needsAttention=len(needsAttention), isForCorp=firstContractInfo[1], firstContractID=firstContractInfo.contractID)
            sm.GetService('notificationSvc').MakeAndScatterNotification(notificationConst.notificationTypeContractNeedsAttention, data)

    def NeocomBlink(self):
        kv = self.contractProxySvc.GetLoginInfo()
        ignoreList = set(settings.user.ui.Get('contracts_ignorelist', []))
        assignedToMe = []
        for contract in kv.assignedToMe:
            if contract.issuerID not in ignoreList:
                assignedToMe.append(contract.contractID)

        self.DispatchAssignedNotification(assignedToMe)
        self.DispatchAttentionNotification(kv.needsAttention)
        if len(kv.inProgress):
            ip = {}
            for contract in kv.inProgress:
                ip[contract.contractID] = [contract.startStationID, contract.endStationID, contract.expires]

            self.contractsInProgress = ip

    def ProcessSessionChange(self, isremote, sess, change):
        if 'charid' in change:
            self.Init()

    def OnContractAssigned(self, contractID):
        contract = self.GetContract(contractID)
        c = contract.contract
        issuerID = [c.issuerID, c.issuerCorpID][c.forCorp]
        ignoreList = settings.user.ui.Get('contracts_ignorelist', [])
        if issuerID in ignoreList:
            return
        self.ContractNotify('UI/Contracts/ContractsService/ContractMessageAssigned', contractID)

    def OnContractCompleted(self, contractID):
        self.ContractNotify('UI/Contracts/ContractsService/ContractMessageCompleted', contractID)

    def OnContractAccepted(self, contractID):
        self.ContractNotify('UI/Contracts/ContractsService/ContractMessageAccepted', contractID)

    def OnContractRejected(self, contractID):
        self.ContractNotify('UI/Contracts/ContractsService/ContractMessageRejected', contractID)

    def OnContractFailed(self, contractID):
        self.ContractNotify('UI/Contracts/ContractsService/ContractMessageFailed', contractID)

    def OnContractOutbid(self, contractID):
        self.ContractNotify('UI/Contracts/ContractsService/ContractMessageOutbid', contractID)

    def OnContractBuyout(self, contractID):
        self.ContractNotify('UI/Contracts/ContractsService/ContractMessageBuyout', contractID)

    def ContractNotify(self, cerberusLabel, contractID):
        MAX_NUM_MESSAGES = 5
        contract = self.GetContract(contractID, force=False)
        c = contract.contract
        title = GetContractTitle(c, contract.items)
        link = '<a href="contract:%d//%d">%s</a>' % (c.startSolarSystemID, contractID, title)
        message = localization.GetByLabel(cerberusLabel, timeStamp=util.FmtDate(blue.os.GetWallclockTime(), 'ls'), contractLink=link)
        self.messages.append(message)
        if len(self.messages) > MAX_NUM_MESSAGES:
            self.messages.pop(0)
        self.Blink()
        self.ClearCache()

    def Blink(self):
        sm.GetService('neocom').Blink('contracts', localization.GetByLabel('UI/Contracts/ContractsWindow/ContractsRequireAttention'), numBlinks=10)

    def ShowAssignedTo(self, *args):
        self.Show()
        self.OpenAvailableTab(3, 1)

    def Show(self, lookup = None, idx = None):
        ContractsWindow.CloseIfOpen()
        ContractsWindow.Open(lookup=lookup, idx=idx)

    def GetRouteSecurityWarning(self, startSolarSystemID, endSolarSystemID):
        mapSvc = sm.GetService('map')
        path = sm.GetService('clientPathfinderService').GetAutopilotPathBetween(startSolarSystemID, endSolarSystemID)
        txt = ''
        if not path:
            txt = '<color=0xffbb0000>%s</color>' % localization.GetByLabel('UI/Common/unreachable').upper()
        else:
            mySecurityClass = mapSvc.GetSecurityClass(session.solarsystemid2)
            pathClasses = set()
            for solarSystemID in path:
                pathClasses.add(mapSvc.GetSecurityClass(solarSystemID))

            securityClassList = []
            for p in pathClasses:
                if p != mySecurityClass:
                    securityClassList.append(GetSecurityClassText(p))

            securityClassString = localization.formatters.FormatGenericList(securityClassList)
            if len(securityClassList) > 0:
                txt = localization.GetByLabel('UI/Contracts/ContractsService/RouteWillTakeYouThrough', listOfSecurityRatings=securityClassString)
        return txt

    def ShowContract(self, contractID):
        self.contractID = contractID
        ContractDetailsWindow.CloseIfOpen()
        ContractDetailsWindow.Open(contractID=contractID)

    def GetContract(self, contractID, force = False):
        v = self.contracts.get(contractID, None)
        diff = 0
        if v:
            diff = blue.os.GetWallclockTime() - v.time
        if contractID not in self.contracts or force or diff > 5 * const.MIN and not force:
            self.LogInfo('Fetching contract %s from the server' % contractID)
            contract = self.contractProxySvc.GetContract(contractID)
            v = util.KeyVal()
            v.time = blue.os.GetWallclockTime()
            v.contract = contract
            self.contracts[contractID] = v
        else:
            self.LogInfo('Using client cache for contract %s' % contractID)
        return self.contracts[contractID].contract

    def AcceptContract(self, contractID, forCorp):
        contract = self.GetContract(contractID, force=None)
        c = contract.contract
        if not contract:
            raise UserError('ConContractNotFound')
        if session.userType == const.userTypeTrial:
            uicore.cmd.OpenTrialUpsell(origin=ORIGIN_CONTRACTS, reason='AcceptContract', message=localization.GetByLabel('UI/TrialUpsell/ContractRestrictionBody'))
            return
        if not self.CheckEndpointAccess(c.startStationID):
            return
        if c.endStationID and c.endStationID != c.startStationID and not self.CheckEndpointAccess(c.endStationID):
            return
        n = sm.GetService('clientPathfinderService').GetAutopilotJumpCount(session.solarsystemid2, c.startSolarSystemID)
        n2 = 0
        if c.endSolarSystemID:
            n2 = sm.GetService('clientPathfinderService').GetAutopilotJumpCount(session.solarsystemid2, c.endSolarSystemID)
        n = max(n, n2)
        if n > 1000:
            if eve.Message('ConConfirmNotReachable', {}, uiconst.YESNO) != uiconst.ID_YES:
                return False
        wallet = sm.GetService('corp').GetMyCorpAccountName()
        args = {}
        if forCorp:
            args['youoryourcorp'] = localization.GetByLabel('UI/Contracts/ContractsService/YouOnBehalfOfYourCorp', corpName=cfg.eveowners.Get(eve.session.corpid).name, wallet=wallet)
        else:
            args['youoryourcorp'] = localization.GetByLabel('UI/Common/You')
        args['contractname'] = GetContractTitle(c, contract.items)
        if c.type == const.conTypeAuction:
            raise RuntimeError('You cannot accept an auction')
        elif c.type == const.conTypeItemExchange:
            msg = 'ConConfirmAcceptItemExchange'
            reportGet = reportPay = ''
            for item in contract.items:
                if item.inCrate:
                    reportGet += '<t>%s.<br>' % cfg.FormatConvert(const.UE_TYPEIDANDQUANTITY, item.itemTypeID, max(1, item.quantity))
                else:
                    reportPay += '<t>%s.<br>' % cfg.FormatConvert(const.UE_TYPEIDANDQUANTITY, item.itemTypeID, max(1, item.quantity))

            if reportGet != '':
                reportGet = localization.GetByLabel('UI/Contracts/ContractsService/ConfirmItemsGet', items=reportGet)
            if reportPay != '':
                reportPay = localization.GetByLabel('UI/Contracts/ContractsService/ConfirmAcceptItemsPay', items=reportPay)
            if reportGet == '' and c.reward == 0 and (reportPay != '' or c.price > 0):
                msg = 'ConConfirmAcceptItemExchangeGift'
            if reportPay != '' and forCorp:
                reportPay += localization.GetByLabel('UI/Contracts/ContractsWindow/ConfirmAcceptCorpItems')
            args['itemsget'] = reportGet
            args['itemspay'] = reportPay
            payorgetmoney = ''
            if c.price > 0:
                payorgetmoney = localization.GetByLabel('UI/Contracts/ContractsService/ConfirmAcceptPayMoney', numISK=FmtISKWithDescription(c.price))
            elif c.reward > 0:
                payorgetmoney = localization.GetByLabel('UI/Contracts/ContractsService/ConfirmAcceptGetMoney', numISK=FmtISKWithDescription(c.reward))
            args['payorgetmoney'] = payorgetmoney
        elif c.type == const.conTypeCourier:
            if c.volume > const_conCourierWarningVolume:
                if eve.Message('ConNeedFreighter', {'vol': c.volume}, uiconst.YESNO, suppress=uiconst.ID_YES) != uiconst.ID_YES:
                    return False
            if c.volume <= const_conCourierWarningVolume:
                ship = sm.GetService('godma').GetItem(eve.session.shipid)
                if ship:
                    maxVolume = ship.GetCapacity().capacity
                    if maxVolume < c.volume:
                        if eve.Message('ConCourierDoesNotFit', {'shipCapacity': maxVolume,
                         'packageVolume': c.volume}, uiconst.YESNO, suppress=uiconst.ID_YES) != uiconst.ID_YES:
                            return False
            msg = 'ConConfirmAcceptCourier'
            args['numdays'] = c.numDays
            args['destination'] = c.endStationID
            args['volume'] = c.volume
            collateral = ''
            if c.collateral > 0:
                collateral = localization.GetByLabel('UI/Contracts/ContractsService/YouWillHaveToProvideCollateralAmount', numISK=FmtISKWithDescription(c.collateral))
            args['collateral'] = collateral
        else:
            raise RuntimeError('Invalid contract type')
        if eve.Message(msg, args, uiconst.YESNO) != uiconst.ID_YES:
            return False
        self.LogInfo('Accepting contract %s' % contractID)
        try:
            contract = self.contractProxySvc.AcceptContract(contractID, forCorp)
        except UserError as e:
            if e.msg == 'TrialAccountRestriction':
                uicore.cmd.OpenTrialUpsell(origin=ORIGIN_CONTRACTS, reason='AcceptContract', message=localization.GetByLabel('UI/TrialUpsell/ContractRestrictionBody'))
            else:
                raise

        if contract.type == const.conTypeCourier:
            self.contractsInProgress[contract.contractID] = [contract.startStationID, contract.endStationID, contract.dateAccepted + const.DAY * contract.numDays]
        self.ClearCache()
        return True

    def DeleteContract(self, contractID):
        contract = self.GetContract(contractID, force=None)
        if not contract:
            raise UserError('ConContractNotFound')
        c = contract.contract
        if c.dateExpired >= blue.os.GetWallclockTime() and c.status != const.conStatusRejected:
            args = {}
            args['contractname'] = GetContractTitle(c, contract.items)
            msg = 'ConConfirmDeleteContract'
            if eve.Message(msg, args, uiconst.YESNO) != uiconst.ID_YES:
                return False
        self.LogInfo('Deleting contract', contractID)
        try:
            if self.contractProxySvc.DeleteContract(contractID):
                sm.ScatterEvent('OnDeleteContract', contractID)
        except UserError as e:
            if e.msg == 'TrialAccountRestriction':
                uicore.cmd.OpenTrialUpsell(origin=ORIGIN_CONTRACTS, reason='DeleteContract', message=localization.GetByLabel('UI/TrialUpsell/ContractRestrictionBody'))
            else:
                raise

        self.ClearCache()
        return True

    def CompleteContract(self, contractID):
        ret = False
        if eve.Message('ConConfirmComplete', None, uiconst.YESNO, suppress=uiconst.ID_YES) == uiconst.ID_YES:
            self.LogInfo('Completing contract %s' % contractID)
            self.ClearCache()
            try:
                ret = self.contractProxySvc.CompleteContract(contractID, const.conStatusFinished)
            except UserError as e:
                if e.msg == 'TrialAccountRestriction':
                    uicore.cmd.OpenTrialUpsell(origin=ORIGIN_CONTRACTS, reason='CompleteContract', message=localization.GetByLabel('UI/TrialUpsell/ContractRestrictionBody'))
                else:
                    raise

            if contractID in self.contractsInProgress:
                del self.contractsInProgress[contractID]
            eve.Message('ConCourierContractDelivered')
        return ret

    def FailContract(self, contractID):
        contract = self.GetContract(contractID, force=None)
        c = contract.contract
        args = {}
        if not contract:
            raise UserError('ConContractNotFound')
        args['contractname'] = GetContractTitle(c, contract.items)
        if c.acceptorID == eve.session.charid or c.acceptorID == eve.session.corpid:
            msg = 'ConConfirmFailContractAcceptor'
            args['collateral'] = localization.GetByLabel('UI/Contracts/ContractsService/ConfirmFailLoseCollateral', numISK=FmtISKWithDescription(c.collateral))
        else:
            dateOverdue = c.dateAccepted + const.DAY * c.numDays
            isOverdue = blue.os.GetWallclockTime() > dateOverdue
            if isOverdue and c.status == const.conStatusInProgress:
                msg = 'ConConfirmFailContractIssuerOverdue'
                args['timeoverdue'] = util.FmtDate(blue.os.GetWallclockTime() - dateOverdue, 'ls')
            else:
                msg = 'ConConfirmFailContractIssuerFinishedAcceptor'
            args['acceptor'] = cfg.eveowners.Get(c.acceptorID).name
        if eve.Message(msg, args, uiconst.YESNO) != uiconst.ID_YES:
            return False
        self.ClearCache()
        self.LogInfo('Failing contract %s' % contractID)
        try:
            ret = self.contractProxySvc.CompleteContract(contractID, const.conStatusFailed)
        except UserError as e:
            if e.msg == 'TrialAccountRestriction':
                uicore.cmd.OpenTrialUpsell(origin=ORIGIN_CONTRACTS, reason='AcceptContract', message=localization.GetByLabel('UI/TrialUpsell/ContractRestrictionBody'))
            else:
                raise
            return

        if contractID in self.contractsInProgress:
            del self.contractsInProgress[contractID]
        return ret

    def RejectContract(self, contractID):
        contract = self.GetContract(contractID, force=None)
        c = contract.contract
        args = {}
        if not contract:
            raise UserError('ConContractNotFound')
        args['contractname'] = GetContractTitle(c, contract.items)
        args['issuer'] = cfg.eveowners.Get({False: c.issuerID,
         True: c.issuerCorpID}[c.forCorp]).name
        if c.assigneeID == session.charid:
            msg = 'ConConfirmRejectContract'
        elif c.assigneeID == session.corpid:
            msg = 'ConConfirmRejectContractCorp'
        else:
            raise UserError('ConNotYourContract')
        if eve.Message(msg, args, uiconst.YESNO, suppress=uiconst.ID_YES) != uiconst.ID_YES:
            return False
        self.LogInfo('Rejecting contract %s' % contractID)
        self.ClearCache()
        try:
            return self.contractProxySvc.CompleteContract(contractID, const.conStatusRejected)
        except UserError as e:
            if e.msg == 'TrialAccountRestriction':
                uicore.cmd.OpenTrialUpsell(origin=ORIGIN_CONTRACTS, reason='AcceptContract', message=localization.GetByLabel('UI/TrialUpsell/ContractRestrictionBody'))
            else:
                raise

    def CreateContract(self, type, avail, assigneeID, expiretime, duration, startStationID, endStationID, price, reward, collateral, title, description, itemList, flag, requestItemTypeList, forCorp, confirm = None):
        self.LogNotice('CreateContract', type, avail, assigneeID, expiretime, duration, startStationID, endStationID, price, reward, collateral, title, description, itemList, flag, requestItemTypeList, forCorp)
        try:
            ret = self.contractProxySvc.CreateContract(type, avail, assigneeID, expiretime, duration, startStationID, endStationID, price, reward, collateral, title, description, itemList=itemList, flag=flag, requestItemTypeList=requestItemTypeList, forCorp=forCorp, confirm=confirm)
        except UserError as e:
            if e.msg == 'TrialAccountRestriction':
                uicore.cmd.OpenTrialUpsell(origin=ORIGIN_CONTRACTS, reason='CreateContract', message=localization.GetByLabel('UI/TrialUpsell/ContractRestrictionBody'))
                return
            raise

        self.ClearCache()
        return ret

    def PlaceBid(self, contractID, force = None):
        uthread.ReentrantLock(self)
        try:
            isContractMgr = eve.session.corprole & const.corpRoleContractManager == const.corpRoleContractManager
            contract = self.GetContract(contractID, force=force)
            self.contract = contract
            c = contract.contract
            if not self.CheckEndpointAccess(c.startStationID):
                return
            currentBid = 0
            numBids = 0
            maxBid = MAX_AMOUNT
            if len(contract.bids) > 0:
                currentBid = contract.bids[0].amount
                numBids = len(contract.bids)
            b = currentBid + max(int(0.1 * c.price), 1000)
            if c.collateral > 0:
                b = min(b, c.collateral)
                maxBid = c.collateral
            minBid = int(max(c.price, b))
            if c.collateral > 0:
                collateral = FmtISKWithDescription(c.collateral)
            else:
                collateral = localization.GetByLabel('UI/Contracts/ContractEntry/NoBuyoutPrice')
            biddingOnLabel = localization.GetByLabel('UI/Contracts/ContractsService/BiddingOnName', contractName=GetContractTitle(c, contract.items))
            startingBidLabel = localization.GetByLabel('UI/Contracts/ContractsWindow/StartingBid')
            buyoutLabel = localization.GetByLabel('UI/Contracts/ContractsWindow/BuyoutPrice')
            currentLabel = localization.GetByLabel('UI/Contracts/ContractsWindow/CurrentBid')
            yourBidLabel = localization.GetByLabel('UI/Contracts/ContractsWindow/YourBid')
            format = [{'type': 'text',
              'text': biddingOnLabel,
              'labelwidth': 100},
             {'type': 'labeltext',
              'label': startingBidLabel,
              'text': FmtISKWithDescription(c.price),
              'labelwidth': 100},
             {'type': 'labeltext',
              'label': buyoutLabel,
              'text': collateral,
              'labelwidth': 100},
             {'type': 'labeltext',
              'label': currentLabel,
              'text': FmtISKWithDescription(currentBid),
              'labelwidth': 100},
             {'type': 'edit',
              'setvalue': '0.1',
              'floatonly': [0, maxBid],
              'setvalue': minBid,
              'key': 'bid',
              'labelwidth': 100,
              'label': yourBidLabel,
              'required': 1,
              'setfocus': 1}]
            if isContractMgr and not (c.forCorp and c.issuerCorpID == eve.session.corpid):
                format.append({'type': 'checkbox',
                 'required': 1,
                 'height': 16,
                 'setvalue': 0,
                 'key': 'forCorp',
                 'label': '',
                 'text': localization.GetByLabel('UI/Contracts/ContractsWindow/PlaceBidForCorp')})
            if c.collateral > 0:
                format.append({'type': 'checkbox',
                 'required': 1,
                 'height': 16,
                 'setvalue': 0,
                 'key': 'buyout',
                 'label': '',
                 'text': localization.GetByLabel('UI/Contracts/ContractsWindow/Buyout'),
                 'onchange': self.PlaceBidBuyoutCallback})
            format.append({'type': 'push'})
            retval = uix.HybridWnd(format, localization.GetByLabel('UI/Contracts/ContractsWindow/BiddingOnContract'), 1, buttons=uiconst.OKCANCEL, minW=340, minH=100, icon='res:/ui/Texture/WindowIcons/wallet.png')
            if retval:
                forCorp = not not retval.get('forCorp', False)
                buyout = not not retval.get('buyout', False)
                bid = int(retval['bid'])
                if buyout:
                    if c.collateral < c.price:
                        raise RuntimeError('Buyout is lower than starting bid!')
                    bid = c.collateral
                try:
                    retval = self.DoPlaceBid(contractID, bid, forCorp)
                except UserError as e:
                    if e.args[0] == 'ConBidTooLow':
                        eve.Message(e.args[0], e.args[1])
                        self.PlaceBid(contractID, force=True)
                    else:
                        raise

            return not not retval
        finally:
            uthread.UnLock(self)
            self.ClearCache()

    def PlaceBidBuyoutCallback(self, chkbox, *args):
        c = self.contract.contract
        buyout = c.collateral
        currentBid = 0
        if len(self.contract.bids) > 0:
            currentBid = self.contract.bids[0].amount
        minBid = int(max(c.price, min(currentBid + 0.1 * c.price + 0.1, c.collateral)))
        wnd = chkbox.parent.parent
        edit = uiutil.FindChild(wnd, 'edit_bid')
        if chkbox.GetValue():
            edit.state = uiconst.UI_DISABLED
            edit.SetText(buyout)
        else:
            edit.state = uiconst.UI_NORMAL
            edit.SetText(minBid)

    def DoPlaceBid(self, contractID, bid, forCorp):
        contract = self.GetContract(contractID, force=None)
        c = contract.contract
        args = {}
        if not contract:
            raise UserError('ConContractNotFound')
        wallet = sm.GetService('corp').GetMyCorpAccountName()
        args = {}
        if forCorp:
            args['youoryourcorp'] = localization.GetByLabel('UI/Contracts/ContractsService/YouOnBehalfOfYourCorp', corpName=cfg.eveowners.Get(eve.session.corpid).name, wallet=wallet)
        else:
            args['youoryourcorp'] = localization.GetByLabel('UI/Common/You')
        args['contractname'] = GetContractTitle(c, contract.items)
        args['amount'] = FmtISKWithDescription(bid)
        reportGet = ''
        for item in contract.items:
            if item.inCrate:
                reportGet += '<t>%s.<br>' % cfg.FormatConvert(const.UE_TYPEIDANDQUANTITY, item.itemTypeID, max(1, item.quantity)).capitalize()

        if reportGet != '':
            reportGet = localization.GetByLabel('UI/Contracts/ContractsService/ConfirmItemsGet', items=reportGet)
        args['itemsget'] = reportGet
        msg = 'ConConfirmPlaceBid'
        if eve.Message(msg, args, uiconst.YESNO, suppress=uiconst.ID_YES) != uiconst.ID_YES:
            return False
        self.LogInfo('Placing bid of %s on contract %s' % (FmtISKWithDescription(bid), contractID))
        try:
            return self.contractProxySvc.PlaceBid(contractID, bid, forCorp)
        except UserError as e:
            if e.msg == 'TrialAccountRestriction':
                uicore.cmd.OpenTrialUpsell(origin=ORIGIN_CONTRACTS, reason='PlaceBid', message=localization.GetByLabel('UI/TrialUpsell/ContractRestrictionBody'))
            else:
                raise

    def FinishAuction(self, contractID, isIssuer):
        self.LogInfo('Finishing Auction %s' % contractID)
        self.ClearCache()
        try:
            return self.contractProxySvc.FinishAuction(contractID, isIssuer)
        except UserError as e:
            if e.msg == 'TrialAccountRestriction':
                uicore.cmd.OpenTrialUpsell(origin=ORIGIN_CONTRACTS, reason='FinishAuction', message=localization.GetByLabel('UI/TrialUpsell/ContractRestrictionBody'))
            else:
                raise

    def GetMarketTypes(self):
        if not self.markettypes:
            self.markettypes = GetMarketTypes()
        return self.markettypes

    def NumOutstandingContracts(self, forCorp = False):
        self.LogInfo('Getting number of outstanding contracts%s' % ['', ' (for corp)'][forCorp])
        return self.contractProxySvc.NumOutstandingContracts()

    def SplitStack(self, stationID, itemID, qty, forCorp, flag):
        self.LogInfo('Splitting stack of item %s, qty=%s%s' % (itemID, qty, ['', ' (for corp)'][forCorp]))
        ret = self.contractProxySvc.SplitStack(stationID, itemID, qty, forCorp, flag)
        if ret:
            wnd = CreateContractWnd.GetIfOpen()
            if wnd is not None and not wnd.destroyed:
                wnd.OnItemSplit(itemID, qty)
                wnd.Refresh()
        return ret

    def GetSolarSystemIDForStationOrStructure(self, stationID):
        if util.IsStation(stationID):
            return sm.GetService('ui').GetStation(stationID).solarSystemID
        else:
            structureInfo = sm.GetService('structureDirectory').GetStructureInfo(stationID)
            if structureInfo is not None:
                return structureInfo.solarSystemID
            return

    def GetItemsInContainer(self, stationID, containerID, forCorp, flag):
        return self.contractProxySvc.GetItemsInContainer(stationID, containerID, forCorp, flag)

    def GetItemsInStation(self, stationID, forCorp):
        return self.contractProxySvc.GetItemsInStation(stationID, forCorp)

    def DeleteNotification(self, contractID, forCorp):
        self.ClearCache()
        return self.contractProxySvc.DeleteNotification(contractID, forCorp)

    def CollectMyPageInfo(self, force = False):
        mpi = util.KeyVal()
        skills = sm.GetService('skills').GetSkills()
        if self.myPageInfo is None or self.myPageInfo.timeout < blue.os.GetWallclockTime() or force:
            mpi = self.contractProxySvc.CollectMyPageInfo()
            skill = skills.get(const.typeContracting, None)
            lvl = getattr(skill, 'skillLevel', 0)
            skill = skills.get(const.typeCorporationContracting, None)
            lvlCorp = getattr(skill, 'skillLevel', 0)
            maxNumContracts = NUM_CONTRACTS_BY_SKILL[lvl]
            maxNumContractsCorp = NUM_CONTRACTS_BY_SKILL_CORP[lvlCorp]
            mpi.numContractsLeft = maxNumContracts - mpi.numOutstandingContractsNonCorp
            mpi.numContractsLeftForCorp = maxNumContractsCorp - mpi.numOutstandingContractsForCorp
            mpi.numContractsTotal = maxNumContracts
            mpi.numContractsLeftInCorp = MAX_NUM_CONTRACTS - mpi.numOutstandingContracts
            mpi.timeout = blue.os.GetWallclockTime() + CACHE_TIME * MINUTE
            self.myPageInfo = mpi
        else:
            self.LogInfo('CollectMyPageInfo returning cached result')
            mpi = self.myPageInfo
        return mpi

    def GetMyExpiredContractList(self):
        l = None
        if self.myExpiredContractList is None or self.myExpiredContractList.timeout < blue.os.GetWallclockTime():
            l = util.KeyVal(mySelf=None, myCorp=None, expires=0)
            l.mySelf = sm.ProxySvc('contractProxy').GetMyExpiredContractList(False)
            l.myCorp = sm.ProxySvc('contractProxy').GetMyExpiredContractList(True)
            l.timeout = blue.os.GetWallclockTime() + CACHE_TIME * MINUTE
            self.myExpiredContractList = l
        else:
            self.LogInfo('GetMyExpiredContractList returning cached result')
            l = self.myExpiredContractList
        return l

    def GetMyBids(self, forCorp):
        l = None
        val = getattr(self, 'myBids_%s' % forCorp, None)
        if val is None or val.timeout < blue.os.GetWallclockTime():
            l = util.KeyVal(mySelf=None, myCorp=None, expires=0)
            l.list = sm.ProxySvc('contractProxy').GetMyBids(forCorp)
            l.timeout = blue.os.GetWallclockTime() + CACHE_TIME * MINUTE
            setattr(self, 'myBids_%s' % forCorp, l)
        else:
            self.LogInfo('GetMyBids(', forCorp, ') returning cached result')
            l = val
        return l

    def GetMyCurrentContractList(self, isAccepted, forCorp):
        l = None
        val = getattr(self, 'myCurrentList_%s_%s' % (isAccepted, forCorp), None)
        if val is None or val.timeout < blue.os.GetWallclockTime():
            l = util.KeyVal(mySelf=None, myCorp=None, expires=0)
            l.list = sm.ProxySvc('contractProxy').GetMyCurrentContractList(isAccepted, forCorp)
            l.timeout = blue.os.GetWallclockTime() + CACHE_TIME * MINUTE
            setattr(self, 'myCurrentList_%s_%s' % (isAccepted, forCorp), l)
        else:
            self.LogInfo('GetMyCurrentContractList(', isAccepted, forCorp, ') returning cached result')
            l = val
        return l

    def ClearCache(self):
        setattr(self, 'myCurrentList_True_True', None)
        setattr(self, 'myCurrentList_True_False', None)
        setattr(self, 'myCurrentList_False_True', None)
        setattr(self, 'myCurrentList_False_False', None)
        setattr(self, 'myBids_False', None)
        setattr(self, 'myBids_True', None)
        self.myExpiredContractList = None
        self.myPageInfo = None
        sm.ScatterEvent('OnContractCacheCleared')

    def OpenJournal(self, status = 0, forCorp = 0):
        settings.user.tabgroups.Set('journalmaintabs', 2)
        sm.GetService('journal').GetWnd(new=True)
        wnd = util.KeyVal(forCorp=forCorp)
        sm.GetService('journal').ShowContracts(wnd, status)

    def OpenCreateContract(self, items = None, contract = None):
        if session.userType != const.userTypeTrial:
            CreateContractWnd.CloseIfOpen()
            CreateContractWnd.Open(recipientID=None, contractItems=items, copyContract=contract)
        else:
            uicore.cmd.OpenTrialUpsell(origin=ORIGIN_CONTRACTS, reason='CreateContract', message=localization.GetByLabel('UI/TrialUpsell/ContractRestrictionBody'))

    def OpenCreateContractFromIGB(self, contractType = None, stationID = None, itemIDs = None):
        if session.userType != const.userTypeTrial:
            CreateContractWnd.CloseIfOpen()
            CreateContractWnd.Open(recipientID=None, contractItems=None, copyContract=None, contractType=contractType, stationID=stationID, itemIDs=itemIDs)
        else:
            uicore.cmd.OpenTrialUpsell(origin=ORIGIN_CONTRACTS, reason='CreateContractIGB', message=localization.GetByLabel('UI/TrialUpsell/ContractRestrictionBody'))

    def OpenAvailableTab(self, view, reset = False, typeID = None, contractType = CONTYPE_AUCTIONANDITEMECHANGE):
        wnd = ContractsWindow.GetIfOpen()
        if wnd is not None:
            assigneeID = {3: const.conAvailMyself,
             4: const.conAvailMyCorp}.get(view, const.conAvailPublic)
            self.OpenSearchTab(typeID, None, None, None, None, None, assigneeID, contractType)

    def OpenSearchTab(self, *args):
        wnd = ContractsWindow.Open()
        blue.pyos.synchro.SleepWallclock(10)
        wnd.sr.maintabs.SelectByIdx(2)
        wnd.sr.contractSearchContent.FindRelated(*args)

    def AddIgnore(self, issuerID):
        ignoreList = settings.user.ui.Get('contracts_ignorelist', [])
        if len(ignoreList) >= MAX_IGNORED:
            raise UserError('ConIgnoreListFull', {'n': MAX_IGNORED})
        if issuerID not in ignoreList:
            ignoreList.append(issuerID)
        settings.user.ui.Set('contracts_ignorelist', ignoreList)
        self.ClearCache()
        sm.ScatterEvent('OnAddIgnore', issuerID)

    def OpenIgnoreList(self):
        IgnoreListWindow.CloseIfOpen()
        IgnoreListWindow.Open()

    def GetMessages(self):
        return self.messages

    def DeliverCourierContractFromItemID(self, itemID):
        info = self.contractProxySvc.GetCourierContractFromItemID(itemID)
        if info is None:
            raise UserError('ConContractNotFoundForCrate')
        contractID = info.contractID
        self.CompleteContract(contractID)

    def FindCourierContractFromItemID(self, itemID):
        info = self.contractProxySvc.GetCourierContractFromItemID(itemID)
        if info is None:
            raise UserError('ConContractNotFoundForCrate')
        self.ShowContract(info.contractID)

    @util.Memoized(1)
    def IsStationInaccessible(self, stationID):
        if stationID is None:
            return False
        if util.IsStation(stationID):
            station = sm.GetService('ui').GetStation(stationID)
            isPlayerOwnable = sm.GetService('godma').GetType(station.stationTypeID).isPlayerOwnable
            if isPlayerOwnable:
                if station.ownerID == session.corpid or stationID == session.stationid:
                    return False
                corpStationMgr = moniker.GetCorpStationManagerEx(stationID)
                try:
                    corpStationMgr.DoStandingCheckForStationService(const.stationServiceDocking)
                except UserError:
                    return True

        else:
            structure = sm.GetService('structureDirectory').GetStructureInfo(stationID)
            if structure:
                if stationID == session.structureid:
                    return False
                if sm.GetService('structureSettings').CharacterHasService(stationID, structures.SERVICE_DOCKING):
                    return False
            return True
        return False

    def CheckEndpointAccess(self, endpointID):
        if util.IsStation(endpointID):
            station = sm.GetService('ui').GetStation(endpointID)
            isPlayerOwnable = sm.GetService('godma').GetType(station.stationTypeID).isPlayerOwnable
            if isPlayerOwnable and station.ownerID != session.corpid and endpointID != session.stationid:
                header = localization.GetByLabel('UI/Common/Confirm')
                question = localization.GetByLabel('UI/Contracts/ContractsService/StartStationPositionInfo', startStation=endpointID, ownerName=cfg.eveowners.Get(station.ownerID).name)
                if eve.Message('CustomQuestion', {'header': header,
                 'question': question}, uiconst.YESNO) != uiconst.ID_YES:
                    return False
            return True
        structure = sm.GetService('structureDirectory').GetStructureInfo(endpointID)
        if structure is not None:
            if session.structureid == endpointID:
                return True
            linkInfo = ('showinfo', structure.typeID)
            header = localization.GetByLabel('UI/Common/Confirm')
            question = localization.GetByLabel('UI/Contracts/ContractsService/StructureMayBeInaccessible', structureID=endpointID, typeID=structure.typeID, linkinfo=linkInfo)
            if eve.Message('CustomQuestion', {'header': header,
             'question': question}, uiconst.YESNO) != uiconst.ID_YES:
                return False
            return True
        raise RuntimeError("Endpoint doesn't resolve to a station or player owned structure")

    def GetSystemSecurityDot(self, solarSystemID):
        sec, col = util.FmtSystemSecStatus(sm.GetService('map').GetSecurityStatus(solarSystemID), 1)
        col.a = 1.0
        colString = hex(col.AsInt() & 4294967295L)
        return u'<color=%s>\u2022</color>' % colString
