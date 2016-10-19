#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\evegraphics\explosions\spaceObjectExplosionManager.py
import blue
import evetypes
import trinity
import geo2
import uthread
import random
import logging
from carbon.common.lib.const import MSEC
from evegraphics.fsd.explosionBuckets import GetRandomExplosion, GetExplosionBucketByTypeID, GetExplosionBucketIDByTypeID
from evegraphics.fsd import graphicIDs
from tacticalNavigation.ballparkFunctions import AddClientBall, RemoveClientBall
log = logging.getLogger(__name__)
RANDOM_LOCATOR_SORTING = 'random'
FROM_CENTER_SORTING = 'fromCenter'
FROM_LOCATOR_SORTING = 'fromLocator'

class SpaceObjectExplosionManager(object):
    USE_EXPLOSION_BUCKETS = False
    BALLPARK_MODE = True
    explosionLinkMap = {}
    explosionLinkWaiters = {}
    __preferredExplosions = {}

    @staticmethod
    def SetUpChildExplosion(explosionModel, spaceObjectModel = None, explosionSorting = 'random', initialLocatorIdx = -1):
        explosionChildren = explosionModel.Find('trinity.EveChildExplosion', 2)
        if spaceObjectModel is not None:
            explosionLocatorSets = None
            if hasattr(spaceObjectModel, 'locatorSets'):
                explosionLocatorSets = spaceObjectModel.locatorSets.FindByName('explosions')
            explosionLocators = explosionLocatorSets.locators if explosionLocatorSets else spaceObjectModel.damageLocators
            locators = [ (each[0], each[1]) for each in explosionLocators ]
            transforms = []
            if explosionSorting == FROM_CENTER_SORTING:
                point = spaceObjectModel.GetBoundingSphereCenter()
                radius = spaceObjectModel.GetBoundingSphereRadius() * 0.2
                locators.sort(key=lambda explosion: geo2.Vec3Distance(point, explosion[0]) + (random.random() - random.random()) * radius)
            elif explosionSorting == FROM_LOCATOR_SORTING:
                if initialLocatorIdx < 0 or initialLocatorIdx > len(locators):
                    initialLocatorIdx = random.randint(0, len(locators) - 1)
                point = locators[initialLocatorIdx][0]
                locators.sort(key=lambda explosion: geo2.Vec3Distance(point, explosion[0]))
            else:
                random.shuffle(locators)
            for position, direction in locators:
                rotation = direction
                transform = geo2.MatrixTransformation((0, 0, 0), (0, 0, 0, 1), (1, 1, 1), (0, 0, 0), rotation, position)
                transforms.append(transform)

            for each in explosionChildren:
                each.SetLocalExplosionTransforms(transforms)

    @staticmethod
    def PlayExplosion(explosionModel):
        explosionChildren = explosionModel.Find('trinity.EveChildExplosion', 2)
        for each in explosionChildren:
            each.Play()

    @staticmethod
    def PlayClientSideExplosionBall(gfxResPath, scene, worldPos, spaceObjectModel, explosionSorting = 'random', initialLocatorIdx = -1, explosionLink = None):
        explosionModel = trinity.Load(gfxResPath)
        if explosionModel is None:
            log.warn('Could not find explosion %s, can not explode model' % gfxResPath)
            return (0, None, 0)
        clientBall = None
        if SpaceObjectExplosionManager.BALLPARK_MODE:
            clientBall = AddClientBall(worldPos)
        if hasattr(spaceObjectModel, 'translationCurve'):
            explosionModel.translationCurve = spaceObjectModel.translationCurve
        if hasattr(spaceObjectModel, 'rotationCurve'):
            explosionModel.rotationCurve = spaceObjectModel.rotationCurve
        scene.objects.append(explosionModel)
        SpaceObjectExplosionManager.SetUpChildExplosion(explosionModel, spaceObjectModel, explosionSorting, initialLocatorIdx)
        explosionDuration = 60.0
        if isinstance(explosionModel, trinity.EveEffectRoot2):
            for child in explosionModel.effectChildren:
                explosionDuration = max(explosionDuration, getattr(child, 'globalDuration', 0))

        if clientBall:
            uthread.new(SpaceObjectExplosionManager._DelayedBallRemove, clientBall, scene, explosionModel, explosionDuration, explosionLink)
        explosionStartTime = blue.os.GetSimTime()
        log.debug('Exploding %s' % gfxResPath)
        SpaceObjectExplosionManager.PlayExplosion(explosionModel)
        return (explosionDuration, explosionModel, explosionStartTime)

    @staticmethod
    def _DelayedBallRemove(clientBall, scene, explosionModel, secTillBallRemove, explosionLink = None):
        blue.synchro.Sleep(secTillBallRemove * 1000)
        if explosionModel in scene.objects:
            scene.objects.fremove(explosionModel)
        RemoveClientBall(clientBall)
        if explosionLink is not None:
            if explosionLink in SpaceObjectExplosionManager.explosionLinkMap:
                del SpaceObjectExplosionManager.explosionLinkMap[explosionLink]
            if explosionLink in SpaceObjectExplosionManager.explosionLinkWaiters:
                del SpaceObjectExplosionManager.explosionLinkWaiters[explosionLink]

    @staticmethod
    def ExplodeBucketForBall(ball, scene, initialLocatorIdx = -1):
        typeID = ball.typeData['typeID']
        explosionBucket = GetExplosionBucketByTypeID(typeID)
        if ball.id in SpaceObjectExplosionManager.__preferredExplosions:
            explosion = SpaceObjectExplosionManager.__preferredExplosions[ball.id]
            del SpaceObjectExplosionManager.__preferredExplosions[ball.id]
        else:
            explosion = GetRandomExplosion(explosionBucket, ball.typeData.get('sofRaceName', 'default'))
        if not explosionBucket or not explosion:
            explosionBucketID = GetExplosionBucketIDByTypeID(typeID)
            log.warning("Could not find an explosion for '%s' (type '%s') with associated explosionBucketID = '%s'" % (ball.id, typeID, explosionBucketID))
            SpaceObjectExplosionManager.__AddExplosionWreckSwitchTime(ball.id, blue.os.GetSimTime())
            return (0, 0, None)
        return SpaceObjectExplosionManager.Explode(explosion.filePath, explosion.modelSwitchDelayInMs, scene, (ball.x, ball.y, ball.z), ball.GetModel(), explosion.childExplosionType, initialLocatorIdx, ball.id)

    @staticmethod
    def Explode(resPath, modelSwitchDelayInMs, scene, pos, spaceObjectModel, explosionSorting = 'random', initialLocatorIdx = -1, explosionLink = None):
        explosionDuration, explosionModel, startTime = SpaceObjectExplosionManager.PlayClientSideExplosionBall(resPath, scene, pos, spaceObjectModel, explosionSorting, initialLocatorIdx, explosionLink)
        wreckSwitchTime = startTime + modelSwitchDelayInMs * MSEC
        SpaceObjectExplosionManager.__AddExplosionWreckSwitchTime(explosionLink, wreckSwitchTime)
        if explosionModel is None:
            modelSwitchDelayInMs = 0
        return (modelSwitchDelayInMs, explosionDuration, explosionModel)

    @staticmethod
    def __AddExplosionWreckSwitchTime(explosionLink, wreckSwitchTime):
        if explosionLink is not None:
            if explosionLink in SpaceObjectExplosionManager.explosionLinkWaiters:
                SpaceObjectExplosionManager.explosionLinkWaiters[explosionLink](wreckSwitchTime)
            else:
                SpaceObjectExplosionManager.explosionLinkMap[explosionLink] = wreckSwitchTime

    @staticmethod
    def GetWreckSwitchTimeWhenItIsAvailable(ballID, callbackFunction):
        wreckSwitchTime = SpaceObjectExplosionManager.explosionLinkMap.get(ballID, None)
        if wreckSwitchTime is not None:
            callbackFunction(wreckSwitchTime)
            return
        SpaceObjectExplosionManager.explosionLinkWaiters[ballID] = callbackFunction

    @staticmethod
    def SetPreferredExplosion(ballID, explosionObject):
        SpaceObjectExplosionManager.__preferredExplosions[ballID] = explosionObject
