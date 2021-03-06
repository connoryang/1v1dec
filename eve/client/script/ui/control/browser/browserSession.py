#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\control\browser\browserSession.py
import browser
import browserutil
import corebrowserutil
import blue
import evetypes
import uthread
import urlparse
import browserConst
import menu
import util
import base64
import log
import os
import carbonui.const as uiconst
import localization
import uicls
import uiutil
import ccpmetrics
import utillib
t = 0
metrics = ccpmetrics.Client('public-metrics.tech.ccp.is')

def ThreadDeco(f):

    def wrapper(*args):
        global t
        dt = 0
        dt = blue.os.GetWallclockTime() - t
        t = blue.os.GetWallclockTime()
        if dt > 900 * const.MSEC:
            uthread.new(f, *args)
        else:
            eve.Message('IGBFunctionThrottling')

    return wrapper


class EveBrowserSession(browser.CoreBrowserSession):

    def AppStartup(self, sessionName, initialUrl = None, browserEventHandler = None, autoHandleLockdown = True, *args):
        self.title = localization.GetByLabel('UI/Browser/UntitledPage')

    def AppCleanup(self):
        pass

    def AppGetJavascriptObjectName(self):
        return 'CCPEVE'

    def AppSetupBrowserSession(self):
        self.RegisterCommonJavascriptCallbacks()
        self.browserHostManager.AddToUserAgent('EVE-IGB')

    def AppGetHomepage(self):
        return str(settings.user.ui.Get('HomePage2', browserutil.DefaultHomepage()))

    def AppOnBlockLoading(self, statusCode):
        sm.GetService('sites').LogInfo('Loading was blocked, code ', statusCode)
        loadError = localization.GetByLabel('UI/Browser/LoadError')
        errorString = '<html><title>%s</title><body><h1>%s</h1>' % (loadError, loadError)
        errorString += '<p>%s</p>' % corebrowserutil.GetErrorString(statusCode)
        errorString += '<p><i>%s: %i</i></p></body>' % (localization.GetByLabel('UI/Browser/ErrorCode'), statusCode)
        self.browser.LoadHTML(errorString)

    def AppOnBlockBlacklistSite(self):
        eve.Message('BrowserSiteCCPBlacklisted')

    def AppOnBlockNonWhitelistSite(self):
        eve.Message('BrowserLockdownEnabled')

    def AppOnOpenContextMenu(self, nodeType, linkUrl, imageUrl, pageUrl, frameUrl, editFlags):
        menuData = []
        eventHandlerCanTab = hasattr(self.browserEventHandler, 'AddTab')
        if nodeType & browserConst.selectedPage and not self.isViewSourceMode:
            if len(menuData) > 0:
                menuData.append(None)
            pageUrl = str(pageUrl)
            menuData.append((localization.GetByLabel('UI/Browser/Back'), self.HistoryBack, []))
            menuData.append((localization.GetByLabel('UI/Browser/Forward'), self.HistoryForward, []))
            menuData.append((localization.GetByLabel('UI/Browser/ReloadPage'), self.ReloadPage, []))
            menuData.append((localization.GetByLabel('UI/Browser/Stop'), self.StopLoading, []))
            menuData.append(None)
            menuData.append((localization.GetByLabel('UI/Browser/ViewPageSource'), self.ViewSourceOfUrl, [pageUrl]))
        if nodeType & browserConst.selectedFrame and not self.isViewSourceMode:
            if len(menuData) > 0:
                menuData.append(None)
            menuData.append((localization.GetByLabel('UI/Browser/Back'), self.HistoryBack, []))
            menuData.append((localization.GetByLabel('UI/Browser/Forward'), self.HistoryForward, []))
            menuData.append((localization.GetByLabel('UI/Browser/Stop'), self.StopLoading, []))
            menuData.append(None)
            frameUrl = str(frameUrl)
            if eventHandlerCanTab:
                menuData.append((localization.GetByLabel('UI/Browser/OpenFrameInNewTab'), self.LaunchNewTab, [frameUrl]))
            menuData.append((localization.GetByLabel('UI/Browser/ViewFrameSource'), self.ViewSourceOfUrl, [frameUrl]))
            menuData.append(None)
            menuData.append((localization.GetByLabel('UI/Browser/ViewPageSource'), self.ViewSourceOfUrl, [pageUrl]))
        if nodeType & browserConst.selectedLink:
            if len(menuData) > 0:
                menuData.append(None)
            linkUrl = str(linkUrl)
            if not self.isViewSourceMode:
                menuData.append((localization.GetByLabel('UI/Browser/OpenLink'), self.BrowseTo, [linkUrl]))
                if eventHandlerCanTab:
                    menuData.append((localization.GetByLabel('UI/Browser/OpenLinkInNewTab'), self.LaunchNewTab, [linkUrl]))
            menuData.append((localization.GetByLabel('UI/Browser/CopyLinkLocation'), self.CopyText, [linkUrl]))
        if nodeType & browserConst.selectedImage and not self.isViewSourceMode:
            if len(menuData) > 0:
                menuData.append(None)
            imageUrl = str(imageUrl)
            menuData.append((localization.GetByLabel('UI/Browser/ViewImage'), self.BrowseTo, [imageUrl]))
            menuData.append((localization.GetByLabel('UI/Browser/CopyImageLocation'), self.CopyText, [imageUrl]))
        tempMenu = []
        if editFlags & browserConst.flagCanCut:
            tempMenu.append((uiutil.MenuLabel('UI/Common/Cut'), self.PerformCommand, [browserConst.commandCut]))
        if editFlags & browserConst.flagCanCopy:
            tempMenu.append((uiutil.MenuLabel('UI/Common/Copy'), self.PerformCommand, [browserConst.commandCopy]))
        if editFlags & browserConst.flagCanPaste:
            tempMenu.append((uiutil.MenuLabel('UI/Common/Paste'), self.PerformCommand, [browserConst.commandPaste]))
        if editFlags & browserConst.flagCanDelete:
            tempMenu.append((uiutil.MenuLabel('UI/Common/Delete'), self.PerformCommand, [browserConst.commandDelete]))
        if len(tempMenu) > 0:
            if len(menuData) > 0:
                menuData.append(None)
            menuData.extend(tempMenu)
            tempMenu = []
        if editFlags & browserConst.flagCanSelectAll:
            tempMenu.append((uiutil.MenuLabel('UI/Common/SelectAll'), self.PerformCommand, [browserConst.commandSelectAll]))
        if len(tempMenu) > 0:
            if len(menuData) > 0:
                menuData.append(None)
            menuData.extend(tempMenu)
            tempMenu = []
        if len(menuData) > 0:
            mv = menu.CreateMenuView(menu.CreateMenuFromList(menuData), None, None)
            x, y = uicore.uilib.x + 10, uicore.uilib.y
            x, y = min(uicore.desktop.width - mv.width, x), min(uicore.desktop.height - mv.height, y)
            mv.left, mv.top = x, y
            uicore.layer.menu.children.insert(0, mv)

    def AddJavascriptCallbackForRestrictedFunction(self, callbackName, callbackFunction):
        if not self:
            return
        if not hasattr(self, 'browser') or self.browser is None:
            return
        self.browser.RegisterJavaScriptCallback(self.AppGetJavascriptObjectName(), callbackName, callbackFunction)
        self.browserHostManager.AssignCallbackToList(self.AppGetJavascriptObjectName(), callbackName, 'trusted')
        self.browserHostManager.AssignCallbackToList(self.AppGetJavascriptObjectName(), callbackName, 'CCP')
        self.browserHostManager.AssignCallbackToList(self.AppGetJavascriptObjectName(), callbackName, 'COMMUNITY')

    def RegisterCommonJavascriptCallbacks(self):
        self.AddJavascriptCallback('openEveMail', OpenEveMail)
        self.AddJavascriptCallback('showInfo', ShowInfo)
        self.AddJavascriptCallback('showRouteTo', self.ShowRouteTo)
        self.AddJavascriptCallback('showMap', self.ShowMap)
        self.AddJavascriptCallback('showPreview', ShowPreview)
        self.AddJavascriptCallback('showFitting', ShowFitting)
        self.AddJavascriptCallback('showContract', ShowContract)
        self.AddJavascriptCallback('showMarketDetails', ShowMarketDetails)
        self.AddJavascriptCallback('requestTrust', self.RequestTrust)
        self.AddJavascriptCallbackForRestrictedFunction('setDestination', self.SetDestination)
        self.AddJavascriptCallbackForRestrictedFunction('addWaypoint', self.AddWaypoint)
        self.AddJavascriptCallbackForRestrictedFunction('joinChannel', self.JoinChannel)
        self.AddJavascriptCallbackForRestrictedFunction('joinMailingList', self.JoinMailingList)
        self.AddJavascriptCallbackForRestrictedFunction('createContract', self.CreateContract)
        self.AddJavascriptCallbackForRestrictedFunction('sellItem', self.SellItem)
        self.AddJavascriptCallbackForRestrictedFunction('buyType', self.BuyType)
        self.AddJavascriptCallbackForRestrictedFunction('findInContracts', self.FindInContracts)
        self.AddJavascriptCallbackForRestrictedFunction('addToMarketQuickBar', self.AddToMarketQuickBar)
        self.AddJavascriptCallbackForRestrictedFunction('showContents', self.ShowContents)
        self.AddJavascriptCallbackForRestrictedFunction('addContact', self.AddContact)
        self.AddJavascriptCallbackForRestrictedFunction('addCorpContact', self.AddCorpContact)
        self.AddJavascriptCallbackForRestrictedFunction('removeContact', self.RemoveContact)
        self.AddJavascriptCallbackForRestrictedFunction('removeCorpContact', self.RemoveCorpContact)
        self.AddJavascriptCallbackForRestrictedFunction('block', self.Block)
        self.AddJavascriptCallbackForRestrictedFunction('addBounty', self.AddBounty)
        self.AddJavascriptCallbackForRestrictedFunction('inviteToFleet', self.InviteToFleet)
        self.AddJavascriptCallbackForRestrictedFunction('startConversation', self.StartConversation)
        self.AddJavascriptCallbackForRestrictedFunction('showContracts', self.ShowContracts)
        self.AddJavascriptCallbackForRestrictedFunction('showOnMap', self.ShowOnMap)
        self.AddJavascriptCallbackForRestrictedFunction('editMember', self.EditMember)
        self.AddJavascriptCallbackForRestrictedFunction('awardDecoration', self.AwardDecoration)
        self.AddJavascriptCallbackForRestrictedFunction('sendMail', self.SendMail)
        self.AddJavascriptCallbackForRestrictedFunction('bookmark', self.Bookmark)
        self.AddJavascriptCallbackForRestrictedFunction('showSovereignty', self.ShowSovereignty)
        self.AddJavascriptCallbackForRestrictedFunction('clearAllWaypoints', self.ClearAllWaypoints)

    def _IsBrowserWindowActive(self):
        if self.browserEventHandler and self.browserEventHandler == uicore.registry.GetActiveStackOrWindow():
            return True
        return False

    @ThreadDeco
    def _ShowCharacter(self, charid, size):
        filename = os.path.join(blue.paths.ResolvePath(u'cache:/Pictures/Portraits/%s_%s.png' % (charid, size)))
        image = base64.b64encode(file(filename, 'rb').read())
        self.browser.BrowseTo("JavaScript:updateImage('%s')" % image)

    @ThreadDeco
    def ShowRouteTo(self, *args):
        submit_metric('igb_show_route_to')
        if not self._IsBrowserWindowActive():
            return
        destinationID = None
        sourceID = None
        if len(args) < 1:
            log.LogError('Insufficient arguments for CCPEVE.ShowRouteTo. You must pass in at least one argument.')
            return
        if len(args) == 1:
            fromto = args[0].split('::')
            if len(fromto) == 2:
                destinationID = fromto[0]
                sourceID = fromto[1]
            else:
                destinationID = args[0]
        else:
            destinationID = args[0]
            sourceID = args[1]
        if eve.session.stationid:
            sm.GetService('station').CleanUp()
        destinationID = browserutil.SanitizedSolarsystemID(destinationID)
        if sourceID is not None:
            sourceID = browserutil.SanitizedSolarsystemID(sourceID)
        if destinationID is None:
            log.LogError('Error when converting destinationID in CCPEVE.ShowRouteTo. First argument must be an integer.')
            return
        interestID = sourceID if sourceID is not None else eve.session.regionid
        from eve.client.script.ui.shared.mapView.mapViewUtil import OpenMap
        OpenMap(interestID=interestID, drawRoute=(sourceID, destinationID))
        if self.browserEventHandler and hasattr(self.browserEventHandler, 'Minimize'):
            self.browserEventHandler.Minimize()

    @ThreadDeco
    def ShowMap(self, *args):
        submit_metric('igb_show_map')
        if not self._IsBrowserWindowActive():
            return
        interestID = None
        for arg in args:
            solarsystemIDs = [ ssID for ssID in arg.split('//') ]
            for ssID in solarsystemIDs:
                interestID = browserutil.SanitizedSolarsystemID(ssID)
                if interestID is not None:
                    break

            if interestID is not None:
                break

        if interestID is None:
            interestID = session.solarsystemid2
        from eve.client.script.ui.shared.mapView.mapViewUtil import OpenMap
        OpenMap(interestID=interestID)
        if self.browserEventHandler and hasattr(self.browserEventHandler, 'Minimize'):
            self.browserEventHandler.Minimize()

    @ThreadDeco
    def SetDestination(self, *args):
        submit_metric('igb_set_destination')
        destinationID = None
        for arg in args:
            destinationID = browserutil.SanitizedDestinationID(arg)
            if destinationID is not None:
                break

        sm.GetService('starmap').SetWaypoint(destinationID, clearOtherWaypoints=True)

    @ThreadDeco
    def AddWaypoint(self, *args):
        submit_metric('igb_add_waypoint')
        destinationIDs = []
        for arg in args:
            ssID = browserutil.SanitizedDestinationID(arg)
            if ssID is not None:
                destinationIDs.append(ssID)

        if len(destinationIDs) > 0:
            starMapSvc = sm.GetService('starmap')
            for destinationID in destinationIDs:
                if destinationID not in starMapSvc.GetWaypoints():
                    starMapSvc.SetWaypoint(destinationID, clearOtherWaypoints=False, first=False)

    def RequestTrust(self, inputUrl):
        submit_metric('igb_request_trust')
        uthread.new(self._RequestTrust, inputUrl)

    def _RequestTrust(self, inputUrl):
        if not inputUrl.startswith('http://') and not inputUrl.startswith('https://'):
            log.LogError('CCPEVE.RequestTrust - Input URL must start with either http:// or https:// -- received', inputUrl)
            return
        scheme, netloc, path, query, fragment = urlparse.urlsplit(inputUrl)
        if path is None or path == '':
            path = '/'
        trustUrl = '%s://%s%s' % (scheme, netloc, path)
        if sm.GetService('sites').IsTrusted(trustUrl) or sm.GetService('sites').IsIgnored(trustUrl):
            log.LogInfo('CCPEVE.RequestTrust - Received top-level URL is already trusted or ignored:', trustUrl)
            return
        currentUrl = self.GetCurrentURL()
        if sm.GetService('sites').IsIgnored(currentUrl):
            log.LogInfo('CCPEVE.RequestTrust - Calling URL is ignored, discarding:', currentUrl)
            return
        wnd = uicls.TrustedSitePromptWindow.GetIfOpen(windowID='trustPromptWindow_%s' % netloc)
        if wnd:
            wnd.Maximize()
            log.LogWarn('CCPEVE.RequestTrust - Trust prompt window was already open - skipping!')
            return
        wnd = uicls.TrustedSitePromptWindow.Open(windowID='trustPromptWindow_%s' % netloc, trustUrl=inputUrl, inputUrl=currentUrl)

    @ThreadDeco
    def JoinChannel(self, channelName):
        submit_metric('igb_join_channel')
        if channelName is None:
            return
        channelName = channelName.strip()
        if len(channelName) > 0:
            sm.GetService('LSC').CreateOrJoinChannel(channelName, create=False)

    @ThreadDeco
    def JoinMailingList(self, mailingListName):
        submit_metric('igb_join_mailing_list')
        if mailingListName is None:
            return
        listName = mailingListName.strip()
        if len(listName) > 0:
            sm.GetService('mailinglists').JoinMailingList(listName)

    @ThreadDeco
    def CreateContract(self, contractType, stationID = None, itemIDs = None):
        submit_metric('igb_create_contract')
        if contractType:
            contractType = int(contractType)
        if itemIDs:
            itemIDs = [ int(i) for i in itemIDs.split(',') ]
        if stationID:
            stationID = int(stationID)
        sm.GetService('contracts').OpenCreateContractFromIGB(contractType, stationID, itemIDs)

    @ThreadDeco
    def SellItem(self, stationID, itemID):
        submit_metric('igb_sell_item')
        itemID = int(itemID)
        stationID = int(stationID)
        items = sm.GetService('invCache').GetInventory(const.containerGlobal).ListStationItems(stationID)
        for item in items:
            if item.itemID == itemID:
                sm.GetService('menu').QuickSell(item)
                return

        log.LogError('SellItem, item', itemID, 'not found in', stationID)

    @ThreadDeco
    def BuyType(self, typeID):
        submit_metric('igb_buy_type')
        typeID = ValidTypeID(typeID)
        if typeID:
            sm.GetService('marketutils').Buy(typeID)

    @ThreadDeco
    def FindInContracts(self, typeID):
        submit_metric('igb_find_in_contracts')
        typeID = ValidTypeID(typeID)
        if typeID:
            sm.GetService('contracts').FindRelated(typeID, 0, 0, 0, 0, 0, 0)

    @ThreadDeco
    def AddToMarketQuickBar(self, typeID):
        submit_metric('igb_add_to_market_quick_bar')
        typeID = ValidTypeID(typeID)
        if typeID:
            sm.GetService('marketutils').AddTypeToQuickBar(typeID)

    @ThreadDeco
    def AddContact(self, characterID):
        submit_metric('igb_add_contact')
        characterID = ValidCharacterID(characterID)
        if characterID:
            addressBookSvc = sm.GetService('addressbook')
            if addressBookSvc.IsInAddressBook(characterID, 'contact'):
                addressBookSvc.EditContacts([characterID], 'contact')
            else:
                addressBookSvc.AddToAddressBook(characterID, 'contact')

    @ThreadDeco
    def RemoveContact(self, characterID):
        submit_metric('igb_remove_contact')
        characterID = ValidCharacterID(characterID)
        if characterID:
            addressBookSvc = sm.GetService('addressbook')
            if addressBookSvc.IsInAddressBook(characterID, 'contact'):
                addressBookSvc.RemoveFromAddressBook([characterID], 'contact')

    @ThreadDeco
    def AddCorpContact(self, corpContactID):
        submit_metric('igb_add_corp_contact')
        corpContactID = ValidCorpID(corpContactID)
        if corpContactID:
            addressBookSvc = sm.GetService('addressbook')
            if addressBookSvc.IsInAddressBook(corpContactID, 'corpcontact'):
                addressBookSvc.EditContacts([corpContactID], 'corpcontact')
            else:
                addressBookSvc.AddToAddressBook(corpContactID, 'corpcontact')

    @ThreadDeco
    def RemoveCorpContact(self, charOrCorpID):
        submit_metric('igb_remove_corp_contact')
        charOrCorpID = ValidCorpID(charOrCorpID)
        if charOrCorpID:
            addressBookSvc = sm.GetService('addressbook')
            if addressBookSvc.IsInAddressBook(charOrCorpID, 'corpcontact'):
                addressBookSvc.RemoveFromAddressBook([charOrCorpID], 'corpcontact')

    @ThreadDeco
    def Block(self, characterID):
        submit_metric('igb_block')
        if eve.Message('BlockUserConfirmation', {'charName': (const.UE_OWNERID, characterID)}, uiconst.YESNO) == uiconst.ID_YES:
            characterID = ValidCharacterID(characterID)
            if characterID:
                addressBookSvc = sm.GetService('addressbook')
                if addressBookSvc.IsInAddressBook(characterID, 'contact'):
                    addressBookSvc.BlockOwner(characterID)

    @ThreadDeco
    def AddBounty(self, characterID):
        submit_metric('igb_add_bounty')
        characterID = ValidCharacterID(characterID)
        if characterID:
            uicore.cmd.OpenMissions(characterID)

    @ThreadDeco
    def InviteToFleet(self, characterID):
        submit_metric('igb_invite_to_fleet')
        if eve.Message('InviteToFleetConfirmation', {'charName': (const.UE_OWNERID, characterID)}, uiconst.YESNO) == uiconst.ID_YES:
            characterID = ValidCharacterID(characterID)
            if characterID:
                sm.GetService('menu').InviteToFleet(characterID)

    @ThreadDeco
    def StartConversation(self, characterID):
        submit_metric('igb_start_conversation')
        if eve.Message('StartConversationConfirmation', {'charName': (const.UE_OWNERID, characterID)}, uiconst.YESNO) == uiconst.ID_YES:
            characterID = ValidCharacterID(characterID)
            if characterID:
                if util.IsNPC(characterID):
                    sm.GetService('agents').InteractWith(characterID)
                else:
                    sm.GetService('LSC').Invite(characterID)

    @ThreadDeco
    def ShowContracts(self, charOrCorpID):
        submit_metric('igb_show_contracts')
        charOrCorpID = ValidCharacterID(charOrCorpID)
        if charOrCorpID:
            sm.GetService('contracts').Show(cfg.eveowners.Get(charOrCorpID).ownerName)

    @ThreadDeco
    def ShowOnMap(self, corpID):
        submit_metric('igb_show_on_map')
        if not self._IsBrowserWindowActive():
            return
        corpID = ValidCorpID(corpID)
        if corpID:
            sm.GetService('menu').ShowInMap(corpID)

    @ThreadDeco
    def EditMember(self, characterID):
        submit_metric('igb_edit_member')
        characterID = ValidCharacterID(characterID)
        if characterID:
            sm.GetService('menu').ShowCorpMemberDetails(characterID)

    @ThreadDeco
    def AwardDecoration(self, characterID):
        submit_metric('igb_award_decoration')
        characterID = ValidCharacterID(characterID)
        if characterID:
            sm.GetService('menu').AwardDecoration(characterID)

    @ThreadDeco
    def SendMail(self, characterID, subject, body):
        submit_metric('igb_send_mail')
        characterID = ValidCharacterID(characterID)
        subject = ValidSubject(subject)
        body = ValidBody(body)
        if characterID and subject and body:
            sm.GetService('mailSvc').SendMsgDlg([characterID], subject=subject, body=body)

    @ThreadDeco
    def ShowContents(self, stationID, itemID):
        submit_metric('igb_show_contents')
        stationID = ValidItemID(stationID)
        itemID = ValidItemID(itemID)
        sm.GetService('menu').DoGetContainerContents(itemID, stationID, True, localization.GetByLabel('UI/Browser/Container'))

    @ThreadDeco
    def Bookmark(self, locationID):
        submit_metric('igb_bookmark')
        locationID = ValidLocationID(locationID)
        parentID = sm.GetService('map').GetParentLocationID(locationID)
        sm.GetService('addressbook').BookmarkLocationPopup(locationID, None, parentID)

    @ThreadDeco
    def ShowSovereignty(self, itemID):
        submit_metric('igb_show_sovereignty')
        if util.IsConstellation(itemID):
            constellationID = itemID
        if util.IsSolarSystem(itemID):
            systemID = itemID
        if util.IsRegion(itemID):
            regionID = itemID
        location = (systemID, constellationID, regionID)
        sm.GetService('sov').GetSovOverview(location)

    @ThreadDeco
    def ClearAllWaypoints(self):
        submit_metric('igb_clear_all_waypoints')
        sm.GetService('starmap').ClearWaypoints()


def ValidTypeID(typeID):
    return int(typeID)


def ValidItemID(itemID):
    return int(itemID)


def ValidLocationID(locationID):
    return int(locationID)


def ValidCharacterID(characterID):
    return int(characterID)


def ValidCorpID(corpID):
    return int(corpID)


def ValidSubject(subject):
    return str(subject)


def ValidBody(body):
    return str(body)


@ThreadDeco
def OpenEveMail():
    submit_metric('igb_open_eve_mail')
    sm.GetService('cmd').OpenMail()


@ThreadDeco
def ShowInfo(*args):
    submit_metric('igb_show_info')
    typeID = None
    itemID = None
    if len(args) <= 0:
        log.LogError('CCPEVE.ShowInfo requires at least one argument!')
        return
    if len(args) == 1:
        typeID = args[0]
        if typeID.find('//') >= 0:
            log.LogWarn('CCPEVE.ShowInfo: Old-style arguments are being passed in!')
            ids = typeID.split('//')
            typeID = ids[0]
            itemID = None
            if len(ids) > 1:
                try:
                    itemID = int(ids[1])
                except:
                    log.LogError('CCPEVE.ShowInfo failed to convert itemID in string:' + ids[1])
                    return

    else:
        typeID = args[0]
        itemID = args[1]
    safeTypeID = browserutil.SanitizedTypeID(typeID)
    if safeTypeID is None:
        log.LogError('Type ID passed to CCPEVE.ShowInfo was invalid:', typeID)
        return
    if itemID is not None:
        itemID = browserutil.SanitizedItemID(itemID)
    if evetypes.GetCategoryID(safeTypeID) == const.categoryAbstract:
        abstractinfo = util.KeyVal()
        if typeID == const.typeCertificate:
            abstractinfo.certificateID = itemID
        sm.GetService('info').ShowInfo(safeTypeID, itemID, abstractinfo=abstractinfo)
    else:
        sm.GetService('info').ShowInfo(safeTypeID, itemID)


@ThreadDeco
def ShowPreview(typeID):
    submit_metric('igb_show_preview')
    safeTypeID = browserutil.SanitizedTypeID(int(typeID))
    if safeTypeID is None or not util.IsPreviewable(safeTypeID):
        log.LogError('Type ID passed to Client.ShowPreview was invalid:', typeID)
        return
    sm.GetService('preview').PreviewType(safeTypeID)


@ThreadDeco
def ShowFitting(fitting):
    submit_metric('igb_show_fitting')
    sm.GetService('fittingSvc').DisplayFittingFromString(fitting)


@ThreadDeco
def ShowContract(*args):
    submit_metric('igb_show_contract')
    if len(args) < 1:
        log.LogError('CCPEVE.ShowContract received insufficient arguments. This method requires a SolarSystemID and a ContractID.')
        return
    if len(args) == 1:
        ids = args[0].split('//')
        if len(ids) < 2:
            log.LogError('CCPEVE.ShowContract received old-style insufficient arguments. This method requires a SolarSystemID and a ContractID.')
            return
        contractID = ids[1]
        solarSystemID = ids[0]
    else:
        contractID = args[1]
        solarSystemID = args[0]
    try:
        contractID = int(contractID)
    except:
        log.LogError('CCPEVE.ShowContract failed to convert contractID to an integer:', contractID)
        return

    solarSystemID = browserutil.SanitizedSolarsystemID(solarSystemID)
    if contractID is None or solarSystemID is None:
        log.LogError('CCPEVE.ShowContract received invalid contract or solarsystem IDs; contractID:', contractID, 'solarSystemID:', solarSystemID)
        return
    sm.GetService('contracts').ShowContract(contractID)


@ThreadDeco
def ShowMarketDetails(typeID):
    submit_metric('igb_show_market_details')
    try:
        safeTypeID = browserutil.SanitizedTypeID(int(typeID))
    except:
        safeTypeID = None

    if safeTypeID is None:
        log.LogError('Type ID passed to Client.ShowMarketDetails was invalid:', typeID)
        return
    sm.GetService('marketutils').ShowMarketDetails(safeTypeID, None)


def submit_metric(metric_name):
    uthread.new(metrics.increment, metric_name, tags={'server': utillib.GetServerName()}, secondary_values={'characterID': session.charid})


exports = {'browser.BrowserSession': EveBrowserSession}
