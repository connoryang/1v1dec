#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\neocom\contracts\ignoreListWnd.py
import localization
import uicontrols
import util
from carbonui import const as uiconst
from carbonui.primitives.container import Container
from eve.client.script.ui.control import entries as listentry
from eve.client.script.util.contractutils import GetContractIcon

class IgnoreListWindow(uicontrols.Window):
    __guid__ = 'form.IgnoreListWindow'
    default_windowID = 'contractignorelist'

    def ApplyAttributes(self, attributes):
        uicontrols.Window.ApplyAttributes(self, attributes)
        self.locationInfo = {}
        self.scope = 'all'
        self.SetCaption(localization.GetByLabel('UI/Contracts/ContractsWindow/IgnoreList'))
        self.SetWndIcon(GetContractIcon(const.conTypeNothing), mainTop=-10)
        self.SetMinSize([200, 200], 1)
        self.SetTopparentHeight(0)
        self.MakeUnMinimizable()
        self.ModalPosition()
        Container(name='push', parent=self.sr.main, align=uiconst.TOLEFT, width=const.defaultPadding)
        Container(name='push', parent=self.sr.main, align=uiconst.TORIGHT, width=const.defaultPadding)
        Container(name='push', parent=self.sr.main, align=uiconst.TOBOTTOM, height=const.defaultPadding)
        hp = Container(name='hintparent', parent=self.sr.main, align=uiconst.TOTOP, height=16, state=uiconst.UI_HIDDEN)
        t = uicontrols.EveLabelMedium(text=localization.GetByLabel('UI/Contracts/ContractsWindow/IgnoreHeader'), parent=hp, top=-3, width=self.minsize[0] - 32, state=uiconst.UI_DISABLED, align=uiconst.CENTER)
        hp.state = uiconst.UI_DISABLED
        hp.height = t.height + 8
        sub = Container(name='subparent', parent=self.sr.main, align=uiconst.TOBOTTOM, height=26)
        self.sr.ignoreListParent = ignoreListParent = Container(name='ignoreList', align=uiconst.TOALL, pos=(0, 0, 0, 0), parent=self.sr.main)
        self.sr.ignoreList = ignoreList = uicontrols.Scroll(parent=ignoreListParent)
        ignoreList.sr.id = 'ignoreList'
        captionparent = Container(name='captionparent', parent=self.sr.main, align=uiconst.TOPLEFT, left=128, top=36, idx=0)
        caption = uicontrols.CaptionLabel(text='', parent=captionparent)
        self.closeBtn = uicontrols.ButtonGroup(btns=[[localization.GetByLabel('UI/Generic/Close'),
          self.Close,
          None,
          81]], parent=sub)
        self.PopulateIgnoreList()
        return self

    def PopulateIgnoreList(self):
        headers = []
        scrolllist = []
        list = settings.user.ui.Get('contracts_ignorelist', [])
        for l in list:
            data = util.KeyVal()
            data.charID = l
            label = '%s<t>' % cfg.eveowners.Get(l).name
            data.label = label
            data.charID = l
            data.OnDblClick = self.DblClickEntry
            scrolllist.append(listentry.Get('User', data=data))

        self.sr.ignoreList.Load(contentList=scrolllist, headers=headers)
        if len(scrolllist) > 0:
            self.sr.ignoreList.ShowHint()
        else:
            self.sr.ignoreList.ShowHint(localization.GetByLabel('UI/Contracts/ContractEntry/NoIgnored'))

    def DblClickEntry(self, entry, *args):
        list = settings.user.ui.Get('contracts_ignorelist', [])
        list = [ l for l in list if l != entry.sr.node.charID ]
        settings.user.ui.Set('contracts_ignorelist', list)
        self.PopulateIgnoreList()
        sm.GetService('contracts').ClearCache()
