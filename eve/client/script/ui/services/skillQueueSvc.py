#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\services\skillQueueSvc.py
from contextlib import contextmanager
from carbonui.util.various_unsorted import GetAttrs
from characterskills.queue import SKILLQUEUE_MAX_NUM_SKILLS, GetQueueEntry, GetSkillQueueTimeLength
from characterskills.util import GetSkillLevelRaw, GetLevelProgress
from eveexceptions import UserError
import service
import form
import sys
from textImporting.importSkillplan import ImportSkillPlan
import uix
import carbonui.const as uiconst
import uiutil
import gametime
import localization
import evetypes
from util import KeyVal
from uthread import UnLock, ReentrantLock

class SkillQueueService(service.Service):
    __exportedcalls__ = {'SkillInTraining': []}
    __guid__ = 'svc.skillqueue'
    __servicename__ = 'skillqueue'
    __displayname__ = 'Skill Queue Client Service'
    __dependencies__ = ['godma', 'skills', 'machoNet']
    __notifyevents__ = ['OnSkillQueuePaused', 'OnMultipleCharactersTrainingUpdated', 'OnNewSkillQueueSaved']

    def __init__(self):
        service.Service.__init__(self)
        self.skillQueue = []
        self.cachedSkillQueue = None
        self.skillQueueCache = None
        self.skillplanImporter = None
        self.maxSkillqueueTimeLength = GetSkillQueueTimeLength(session.userType)

    def Run(self, memStream = None):
        self.skillQueue, freeSkillPoints = self.skills.GetSkillHandler().GetSkillQueueAndFreePoints()
        if freeSkillPoints is not None and freeSkillPoints > 0:
            self.skills.SetFreeSkillPoints(freeSkillPoints)

    def BeginTransaction(self):
        with self.ChangeQueueLock():
            sendEvent = False
            skillInTraining = self.SkillInTraining()
            if self.cachedSkillQueue is not None:
                sendEvent = True
                self.LogError('%s: New skill queue transaction being opened - skill queue being overwritten!' % session.charid)
            self.skillQueueCache = None
            self.skillQueue, freeSkillPoints = self.skills.GetSkillHandler().GetSkillQueueAndFreePoints()
            if freeSkillPoints > 0:
                self.skills.SetFreeSkillPoints(freeSkillPoints)
            self.cachedSkillQueue = self.GetQueue()
            if not skillInTraining:
                queueWithTimestamps = []
                for idx, trainingSkill in enumerate(self.skillQueue):
                    startTime = None
                    if idx > 0:
                        startTime = self.skillQueue[idx - 1].trainingEndTime
                    currentSkill = self.skills.GetSkill(trainingSkill.trainingTypeID)
                    queueEntry = GetQueueEntry(trainingSkill.trainingTypeID, trainingSkill.trainingToLevel, idx, currentSkill, queueWithTimestamps, lambda x, y: self.GetTimeForTraining(x, y, startTime), KeyVal, True)
                    queueWithTimestamps.append(queueEntry)

                self.skillQueue = queueWithTimestamps
            if sendEvent:
                sm.ScatterEvent('OnSkillQueueRefreshed')

    def RollbackTransaction(self):
        with self.ChangeQueueLock():
            if self.cachedSkillQueue is None:
                self.LogError('%s: Cannot rollback a skill queue transaction - no transaction was opened!' % session.charid)
                return
            self.skillQueue = self.cachedSkillQueue
            self.skillQueueCache = None
            self.cachedSkillQueue = None

    def CommitTransaction(self, activate = True):
        with self.ChangeQueueLock():
            if self.cachedSkillQueue is None:
                self.LogError('%s: Cannot commit a skill queue transaction - no transaction was opened!' % session.charid)
                return
            self.PrimeCache(force=True)
            if self.IsQueueChanged() or activate:
                try:
                    self.TrimQueue()
                    queueInfo = {idx:(x.trainingTypeID, x.trainingToLevel) for idx, x in enumerate(self.skillQueue)}
                    skillHandler = self.skills.GetSkillHandler()
                    skillHandler.SaveNewQueue(queueInfo, activate=activate)
                    self.cachedSkillQueue = None
                    sm.ScatterEvent('OnSkillQueueRefreshed')
                except Exception as e:
                    msg = getattr(e, 'msg', None)
                    if msg != 'UserAlreadyHasSkillInTraining':
                        self.RollbackTransaction()
                        sm.ScatterEvent('OnSkillQueueRefreshed')
                    raise

    def CheckCanInsertSkillAtPosition(self, skillTypeID, skillLevel, position, check = 0, performLengthTest = True):
        if position is None or position < 0 or position > len(self.skillQueue):
            raise UserError('QueueInvalidPosition')
        self.PrimeCache()
        mySkill = self.skills.GetSkill(skillTypeID)
        ret = True
        try:
            if mySkill is None:
                raise UserError('QueueSkillNotUploaded')
            if mySkill.skillLevel >= skillLevel:
                raise UserError('QueueCannotTrainPreviouslyTrainedSkills')
            if mySkill.skillLevel >= 5:
                raise UserError('QueueCannotTrainPastMaximumLevel', {'typeName': (const.UE_TYPEID, skillTypeID)})
            if skillTypeID in self.skillQueueCache:
                for lvl, lvlPosition in self.skillQueueCache[skillTypeID].iteritems():
                    if lvl < skillLevel and lvlPosition >= position:
                        raise UserError('QueueCannotPlaceSkillLevelsOutOfOrder')
                    elif lvl > skillLevel and lvlPosition < position:
                        raise UserError('QueueCannotPlaceSkillLevelsOutOfOrder')

            if position >= 0 and performLengthTest:
                if self.GetTrainingLengthOfQueue(position) > self.maxSkillqueueTimeLength:
                    raise UserError('QueueTooLong')
            if mySkill.skillPoints == 0:
                requirements = sm.GetService('skills').GetRequiredSkills(skillTypeID)
                for requiredTypeID, requiredLevel in requirements.iteritems():
                    isRequirementsQueued = False
                    if requiredTypeID in self.skillQueueCache:
                        for level, queuedPosition in self.skillQueueCache[requiredTypeID].iteritems():
                            if level <= requiredLevel and queuedPosition > position:
                                raise UserError('QueueCannotPlaceSkillBeforeRequirements')
                            if level == requiredLevel and queuedPosition < position:
                                isRequirementsQueued = True

                    skill = self.skills.GetSkill(requiredTypeID)
                    if skill is None:
                        raise UserError('QueueCannotPlaceSkillBeforeRequirements')
                    isRequirementsTrained = skill.skillLevel >= requiredLevel
                    if not isRequirementsTrained and not isRequirementsQueued:
                        raise UserError('QueueCannotPlaceSkillBeforeRequirements')

            dependencies = sm.GetService('skills').GetDependentSkills(skillTypeID)
            for dependentTypeID, requiredLevel in dependencies.iteritems():
                if dependentTypeID not in self.skillQueueCache:
                    continue
                for level, queuedPosition in self.skillQueueCache[dependentTypeID].iteritems():
                    if requiredLevel == skillLevel and queuedPosition < position:
                        raise UserError('QueueCannotPlaceSkillAfterDependentSkills')

        except UserError as ue:
            checkedErrors = ('QueueCannotPlaceSkillAfterDependentSkills', 'QueueCannotPlaceSkillBeforeRequirements', 'QueueCannotPlaceSkillLevelsOutOfOrder', 'QueueCannotTrainPreviouslyTrainedSkills', 'QueueSkillNotUploaded', 'QueueTooLong')
            if check and ue.msg in checkedErrors:
                sys.exc_clear()
                ret = False
            else:
                raise

        return ret

    def AddSkillToQueue(self, skillTypeID, skillLevel, position = None):
        if self.FindInQueue(skillTypeID, skillLevel) is not None:
            raise UserError('QueueSkillAlreadyPresent')
        skillQueueLength = len(self.skillQueue)
        if skillQueueLength >= SKILLQUEUE_MAX_NUM_SKILLS:
            raise UserError('QueueTooManySkills', {'num': SKILLQUEUE_MAX_NUM_SKILLS})
        newPos = position if position is not None and position >= 0 else skillQueueLength
        currentSkill = self.skills.GetSkill(skillTypeID)
        self.CheckCanInsertSkillAtPosition(skillTypeID, skillLevel, newPos)
        startTime = None
        if newPos != 0:
            startTime = self.skillQueue[newPos - 1].trainingEndTime
        queueEntry = GetQueueEntry(skillTypeID, skillLevel, newPos, currentSkill, self.skillQueue, lambda x, y: self.GetTimeForTraining(x, y, startTime), KeyVal, self.SkillInTraining() is not None)
        if newPos == skillQueueLength:
            self.skillQueue.append(queueEntry)
        else:
            if newPos > skillQueueLength:
                raise UserError('QueueInvalidPosition')
            self.skillQueue.insert(newPos, queueEntry)
            for entry in self.skillQueue[newPos + 1:]:
                entry.queuePosition += 1

            self.skillQueueCache = None
        self.AddToCache(skillTypeID, skillLevel, newPos)
        self.TrimQueue()
        sm.ScatterEvent('OnSkillQueueModified')
        return newPos

    def RemoveSkillFromQueue(self, skillTypeID, skillLevel):
        self.CheckCanRemoveSkillFromQueue(skillTypeID, skillLevel)
        self.InternalRemoveFromQueue(skillTypeID, skillLevel)
        sm.ScatterEvent('OnSkillQueueModified')

    def CheckCanRemoveSkillFromQueue(self, skillTypeID, skillLevel):
        self.PrimeCache()
        if skillTypeID not in self.skillQueueCache:
            return
        for cacheLevel in self.skillQueueCache[skillTypeID]:
            if cacheLevel > skillLevel:
                raise UserError('QueueCannotRemoveSkillsWithHigherLevelsStillInQueue')

        dependencies = sm.GetService('skills').GetDependentSkills(skillTypeID)
        for dependentTypeID, requiredLevel in dependencies.iteritems():
            if skillLevel <= requiredLevel and dependentTypeID in self.skillQueueCache:
                raise UserError('QueueCannotRemoveSkillsWithDependentSkillsInQueue')

    def FindInQueue(self, skillTypeID, skillLevel):
        self.PrimeCache()
        if skillTypeID not in self.skillQueueCache:
            return None
        if skillLevel not in self.skillQueueCache[skillTypeID]:
            return None
        return self.skillQueueCache[skillTypeID][skillLevel]

    def MoveSkillToPosition(self, skillTypeID, skillLevel, position):
        self.CheckCanInsertSkillAtPosition(skillTypeID, skillLevel, position)
        self.PrimeCache()
        currentPosition = self.skillQueueCache[skillTypeID][skillLevel]
        if currentPosition < position:
            position -= 1
        self.InternalRemoveFromQueue(skillTypeID, skillLevel)
        newPosition = self.AddSkillToQueue(skillTypeID, skillLevel, position)
        sm.ScatterEvent('OnSkillQueueModified')
        return newPosition

    def GetQueue(self):
        return self.skillQueue[:]

    def GetServerQueue(self):
        if self.cachedSkillQueue is not None:
            return self.cachedSkillQueue[:]
        else:
            return self.GetQueue()

    def GetNumberOfSkillsInQueue(self):
        return len(self.skillQueue)

    def GetTrainingLengthOfQueue(self, position = None):
        if position is not None and position < 0:
            raise RuntimeError('Invalid queue position: ', position)
        trainingTime = 0
        skillBoosters = self.GetSkillAcceleratorBoosters()
        playerTheoreticalSkillPoints = {}
        skills = self.skills.GetSkills()
        currentIndex = 0
        finalIndex = position
        if finalIndex is None:
            finalIndex = len(self.skillQueue)
        for trainingSkill in self.skillQueue:
            queueSkillTypeID = trainingSkill.trainingTypeID
            queueSkillLevel = trainingSkill.trainingToLevel
            if currentIndex >= finalIndex:
                break
            currentIndex += 1
            if queueSkillTypeID not in playerTheoreticalSkillPoints:
                skill = self.skills.GetSkill(queueSkillTypeID)
                playerTheoreticalSkillPoints[queueSkillTypeID] = self.GetSkillPointsFromSkillObject(queueSkillTypeID, skill)
            addedSP, addedTime, isAccelerated = self.GetAddedSpAndAddedTimeForSkill(queueSkillTypeID, queueSkillLevel, skills, playerTheoreticalSkillPoints, trainingTime, skillBoosters)
            trainingTime += addedTime
            playerTheoreticalSkillPoints[queueSkillTypeID] += addedSP

        return trainingTime

    def GetTrainingEndTimeOfQueue(self):
        return gametime.GetWallclockTime() + self.GetTrainingLengthOfQueue()

    def GetTrainingLengthOfSkill(self, skillTypeID, skillLevel, position = None):
        if position is not None and (position < 0 or position > len(self.skillQueue)):
            raise RuntimeError('GetTrainingLengthOfSkill received an invalid position.')
        trainingTime = 0
        currentIndex = 0
        targetIndex = position
        if targetIndex is None:
            targetIndex = self.FindInQueue(skillTypeID, skillLevel)
            if targetIndex is None:
                targetIndex = len(self.skillQueue)
        playerTheoreticalSkillPoints = {}
        skills = self.skills.GetSkills()
        skillBoosters = self.GetSkillAcceleratorBoosters()
        for trainingSkill in self.skillQueue:
            queueSkillTypeID = trainingSkill.trainingTypeID
            queueSkillLevel = trainingSkill.trainingToLevel
            if currentIndex >= targetIndex:
                break
            elif queueSkillTypeID == skillTypeID and queueSkillLevel == skillLevel and currentIndex < targetIndex:
                currentIndex += 1
                continue
            addedSP, addedTime, _ = self.GetAddedSpAndAddedTimeForSkill(queueSkillTypeID, queueSkillLevel, skills, playerTheoreticalSkillPoints, trainingTime, skillBoosters)
            currentIndex += 1
            trainingTime += addedTime
            playerTheoreticalSkillPoints[queueSkillTypeID] += addedSP

        addedSP, addedTime, isAccelerated = self.GetAddedSpAndAddedTimeForSkill(skillTypeID, skillLevel, skills, playerTheoreticalSkillPoints, trainingTime, skillBoosters)
        trainingTime += addedTime
        return (long(trainingTime), long(addedTime), isAccelerated)

    def GetSkillPointsAndTimeNeededToTrain(self, skillTypeID, skillLevel, existingSkillPoints = 0, trainingStartTime = None):
        calculator = self.skills.GetSkillTrainingTimeCalculator()
        if existingSkillPoints:
            skillPointsToTrain, trainingTime = calculator.get_skill_points_and_time_to_train_given_existing_skill_points(skillTypeID, skillLevel, trainingStartTime, existingSkillPoints)
        else:
            skillPointsToTrain, trainingTime = calculator.get_skill_points_and_time_to_train(skillTypeID, skillLevel, trainingStartTime)
        return (skillPointsToTrain, float(trainingTime))

    def TrimQueue(self):
        trainingTime = 0
        skillBoosters = self.GetSkillAcceleratorBoosters()
        playerTheoreticalSkillPoints = {}
        skills = self.skills.GetSkills()
        cutoffIndex = 0
        for trainingSkill in self.skillQueue:
            queueSkillTypeID = trainingSkill.trainingTypeID
            queueSkillLevel = trainingSkill.trainingToLevel
            cutoffIndex += 1
            addedSP, addedTime, isAccelerated = self.GetAddedSpAndAddedTimeForSkill(queueSkillTypeID, queueSkillLevel, skills, playerTheoreticalSkillPoints, trainingTime, skillBoosters)
            trainingTime += addedTime
            playerTheoreticalSkillPoints[queueSkillTypeID] += addedSP
            if trainingTime > self.maxSkillqueueTimeLength:
                break

        if cutoffIndex < len(self.skillQueue):
            removedSkills = self.skillQueue[cutoffIndex:]
            self.skillQueue = self.skillQueue[:cutoffIndex]
            self.skillQueueCache = None
            eve.Message('skillQueueTrimmed', {'num': len(removedSkills)})

    def GetSkillAcceleratorBoosters(self):
        return self.skills.GetSkillAcceleratorBoosters()

    def GetAddedSpAndAddedTimeForSkill(self, skillTypeID, skillLevel, skillSet, theoreticalSkillPointsDict, trainingTimeOffset, skillBoosters):
        skillStartTime = long(trainingTimeOffset) + gametime.GetWallclockTime()
        isAccelerated = skillBoosters.is_any_booster_active_at_time(skillStartTime)
        if skillTypeID not in theoreticalSkillPointsDict:
            skillObj = skillSet.get(skillTypeID, None)
            theoreticalSkillPointsDict[skillTypeID] = self.GetSkillPointsFromSkillObject(skillTypeID, skillObj)
        addedSP, addedTime = self.GetSkillPointsAndTimeNeededToTrain(skillTypeID, skillLevel, theoreticalSkillPointsDict[skillTypeID], skillStartTime)
        return (addedSP, addedTime, isAccelerated)

    def GetAllTrainingLengths(self):
        trainingTime = 0
        skillBoosters = self.GetSkillAcceleratorBoosters()
        resultsDict = {}
        playerTheoreticalSkillPoints = {}
        skills = self.skills.GetSkills()
        for trainingSkill in self.skillQueue:
            queueSkillTypeID = trainingSkill.trainingTypeID
            queueSkillLevel = trainingSkill.trainingToLevel
            addedSP, addedTime, isAccelerated = self.GetAddedSpAndAddedTimeForSkill(queueSkillTypeID, queueSkillLevel, skills, playerTheoreticalSkillPoints, trainingTime, skillBoosters)
            trainingTime += addedTime
            playerTheoreticalSkillPoints[queueSkillTypeID] += addedSP
            resultsDict[queueSkillTypeID, queueSkillLevel] = (trainingTime, addedTime, isAccelerated)

        return resultsDict

    def ApplyFreeSkillPointsToQueue(self):
        handler = sm.GetService('skills').GetSkillHandler()
        pointsBySkillTypeID = handler.GetFreeSkillPointsAppliedToQueue()
        if not pointsBySkillTypeID:
            return
        levelAndProgressBySkillTypeID = self._GetSkillLevelAndProgressWithFreePoints(pointsBySkillTypeID)
        skillEntries = []
        for typeID, (level, progress) in levelAndProgressBySkillTypeID.iteritems():
            label = evetypes.GetName(typeID) + ' '
            if progress > 0.0:
                extra = '{}%'.format(int(progress * 100))
                label += localization.GetByLabel('UI/SkillQueue/Skills/SkillLevelWordAndValueWithExtra', skillLevel=level, extra=extra)
            else:
                label += localization.GetByLabel('UI/SkillQueue/Skills/SkillLevelWordAndValue', skillLevel=level)
            skillEntries.append(label)

        totalFreePointsApplied = sum(pointsBySkillTypeID.values())
        key = 'ConfirmApplyFreeSkillPointsToQueue'
        parameters = {'skills': '<br>'.join(sorted(skillEntries, key=lambda x: x.lower())),
         'totalPoints': totalFreePointsApplied}
        if eve.Message(key, parameters, uiconst.YESNO) == uiconst.ID_YES:
            handler.ApplyFreeSkillPointsToQueue()

    def _GetSkillLevelAndProgressWithFreePoints(self, pointsBySkillTypeID):
        skillSvc = sm.GetService('skills')
        levelBySkillTypeID = {}
        for typeID, points in pointsBySkillTypeID.iteritems():
            currentPoints = skillSvc.MySkillPoints(typeID)
            totalPoints = currentPoints + points
            rank = skillSvc.GetSkillRank(typeID)
            level = GetSkillLevelRaw(totalPoints, rank)
            progress = GetLevelProgress(totalPoints, rank)
            levelBySkillTypeID[typeID] = (level, progress)

        return levelBySkillTypeID

    def InternalRemoveFromQueue(self, skillTypeID, skillLevel):
        if not len(self.skillQueue):
            return
        skillPosition = self.FindInQueue(skillTypeID, skillLevel)
        if skillPosition is None:
            raise UserError('QueueSkillNotPresent')
        if skillPosition == len(self.skillQueue):
            del self.skillQueueCache[skillTypeID][skillLevel]
            self.skillQueue.pop()
        else:
            self.skillQueueCache = None
            self.skillQueue.pop(skillPosition)

    def ClearCache(self):
        self.skillQueueCache = None

    def AddToCache(self, skillTypeID, skillLevel, position):
        self.PrimeCache()
        if skillTypeID not in self.skillQueueCache:
            self.skillQueueCache[skillTypeID] = {}
        self.skillQueueCache[skillTypeID][skillLevel] = position

    def GetPlayerAttributeDict(self):
        return self.skills.GetCharacterAttributes()

    def PrimeCache(self, force = False):
        if force:
            self.skillQueueCache = None
        if self.skillQueueCache is None:
            i = 0
            self.skillQueueCache = {}
            for trainingSkill in self.skillQueue:
                self.AddToCache(trainingSkill.trainingTypeID, trainingSkill.trainingToLevel, i)
                i += 1

    def GetSkillPointsFromSkillObject(self, skillTypeID, skillInfo):
        if skillInfo is None:
            return 0
        totalSkillPoints = skillInfo.skillPoints
        trainingSkill = self.SkillInTraining(skillTypeID)
        serverQueue = self.GetServerQueue()
        if trainingSkill and len(serverQueue):
            skillPointsTrained = self.GetEstimatedSkillPointsTrained(skillTypeID)
            totalSkillPoints = max(skillPointsTrained, totalSkillPoints)
        return totalSkillPoints

    def GetEstimatedSkillPointsTrained(self, skillTypeID):
        startTime = self.GetStartTimeOfQueue()
        currentTime = gametime.GetWallclockTime()
        if startTime is None:
            startTime = currentTime
        trainingCalculator = self.skills.GetSkillTrainingTimeCalculator()
        with trainingCalculator.specific_current_time_context(startTime):
            skillPointsTrained = trainingCalculator.get_skill_points_trained_at_sample_time(skillTypeID, startTime, currentTime)
        return skillPointsTrained

    def OnServerSkillsChanged(self, skillInfos):
        self.PrimeCache()
        for skillTypeID, skillInfo in skillInfos.iteritems():
            skill = self.skills.GetSkill(skillTypeID)
            if not skill and skillInfo.skillLevel > 0:
                self.LogError('skillQueueSvc::OnServerSkillsChanged skill %s not found' % skillTypeID)
                continue
            self._RemoveSkillFromQueueCacheIfTrained(skillInfo, skillTypeID)
            self._RemoveSkillFromCachedQueueIfTrained(skillInfos, skillTypeID)

    def _RemoveSkillFromQueueCacheIfTrained(self, skillInfo, skillTypeID):
        skillLevel = skillInfo.skillLevel
        if self.skillQueueCache and skillTypeID in self.skillQueueCache:
            if skillLevel in self.skillQueueCache[skillTypeID]:
                self.InternalRemoveFromQueue(skillTypeID, skillLevel)

    def _RemoveSkillFromCachedQueueIfTrained(self, skillInfos, skillTypeID):
        if self.cachedSkillQueue:
            keepSkills = []
            for trainingSkill in self.cachedSkillQueue:
                if trainingSkill.trainingTypeID == skillTypeID:
                    finishedSkill = skillInfos[skillTypeID]
                    if trainingSkill.trainingToLevel <= finishedSkill.skillLevel:
                        continue
                keepSkills.append(trainingSkill)

            self.cachedSkillQueue = keepSkills

    def OnSkillQueuePaused(self, *args):
        queue = self.skillQueue
        if self.cachedSkillQueue is not None:
            queue = self.cachedSkillQueue
        if queue:
            for skillEntry in queue:
                skillEntry.trainingStartTime = skillEntry.trainingEndTime = None

        sm.ScatterEvent('OnSkillQueueChanged')

    def OnNewSkillQueueSaved(self, newQueue):
        if self.cachedSkillQueue is not None:
            self.cachedSkillQueue = newQueue
        self.skillQueue = newQueue
        sm.ScatterEvent('OnSkillQueueChanged')

    def TrainSkillNow(self, skillTypeID, toSkillLevel, *args):
        inTraining = self.SkillInTraining()
        if inTraining and eve.Message('ConfirmSkillTrainingNow', {'name': evetypes.GetName(inTraining.typeID),
         'lvl': inTraining.skillLevel + 1}, uiconst.OKCANCEL) != uiconst.ID_OK:
            return
        self.BeginTransaction()
        try:
            if self.FindInQueue(skillTypeID, toSkillLevel) is not None:
                self.MoveSkillToPosition(skillTypeID, toSkillLevel, 0)
                message = ('SkillQueueStarted',)
            else:
                self.AddSkillToQueue(skillTypeID, toSkillLevel, 0)
                skillName = localization.GetByLabel('UI/SkillQueue/Skills/SkillNameAndLevel', skill=skillTypeID, amount=toSkillLevel)
                if inTraining:
                    message = ('AddedToQueue', {'skillname': skillName})
                else:
                    message = ('AddedToQueueAndStarted', {'skillname': skillName})
            self.CommitTransaction()
            eve.Message(*message)
        except Exception:
            self.RollbackTransaction()
            raise

    def AddSkillToEnd(self, skillTypeID, current, nextLevel = None):
        queueLength = self.GetNumberOfSkillsInQueue()
        if queueLength >= SKILLQUEUE_MAX_NUM_SKILLS:
            raise UserError('QueueTooManySkills', {'num': SKILLQUEUE_MAX_NUM_SKILLS})
        totalTime = self.GetTrainingLengthOfQueue()
        if totalTime > self.maxSkillqueueTimeLength:
            raise UserError('QueueTooLong')
        if nextLevel is None:
            queue = self.GetServerQueue()
            nextLevel = self.FindNextLevel(skillTypeID, current, queue)
        if self.FindInQueue(skillTypeID, nextLevel) is not None:
            raise UserError('QueueSkillAlreadyPresent')
        self.BeginTransaction()
        try:
            self.AddSkillToQueue(skillTypeID, nextLevel)
            self.CommitTransaction()
        except Exception:
            self.RollbackTransaction()
            raise

        text = localization.GetByLabel('UI/SkillQueue/Skills/SkillNameAndLevel', skill=skillTypeID, amount=nextLevel)
        if self.SkillInTraining():
            eve.Message('AddedToQueue', {'skillname': text})
        else:
            eve.Message('AddedToQueueAndStarted', {'skillname': text})
        sm.ScatterEvent('OnSkillQueueRefreshed')

    def FindNextLevel(self, skillTypeID, current, skillQueue = None):
        if skillQueue is None:
            skillQueue = self.GetServerQueue()
        skillQueue = [ (skill.trainingTypeID, skill.trainingToLevel) for skill in skillQueue ]
        nextLevel = None
        for i in xrange(1, 7):
            if i <= current:
                continue
            inQueue = bool((skillTypeID, i) in skillQueue)
            if inQueue is False:
                nextLevel = i
                break

        return nextLevel

    def OnMultipleCharactersTrainingUpdated(self):
        sm.GetService('objectCaching').InvalidateCachedMethodCall('userSvc', 'GetMultiCharactersTrainingSlots')
        self.PrimeCache(True)
        sm.ScatterEvent('OnMultipleCharactersTrainingRefreshed')

    def GetMultipleCharacterTraining(self, force = False):
        if force:
            sm.GetService('objectCaching').InvalidateCachedMethodCall('userSvc', 'GetMultiCharactersTrainingSlots')
        return sm.RemoteSvc('userSvc').GetMultiCharactersTrainingSlots()

    def IsQueueWndOpen(self):
        return form.SkillQueue.IsOpen()

    def GetAddMenuForSkillEntries(self, skillTypeID, skillInfo):
        m = []
        if skillInfo is None:
            return m
        skillLevel = skillInfo.skillLevel
        if skillLevel is not None:
            sqWnd = form.SkillQueue.GetIfOpen()
            if skillLevel < 5:
                queue = self.GetQueue()
                nextLevel = self.FindNextLevel(skillTypeID, skillInfo.skillLevel, queue)
                if not self.SkillInTraining(skillTypeID):
                    trainingTime, totalTime, _ = self.GetTrainingLengthOfSkill(skillTypeID, skillInfo.skillLevel + 1, 0)
                    if trainingTime <= 0:
                        takesText = localization.GetByLabel('UI/SkillQueue/Skills/CompletionImminent')
                    else:
                        takesText = localization.GetByLabel('UI/SkillQueue/Skills/SkillTimeLeft', timeLeft=long(trainingTime))
                    if sqWnd:
                        if nextLevel < 6 and self.FindInQueue(skillTypeID, skillInfo.skillLevel + 1) is None:
                            trainText = uiutil.MenuLabel('UI/SkillQueue/AddSkillMenu/AddToFrontOfQueueTime', {'takes': takesText})
                            m.append((trainText, sqWnd.AddSkillsThroughOtherEntry, (skillTypeID,
                              0,
                              queue,
                              nextLevel,
                              1)))
                    else:
                        trainText = uiutil.MenuLabel('UI/SkillQueue/AddSkillMenu/TrainNowWithTime', {'skillLevel': skillInfo.skillLevel + 1,
                         'takes': takesText})
                        m.append((trainText, self.TrainSkillNow, (skillTypeID, skillInfo.skillLevel + 1)))
                if nextLevel < 6:
                    if sqWnd:
                        label = uiutil.MenuLabel('UI/SkillQueue/AddSkillMenu/AddToEndOfQueue', {'nextLevel': nextLevel})
                        m.append((label, sqWnd.AddSkillsThroughOtherEntry, (skillInfo.typeID,
                          -1,
                          queue,
                          nextLevel,
                          1)))
                    else:
                        label = uiutil.MenuLabel('UI/SkillQueue/AddSkillMenu/TrainAfterQueue', {'nextLevel': nextLevel})
                        m.append((label, self.AddSkillToEnd, (skillInfo.typeID, skillInfo.skillLevel, nextLevel)))
                if sm.GetService('skills').GetFreeSkillPoints() > 0:
                    diff = sm.GetService('skills').SkillpointsNextLevel(skillTypeID) + 0.5 - skillInfo.skillPoints
                    m.append((uiutil.MenuLabel('UI/SkillQueue/AddSkillMenu/ApplySkillPoints'), self.UseFreeSkillPoints, (skillInfo.typeID, diff)))
            if self.SkillInTraining(skillTypeID):
                m.append((uiutil.MenuLabel('UI/SkillQueue/AddSkillMenu/AbortTraining'), sm.StartService('skills').AbortTrain))
        if m:
            m.append(None)
        return m

    def UseFreeSkillPoints(self, skillTypeID, diff):
        inTraining = self.SkillInTraining()
        if inTraining is not None and inTraining.typeID == skillTypeID:
            eve.Message('CannotApplyFreePointsWhileTrainingSkill')
            return
        freeSkillPoints = sm.StartService('skills').GetFreeSkillPoints()
        text = localization.GetByLabel('UI/SkillQueue/AddSkillMenu/UseSkillPointsWindow', skill=skillTypeID, skillPoints=int(diff))
        caption = localization.GetByLabel('UI/SkillQueue/AddSkillMenu/ApplySkillPoints')
        ret = uix.QtyPopup(maxvalue=freeSkillPoints, caption=caption, label=text)
        if ret is None:
            return
        sp = int(ret.get('qty', ''))
        sm.StartService('skills').ApplyFreeSkillPoints(skillTypeID, sp)
        sm.GetService('audio').SendUIEvent('st_allocate_skillpoints_play')

    def SkillInTraining(self, skillTypeID = None):
        activeQueue = self.GetServerQueue()
        if len(activeQueue) and activeQueue[0].trainingEndTime:
            if skillTypeID is None or activeQueue[0].trainingTypeID == skillTypeID:
                return self.skills.GetSkill(activeQueue[0].trainingTypeID)

    def GetTimeForTraining(self, skillTypeID, toLevel, trainingStartTime = 0):
        currentTraining = self.SkillInTraining(skillTypeID)
        currentSkillPointsDict = {}
        currentTime = gametime.GetWallclockTime()
        if currentTraining:
            trainingEndTime = self.GetEndOfTraining(skillTypeID)
            timeForTraining = trainingEndTime - currentTime
        else:
            timeOffset = 0
            if trainingStartTime:
                timeOffset = trainingStartTime - currentTime
            skill = self.skills.GetSkill(skillTypeID)
            attributes = self.GetPlayerAttributeDict()
            skillBoosters = self.GetSkillAcceleratorBoosters()
            skillBoosters.apply_expired_attributes_at_time_offset(attributes, timeOffset)
            currentSkillPointsDict[skillTypeID] = self.GetSkillPointsFromSkillObject(skillTypeID, skill)
            _, timeForTraining = self.GetSkillPointsAndTimeNeededToTrain(skillTypeID, toLevel, currentSkillPointsDict[skillTypeID], trainingStartTime or currentTime)
        return long(timeForTraining)

    def GetEndOfTraining(self, skillTypeID):
        skillQueue = self.GetServerQueue()
        if not len(skillQueue) or skillQueue[0].trainingTypeID != skillTypeID:
            return None
        else:
            return skillQueue[0].trainingEndTime

    def GetStartTimeOfQueue(self):
        skillQueue = self.GetServerQueue()
        if not skillQueue:
            return None
        else:
            return skillQueue[0].trainingStartTime

    def IsMoveAllowed(self, draggedNode, checkedIdx):
        queue = self.GetQueue()
        if checkedIdx is None:
            checkedIdx = len(queue)
        if draggedNode.skillID:
            if draggedNode.panel and draggedNode.panel.__guid__ == 'listentry.SkillEntry':
                level = self.FindNextLevel(draggedNode.skillID, draggedNode.skill.skillLevel, queue)
            else:
                level = draggedNode.Get('trainToLevel', 1)
                if draggedNode.inQueue is None:
                    level += 1
            return self.CheckCanInsertSkillAtPosition(draggedNode.skillID, level, checkedIdx, check=1, performLengthTest=False)
        if draggedNode.__guid__ in ('xtriui.InvItem', 'listentry.InvItem'):
            category = GetAttrs(draggedNode, 'rec', 'categoryID')
            if category != const.categorySkill:
                return
            typeID = GetAttrs(draggedNode, 'rec', 'typeID')
            if typeID is None:
                return
            skill = sm.StartService('skills').GetSkill(typeID)
            if skill:
                return False
            meetsReq = sm.StartService('godma').CheckSkillRequirementsForType(typeID)
            if not meetsReq:
                return False
            return True
        if draggedNode.__guid__ == 'listentry.SkillTreeEntry':
            typeID = draggedNode.typeID
            if typeID is None:
                return
            mySkills = sm.StartService('skills').GetMyGodmaItem().skills
            skill = mySkills.get(typeID, None)
            if skill is None:
                return
            skill = sm.StartService('skills').GetSkill(typeID)
            level = self.FindNextLevel(typeID, skill.skillLevel, queue)
            return self.CheckCanInsertSkillAtPosition(typeID, level, checkedIdx, check=1, performLengthTest=False)

    def IsRemoveAllowed(self, typeID, level):
        try:
            self.CheckCanRemoveSkillFromQueue(typeID, level)
            return True
        except UserError:
            return False

    def GetSkillPlanImporter(self):
        if self.skillplanImporter is None:
            self.skillplanImporter = ImportSkillPlan()
        return self.skillplanImporter

    @contextmanager
    def ChangeQueueLock(self):
        ReentrantLock(self, 'SkillQueueSvc:xActLock')
        try:
            yield
        finally:
            UnLock(self, 'SkillQueueSvc:xActLock')

    def IsQueueChanged(self):
        if self.cachedSkillQueue is None:
            return False
        if len(self.skillQueue) != len(self.cachedSkillQueue):
            return True
        for s1, s2 in zip(self.skillQueue, self.cachedSkillQueue):
            isSameType = s1.trainingTypeID == s2.trainingTypeID
            isSameLevel = s1.trainingToLevel == s2.trainingToLevel
            if not isSameType or not isSameLevel:
                return True

        return False
