#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\neocom\Alliances\all_ui_rankings.py
import blue
import uiprimitives
import uicontrols
import util
from eve.client.script.ui.control import entries as listentry
import carbonui.const as uiconst
import log
import localization

class FormAlliancesRankings(uiprimitives.Container):
    __guid__ = 'form.AlliancesRankings'
    __nonpersistvars__ = []

    def CreateWindow(self):
        self.toolbarContainer = uiprimitives.Container(name='toolbarContainer', align=uiconst.TOBOTTOM, parent=self)
        buttonLabel = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Rankings/ShowAll')
        buttonOptions = [[buttonLabel,
          self.ShowRankings,
          (0,),
          81]]
        btns = uicontrols.ButtonGroup(btns=buttonOptions, parent=self.toolbarContainer)
        self.toolbarContainer.height = btns.height
        self.sr.mainBtns = btns
        self.sr.scroll = uicontrols.Scroll(parent=self, padding=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding))
        self.ShowRankings()

    def SetHint(self, hintstr = None):
        if self.sr.scroll:
            self.sr.scroll.ShowHint(hintstr)

    def ShowRankings(self, maxLen = 100):
        log.LogInfo('ShowRankings', maxLen)
        alliancesLabel = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Alliances')
        cachedLabel = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Rankings/RankingsCached15')
        sm.GetService('corpui').LoadTop('res:/ui/Texture/WindowIcons/alliances.png', alliancesLabel, cachedLabel)
        if maxLen == 0 and eve.Message('ConfirmShowAllRankedAlliances', {}, uiconst.YESNO, suppress=uiconst.ID_YES) != uiconst.ID_YES:
            return
        try:
            sm.GetService('corpui').ShowLoad()
            headers = [localization.GetByLabel('UI/Common/Name'),
             localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Rankings/ExecutorCorp'),
             localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Rankings/ShortName'),
             localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Rankings/Created'),
             localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Members'),
             localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Rankings/AllianceStanding')]
            scrolllist = []
            hint = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Rankings/NoRankingsFound')
            if self is None or self.destroyed:
                log.LogInfo('ShowRankings Destroyed or None')
            else:
                data = sm.GetService('alliance').GetRankedAlliances(maxLen)
                rows = data.alliances
                owners = []
                for row in rows:
                    if row.executorCorpID not in owners:
                        owners.append(row.executorCorpID)

                if len(owners):
                    cfg.eveowners.Prime(owners)
                for row in rows:
                    standing = data.standings.get(row.allianceID, 0)
                    self.__AddToList(row, standing, scrolllist)

            self.sr.scroll.adjustableColumns = 1
            self.sr.scroll.sr.id = 'alliances_rankings'
            noFoundLabel = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Rankings/NoRankingsFound')
            self.sr.scroll.Load(contentList=scrolllist, headers=headers, noContentHint=noFoundLabel)
        finally:
            sm.GetService('corpui').HideLoad()

    def __GetLabel(self, row, standing):
        executor = None
        if row.executorCorpID is not None:
            executor = cfg.eveowners.GetIfExists(row.executorCorpID)
        if executor is not None:
            executorCorpName = executor.ownerName
        else:
            executorCorpName = ''
        if standing is None:
            standing = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Rankings/NotSet')
        label = '%s<t>%s<t>%s<t>%s<t>%s<t>%s' % (row.allianceName,
         executorCorpName,
         row.shortName,
         util.FmtDate(row.startDate, 'ls'),
         row.memberCount,
         standing)
        return label

    def __AddToList(self, ranking, standing, scrolllist):
        data = util.KeyVal()
        data.label = self.__GetLabel(ranking, standing)
        data.ranking = ranking
        data.GetMenu = self.GetRankingMenu
        scrolllist.append(listentry.Get('Generic', data=data))

    def GetRankingMenu(self, entry):
        allianceID = entry.sr.node.ranking.allianceID
        res = sm.GetService('menu').GetMenuFormItemIDTypeID(allianceID, const.typeAlliance)
        if eve.session.allianceid is None:
            joinLabel = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Rankings/ApplyToJoin')
            res.append([joinLabel, [[joinLabel, self.ApplyToJoin, [allianceID]]]])
        return res

    def ApplyToJoin(self, allianceID):
        wars = sm.GetService('war').GetWars(session.corpid)
        yesterday = blue.os.GetWallclockTime() - (const.DAY + const.HOUR)
        for war in wars.itervalues():
            if war.timeFinished is not None and yesterday > war.timeFinished:
                continue
            if war.declaredByID == session.corpid:
                eve.Message('CanNotJoinAllianceWhileAgressor')
                return

        sm.GetService('corpui').ApplyToJoinAlliance(allianceID)

    def DeclareWarAgainst(self, allianceID):
        sm.GetService('alliance').DeclareWarAgainst(allianceID)
