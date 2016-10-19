#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\neocom\contracts\createContractWnd.py
import math
import sys
from collections import defaultdict
import base
import evetypes
import uicontrols
import uiutil
import uix
import uthread
import util
import log
from carbon.common.script.util.linkUtil import GetShowInfoLink
from carbonui import const as uiconst
from carbonui.primitives.line import Line
from carbonui.primitives.container import Container
from eve.client.script.ui.control import entries as listentry
from eve.client.script.ui.util import searchUtil
from eve.client.script.ui.util.form import FormWnd
from contractutils import *
from inventorycommon.util import GetItemVolume
from localization import GetByLabel
import blue
MIN_CONTRACT_MONEY = 1000

class CreateContractWnd(uicontrols.Window):
    __guid__ = 'form.CreateContract'
    __notifyevents__ = ['OnDeleteContract']
    default_windowID = 'createcontract'

    def ApplyAttributes(self, attributes):
        uicontrols.Window.ApplyAttributes(self, attributes)
        self.ResetWizard()
        recipientID = attributes.recipientID
        contractItems = attributes.contractItems
        copyContract = attributes.copyContract
        stationID = attributes.stationID
        flag = attributes.flag
        itemIDs = attributes.itemIDs
        if stationID and not self.CanContractItemsFromLocation(stationID):
            stationID = None
        if stationID:
            self.data.startStation = stationID
            self.data.startStationDivision = const.flagHangar
        if flag:
            self.data.startStationDivision = flag
        if attributes.contractType:
            self.data.type = attributes.contractType
        else:
            self.contractType = const.conTypeNothing
        self.data.items = {}
        self.data.childItems = {}
        if stationID and itemIDs:
            foundItems = []
            itemsInStation = sm.GetService('contracts').GetItemsInStation(self.data.startStation, False)
            for item in itemsInStation:
                if item.itemID in itemIDs:
                    foundItems.append(item)

            if foundItems:
                self.data.startStationDivision = foundItems[0].flagID
                for item in foundItems:
                    self.data.items[item.itemID] = [item.typeID, item.stacksize, item]

        self.currPage = 0
        self.NUM_STEPS = 4
        self.CREATECONTRACT_TITLES = {const.conTypeNothing: [GetByLabel('UI/Contracts/ContractsWindow/SelectContractType'),
                                '',
                                '',
                                ''],
         const.conTypeAuction: [GetByLabel('UI/Contracts/ContractsWindow/SelectContractType'),
                                GetByLabel('UI/Contracts/ContractsWindow/PickItems'),
                                GetByLabel('UI/Contracts/ContractsWindow/SelectOptions'),
                                GetByLabel('UI/Common/Confirm')],
         const.conTypeItemExchange: [GetByLabel('UI/Contracts/ContractsWindow/SelectContractType'),
                                     GetByLabel('UI/Contracts/ContractsWindow/PickItems'),
                                     GetByLabel('UI/Contracts/ContractsWindow/SelectOptions'),
                                     GetByLabel('UI/Common/Confirm')],
         const.conTypeCourier: [GetByLabel('UI/Contracts/ContractsWindow/SelectContractType'),
                                GetByLabel('UI/Contracts/ContractsWindow/PickItems'),
                                GetByLabel('UI/Contracts/ContractsWindow/SelectOptions'),
                                GetByLabel('UI/Common/Confirm')]}
        self.isContractMgr = eve.session.corprole & const.corpRoleContractManager == const.corpRoleContractManager
        self.SetWndIcon(GetContractIcon(const.conTypeNothing), mainTop=-10)
        self.SetCaption(GetByLabel('UI/Inventory/ItemActions/CreateContract'))
        self.SetMinSize([400, 345])
        self.NoSeeThrough()
        self.SetScope('all')
        main = self.sr.main
        uix.Flush(self.sr.main)
        self.marketTypes = sm.GetService('contracts').GetMarketTypes()
        self.sr.pageWnd = {}
        self.lockedItems = {}
        self.state = uiconst.UI_NORMAL
        self.blockconfirmonreturn = 1
        setattr(self, 'first', True)
        if contractItems is not None:
            self._SetStartVariablesInData(contractItems)
        self.buttons = [(GetByLabel('UI/Common/Cancel'),
          self.OnCancel,
          (),
          84), (GetByLabel('UI/Common/Previous'),
          self.OnStepChange,
          -1,
          84), (GetByLabel('UI/Common/Next'),
          self.OnStepChange,
          1,
          84)]
        self.sr.buttonWnd = uicontrols.ButtonGroup(btns=self.buttons, parent=self.sr.main, unisize=1)
        self.sr.buttonCancel = self.sr.buttonWnd.GetBtnByIdx(0)
        self.sr.buttonPrev = self.sr.buttonWnd.GetBtnByIdx(1)
        self.sr.buttonNext = self.sr.buttonWnd.GetBtnByIdx(2)
        if copyContract:
            self.CopyContract(copyContract)
        self.formWnd = FormWnd(name='form', align=uiconst.TOALL, pos=(0, 0, 0, 0), parent=self.sr.main)
        self.GotoPage(0)
        return self

    def _SetStartVariablesInData(self, contractItems):
        firstItem = contractItems[0]
        startStation = sm.StartService('invCache').GetStationIDOfItem(firstItem)
        if not self.CanContractItemsFromLocation(startStation):
            return
        self.data.startStation = startStation
        dataItems = {}
        for item in contractItems:
            dataItems[item.itemID] = [item.typeID, item.stacksize, item]
            if item.ownerID == session.corpid:
                if not self.isContractMgr:
                    raise UserError('ConNotContractManager')
                self.data.forCorp = True
                self.data.startStation = sm.StartService('invCache').GetStationIDOfItem(item)
                self.data.startStationDivision = item.flagID
            elif item.ownerID != session.charid:
                raise RuntimeError('Not your item!')

        self.data.items = dataItems

    def CopyContract(self, contract):
        c = contract.contract
        self.data.type = c.type
        self.data.startStation = c.startStationID
        self.data.endStation = c.endStationID
        expireTime = 1440 * ((c.dateExpired - c.dateIssued) / const.DAY)
        self.data.expiretime = expireTime
        self.data.duration = c.numDays
        self.data.description = c.title
        self.data.assigneeID = c.assigneeID
        if c.availability == 0:
            self.data.avail = 0
        elif c.assigneeID == session.corpid:
            self.data.avail = 2
            self.data.assigneeID = None
        elif session.allianceid and c.assigneeID == session.allianceid:
            self.data.avail = 3
            self.data.assigneeID = None
        else:
            self.data.avail = 1
        if self.data.assigneeID:
            self.data.name = cfg.eveowners.Get(self.data.assigneeID).name
        self.data.price = c.price
        self.data.reward = c.reward
        self.data.collateral = c.collateral
        self.data.forCorp = c.forCorp
        self.data.reqItems = {}
        requestItems = defaultdict(int)
        sellItems = defaultdict(int)
        if self.data.type == const.conTypeCourier:
            uthread.new(eve.Message, 'ConCopyContractCourier')
        foundBlueprint = False
        if contract.items:
            for contractItem in contract.items:
                if contractItem.inCrate:
                    if evetypes.GetCategoryID(contractItem.itemTypeID) == const.categoryBlueprint:
                        foundBlueprint = True
                    sellItems[contractItem.itemTypeID] += contractItem.quantity
                else:
                    requestItems[contractItem.itemTypeID] += contractItem.quantity

            for typeID, quantity in requestItems.iteritems():
                self.data.reqItems[typeID] = quantity

            self.data.items = {}
            self.data.childItems = {}
            if sellItems:
                foundItems = defaultdict(list)
                itemsInStation = sm.GetService('contracts').GetItemsInStation(self.data.startStation, self.data.forCorp)
                for item in itemsInStation:
                    if item.typeID in sellItems and sellItems[item.typeID] == item.stacksize:
                        for foundItem in foundItems[item.flagID]:
                            if item.typeID == foundItem.typeID:
                                break
                        else:
                            foundItems[item.flagID].append(item)

                flagID = const.flagHangar
                if len(foundItems) > 1:
                    maxLen = 0
                    l = []
                    for flag, itemList in foundItems.iteritems():
                        if len(itemList) > maxLen or len(itemList) == maxLen and flag == const.flagHangar:
                            l = itemList
                            flagID = flag

                    foundItems = l
                elif len(foundItems) == 1:
                    foundItems = foundItems.values()[0]
                notFound = []
                for typeID, quantity in sellItems.iteritems():
                    for item in foundItems:
                        if item.typeID == typeID and item.stacksize == quantity:
                            break
                    else:
                        notFound.append((typeID, quantity))

                if notFound:
                    types = ''
                    for t, q in notFound:
                        typeXquantityLabel = GetByLabel('UI/Contracts/ContractsService/NameXQuantity', typeID=t, quantity=q)
                        types += u'  \u2022' + typeXquantityLabel + '<br>'

                    uthread.new(eve.Message, 'ConCopyContractMissingItems', {'types': types})
                if foundItems:
                    self.data.startStationDivision = foundItems[0].flagID
                    for item in foundItems:
                        self.data.items[item.itemID] = [item.typeID, item.stacksize, item]

        if foundBlueprint:
            uthread.new(eve.Message, 'ConCopyContractBlueprint')

    def _OnClose(self, *args):
        self.UnlockItems()

    def Refresh(self):
        self.GotoPage(self.currPage)

    def Confirm(self, *args):
        pass

    def SetTitle(self):
        pageTitle = self.CREATECONTRACT_TITLES[self.data.type][self.currPage]
        titleLabel = GetByLabel('UI/Contracts/ContractsService/PageOfTotal', pageTitle=pageTitle, pageNum=self.currPage + 1, numPages=self.NUM_STEPS)
        title = titleLabel
        if self.sr.Get('windowCaption', None) is None:
            self.sr.windowCaption = uicontrols.EveCaptionMedium(text=title, parent=self.sr.topParent, align=uiconst.RELATIVE, left=60, top=18, state=uiconst.UI_DISABLED)
        else:
            self.sr.windowCaption.text = title

    def UnlockItems(self):
        for i in self.lockedItems.iterkeys():
            sm.StartService('invCache').UnlockItem(i)

        self.lockedItems = {}

    def LockItems(self, itemIDs):
        for i, item in itemIDs.iteritems():
            self.lockedItems[i] = i
            userErrorDict = {'typeID': item[0],
             'action': GetByLabel('UI/Contracts/ContractsWindow/CreatingContract').lower()}
            sm.StartService('invCache').TryLockItem(i, 'lockItemContractFunction', userErrorDict, 1)

    def GotoPage(self, n):
        uthread.Lock(self)
        try:
            if n < 2:
                self.UnlockItems()
            self.currPage = n
            self.SetTitle()
            for p in self.sr.pageWnd:
                self.sr.pageWnd[p].state = uiconst.UI_HIDDEN

            uix.Flush(self.formWnd)
            format = []
            self.form = retfields = reqresult = errorcheck = []
            self.sr.buttonNext.SetLabel(GetByLabel('/Carbon/UI/Common/Next'))
            self.sr.buttonPrev.state = uiconst.UI_NORMAL
            contractIconType = const.conTypeNothing if n == 0 else self.data.type
            self.SetWndIcon(GetContractIcon(contractIconType), mainTop=-10)
            if n == 0:
                retfields, reqresult, errorcheck = self.BuildPage0()
            elif n == 1:
                self.WriteSelectItems(GetByLabel('UI/Contracts/ContractsWindow/SelectStationToGetItems'))
            elif n == 2:
                errorcheck, reqresult, retfields = self.BuildPage2()
            elif n == 3:
                self.BuildPage3()
            self.formdata = [retfields, reqresult, errorcheck]
        finally:
            uthread.UnLock(self)

    def BuildPage0(self):
        self.sr.buttonPrev.state = uiconst.UI_HIDDEN
        Container(name='push', parent=self.formWnd, align=uiconst.TOLEFT, width=const.defaultPadding)
        s = [0,
         0,
         0,
         0,
         0,
         0,
         0]
        s[self.data.type] = 1
        if self.data.type == const.conTypeNothing:
            s[const.conTypeItemExchange] = 1
        format = []
        format += self.Page0_GetContractTypeOptions(s)
        s = [0,
         0,
         0,
         0]
        s[getattr(self.data, 'avail', 0)] = 1
        format += self.Page0_GetAvailabilityOptions(s)
        forCorp = getattr(self.data, 'forCorp', 0)
        if self.isContractMgr:
            corpAcctName = sm.GetService('corp').GetMyCorpAccountName() or GetByLabel('UI/Common/None')
            behalfLabel = GetByLabel('UI/Contracts/ContractsService/OnBehalfOfCorp', corpName=cfg.eveowners.Get(eve.session.corpid).name, corpAccountName=corpAcctName)
            format += [{'type': 'btline'}]
            format += [{'type': 'checkbox',
              'label': '_hide',
              'key': 'forCorp',
              'text': behalfLabel,
              'required': 1,
              'frame': 0,
              'setvalue': forCorp,
              'onchange': self.OnForCorpChange}]
        else:
            format += [{'type': 'data',
              'key': 'forCorp',
              'data': {'forCorp': 0}}]
        uthread.new(self.WriteNumContractsAndLimitsLazy)
        limitsParent = Container(name='limitsParent', parent=self.formWnd, align=uiconst.TOBOTTOM, height=10, idx=0)
        outstandingContractsLabel = GetByLabel('UI/Contracts/ContractsService/OutstandingContractsUnknown')
        labelText = '<color=0xff999999>%s</color>' % outstandingContractsLabel
        self.limitTextWnd = uicontrols.EveLabelSmall(text=labelText, parent=limitsParent, left=6, state=uiconst.UI_DISABLED)
        self.form, retfields, reqresult, self.panels, errorcheck, refresh = sm.GetService('form').GetForm(format, self.formWnd)
        nameEditField = uiutil.FindChild(self.form, 'edit_name')
        privateCheckbox = uiutil.FindChild(self.form, 'privateCb')
        if nameEditField and privateCheckbox:
            nameEditField.OnChange = lambda *args: self.OnChangePrivateName(privateCheckbox, *args)
        return (retfields, reqresult, errorcheck)

    def Page0_GetContractTypeOptions(self, s):
        format = [{'type': 'text',
          'text': GetByLabel('UI/Contracts/ContractType')},
         {'type': 'checkbox',
          'label': '_hide',
          'key': const.conTypeItemExchange,
          'text': GetByLabel('UI/Contracts/ContractsWindow/ItemExchange'),
          'required': 1,
          'frame': 0,
          'setvalue': s[const.conTypeItemExchange],
          'group': 'type'},
         {'type': 'checkbox',
          'label': '_hide',
          'key': const.conTypeAuction,
          'text': GetByLabel('UI/Contracts/Auction'),
          'required': 1,
          'frame': 0,
          'setvalue': s[const.conTypeAuction],
          'group': 'type'},
         {'type': 'checkbox',
          'label': '_hide',
          'key': const.conTypeCourier,
          'text': GetByLabel('UI/Contracts/ContractsWindow/Courier'),
          'required': 1,
          'frame': 0,
          'setvalue': s[const.conTypeCourier],
          'group': 'type'},
         {'type': 'btline'}]
        return format

    def Page0_GetAvailabilityOptions(self, s):
        n = getattr(self.data, 'name', '')

        def ChangeSearchBy(combo, *args):
            combo.UpdateSettings()

        searchTypePrefsKey = ('char', 'ui', 'contracts_searchNameBy')
        selectSearchBy = settings.char.ui.Get('contracts_searchNameBy', const.searchByPartialTerms)
        f = [{'type': 'text',
          'text': GetByLabel('UI/Contracts/ContractsWindow/Availability')},
         {'type': 'checkbox',
          'label': '_hide',
          'key': 0,
          'text': GetByLabel('UI/Generic/Public'),
          'required': 1,
          'frame': 0,
          'setvalue': s[0],
          'group': 'avail',
          'onchange': self.OnAvailChange},
         {'type': 'checkbox',
          'label': '_hide',
          'key': 1,
          'text': GetByLabel('UI/Generic/Private'),
          'required': 1,
          'frame': 0,
          'setvalue': s[1],
          'group': 'avail',
          'onchange': self.OnAvailChange,
          'name': 'privateCb'},
         {'type': 'edit',
          'width': 120,
          'label': GetByLabel('UI/Contracts/ContractsService/IndentedName'),
          'key': 'name',
          'required': 0,
          'frame': 0,
          'setvalue': n,
          'group': 'name',
          'isCharacterField': True},
         {'type': 'combo',
          'width': 120,
          'label': GetByLabel('UI/Common/SearchBy'),
          'key': 'searchBy',
          'options': searchUtil.searchByChoices,
          'setvalue': selectSearchBy,
          'group': 'name',
          'callback': ChangeSearchBy,
          'prefskey': searchTypePrefsKey}]
        if not util.IsNPC(session.corpid):
            f += [{'type': 'checkbox',
              'label': '_hide',
              'key': 2,
              'text': GetByLabel('UI/Contracts/ContractsWindow/MyCorporation'),
              'required': 1,
              'frame': 0,
              'setvalue': s[2],
              'group': 'avail',
              'onchange': self.OnAvailChange}]
        if session.allianceid:
            f += [{'type': 'checkbox',
              'label': '_hide',
              'key': 3,
              'text': GetByLabel('UI/Contracts/ContractsWindow/MyAlliance'),
              'required': 1,
              'frame': 0,
              'setvalue': s[3],
              'group': 'avail',
              'onchange': self.OnAvailChange}]
        return f

    def BuildPage2(self):
        retfields = reqresult = errorcheck = []
        duration, expireTime, expireTimeOptions = self.GetDurationAndExpireTimes()
        if self.data.type == const.conTypeAuction:
            errorcheck, reqresult, retfields = self.BuildPage2_AddAuctionOption(expireTime, expireTimeOptions, errorcheck, reqresult, retfields)
        elif self.data.type == const.conTypeItemExchange:
            errorcheck, reqresult, retfields = self.BuildPage2_AddItemExchangeOptions(expireTime, expireTimeOptions)
        elif self.data.type == const.conTypeCourier:
            errorcheck, reqresult, retfields = self.BuildPage2_AddCourierOptions(duration, expireTime, expireTimeOptions)
        return (errorcheck, reqresult, retfields)

    def GetDurationAndExpireTimes(self):
        expireTime = getattr(self.data, 'expiretime', None)
        if expireTime is None:
            expireTime = settings.char.ui.Get('contracts_expiretime_%s' % self.data.type, 1440)
        duration = getattr(self.data, 'duration', None)
        if duration is None:
            duration = settings.char.ui.Get('contracts_duration_%s' % self.data.type, 1)
        expireTimeOptions = []
        for t in EXPIRE_TIMES:
            num = numDays = t / 1440
            txt = GetByLabel('UI/Contracts/ContractsService/QuantityDays', numDays=num)
            numWeeks = t / 10080
            if numWeeks >= 1:
                num = numWeeks
                txt = GetByLabel('UI/Contracts/ContractsService/QuantityWeeks', numWeeks=num)
            expireTimeOptions.append((txt, t))

        return (duration, expireTime, expireTimeOptions)

    def BuildPage2_AddAuctionOption(self, expireTime, expireTimeOptions, errorcheck, reqresult, retfields):
        del expireTimeOptions[-1]
        format = [{'type': 'push'},
         {'type': 'edit',
          'labelwidth': 150,
          'width': 120,
          'label': GetByLabel('UI/Contracts/ContractsWindow/StartingBid'),
          'key': 'price',
          'autoselect': 1,
          'required': 0,
          'frame': 0,
          'group': 'avail',
          'floatonly': [0, MAX_AMOUNT],
          'setvalue': getattr(self.data, 'price', 0)},
         {'type': 'push'},
         {'type': 'edit',
          'labelwidth': 150,
          'width': 120,
          'label': GetByLabel('UI/Contracts/ContractsWindow/BuyoutPriceOptional'),
          'key': 'collateral',
          'autoselect': 1,
          'required': 0,
          'frame': 0,
          'group': 'avail',
          'floatonly': [0, MAX_AMOUNT],
          'setvalue': getattr(self.data, 'collateral', 0)},
         {'type': 'push'},
         {'type': 'combo',
          'labelwidth': 150,
          'width': 120,
          'label': GetByLabel('UI/Contracts/ContractsWindow/AuctionTime'),
          'key': 'expiretime',
          'options': expireTimeOptions,
          'setvalue': getattr(self.data, 'expiretime', expireTime)},
         {'type': 'push'},
         {'type': 'edit',
          'labelwidth': 150,
          'width': 220,
          'label': GetByLabel('UI/Contracts/ContractEntry/DescriptionOptional'),
          'key': 'description',
          'required': 0,
          'frame': 0,
          'group': 'avail',
          'setvalue': getattr(self.data, 'description', '')}]
        self.form, retfields, reqresult, self.panels, errorcheck, refresh = sm.GetService('form').GetForm(format, self.formWnd)
        btnparent = Container(name='btnparent', parent=self.formWnd.sr.price.parent, align=uiconst.TOALL, padLeft=const.defaultPadding)
        uicontrols.Button(parent=btnparent, label=GetByLabel('UI/Contracts/ContractsWindow/BasePrice'), func=self.CalcBasePricePrice, btn_default=0, align=uiconst.CENTERLEFT)
        return (errorcheck, reqresult, retfields)

    def BuildPage2_AddItemExchangeOptions(self, expireTime, expireTimeOptions):
        isRequestItems = not not self.data.reqItems
        format = [{'type': 'push'},
         {'type': 'edit',
          'labelwidth': 150,
          'width': 120,
          'label': GetByLabel('UI/Contracts/ContractEntry/IWillPay'),
          'key': 'reward',
          'autoselect': 1,
          'required': 0,
          'frame': 0,
          'group': 'avail',
          'floatonly': [0, MAX_AMOUNT],
          'setvalue': getattr(self.data, 'reward', 0)},
         {'type': 'push'},
         {'type': 'edit',
          'labelwidth': 150,
          'width': 120,
          'label': GetByLabel('UI/Contracts/ContractEntry/IWillRecieve'),
          'key': 'price',
          'autoselect': 1,
          'required': 0,
          'frame': 0,
          'group': 'avail',
          'floatonly': [0, MAX_AMOUNT],
          'setvalue': getattr(self.data, 'price', 0)},
         {'type': 'push'},
         {'type': 'combo',
          'labelwidth': 150,
          'width': 120,
          'label': GetByLabel('UI/Contracts/ContractsWindow/Expiration'),
          'key': 'expiretime',
          'options': expireTimeOptions,
          'setvalue': getattr(self.data, 'expiretime', expireTime)},
         {'type': 'push'},
         {'type': 'edit',
          'labelwidth': 150,
          'width': 220,
          'label': GetByLabel('UI/Contracts/ContractEntry/DescriptionOptional'),
          'key': 'description',
          'required': 0,
          'frame': 0,
          'maxLength': 50,
          'group': 'avail',
          'setvalue': getattr(self.data, 'description', '')},
         {'type': 'push',
          'height': 10},
         {'type': 'checkbox',
          'required': 1,
          'height': 16,
          'setvalue': isRequestItems,
          'key': 'requestitems',
          'label': '',
          'text': GetByLabel('UI/Contracts/ContractsWindow/AlsoReqItemsFromBuyer'),
          'frame': 0,
          'onchange': self.OnRequestItemsChange}]
        self.form, retfields, reqresult, self.panels, errorcheck, refresh = sm.GetService('form').GetForm(format, self.formWnd)
        self.sr.reqItemsParent = reqItemsParent = Container(name='reqItemsParent', parent=self.formWnd, align=uiconst.TOALL, pos=(0, 0, 0, 0), idx=50)
        left = const.defaultPadding + 3
        top = 16
        self.reqItemTypeWnd = c = uicontrols.SinglelineEdit(name='itemtype', parent=reqItemsParent, label=GetByLabel('UI/Contracts/ContractsWindow/ItemType'), align=uiconst.TOPLEFT, width=248, isTypeField=True)
        c.OnFocusLost = self.ParseItemType
        c.left = left
        c.top = top
        left += c.width + 5
        self.reqItemQtyWnd = c = uicontrols.SinglelineEdit(name='itemqty', parent=reqItemsParent, label=GetByLabel('UI/Inventory/ItemQuantity'), align=uiconst.TOPLEFT, width=50, ints=[0], setvalue=1)
        c.left = left
        c.top = top
        left += c.width + 5
        c = uicontrols.Button(parent=reqItemsParent, label=GetByLabel('UI/Contracts/ContractEntry/AddItem'), func=self.AddRequestItem, pos=(left,
         top,
         0,
         0), align=uiconst.TOPLEFT)
        c.top = top
        self.reqItemScroll = uicontrols.Scroll(parent=reqItemsParent, padding=(const.defaultPadding,
         top + c.height + const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding))
        self.reqItemScroll.sr.id = 'reqitemscroll'
        self.PopulateReqItemScroll()
        btnparent = Container(name='btnparent', parent=self.formWnd.sr.price.parent, align=uiconst.TOALL, padLeft=const.defaultPadding)
        uicontrols.Button(parent=btnparent, label=GetByLabel('UI/Contracts/ContractsWindow/BasePrice'), func=self.CalcBasePricePrice, btn_default=0, align=uiconst.CENTERLEFT)
        self.ToggleShowRequestItems(isRequestItems)
        return (errorcheck, reqresult, retfields)

    def BuildPage2_AddCourierOptions(self, duration, expireTime, expireTimeOptions):
        stationName = ''
        if not self.data.endStation and len(self.data.items) == 1 and self.data.items.values()[0][0] == const.typePlasticWrap:
            stationName = cfg.evelocations.Get(self.data.items.keys()[0]).name.replace('>>', '')
        format = [{'type': 'push'},
         {'type': 'edit',
          'label': GetByLabel('UI/Contracts/ContractsWindow/ShipTo'),
          'labelwidth': 150,
          'width': 120,
          'key': 'endStationName',
          'frame': 0,
          'maxLength': 80,
          'setvalue': stationName},
         {'type': 'push'},
         {'type': 'edit',
          'labelwidth': 150,
          'width': 120,
          'label': GetByLabel('UI/Contracts/ContractsWindow/Reward'),
          'key': 'reward',
          'autoselect': 1,
          'required': 0,
          'frame': 0,
          'group': 'avail',
          'floatonly': [0, MAX_AMOUNT],
          'setvalue': getattr(self.data, 'reward', 0)},
         {'type': 'push'},
         {'type': 'edit',
          'labelwidth': 150,
          'width': 120,
          'label': GetByLabel('UI/Contracts/ContractsWindow/Collateral'),
          'key': 'collateral',
          'autoselect': 1,
          'required': 0,
          'frame': 0,
          'group': 'avail',
          'floatonly': [0, MAX_AMOUNT],
          'setvalue': getattr(self.data, 'collateral', 0)},
         {'type': 'push'},
         {'type': 'combo',
          'labelwidth': 150,
          'width': 120,
          'label': GetByLabel('UI/Contracts/ContractsWindow/Expiration'),
          'key': 'expiretime',
          'options': expireTimeOptions,
          'setvalue': expireTime},
         {'type': 'push'},
         {'type': 'edit',
          'labelwidth': 150,
          'width': 32,
          'label': GetByLabel('UI/Contracts/ContractsWindow/DaysToComplete'),
          'key': 'duration',
          'autoselect': 1,
          'required': 0,
          'frame': 0,
          'group': 'duration',
          'setvalue': duration,
          'intonly': [1, 365]},
         {'type': 'push'},
         {'type': 'edit',
          'labelwidth': 150,
          'width': 220,
          'label': GetByLabel('UI/Contracts/ContractEntry/DescriptionOptional'),
          'key': 'description',
          'required': 0,
          'frame': 0,
          'group': 'avail',
          'setvalue': getattr(self.data, 'description', '')}]
        self.form, retfields, reqresult, self.panels, errorcheck, refresh = sm.GetService('form').GetForm(format, self.formWnd)
        if self.data.endStation:
            self.SearchStation(self.data.endStation)
        endStationEdit = self.formWnd.sr.endStationName
        endStationEdit.OnFocusLost = self.SearchStationFromEdit
        endStationEdit.isLocationField = True
        endStationEdit.SetValueAfterDragging = self.EndStationSetValueAfterDragging
        btnparent = Container(name='btnparent', parent=endStationEdit.parent, align=uiconst.TOALL, padLeft=const.defaultPadding)
        btn = uicontrols.Button(parent=btnparent, label=GetByLabel('UI/Common/Search'), func=self.SearchStationFromEdit, args=(endStationEdit,), btn_default=0, align=uiconst.CENTERLEFT)
        Line(parent=self.formWnd, align=uiconst.TOTOP, padTop=10)
        self.sr.courierHint = uicontrols.EveLabelSmall(name='courierHint', text='', align=uiconst.TOTOP, parent=self.formWnd, state=uiconst.UI_DISABLED, padding=6)
        self.UpdateCourierHint()
        if not getattr(self, 'courierHint', None):
            self.courierHint = base.AutoTimer(1000, self.UpdateCourierHint)
        btnparent2 = Container(name='btnparent', parent=self.formWnd.sr.collateral.parent, align=uiconst.TOALL, padLeft=const.defaultPadding)
        btn2 = uicontrols.Button(parent=btnparent2, label=GetByLabel('UI/Contracts/ContractsWindow/BasePrice'), func=self.CalcBasePriceCollateral, btn_default=0, align=uiconst.CENTERLEFT)
        return (errorcheck, reqresult, retfields)

    def EndStationSetValueAfterDragging(self, name, locationID):
        if self.IsDockableLocation(locationID):
            uicontrols.SinglelineEdit.SetValueAfterDragging(self.formWnd.sr.endStationName, name, locationID)
            self.data.endStation = None

    def GetItemQtyLabel(self, iQty, iTypeID):
        return GetByLabel('UI/Contracts/ContractsService/NameXQuantity', typeID=iTypeID, quantity=util.FmtAmt(iQty))

    def BuildPage3(self):
        if hasattr(self.data, 'expiretime'):
            settings.char.ui.Set('contracts_expiretime_%s' % self.data.type, self.data.expiretime)
        if hasattr(self.data, 'duration'):
            settings.char.ui.Set('contracts_duration_%s' % self.data.type, self.data.duration)
        rows = []
        rows.append([GetByLabel('UI/Contracts/ContractType'), GetContractTypeText(self.data.type)])
        desc = self.data.description
        if desc == '':
            desc = GetByLabel('UI/Contracts/ContractEntry/NoneParen')
        rows.append([GetByLabel('UI/Contracts/ContractsWindow/Description'), desc])
        avail = self.data.avail
        a = GetByLabel('UI/Generic/Public')
        if avail > 0:
            a = GetByLabel('UI/Generic/Private')
            assignee = cfg.eveowners.Get(self.data.assigneeID)
            a += ' (<a href=showinfo:%s//%s>%s</a>)' % (assignee.typeID, self.data.assigneeID, assignee.name)
        else:
            regionID = None
            if util.IsStation(self.data.startStation):
                regionID = cfg.evelocations.Get(self.data.startStation).Station().regionID
            else:
                structureInfo = sm.GetService('structureDirectory').GetStructureInfo(self.data.startStation)
                if structureInfo is not None:
                    regionID = cfg.mapSystemCache.Get(structureInfo.solarSystemID).regionID
            if regionID:
                regionLabel = GetByLabel('UI/Contracts/ContractsService/RegionName', region=regionID)
            else:
                log.LogTraceback('No Region?')
                regionLabel = ''
            a += regionLabel
        rows.append([GetByLabel('UI/Contracts/ContractsWindow/Availability'), a])
        loc = GetByLabel('UI/Contracts/ContractEntry/NoneParen')
        if self.data.startStation:
            loc = cfg.evelocations.Get(self.data.startStation).name
            if util.IsStation(self.data.startStation):
                startStationTypeID = sm.GetService('ui').GetStation(self.data.startStation).stationTypeID
            else:
                startStationTypeID = sm.GetService('structureDirectory').GetStructureInfo(self.data.startStation).typeID
            loc = GetShowInfoLink(startStationTypeID, loc, self.data.startStation)
        rows.append([GetByLabel('UI/Contracts/ContractsWindow/Location'), loc])
        expireLabel = GetByLabel('UI/Contracts/ContractsService/TimeLeftWithoutCaption', timeLeft=util.FmtDate(self.data.expiretime * const.MIN + blue.os.GetWallclockTime(), 'ss'), expireTime=util.FmtDate(self.data.expiretime * const.MIN))
        rows.append([GetByLabel('UI/Contracts/ContractsWindow/Expiration'), expireLabel])
        brokersFee, deposit, salesTax = self.GetFeeText()
        rows.append([GetByLabel('UI/Contracts/ContractsWindow/SalesTax'), salesTax])
        rows.append([GetByLabel('UI/Contracts/ContractsWindow/BrokersFee'), brokersFee])
        rows.append([GetByLabel('UI/Contracts/ContractsWindow/Deposit'), deposit])
        rows.append([])
        if self.data.type == const.conTypeAuction:
            auctionRows = self.BuildPage3_AddAuctionOptions()
            rows += auctionRows
        elif self.data.type == const.conTypeItemExchange:
            itemExchangeRows = self.BuildPage3_AddItemExchangeOptions()
            rows += itemExchangeRows
        elif self.data.type == const.conTypeCourier:
            courierRows = self.BuildPage3_AddCourierOptions()
            rows += courierRows
        else:
            raise RuntimeError('Contract type not implemented!')
        self.WriteConfirm(rows)
        self.sr.buttonNext.SetLabel(GetByLabel('UI/Contracts/ContractsWindow/Finish'))

    def GetFeeText(self):
        if self.data.avail > 0:
            salesTax = GetByLabel('UI/Contracts/ContractEntry/NoneParen')
            brokersFee = util.FmtISK(const_conBrokersFeeMinimum, 0)
            deposit = util.FmtISK(0.0, 0)
        else:
            skills = sm.GetService('skills').GetSkills()
            skillLevels = util.KeyVal()
            skillLevels.brokerRelations = getattr(skills.get(const.typeBrokerRelations, None), 'skillLevel', 0)
            skillLevels.accounting = getattr(skills.get(const.typeAccounting, None), 'skillLevel', 0)
            ret = CalcContractFees(self.data.Get('price', 0), self.data.Get('reward', 0), self.data.type, self.data.expiretime, skillLevels, session.solarsystemid2, session.warfactionid)
            salesTax = GetByLabel('UI/Contracts/ContractsService/ISKFollowedByPercent', numISK=util.FmtISK(ret.salesTaxAmt, 0), percentage=ret.salesTax * 100.0)
            if ret.brokersFeeAmt == const_conBrokersFeeMinimum:
                brokersFee = GetByLabel('UI/Contracts/ContractsService/ISKMinimumQuantity', numISK=util.FmtISK(ret.brokersFeeAmt, 0))
            else:
                brokersFee = GetByLabel('UI/Contracts/ContractsService/ISKFollowedByPercent', numISK=util.FmtISK(ret.brokersFeeAmt, 0), percentage=ret.brokersFee * 100.0)
            minDeposit = const_conDepositMinimum
            if self.data.type == const.conTypeCourier:
                minDeposit = minDeposit / 10
            if ret.depositAmt == minDeposit:
                deposit = GetByLabel('UI/Contracts/ContractsService/ISKMinimumQuantity', numISK=util.FmtISK(ret.depositAmt, 0))
            else:
                deposit = GetByLabel('UI/Contracts/ContractsService/ISKFollowedByPercent', numISK=util.FmtISK(ret.depositAmt, 0), percentage=ret.deposit * 100.0)
            if self.data.type == const.conTypeAuction:
                p = const_conSalesTax - float(skillLevels.accounting) * 0.001
                buyout = self.data.collateral
                if buyout < self.data.Get('price', 0):
                    buyout = MAX_AMOUNT
                ret2 = CalcContractFees(buyout, self.data.Get('reward', 0), self.data.type, self.data.expiretime, skillLevels, session.solarsystemid2, session.warfactionid)
                maxSalesTax = ret2.salesTaxAmt
                salesTax = GetByLabel('UI/Contracts/ContractsService/PercentOfSalesPriceAtTax', percent=100.0 * p, formattedISKWithUnits=FmtISKWithDescription(maxSalesTax, True))
            elif self.data.type == const.conTypeCourier:
                salesTax = GetByLabel('UI/Contracts/ContractEntry/NoneParen')
        return (brokersFee, deposit, salesTax)

    def BuildPage3_AddAuctionOptions(self):
        rows = []
        rows.append([GetByLabel('UI/Contracts/ContractsWindow/StartingBid'), FmtISKWithDescription(self.data.price)])
        buyout = GetByLabel('UI/Contracts/ContractEntry/NoneParen')
        if self.data.collateral > 0:
            buyout = FmtISKWithDescription(self.data.collateral)
        rows.append([GetByLabel('UI/Contracts/ContractsWindow/BuyoutPrice'), buyout])
        itemList = []
        for i in self.data.items:
            item = self.data.items[i]
            itemLabel = self.GetItemQtyLabel(item[1], item[0])
            itemList.append(itemLabel)
            chld = self.data.childItems.get(i, [])
            for c in chld:
                childItemLabel = GetByLabel('UI/Contracts/ContractsService/NameXQuantityChild', typeID=c[1], quantity=c[2])
                itemList.append(childItemLabel)

        items = '<br>'.join(itemList)
        rows.append([GetByLabel('UI/Contracts/ContractEntry/ItemsForSale'), items])
        return rows

    def BuildPage3_AddItemExchangeOptions(self):
        rows = []
        rows.append([GetByLabel('UI/Contracts/ContractEntry/IWillPay'), FmtISKWithDescription(self.data.reward)])
        rows.append([GetByLabel('UI/Contracts/ContractEntry/IWillRecieve'), FmtISKWithDescription(self.data.price)])
        items = ''
        itemList = []
        for i in self.data.items:
            itemLabel = self.GetItemQtyLabel(self.data.items[i][1], self.data.items[i][0])
            itemList.append(itemLabel)
            chld = self.data.childItems.get(i, [])
            for c in chld:
                childItemLabel = GetByLabel('UI/Contracts/ContractsService/NameXQuantityChild', typeID=c[1], quantity=c[2])
                itemList.append(childItemLabel)

        items = '<br>'.join(itemList)
        rows.append([GetByLabel('UI/Contracts/ContractEntry/ItemsForSale'), items])
        listToJoin = []
        for typeID, qty in self.data.reqItems.iteritems():
            labelToAppend = self.GetItemQtyLabel(qty, typeID)
            listToJoin.append(labelToAppend)

        itemStr = '<br>'.join(listToJoin)
        rows.append([GetByLabel('UI/Contracts/ContractEntry/ItemsRequired'), itemStr])
        return rows

    def BuildPage3_AddCourierOptions(self):
        rows = []
        rows.append([GetByLabel('UI/Contracts/ContractsWindow/Reward'), FmtISKWithDescription(self.data.reward)])
        rows.append([GetByLabel('UI/Contracts/ContractsWindow/Collateral'), FmtISKWithDescription(self.data.collateral)])
        loc = ''
        if self.data.startStation:
            loc = cfg.evelocations.Get(self.data.endStation).name
            if util.IsStation(self.data.endStation):
                typeID = sm.GetService('ui').GetStation(self.data.endStation).stationTypeID
            else:
                typeID = sm.GetService('structureDirectory').GetStructureInfo(self.data.endStation).typeID
            loc = GetShowInfoLink(typeID, loc, itemID=self.data.endStation)
        rows.append([GetByLabel('UI/Common/Destination'), loc])
        rows.append([GetByLabel('UI/Contracts/ContractsWindow/DaysToComplete'), self.data.duration])
        volume = 0
        for i in self.data.items:
            volume += GetItemVolume(self.data.items[i][2], int(self.data.items[i][1]))

        if 0 < volume < 1:
            significantDigits = 2
            decimalPlaces = int(-math.ceil(math.log10(volume)) + significantDigits)
        else:
            decimalPlaces = 2
        volumeLabel = GetByLabel('UI/Contracts/ContractsWindow/NumericVolume', volume=util.FmtAmt(volume, showFraction=decimalPlaces))
        rows.append([GetByLabel('UI/Inventory/ItemVolume'), volumeLabel])
        items = ''
        itemList = []
        for i in self.data.items:
            item = self.data.items[i]
            itemLabel = self.GetItemQtyLabel(item[1], item[0])
            itemList.append(itemLabel)
            chld = self.data.childItems.get(i, [])
            for c in chld:
                childItemLabel = GetByLabel('UI/Contracts/ContractsService/NameXQuantityChild', typeID=c[1], quantity=c[2])
                itemList.append(childItemLabel)

        items = '<br>'.join(itemList)
        rows.append([GetByLabel('UI/Contracts/ContractEntry/Items'), items])
        return rows

    def OnChangePrivateName(self, privateCheckbox, text):
        if text:
            privateCheckbox.ToggleState()

    def OnRequestItemsChange(self, chkbox, *args):
        if not chkbox.GetValue():
            self.reqItemScroll.Clear()
            self.data.reqItems = {}
        self.ToggleShowRequestItems(not not chkbox.GetValue())

    def ToggleShowRequestItems(self, isIt):
        self.sr.reqItemsParent.state = [uiconst.UI_HIDDEN, uiconst.UI_NORMAL][isIt]

    def WriteNumContractsAndLimitsLazy(self):
        try:
            n, maxNumContracts = self.GetNumContractsAndLimits(getattr(self.data, 'forCorp', 0), getattr(self.data, 'assigneeID', 0))
            outstandingLabel = GetByLabel('UI/Contracts/ContractsService/OutstandingContractsDisplay', numContracts=n, maxContracts=maxNumContracts)
            self.limitTextWnd.text = '<color=0xff999999>%s</color>' % outstandingLabel
        except:
            sys.exc_clear()

    def OnForCorpChange(self, wnd, *args):
        self.data.forCorp = wnd.GetValue()
        self.OnAvailChange(None)
        self.data.items = {}

    def OnAvailChange(self, wnd, *args):
        uthread.new(self._OnAvailChange, wnd)

    def _OnAvailChange(self, wnd, *args):
        if self.destroyed:
            return
        if not wnd:
            key = getattr(self.data, 'lastAvailKey', 0)
        else:
            key = wnd.data.get('key')
            self.data.lastAvailKey = key
        if key == 2:
            n, maxNumContracts = self.GetNumContractsAndLimits(getattr(self.data, 'forCorp', 0), eve.session.corpid)
        elif key == 1:
            n, maxNumContracts = self.GetNumContractsAndLimits(getattr(self.data, 'forCorp', 0), getattr(self.data, 'assigneeID', 0))
        else:
            n, maxNumContracts = self.GetNumContractsAndLimits(getattr(self.data, 'forCorp', 0), 0)
        try:
            outstandingLabel = GetByLabel('UI/Contracts/ContractsService/OutstandingContractsDisplay', numContracts=n, maxContracts=maxNumContracts)
            self.limitTextWnd.text = '<color=0xff999999>%s</color>' % outstandingLabel
        except:
            sys.exc_clear()

    def CreateContract(self):
        sm.GetService('loading').ProgressWnd(GetByLabel('UI/Contracts/ContractsWindow/CreatingContract'), '', 2, 10)
        try:
            self.state = uiconst.UI_HIDDEN
            type = getattr(self.data, 'type', const.conTypeNothing)
            assigneeID = getattr(self.data, 'assigneeID', 0)
            startStationID = getattr(self.data, 'startStation', 0)
            startStationDivision = getattr(self.data, 'startStationDivision', None)
            endStationID = getattr(self.data, 'endStation', 0)
            forCorp = getattr(self.data, 'forCorp', 0) > 0
            if not forCorp:
                startStationDivision = 4
            price = getattr(self.data, 'price', 0)
            reward = getattr(self.data, 'reward', 0)
            collateral = getattr(self.data, 'collateral', 0)
            expiretime = getattr(self.data, 'expiretime', 0)
            duration = getattr(self.data, 'duration', 0)
            title = getattr(self.data, 'description', '')
            description = getattr(self.data, 'body', '')
            items = []
            itemsReq = map(list, self.data.reqItems.items())
            for i in self.data.items:
                items.append([i, self.data.items[i][1]])

            isPrivate = not not assigneeID
            args = (type,
             isPrivate,
             assigneeID,
             expiretime,
             duration,
             startStationID,
             endStationID,
             price,
             reward,
             collateral,
             title,
             description,
             items,
             startStationDivision,
             itemsReq,
             forCorp)
            try:
                contractID = sm.GetService('contracts').CreateContract(*args)
            except UserError as e:
                if e.msg == 'NotEnoughCargoSpace':
                    if eve.Message('ConAskRemoveToHangar', {}, uiconst.YESNO) == uiconst.ID_YES:
                        contractID = sm.GetService('contracts').CreateContract(confirm=CREATECONTRACT_CONFIRM_CHARGESTOHANGAR, *args)
                    else:
                        raise
                else:
                    raise

            if contractID:
                locData = util.KeyVal(**{'locationID': startStationID,
                 'groupID': const.groupStation})
                sm.GetService('contracts').ShowContract(contractID)
                self.Close()
            else:
                self.state = uiconst.UI_NORMAL
        finally:
            self.state = uiconst.UI_NORMAL
            sm.GetService('loading').ProgressWnd(GetByLabel('UI/Contracts/ContractsWindow/CreatingContract'), '', 10, 10)

    def WriteConfirm(self, rows):
        body = ''
        for r in rows:
            if r == []:
                body += '<tr><td colspan=2><hr></td></tr>'
            else:
                boldKey = GetByLabel('UI/Contracts/ContractsService/BoldGenericLabel', labelText=r[0])
                body += '<tr><td width=100 valign=top>%(key)s</td><td>%(val)s</td></tr>' % {'key': boldKey,
                 'val': r[1]}

        message = '\n              <TABLE width="98%%">%s</TABLE>\n        ' % body
        messageArea = uicontrols.Edit(parent=self.formWnd, readonly=1, hideBackground=1)
        messageArea.SetValue(message)

    def ParseItemType(self, wnd, *args):
        if self.destroyed or getattr(self, 'parsingItemType', False):
            return
        try:
            self.parsingItemType = True
            txt = wnd.GetValue()
            if len(txt) == 0 or not IsSearchStringLongEnough(txt):
                return
            types = []
            for t in self.marketTypes:
                if MatchInvTypeName(txt, t.typeID):
                    if CanRequestType(t.typeID):
                        types.append(t.typeID)

            typeID = SelectItemTypeDlg(types)
            if typeID:
                wnd.SetValue(TypeName(typeID))
                self.parsedItemType = typeID
            return typeID
            self.parsedItemType = typeID
        finally:
            self.parsingItemType = False

    def AddRequestItem(self, *args):
        typeID = getattr(self, 'parsedItemType', None) or self.ParseItemType(self.reqItemTypeWnd)
        self.parsedItemType = None
        if not typeID:
            return
        qty = self.reqItemQtyWnd.GetValue()
        if qty < 1:
            return
        self.data.reqItems[typeID] = qty
        self.reqItemTypeWnd.SetValue('')
        self.reqItemQtyWnd.SetValue(1)
        self.PopulateReqItemScroll()

    def RemoveRequestItem(self, wnd, *args):
        del self.data.reqItems[wnd.sr.node.typeID]
        self.PopulateReqItemScroll()

    def PopulateReqItemScroll(self):
        scrolllist = []
        self.reqItemScroll.Clear()
        for typeID, qty in self.data.reqItems.iteritems():
            typeName = TypeName(typeID)
            data = util.KeyVal()
            data.label = GetByLabel('UI/Contracts/ContractsService/NameXQuantity', typeID=typeID, quantity=qty)
            data.typeID = typeID
            data.name = typeName
            data.OnDblClick = self.RemoveRequestItem
            data.GetMenu = self.GetReqItemMenu
            scrolllist.append(listentry.Get('Generic', data=data))

        self.reqItemScroll.Load(contentList=scrolllist, headers=[])
        if scrolllist == []:
            self.reqItemScroll.ShowHint(GetByLabel('UI/Contracts/ContractsWindow/AddItemsAbove'))
        else:
            self.reqItemScroll.ShowHint()

    def GetReqItemMenu(self, wnd, *args):
        m = []
        m.append((uiutil.MenuLabel('UI/Generic/RemoveItem'), self.RemoveRequestItem, (wnd,)))
        return m

    def SearchStationFromEdit(self, editField):
        stationID = editField.draggedValue
        self.SearchStation(stationID)

    def SearchStation(self, stationID = None, *args):
        searchstr = self.form.sr.endStationName.GetValue().strip()
        if stationID is None and not IsSearchStringLongEnough(searchstr):
            return
        sm.GetService('loading').Cycle(GetByLabel('UI/Common/Searching'), GetByLabel('UI/Contracts/ContractsService/LoadingSearchHint', searchStr=searchstr))
        if stationID and not self.IsDockableLocation(stationID):
            stationID = None
        if stationID is None:
            stationID = uix.Search(searchstr.lower(), const.groupStation, categoryID=const.categoryStructure, searchWndName='contractSearchStationSearch')
        sm.GetService('loading').StopCycle()
        if stationID:
            locationName = cfg.evelocations.Get(stationID).name
            self.courierDropLocation = stationID
            self.form.sr.endStationName.SetValue(locationName)
        self.data.endStation = stationID

    def IsDockableLocation(self, dockableItemID):
        if util.IsStation(dockableItemID):
            return True
        return sm.GetService('structureDirectory').GetStructureInfo(dockableItemID) is not None

    def UpdateCourierHint(self):
        if self.data.endStation and self.data.startStation and self.sr.courierHint and not self.sr.courierHint.destroyed:
            startSolarSystemID = sm.GetService('contracts').GetSolarSystemIDForStationOrStructure(self.data.startStation)
            endSolarSystemID = sm.GetService('contracts').GetSolarSystemIDForStationOrStructure(self.data.endStation)
            numJumps = sm.GetService('clientPathfinderService').GetAutopilotJumpCount(endSolarSystemID, startSolarSystemID)
            perJump = 0
            perJump = self.formWnd.sr.reward.GetValue() / (numJumps or 1)
            sec = sm.GetService('contracts').GetRouteSecurityWarning(startSolarSystemID, endSolarSystemID)
            if numJumps == 0:
                hint = GetByLabel('UI/Contracts/ContractsService/CourierHintNoJumps', numISK=util.FmtISK(perJump))
            elif numJumps == 1:
                hint = GetByLabel('UI/Contracts/ContractsService/CourierHintOneJump', numISK=util.FmtISK(perJump))
            else:
                hint = GetByLabel('UI/Contracts/ContractsService/CourierHintManyJumps', numJumps=numJumps, numISK=util.FmtISK(perJump))
            if sec:
                hint += '<br>' + sec
            self.sr.courierHint.SetText(hint)

    def GetNumContractsAndLimits(self, forCorp, assigneeID):
        skills = sm.GetService('skills').GetSkills()
        skillTypeID = [const.typeContracting, const.typeCorporationContracting][forCorp]
        skill = skills.get(skillTypeID, None)
        if skill is None:
            lvl = 0
        else:
            lvl = skill.skillLevel
        if forCorp:
            maxNumContracts = NUM_CONTRACTS_BY_SKILL_CORP[lvl]
        else:
            maxNumContracts = NUM_CONTRACTS_BY_SKILL[lvl]
        innerCorp = False
        if assigneeID > 0:
            if util.IsCorporation(assigneeID):
                if assigneeID == eve.session.corpid:
                    innerCorp = True
            elif util.IsCharacter(assigneeID):
                corpID = sm.RemoteSvc('corpmgr').GetCorporationIDForCharacter(assigneeID)
                if corpID == eve.session.corpid and not util.IsNPC(eve.session.corpid):
                    innerCorp = True
        n = 0
        try:
            if getattr(self, 'numOutstandingContracts', None) is None:
                self.numOutstandingContracts = sm.GetService('contracts').NumOutstandingContracts()
            if forCorp:
                if innerCorp:
                    n = self.numOutstandingContracts.myCorpTotal
                else:
                    n = self.numOutstandingContracts.nonCorpForMyCorp
            elif innerCorp:
                n = self.numOutstandingContracts.myCharTotal
            else:
                n = self.numOutstandingContracts.nonCorpForMyChar
        finally:
            return (n, [maxNumContracts, MAX_NUM_CONTRACTS][innerCorp])

    def FinishStep(self, step):
        uthread.Lock(self)
        try:
            result = sm.GetService('form').ProcessForm(self.formdata[0], self.formdata[1])
            lastType = getattr(self.data, 'type', None)
            if step == 0 and result['type'] != lastType and not getattr(self, 'first', False):
                self.ResetWizard()
            setattr(self, 'first', False)
            for i in result:
                setattr(self.data, str(i), result[i])

            if step == 0:
                doContinue = self.FinishPage0()
                if not doContinue:
                    return False
            elif step == 1:
                doContinue = self.FinishStep1()
                if not doContinue:
                    return False
            else:
                if step == 2:
                    return self.FinishStep2()
                raise RuntimeError('Illegal step (%s)' % step)
            return True
        finally:
            uthread.UnLock(self)

    def FinishPage0(self):
        ownerID = None
        if self.data.avail == 1:
            if IsSearchStringLongEnough(self.data.name):
                exact = getattr(self.data, 'searchBy', const.searchByPartialTerms)
                ownerID = uix.Search(self.data.name.lower(), const.groupCharacter, const.categoryOwner, exact=exact, hideNPC=1, searchWndName='contractFinishStepSearch', hideDustChars=True)
            if not ownerID:
                return False
            if self.data.type == const.conTypeAuction:
                owner = cfg.eveowners.Get(ownerID)
                if owner.IsCharacter() or owner.IsCorporation() and ownerID != session.corpid:
                    raise UserError('CustomInfo', {'info': GetByLabel('UI/Contracts/ContractsService/UserErrorCannotCreatePrivateAuction')})
        elif self.data.name != '':
            raise UserError('CustomInfo', {'info': GetByLabel('UI/Contracts/ContractsService/UserErrorPrivateNameAndStateDontMatch')})
        elif self.data.avail == 2:
            ownerID = eve.session.corpid
        elif self.data.avail == 3:
            ownerID = eve.session.allianceid
            if not ownerID:
                raise UserError('CustomInfo', {'info': GetByLabel('UI/CapitalNavigation/CapitalNavigationWindow/CorporationNotInAllianceMessage')})
        self.data.assigneeID = ownerID
        forCorp = bool(self.data.forCorp)
        n, maxNumContracts = self.GetNumContractsAndLimits(forCorp, self.data.assigneeID)
        if n >= maxNumContracts >= 0:
            if forCorp is True:
                skillLabel = GetByLabel('UI/Contracts/ContractsService/IncreaseSkillInfo', skillType=const.typeCorporationContracting)
            else:
                skillLabel = GetByLabel('UI/Contracts/ContractsService/IncreaseSkillInfo', skillType=const.typeContracting)
            errorLabel = GetByLabel('UI/Contracts/ContractsService/UserErrorMaxContractsReached', numContracts=maxNumContracts, skillInfo=skillLabel)
            raise UserError('CustomInfo', {'info': errorLabel})
        return True

    def FinishStep1(self):
        ILLEGAL_ITEMGROUPS = [const.groupCapsule]
        self.data.childItems = {}
        for i in self.data.items:
            typeID = self.data.items[i][0]
            groupID = evetypes.GetGroupID(typeID)
            categoryID = evetypes.GetCategoryID(typeID)
            if groupID in ILLEGAL_ITEMGROUPS:
                raise UserError('ConIllegalType')
            if i in (eve.session.shipid, util.GetActiveShip()):
                raise UserError('ConCannotTradeCurrentShip')
            isContainer = categoryID == const.categoryShip or groupID in (const.groupCargoContainer,
             const.groupSecureCargoContainer,
             const.groupAuditLogSecureContainer,
             const.groupFreightContainer)
            if isContainer:
                div = const.flagHangar
                if self.data.forCorp:
                    div = self.data.startStationDivision
                items = sm.GetService('contracts').GetItemsInContainer(self.data.startStation, i, self.data.forCorp, div)
                if items is not None and len(items) > 0:
                    itemNameList = []
                    totalVolume = 0
                    for l in items:
                        itemNameList.append(TypeName(l.typeID))
                        val = [l.itemID, l.typeID, l.stacksize]
                        if i not in self.data.childItems:
                            self.data.childItems[i] = []
                        self.data.childItems[i].append(val)
                        totalVolume += GetItemVolume(l, l.stacksize)

                    itemsText = ', '.join(itemNameList)
                    if eve.Message('ConNonEmptyContainer2', {'container': typeID,
                     'items': itemsText,
                     'volume': totalVolume}, uiconst.YESNO) != uiconst.ID_YES:
                        return False

        if self.data.type == const.conTypeCourier:
            volume = 0
            for i in self.data.items:
                evetypes.RaiseIFNotExists(self.data.items[i][0])
                item = self.data.items[i][2]
                volume += GetItemVolume(item, int(self.data.items[i][1]))

            if volume > const_conCourierMaxVolume:
                raise UserError('ConExceedsMaxVolume', {'max': const_conCourierMaxVolume,
                 'vol': volume})
            elif volume > const_conCourierWarningVolume:
                if eve.Message('ConNeedFreighter', {'vol': volume}, uiconst.YESNO, suppress=uiconst.ID_YES) != uiconst.ID_YES:
                    return False
        if not self.data.startStation or self.data.startStation == 0:
            raise UserError('CustomInfo', {'info': GetByLabel('UI/Contracts/ContractsService/UserErrorSelectStartingPointForContract')})
        elif self.data.type in [const.conTypeCourier, const.conTypeAuction] and len(self.data.items) == 0:
            raise UserError('CustomInfo', {'info': GetByLabel('UI/Contracts/ContractsService/UserErrorSelectItemsForContract')})
        if self.data.type in [const.conTypeAuction, const.conTypeItemExchange]:
            insuranceContracts = []
            for i in self.data.items:
                item = self.data.items[i]
                categoryID = evetypes.GetCategoryID(item[0])
                if item[2].singleton and categoryID == const.categoryShip:
                    contract = sm.RemoteSvc('insuranceSvc').GetContractForShip(i)
                    if contract:
                        insuranceContracts.append([contract, item[0]])

            for contract in insuranceContracts:
                example = contract[1]
                if (contract[0].ownerID == eve.session.corpid or self.data.forCorp) and self.data.avail != const.conAvailPublic:
                    if eve.Message('ConInsuredShipCorp', {'example': example}, uiconst.YESNO) != uiconst.ID_YES:
                        doContinue = False
                        return doContinue
                elif eve.Message('ConInsuredShip', {'example': example}, uiconst.YESNO) != uiconst.ID_YES:
                    return False

            for i in self.data.items:
                item = self.data.items[i]
                categoryID = evetypes.GetCategoryID(item[0])
                if categoryID == const.categoryShip and item[2].singleton:
                    sm.GetService('invCache').RemoveInventoryContainer(item[2])

        self.LockItems(self.data.items)
        return True

    def FinishStep2(self):
        if hasattr(self.data, 'price'):
            self.data.price = int(self.data.price)
        if hasattr(self.data, 'reward'):
            self.data.reward = int(self.data.reward)
        if hasattr(self.data, 'collateral'):
            self.data.collateral = int(self.data.collateral)
        if len(self.data.description) > MAX_TITLE_LENGTH:
            errorLabel = GetByLabel('UI/Contracts/ContractsService/UserErrorContractTitleTooLong', length=len(self.data.description), maxLength=MAX_TITLE_LENGTH)
            raise UserError('CustomInfo', {'info': errorLabel})
        if self.data.type == const.conTypeAuction:
            self.FinishStep2_AuctionContracts()
        elif self.data.type == const.conTypeCourier:
            doContinue = self.FinishStep2_CourierContract()
            if not doContinue:
                return False
        elif self.data.type == const.conTypeItemExchange:
            self.FinishStep2_ItemExchangeContract()
        else:
            raise RuntimeError('Not implemented!')
        return True

    def FinishStep2_AuctionContracts(self):
        if self.data.price < const_conBidMinimum and self.data.avail == 0:
            errorLabel = GetByLabel('UI/Contracts/ContractsWindow/ErrorMinimumBidTooLow', minimumBid=const_conBidMinimum)
            raise UserError('CustomInfo', {'info': errorLabel})
        elif self.data.price > self.data.collateral and self.data.collateral > 0:
            errorLabel = GetByLabel('UI/Contracts/ContractsService/UserErrorCannotSpecifyBidOverBuyout')
            raise UserError('CustomInfo', {'info': errorLabel})

    def FinishStep2_CourierContract(self):
        if not self.data.endStation and len(self.form.sr.endStationName.GetValue()) > 0:
            self.SearchStationFromEdit(self.form.sr.endStationName)
            if not self.data.endStation:
                return False
        if not self.data.endStation:
            errorLabel = GetByLabel('UI/Contracts/ContractsService/UserErrorMustSpecifyContractDestination')
            raise UserError('CustomInfo', {'info': errorLabel})
        if not self.data.assigneeID:
            if self.data.reward < MIN_CONTRACT_MONEY:
                errorLabel = GetByLabel('UI/Contracts/ContractsService/UserErrorMinimumRewardNotMet', minimum=MIN_CONTRACT_MONEY)
                raise UserError('CustomInfo', {'info': errorLabel})
            if self.data.collateral < MIN_CONTRACT_MONEY:
                errorLabel = GetByLabel('UI/Contracts/ContractsService/UserErrorMinimumCollateralNotMet', minimum=MIN_CONTRACT_MONEY)
                raise UserError('CustomInfo', {'info': errorLabel})
        return True

    def FinishStep2_ItemExchangeContract(self):
        if self.data.price != 0.0 and self.data.reward != 0.0:
            errorLabel = GetByLabel('UI/Contracts/ContractsService/UserErrorCannotGiveAndReceiveISK')
            raise UserError('CustomInfo', {'info': errorLabel})
        if not self.data.assigneeID:
            if self.data.reqItems == {} and self.data.price < MIN_CONTRACT_MONEY:
                errorLabel = GetByLabel('UI/Contracts/ContractsService/UserErrorExchangeContractRequestNotMet', minimum=MIN_CONTRACT_MONEY)
                raise UserError('CustomInfo', {'info': errorLabel})
        if self.reqItemTypeWnd.GetValue() != '':
            errorLabel = GetByLabel('UI/Contracts/ContractsService/UserErrorMustClickAddItem')
            raise UserError('CustomInfo', {'info': errorLabel})
        if not self.data.assigneeID:
            if (self.data.reqItems != {} or self.data.price > 0) and len(self.data.items) == 0 and self.data.reward == 0:
                errorLabel = GetByLabel('UI/Contracts/ContractsService/UserErrorCannotCreateOneSidedExchangeContract')
                raise UserError('CustomInfo', {'info': errorLabel})

    def OnComboChange(self, wnd, *args):
        if wnd.name == 'startStation' or wnd.name == 'startStationDivision':
            if wnd.name == 'startStation':
                self.data.startStation = wnd.GetValue()
            else:
                self.data.startStationDivision = wnd.GetValue()
            self.data.items = {}
            self.GotoPage(self.currPage)

    def OnStepChange(self, move, *args):
        if self.currPage + move >= 4:
            if eve.Message('ConConfirmCreateContract', {}, uiconst.YESNO, suppress=uiconst.ID_YES) == uiconst.ID_YES:
                try:
                    self.CreateContract()
                except:
                    self.Maximize()
                    raise

        elif self.currPage + move >= 0 and (move < 0 or self.FinishStep(self.currPage)):
            self.GotoPage(self.currPage + move)

    def ClickItem(self, *args):
        pass

    def OnDeleteContract(self, contractID, *args):
        self.numOutstandingContracts = None

    def OnCancel(self, *args):
        if eve.Message('ConAreYouSureYouWantToCancel', None, uiconst.YESNO, suppress=uiconst.ID_YES) == uiconst.ID_YES:
            self.Close()

    def ResetWizard(self):
        self.data = util.KeyVal()
        self.data.items = {}
        self.data.reqItems = {}
        self.data.startStation = None
        self.data.endStation = None
        self.data.startStationDivision = 0
        self.data.type = const.conTypeNothing
        self.SetWndIcon(GetContractIcon(const.conTypeNothing), mainTop=-10)

    def WriteSelectItems(self, title):
        forCorp = self.data.forCorp
        deliveriesRoles = const.corpRoleAccountant | const.corpRoleJuniorAccountant | const.corpRoleTrader
        if forCorp:
            rows = sm.RemoteSvc('corpmgr').GetAssetInventory(eve.session.corpid, 'offices')
            sortops = []
            for r in rows:
                stationName = cfg.evelocations.Get(r.locationID).name
                sortops.append((stationName, (stationName, r.locationID)))

            if session.corprole & deliveriesRoles > 0:
                rows = sm.RemoteSvc('corpmgr').GetAssetInventory(eve.session.corpid, 'deliveries')
                for r in rows:
                    stationName = cfg.evelocations.Get(r.locationID).name
                    stat = (stationName, (stationName, r.locationID))
                    if stat not in sortops:
                        sortops.append(stat)

            ops = [(title, 0)] + uiutil.SortListOfTuples(sortops)
        else:
            stations = sm.GetService('invCache').GetInventory(const.containerGlobal).ListStations()
            stations = [ s for s in stations if self.CanContractItemsFromLocation(s.stationID) ]
            primeloc = []
            for station in stations:
                primeloc.append(station.stationID)

            if len(primeloc):
                cfg.evelocations.Prime(primeloc)
            sortops = []
            for station in stations:
                stationName = cfg.evelocations.Get(station.stationID).name
                itemCount = station.itemCount
                if station.stationID in (session.stationid, session.structureid):
                    itemCount -= 1
                itemsInStationLabel = GetByLabel('UI/Contracts/ContractsService/ItemsInStation', station=station.stationID, numItems=itemCount)
                sortops.append((stationName.lower(), (itemsInStationLabel, station.stationID)))

            ops = [(title, 0)] + uiutil.SortListOfTuples(sortops)
        comboParent = Container(name='comboParent', parent=self.formWnd, align=uiconst.TOTOP, top=const.defaultPadding)
        Container(name='push', parent=comboParent, align=uiconst.TOLEFT, width=1)
        Container(name='push', parent=comboParent, align=uiconst.TORIGHT, width=1)
        combo = uicontrols.Combo(label=None, parent=comboParent, options=ops, name='startStation', select=None, callback=self.OnComboChange, align=uiconst.TOALL)
        comboParent.height = 18
        if self.data.startStation is None:
            if eve.session.stationid:
                self.data.startStation = eve.session.stationid
            elif eve.session.structureid:
                self.data.startStation = eve.session.structureid
        if forCorp:
            divs = [(GetByLabel('UI/Contracts/ContractsWindow/SelectDivision'), 0)]
            paramsByDivision = {1: (const.flagHangar, const.corpRoleHangarCanQuery1, const.corpRoleHangarCanTake1),
             2: (const.flagCorpSAG2, const.corpRoleHangarCanQuery2, const.corpRoleHangarCanTake2),
             3: (const.flagCorpSAG3, const.corpRoleHangarCanQuery3, const.corpRoleHangarCanTake3),
             4: (const.flagCorpSAG4, const.corpRoleHangarCanQuery4, const.corpRoleHangarCanTake4),
             5: (const.flagCorpSAG5, const.corpRoleHangarCanQuery5, const.corpRoleHangarCanTake5),
             6: (const.flagCorpSAG6, const.corpRoleHangarCanQuery6, const.corpRoleHangarCanTake6),
             7: (const.flagCorpSAG7, const.corpRoleHangarCanQuery7, const.corpRoleHangarCanTake7)}
            if self.data.startStation and not util.IsStation(self.data.startStation):
                paramsByDivision[1] = (const.flagCorpSAG1, const.corpRoleHangarCanQuery1, const.corpRoleHangarCanTake1)
            divisions = sm.GetService('corp').GetDivisionNames()
            i = 0
            NUM_DIVISIONS = 7
            while i < NUM_DIVISIONS:
                i += 1
                flag, roleCanQuery, roleCanTake = paramsByDivision[i]
                divisionName = divisions[i]
                divs.append((divisionName, flag))

            if eve.session.corprole & deliveriesRoles > 0:
                divs.append((GetByLabel('UI/Contracts/ContractsWindow/Deliveries'), const.flagCorpMarket))
            comboDiv = uicontrols.Combo(label='', parent=comboParent, options=divs, name='startStationDivision', select=None, callback=self.OnComboChange, align=uiconst.TORIGHT, width=100, pos=(1, 0, 0, 0), idx=0)
            Container(name='push', parent=comboParent, align=uiconst.TORIGHT, width=4, idx=1)
            nudge = 18
        i = 0
        for name, val in combo.entries:
            if val == self.data.startStation:
                combo.SelectItemByIndex(i)
                break
            i += 1

        if forCorp:
            i = 0
            for name, val in comboDiv.entries:
                if val == self.data.startStationDivision:
                    comboDiv.SelectItemByIndex(i)
                    break
                i += 1

        c = Container(name='volume', parent=self.formWnd, align=uiconst.TOBOTTOM, width=6, height=20)
        numVolLabel = GetByLabel('UI/Contracts/ContractsService/NumberOfWithVolume', number=0, volume=0)
        self.sr.volumeText = uicontrols.EveLabelMedium(text=numVolLabel, parent=c, state=uiconst.UI_DISABLED, align=uiconst.CENTERRIGHT)
        self.UpdateNumberOfItems()
        selectBtn = uicontrols.ButtonGroup(btns=[[GetByLabel('UI/Common/SelectAll'),
          self.SelectAll,
          (),
          None], [GetByLabel('UI/Common/DeselectAll'),
          self.DeselectAll,
          (),
          None]], parent=self.formWnd)
        selectBtn.display = False
        self.sr.itemsScroll = uicontrols.Scroll(parent=self.formWnd, padTop=const.defaultPadding, padBottom=const.defaultPadding)
        if forCorp:
            if not self.data.startStation:
                self.sr.itemsScroll.ShowHint(GetByLabel('UI/Search/SelectStation'))
                if self.data.startStationDivision == 0:
                    self.sr.itemsScroll.ShowHint(GetByLabel('UI/Contracts/ContractEntry/SelectStationDivision'))
            elif self.data.startStationDivision == 0:
                self.sr.itemsScroll.ShowHint(GetByLabel('UI/Contracts/ContractsWindow/SelectDivision'))
        validStartStation = self.data.startStation and self.CanContractItemsFromLocation(self.data.startStation)
        if validStartStation and (not forCorp or self.data.startStationDivision):
            self.sr.itemsScroll.Load(contentList=[], headers=[], noContentHint=GetByLabel('UI/Contracts/ContractsWindow/NoItemsFound'))
            self.sr.itemsScroll.ShowHint(GetByLabel('UI/Contracts/ContractsWindow/GettingItems'))
            items = sm.GetService('contracts').GetItemsInStation(self.data.startStation, forCorp)
            self.sr.itemsScroll.hiliteSorted = 0
            scrolllist = []

            def sameFlag(itemFlag):
                if itemFlag == self.data.startStationDivision:
                    return True
                if set((itemFlag, self.data.startStationDivision)) == set((const.flagHangar, const.flagCorpSAG1)):
                    return True
                return False

            for item in items:
                if forCorp and not sameFlag(item.flagID):
                    continue
                data = uix.GetItemData(item, 'list', viewOnly=1)
                volume = GetItemVolume(item)
                itemName = ''
                isContainer = item.groupID in (const.groupCargoContainer,
                 const.groupSecureCargoContainer,
                 const.groupAuditLogSecureContainer,
                 const.groupFreightContainer) and item.singleton
                if item.categoryID == const.categoryShip or isContainer:
                    if item.itemID == util.GetActiveShip():
                        continue
                    shipName = cfg.evelocations.GetIfExists(item.itemID)
                    if shipName is not None:
                        itemName = shipName.locationName
                details = itemName
                label = '%s<t>%s<t>%s<t>%s' % (evetypes.GetName(item.typeID),
                 item.stacksize,
                 volume,
                 details)
                scrolllist.append(listentry.Get('ContractItemSelect', {'info': item,
                 'stationID': self.data.startStation,
                 'forCorp': forCorp,
                 'flag': item.flagID,
                 'itemID': item.itemID,
                 'typeID': item.typeID,
                 'isCopy': item.categoryID == const.categoryBlueprint and item.singleton == const.singletonBlueprintCopy,
                 'label': label,
                 'quantity': item.stacksize,
                 'getIcon': 1,
                 'item': item,
                 'checked': item.itemID in self.data.items,
                 'cfgname': item.itemID,
                 'retval': (item,
                            item.itemID,
                            item.typeID,
                            item.stacksize),
                 'OnChange': self.OnItemSelectedChanged}))

            if self.sr.itemsScroll is not None:
                if scrolllist:
                    self.sr.itemsScroll.ShowHint()
                    selectBtn.display = True
                self.sr.itemsScroll.sr.id = 'itemsScroll'
                self.sr.itemsScroll.sr.lastSelected = None
                self.sr.itemsScroll.Load(contentList=scrolllist, headers=[GetByLabel('UI/Common/Type'),
                 GetByLabel('UI/Inventory/ItemQuantityShort'),
                 GetByLabel('UI/Common/Volume'),
                 GetByLabel('UI/Common/Details')])

    def CanContractItemsFromLocation(self, locationID):
        if util.IsStation(locationID):
            return True
        return sm.GetService('structureDirectory').CanContractFrom(locationID)

    def DeselectAll(self, *args):
        self.ChangeCheckboxStates(onoff=False)

    def SelectAll(self, *args):
        self.ChangeCheckboxStates(onoff=True)

    def ChangeCheckboxStates(self, onoff):
        if not self.sr.itemsScroll:
            return
        for node in self.sr.itemsScroll.GetNodes():
            if node:
                node.checked = onoff
                if node.panel:
                    node.panel.sr.checkbox.SetChecked(onoff, 0)
                self.ChangeItemSelection(onoff, updateNumber=False, *node.retval)

        self.UpdateNumberOfItems()

    def OnItemSelectedChanged(self, checkbox, *args):
        item, itemID, typeID, qty = checkbox.data['retval']
        gv = True
        try:
            gv = checkbox.GetValue()
        except:
            pass

        self.ChangeItemSelection(gv, item, itemID, typeID, qty)

    def ChangeItemSelection(self, checkboxSelected, item, itemID, typeID, qty, updateNumber = True):
        if checkboxSelected:
            self.data.items[itemID] = [typeID, qty, item]
        elif itemID in self.data.items:
            del self.data.items[itemID]
        if updateNumber:
            self.UpdateNumberOfItems()

    def UpdateNumberOfItems(self):
        totalVolume = 0
        num = 0
        for itemID, item in self.data.items.iteritems():
            totalVolume += GetItemVolume(item[2])
            num += 1

        numVolLabel = GetByLabel('UI/Contracts/ContractsService/NumberOfWithVolume', number=num, volume=util.FmtAmt(totalVolume))
        if num > MAX_NUM_ITEMS:
            numVolLabel = '<color=red>' + numVolLabel + '</color>'
        self.sr.volumeText.text = numVolLabel

    def CalcBasePrice(self):
        price = 0
        for item in self.data.items.itervalues():
            price += int(float(evetypes.GetBasePrice(item[0])) / evetypes.GetPortionSize(item[0]) * item[1])

        if price > 1000000:
            price = int(price / 100000) * 100000
        if price == 0:
            raise UserError('ConNoBasePrice')
        return price

    def CalcBasePriceCollateral(self, *args):
        price = self.CalcBasePrice()
        if eve.Message('ConBasePrice', {'price': util.FmtISK(price, 0)}, uiconst.YESNO, suppress=uiconst.ID_YES) == uiconst.ID_YES:
            self.formWnd.sr.collateral.SetValue(price)

    def CalcBasePricePrice(self, *args):
        price = self.CalcBasePrice()
        if eve.Message('ConBasePrice', {'price': util.FmtISK(price, 0)}, uiconst.YESNO, suppress=uiconst.ID_YES) == uiconst.ID_YES:
            self.formWnd.sr.price.SetValue(price)

    def OnItemSplit(self, itemID, amountRemoved):
        if itemID in self.data.items:
            self.data.items[itemID][1] -= amountRemoved
            if self.data.items[itemID][1] <= 0:
                del self.data.items[itemID]
