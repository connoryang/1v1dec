#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\services\jumpQueue.py
import uthread
import blue
import localization
import util
import log
import sys
import service
import const

class JumpQueue(service.Service):
    __guid__ = 'svc.jumpQueue'
    __exportedcalls__ = {'IsJumpQueued': [service.ROLE_SERVICE]}
    __dependencies__ = ['machoNet']
    __notifyevents__ = ['OnJumpQueueUpdate', 'DoSessionChanging']

    def Run(self, ms):
        service.Service.Run(self, ms)
        self.jumpQueue = None
        self.queueCharID = None
        uthread.worker('jumpQueue::Timer', self.__Timer)

    def PrepareQueueForCharID(self, charID):
        self.jumpQueue = None
        self.queueCharID = charID

    def GetPreparedQueueCharID(self):
        return self.queueCharID

    def DoSessionChanging(self, isRemote, session, change):
        if 'solarsystemid2' in change:
            self.LogInfo('Jump Queue:  DoSessionChanging is cleaning jump queue info')
            self.jumpQueue = None

    def __Timer(self):
        while self.state == service.SERVICE_RUNNING:
            if self.jumpQueue is None:
                blue.pyos.synchro.SleepWallclock(500)
            else:
                try:
                    if self.jumpQueue is not None and eve.session.IsItSafe() and (eve.session.solarsystemid2 is None or eve.session.nextSessionChange is None or blue.os.GetSimTime() > eve.session.nextSessionChange):
                        if eve.session.solarsystemid2 and eve.session.solarsystemid2 == self.jumpQueue.solarsystemID:
                            self.jumpQueue = None
                        elif self.queueCharID in self.jumpQueue.jumpKeys:
                            expires = self.jumpQueue.jumpKeys[self.queueCharID] + const.SEC * self.jumpQueue.keyLife
                            if blue.os.GetWallclockTime() > expires:
                                sm.ScatterEvent('OnJumpQueueMessage', localization.GetByLabel('UI/JumpQueue/KeyExpired', system=self.jumpQueue.solarsystemID), False)
                                self.jumpQueue = None
                            else:
                                sm.ScatterEvent('OnJumpQueueMessage', localization.GetByLabel('UI/JumpQueue/KeyIssued', system=self.jumpQueue.solarsystemID, expiration=expires - blue.os.GetWallclockTime()), True)
                        else:
                            try:
                                idx = 1 + self.jumpQueue.queue.index(self.queueCharID)
                                position = max(1, idx - self.jumpQueue.space)
                                sm.ScatterEvent('OnJumpQueueMessage', localization.GetByLabel('UI/JumpQueue/Waiting', system=self.jumpQueue.solarsystemID, pos=position), False)
                            except ValueError:
                                sys.exc_clear()

                except:
                    log.LogException()
                    sys.exc_clear()

                blue.pyos.synchro.SleepWallclock(4500)

    def IsJumpQueued(self):
        if self.jumpQueue is None:
            return False
        if self.queueCharID in self.jumpQueue.jumpKeys:
            if blue.os.GetWallclockTime() - self.jumpQueue.jumpKeys[self.queueCharID] < const.SEC * self.jumpQueue.keyLife:
                self.jumpQueue = None
            else:
                return False
        self.LogInfo('Jump Queued, queue=', self.jumpQueue)
        return True

    def OnJumpQueueUpdate(self, solarsystemID, space, queue, jumpKeys, keyLife):
        if self.jumpQueue is None:
            self.LogInfo('Jump Queue:  Entering Queue for ', solarsystemID, ', space=', space, ', queue=', queue)
            self.jumpQueue = util.KeyVal(solarsystemID=solarsystemID, space=space, queue=queue, jumpKeys=jumpKeys, keyLife=keyLife)
        elif self.queueCharID in queue:
            self.LogInfo('Jump Queue:  Queue update for ', solarsystemID, ', space=', space, ', queue=', queue, ', keys=', jumpKeys)
            self.jumpQueue.space = space
            self.jumpQueue.queue = queue
            self.jumpQueue.jumpKeys = jumpKeys
            self.jumpQueue.keyLife = keyLife
        else:
            self.LogInfo('Jump Queue:  ', self.queueCharID, ' is leaving queue for ', solarsystemID)
            self.jumpQueue = None
