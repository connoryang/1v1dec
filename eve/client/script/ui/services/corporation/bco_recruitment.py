#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\services\corporation\bco_recruitment.py
import corpObject
import uthread
import blue
from eve.common.script.sys.rowset import Rowset

class CorporationRecruitmentO(corpObject.base):
    __guid__ = 'corpObject.recruitment'

    def __init__(self, boundObject):
        corpObject.base.__init__(self, boundObject)
        self.__lock = uthread.Semaphore()
        self.corpRecruitment = None
        self.myRecruitment = None

    def DoSessionChanging(self, isRemote, session, change):
        if 'charid' in change:
            self.myRecruitment = None
        if 'corpid' in change:
            self.corpRecruitment = None

    def OnSessionChanged(self, isRemote, session, change):
        if 'corpid' not in change:
            return
        oldID, newID = change['corpid']
        if newID is None:
            return

    def OnCorporationRecruitmentAdChanged(self):
        self.corpRecruitment = None
        sm.GetService('corpui').OnCorporationRecruitmentAdChanged()

    def __len__(self):
        return len(self.GetRecruitmentAdsForCorporation())

    def GetRecruitmentAdsForCorporation(self):
        if self.corpRecruitment is None:
            self.corpRecruitment = {}
            recruitments = sm.ProxySvc('corpRecProxy').GetRecruitmentAdsForCorporation()
            for recruitment in recruitments:
                key = (recruitment.corporationID, recruitment.adID)
                self.corpRecruitment[key] = recruitment

        res = []
        for recruitment in self.corpRecruitment.itervalues():
            if res == []:
                if type(recruitment) == blue.DBRow:
                    res = Rowset(recruitment.__columns__)
                else:
                    res = Rowset(recruitment.header)
            res.lines.append(recruitment)

        return res
