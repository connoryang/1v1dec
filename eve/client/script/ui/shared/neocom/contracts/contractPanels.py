#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\neocom\contracts\contractPanels.py
import uiutil
import uix
import uthread
import util
from carbonui import const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.frame import Frame
from eve.client.script.ui.control import entries as listentry
from eve.client.script.ui.control.buttons import Button
from eve.client.script.ui.control.eveCombo import Combo
from eve.client.script.ui.control.eveLabel import EveCaptionLarge
from eve.client.script.ui.control.eveScroll import Scroll
from eve.client.script.ui.control.eveSinglelineEdit import SinglelineEdit
from eve.client.script.util.contractutils import IsSearchStringLongEnough, ConFmtDate, GetColoredContractStatusText
from eve.common.script.util.contractscommon import CONTYPE_AUCTIONANDITEMECHANGE
from localization import GetByLabel
import blue
RESULTS_PER_PAGE = 100
MAX_IGNORED = 1000

class StartPagePanel(Container):
    __notifyevents__ = ['OnContractCacheCleared']
    __guid__ = 'xtriui.StartPagePanel'
    inited = 0
    submitFunc = None

    def Init(self):
        scrollEntries = []

        def AddItem(icon, header, text, url = None, isSmall = False):
            if url:
                header = '<url=localsvc:service=contracts&%s>%s</url>' % (url, header.rstrip('\n'))
            else:
                header = header.rstrip('\n')
            text = text.rstrip('\n')
            data = {'header': header,
             'text': text,
             'icon': icon,
             'isSmall': isSmall}
            entry = listentry.Get('ContractStartPageEntry', data)
            scrollEntries.append(entry)

        if not getattr(self, 'startPageScroll', None):
            header = EveCaptionLarge(text=GetByLabel('UI/Contracts/ContractEntry/MyStartPage'), parent=self, left=const.defaultPadding * 2, top=const.defaultPadding)
            self.startPageScroll = Scroll(parent=self, align=uiconst.TOALL, padding=(const.defaultPadding,
             header.textheight + const.defaultPadding * 2,
             const.defaultPadding,
             const.defaultPadding))
            self.startPageScroll.HideBackground()
            self.startPageScroll.RemoveActiveFrame()
            Frame(parent=self.startPageScroll, color=(1.0, 1.0, 1.0, 0.2))
            self.inited = 1
            sm.RegisterNotify(self)
        mpi = sm.GetService('contracts').CollectMyPageInfo()
        n = mpi.numContractsLeft
        ntot = mpi.numContractsTotal
        np = mpi.numContractsLeftInCorp
        nforcorp = mpi.numContractsLeftForCorp
        desc = GetByLabel('UI/Contracts/ContractsService/YouCanCreateNew', numContracts=ntot)
        if not util.IsNPC(eve.session.corpid):
            desc += '<br>' + GetByLabel('UI/Contracts/ContractsService/YouCanCreateForCorp', numContracts=np)
        if session.corprole & const.corpRoleContractManager == const.corpRoleContractManager:
            desc += '<br>' + GetByLabel('UI/Contracts/ContractsService/YouCanCreateOnBehalfOfCorp', numContracts=nforcorp)
        createLabel = GetByLabel('UI/Contracts/ContractsService/YouCanCreate', numContracts=n)
        AddItem('res:/ui/Texture/WindowIcons/contracts.png', createLabel, desc, 'method=OpenCreateContract')
        ignoreList = set(settings.user.ui.Get('contracts_ignorelist', []))
        numAssignedToMeAuctionItemExchange = 0
        numAssignedToMeCourier = 0
        numAssignedToMyCorpAuctionItemExchange = 0
        numAssignedToMyCorpCourier = 0
        if mpi.outstandingContracts is None:
            eve.Message('ConNotReady')
            mpi.outstandingContracts = []
        else:
            for contract in mpi.outstandingContracts:
                if contract[0] in ignoreList or contract[1] in ignoreList:
                    continue
                if contract[2] == session.charid:
                    if contract[3] == const.conTypeCourier:
                        numAssignedToMeCourier += 1
                    else:
                        numAssignedToMeAuctionItemExchange += 1
                elif contract[3] == const.conTypeCourier:
                    numAssignedToMyCorpCourier += 1
                else:
                    numAssignedToMyCorpAuctionItemExchange += 1

        if mpi.numRequiresAttention > 0:
            attentionReqLabel = GetByLabel('UI/Contracts/ContractsService/RequireAttention', numContracts=mpi.numRequiresAttention)
            attentionReqDescLabel = GetByLabel('UI/Contracts/ContractsService/RequiresAttentionDesc')
            AddItem('res:/ui/Texture/WindowIcons/warning.png', attentionReqLabel, attentionReqDescLabel, 'method=OpenJournal&status=0&forCorp=0')
        if mpi.numRequiresAttentionCorp > 0:
            attentionReqCorpLabel = GetByLabel('UI/Contracts/ContractsService/RequireAttentionCorp', numContracts=mpi.numRequiresAttentionCorp)
            attentionReqCorpDescLabel = GetByLabel('UI/Contracts/ContractsService/RequireAttentionCorpDesc')
            AddItem('res:/ui/Texture/WindowIcons/warning.png', attentionReqCorpLabel, attentionReqCorpDescLabel, 'method=OpenJournal&forCorp=1')
        if numAssignedToMeAuctionItemExchange > 0 or numAssignedToMeCourier > 0:
            assignedLabel = GetByLabel('UI/Contracts/ContractsService/AssignedPersonal', numContracts=numAssignedToMeAuctionItemExchange + numAssignedToMeCourier)
            subText = ''
            subTextList = []
            if numAssignedToMeAuctionItemExchange > 0:
                auctionLabel = GetByLabel('UI/Contracts/ContractsService/AuctionItemExchange', numContracts=numAssignedToMeAuctionItemExchange)
                method = self._GetContractMethodText(CONTYPE_AUCTIONANDITEMECHANGE, isCorp=0)
                subText += self._GetContractLink(auctionLabel, method)
            if numAssignedToMeCourier > 0:
                assignedCourierLabel = GetByLabel('UI/Contracts/ContractsService/AssignedCourier', numContracts=numAssignedToMeCourier)
                method = self._GetContractMethodText(const.conTypeCourier, isCorp=0)
                subText += self._GetContractLink(assignedCourierLabel, method, numSpaces=2)
            AddItem('res:/ui/Texture/WindowIcons/info.png', assignedLabel, subText)
        if numAssignedToMyCorpAuctionItemExchange > 0 or numAssignedToMyCorpCourier > 0:
            numContracts = numAssignedToMyCorpAuctionItemExchange + numAssignedToMyCorpCourier
            corpAssignedLabel = GetByLabel('UI/Contracts/ContractsService/AssignedCorp', numContracts=numContracts)
            subText = ''
            if numAssignedToMyCorpAuctionItemExchange > 0:
                corpExchangeLabel = GetByLabel('UI/Contracts/ContractsService/AssignedCorpAuctionItemExchange', numContracts=numAssignedToMyCorpAuctionItemExchange)
                method = self._GetContractMethodText(CONTYPE_AUCTIONANDITEMECHANGE, isCorp=1)
                subText += self._GetContractLink(corpExchangeLabel, method)
            if numAssignedToMyCorpCourier > 0:
                corpCourierLabel = GetByLabel('UI/Contracts/ContractsService/AssignedCorpCourier', numContracts=numAssignedToMyCorpCourier)
                method = self._GetContractMethodText(const.conTypeCourier, isCorp=1)
                subText += self._GetContractLink(corpCourierLabel, method)
            AddItem('res:/ui/Texture/WindowIcons/info.png', corpAssignedLabel, subText)
        if mpi.numBiddingOn > 0:
            activeLabel = GetByLabel('UI/Contracts/ContractsService/BiddingOn', numAuctions=mpi.numBiddingOn)
            activeDescLabel = GetByLabel('UI/Contracts/ContractsService/BiddingOnDesc')
            AddItem('64_16', activeLabel, activeDescLabel, 'method=OpenJournal&status=3&forCorp=0')
        if mpi.numInProgress > 0:
            progressLabel = GetByLabel('UI/Contracts/ContractsService/InProgress', numContracts=mpi.numInProgress)
            progressDescLabel = GetByLabel('UI/Contracts/ContractsService/InProgressDesc')
            AddItem('res:/ui/Texture/WindowIcons/info.png', progressLabel, progressDescLabel, 'method=OpenJournal&status=2&forCorp=0')
        if mpi.numBiddingOnCorp > 0:
            biddingOnLabel = GetByLabel('UI/Contracts/ContractsService/BiddingOnCorp', numAuctions=mpi.numBiddingOnCorp)
            biddingOnDescLabel = GetByLabel('UI/Contracts/ContractsService/BiddingOnCorpDesc')
            AddItem('64_16', biddingOnLabel, biddingOnDescLabel, 'method=OpenJournal&status=3&forCorp=1')
        if mpi.numInProgressCorp > 0:
            inProgressCorpLabel = GetByLabel('UI/Contracts/ContractsService/InProgressCorp', numContracts=mpi.numInProgressCorp)
            inProgressCorpDescLabel = GetByLabel('UI/Contracts/ContractsService/InProgressCorpDesc')
            AddItem('res:/ui/Texture/WindowIcons/info.png', inProgressCorpLabel, inProgressCorpDescLabel, 'method=OpenJournal&status=2&forCorp=1')
        ignoreList = settings.user.ui.Get('contracts_ignorelist', [])
        l = len(ignoreList)
        if l > 0:
            ignoreLabel = GetByLabel('UI/Contracts/ContractsService/Ignoring', numIssuers=l)
            ignoreDescLabel = GetByLabel('UI/Contracts/ContractsService/IngoringDesc', numIssuers=MAX_IGNORED)
            AddItem('ui_38_16_208', ignoreLabel, ignoreDescLabel, 'method=OpenIgnoreList', isSmall=True)
        mess = sm.GetService('contracts').GetMessages()
        for i in mess:
            AddItem('ui_38_16_208', '', i, isSmall=True)

        self.startPageScroll.LoadContent(contentList=scrollEntries)

    def _GetContractMethodText(self, contractType, isCorp):
        methodTextCorp = 'method=OpenAssignedToMe&contractType=%s&isCorp=%s' % (contractType, isCorp)
        return methodTextCorp

    def _GetContractLink(self, label, method, numSpaces = 1):
        link = ' ' * numSpaces
        link += '- <a href="localsvc:service=contracts&%s">%s</a><br>' % (method, label)
        return link

    def OnContractCacheCleared(self, *args):
        if self.IsVisible():
            self.Init()

    def IsVisible(self):
        tabs = uiutil.FindChild(self.parent.parent, 'contractsTabs')
        selectedTab = tabs.GetVisible()
        return selectedTab.name == 'startPageParent'


class MyContractsPanel(Container):
    __guid__ = 'xtriui.MyContractsPanel'
    inited = 0
    submitFunc = None

    def _OnClose(self):
        Container._OnClose(self)
        if self.inited:
            settings.user.ui.Set('mycontracts_filter_tofrom', self.sr.fltToFrom.GetValue())
            settings.char.ui.Set('mycontracts_filter_owner', self.sr.fltOwner.GetValue())
            settings.user.ui.Set('mycontracts_filter_status', self.sr.fltStatus.GetValue())
            settings.user.ui.Set('mycontracts_filter_type', self.sr.fltType.GetValue())

    def Init(self):
        if not self.inited:
            self.WriteFilters()
            self.sr.contractlistParent = contractlistParent = Container(name='contractlistParent', align=uiconst.TOALL, pos=(const.defaultPadding,
             const.defaultPadding,
             const.defaultPadding,
             const.defaultPadding), parent=self)
            self.sr.contractlist = contractlist = Scroll(parent=contractlistParent, name='mycontractlist')
            contractlist.sr.id = 'mycontractlist'
            contractlist.ShowHint(GetByLabel('UI/Contracts/ContractsWindow/ClickGetContracts'))
            contractlist.multiSelect = 0
            contractlistParent.top = 5
            self.currPage = 0
            self.pages = {0: None}
            self.fetchingContracts = 0
        self.inited = 1

    def WriteFilters(self):
        self.sr.filters = filters = Container(name='filters', parent=self, height=34, align=uiconst.TOTOP)
        top = 16
        left = 5
        options = [(GetByLabel('UI/Contracts/ContractsWindow/IssuedToBy'), None), (GetByLabel('UI/Contracts/ContractsWindow/IssuedBy'), False), (GetByLabel('UI/Contracts/ContractsWindow/IssuedTo'), True)]
        c = self.sr.fltToFrom = Combo(label=GetByLabel('UI/Contracts/ContractsWindow/Action'), parent=filters, options=options, name='tofrom', select=settings.user.ui.Get('mycontracts_filter_tofrom', None), callback=self.OnComboChange, pos=(left,
         top,
         0,
         0), adjustWidth=True)
        left += c.width + 5
        corpName = cfg.eveowners.Get(eve.session.corpid).name
        charName = cfg.eveowners.Get(eve.session.charid).name
        val = getattr(self, 'lookup', None)
        if not val:
            val = settings.char.ui.Get('mycontracts_filter_owner', charName)
        self.sr.fltOwner = c = SinglelineEdit(name='edit', parent=filters, width=120, label=GetByLabel('UI/Contracts/ContractsWindow/Owner'), setvalue=val, left=left, top=top)
        left += c.width + 5
        ops = [(charName, charName), (corpName, corpName)]
        c.LoadCombo('usernamecombo', ops, self.OnComboChange)
        self.status = [(GetByLabel('UI/Contracts/ContractEntry/Outstanding'), const.conStatusOutstanding), (GetByLabel('UI/Contracts/ContractsWindow/InProgress'), const.conStatusInProgress), (GetByLabel('UI/Contracts/ContractsWindow/Finished'), const.conStatusFinished)]
        c = self.sr.fltStatus = Combo(label=GetByLabel('UI/Contracts/ContractsWindow/Status'), parent=filters, options=self.status, name='status', select=settings.user.ui.Get('mycontracts_filter_status', None), callback=self.OnComboChange, pos=(left,
         top,
         0,
         0))
        left += c.width + 5
        mrk = '----------'
        fltTypeOptions = [(GetByLabel('UI/Common/All'), None),
         (mrk, -1),
         (GetByLabel('UI/Contracts/Auction'), const.conTypeAuction),
         (GetByLabel('UI/Contracts/ContractsWindow/ItemExchange'), const.conTypeItemExchange),
         (GetByLabel('UI/Contracts/ContractsWindow/Courier'), const.conTypeCourier)]
        self.sr.fltType = c = Combo(label=GetByLabel('UI/Contracts/ContractsWindow/ContractType'), parent=filters, options=fltTypeOptions, name='types', select=settings.user.ui.Get('mycontracts_filter_type', None), callback=self.OnComboChange, pos=(left,
         top,
         0,
         0))
        left += c.width + 5
        self.sr.submitBtn = submit = Button(parent=filters, label=GetByLabel('UI/Contracts/ContractsWindow/GetContracts'), func=self.FetchContracts, pos=(const.defaultPadding,
         top,
         0,
         0), align=uiconst.TOPRIGHT)
        sidepar = Container(name='sidepar', parent=filters, align=uiconst.BOTTOMRIGHT, left=const.defaultPadding, width=54, height=30)
        btn = uix.GetBigButton(24, sidepar, 4, 6)
        btn.state = uiconst.UI_HIDDEN
        btn.OnClick = (self.BrowseMyContracts, -1)
        btn.hint = GetByLabel('UI/Common/Previous')
        btn.sr.icon.LoadIcon('ui_23_64_1')
        self.sr.transMyBackBtn = btn
        btn = uix.GetBigButton(24, sidepar, 28, 6)
        btn.state = uiconst.UI_HIDDEN
        btn.OnClick = (self.BrowseMyContracts, 1)
        btn.hint = GetByLabel('UI/Common/ViewMore')
        btn.sr.icon.LoadIcon('ui_23_64_2')
        self.sr.transMyFwdBtn = btn
        sidepar.left = submit.width + const.defaultPadding

    def BrowseMyContracts(self, direction, *args):
        self.currPage = max(0, self.currPage + direction)
        self.DoFetchContracts()

    def FetchContracts(self, *args):
        if self.fetchingContracts:
            return
        self.sr.submitBtn.Disable()
        self.fetchingContracts = 1
        uthread.new(self.EnableButtonTimer)
        self.currPage = 0
        self.pages = {0: None}
        self.DoFetchContracts()

    def EnableButtonTimer(self):
        blue.pyos.synchro.SleepWallclock(5000)
        try:
            self.fetchingContracts = 0
            self.sr.submitBtn.Enable()
        except:
            pass

    def DoFetchContracts(self):
        self.sr.contractlist.Load(contentList=[])
        self.sr.contractlist.ShowHint(GetByLabel('UI/Contracts/ContractsWindow/FetchingData'))
        try:
            if self.currPage == 0:
                self.sr.transMyBackBtn.state = uiconst.UI_HIDDEN
            else:
                self.sr.transMyBackBtn.state = uiconst.UI_NORMAL
            isAccepted = self.sr.fltToFrom.GetValue()
            ownerName = self.sr.fltOwner.GetValue()
            ownerID = None
            if ownerName == cfg.eveowners.Get(eve.session.charid).name:
                ownerID = eve.session.charid
            elif ownerName == cfg.eveowners.Get(eve.session.corpid).name:
                ownerID = eve.session.corpid
            elif IsSearchStringLongEnough(ownerName):
                ownerID = uix.Search(ownerName.lower(), None, const.categoryOwner, hideNPC=1, exact=1, searchWndName='contractOwnerNameSearch')
            if ownerID == None:
                return
            filtStatus = int(self.sr.fltStatus.GetValue())
            contractType = self.sr.fltType.GetValue()
            startContractID = self.pages.get(self.currPage, None)
            _contracts = sm.ProxySvc('contractProxy').GetContractListForOwner(ownerID, filtStatus, contractType, isAccepted, num=RESULTS_PER_PAGE, startContractID=startContractID)
            contracts = _contracts.contracts
            ownerIDs = set()
            for r in contracts:
                ownerIDs.add(r.issuerID)
                ownerIDs.add(r.issuerCorpID)
                ownerIDs.add(r.acceptorID)
                ownerIDs.add(r.assigneeID)

            if 0 in ownerIDs:
                ownerIDs.remove(0)
            cfg.eveowners.Prime(ownerIDs)
            scrolllist = []
            for c in contracts:
                timeLeftValue = 0
                additionalColumns = ''
                if filtStatus == const.conStatusOutstanding:
                    issued = {False: util.FmtDate(c.dateIssued, 'ss'),
                     True: '-'}[c.type == const.conTypeAuction and c.issuerID != eve.session.charid]
                    timeLeftValue = c.dateExpired - blue.os.GetWallclockTime()
                    additionalColumns = '<t>%s<t>%s' % (issued, ConFmtDate(timeLeftValue, c.type == const.conTypeAuction))
                elif filtStatus == const.conStatusInProgress:
                    timeLeftValue = c.dateAccepted + const.DAY * c.numDays - blue.os.GetWallclockTime()
                    additionalColumns = '<t>%s<t>%s' % (util.FmtDate(c.dateAccepted, 'ss'), ConFmtDate(timeLeftValue, c.type == const.conTypeAuction))
                else:
                    additionalColumns = '<t>%s<t>%s' % (GetColoredContractStatusText(c.status), util.FmtDate(c.dateCompleted, 'ss'))
                additionalColumns += '<t>%s' % c.title
                text = '...'
                data = {'contract': c,
                 'contractItems': _contracts.items.get(c.contractID, []),
                 'status': filtStatus,
                 'text': text,
                 'label': text,
                 'additionalColumns': additionalColumns,
                 'callback': self.OnSelectContract,
                 'sort_%s' % GetByLabel('UI/Common/Contract'): text,
                 'sort_%s' % GetByLabel('UI/Contracts/ContractsWindow/DateCompleted'): -c.dateCompleted,
                 'sort_%s' % GetByLabel('UI/Contracts/ContractsWindow/TimeLeft'): timeLeftValue}
                scrolllist.append(listentry.Get('ContractEntrySmall', data))

            headers = [GetByLabel('UI/Common/Contract'),
             GetByLabel('UI/Common/Type'),
             GetByLabel('UI/Common/From'),
             GetByLabel('UI/Common/To')]
            if filtStatus == const.conStatusOutstanding:
                headers.extend([GetByLabel('UI/Contracts/ContractsWindow/DateIssued'), GetByLabel('UI/Contracts/ContractsWindow/TimeLeft')])
            elif filtStatus == const.conStatusInProgress:
                headers.extend([GetByLabel('UI/Contracts/ContractsWindow/DateAccepted'), GetByLabel('UI/Contracts/ContractsWindow/TimeLeft')])
            else:
                headers.extend([GetByLabel('UI/Contracts/ContractsWindow/Status'), GetByLabel('UI/Contracts/ContractsWindow/DateCompleted')])
            headers.append(GetByLabel('UI/Contracts/ContractsWindow/InfoByIssuer'))
            self.sr.contractlist.ShowHint()
            self.sr.contractlist.Load(contentList=scrolllist, headers=headers)
            if len(scrolllist) == 0:
                self.sr.contractlist.ShowHint(GetByLabel('UI/Contracts/ContractEntry/NoContractsFound'))
            if len(contracts) >= 2:
                self.pages[self.currPage] = contracts[0].contractID
                self.pages[self.currPage + 1] = contracts[-1].contractID
            if len(scrolllist) < RESULTS_PER_PAGE:
                self.sr.transMyFwdBtn.state = uiconst.UI_HIDDEN
            else:
                self.sr.transMyFwdBtn.state = uiconst.UI_NORMAL
        except UserError:
            self.sr.contractlist.ShowHint(GetByLabel('UI/Contracts/ContractEntry/NoContractsFound'))
            raise

    def OnComboChange(self, obj, *args):
        if obj == self.sr.fltType and self.sr.fltType.GetValue() == -1:
            self.sr.fltType.SetValue(None)

    def OnSelectContract(self, *args):
        pass
