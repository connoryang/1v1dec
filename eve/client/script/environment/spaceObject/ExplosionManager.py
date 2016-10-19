#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\environment\spaceObject\ExplosionManager.py
import math
from collections import deque
import blue
from eve.client.script.ui.shared.systemMenu import betaOptions
import trinity
import geo2
import telemetry
import uthread
import random
import carbon.common.script.util.logUtil as log
import evecamera.utils as camutils
import evegraphics.settings as gfxsettings
from tacticalNavigation.ballparkFunctions import AddClientBall, RemoveClientBall
SECOND = 10000000

class Singleton(type):

    def __init__(cls, mcs, bases, dic):
        super(Singleton, cls).__init__(mcs, bases, dic)
        cls.instance = None

    def __call__(cls, *args, **kw):
        if cls.instance is None:
            cls.instance = super(Singleton, cls).__call__(*args, **kw)
        return cls.instance


class PooledExplosion:

    def __init__(self, path):
        self.path = path
        self.refCount = 0
        self.timestamp = -1
        self.timeoutCountdown = 0
        self.total = 1
        self.active = 0
        self.maxActiveTick = 0
        self.inactive = 1
        self.maxRecentUsed = deque([1], 30)
        self.totalLoads = 1
        self.pool = [trinity.Load(self.path)]
        self.effectDuration = self.pool[0].duration
        if self.effectDuration == -1:
            self.effectDuration = 10
        self.effectDuration = self.effectDuration * SECOND

    def GetDuration(self):
        return self.effectDuration

    def AddRef(self, count):
        self.refCount += count

    def DecRef(self, count):
        self.refCount -= count

    def _AddActive(self, count):
        self.active += count
        self.maxActiveTick = max(self.maxActiveTick, self.active)

    def Pop(self):
        self._AddActive(1)
        if self.inactive > 0:
            self.inactive -= 1
            return self.pool.pop()
        self.total += 1
        self.totalLoads += 1
        return trinity.Load(self.path)

    def Push(self, explosion):
        self.pool.append(explosion)
        self._AddActive(-1)
        self.inactive += 1

    def PrunePool(self, timestamp):
        if self.refCount > 0:
            self.timestamp = -1
        self.maxRecentUsed.append(self.maxActiveTick)
        self.maxActiveTick = 0
        recentMax = max(self.maxRecentUsed)
        if recentMax < self.total:
            recentMax = min(self.total - recentMax, 4)
            self.total -= recentMax
            self.inactive -= recentMax
            del self.pool[:recentMax]
        if self.refCount <= 0:
            if self.timestamp < 0:
                self.timestamp = timestamp
            if timestamp - self.timestamp > 15 * SECOND:
                return True
        return False


class ExplosionManager(object):
    __metaclass__ = Singleton

    def __init__(self, limit = 100):
        self.queue = []
        self.pooledExplosions = {}
        self.ageLimit = 20 * SECOND
        self.limit = limit
        self.running = True
        self.Start()

    def Run(self):
        while self.running:
            blue.synchro.SleepSim(1000)
            self._Prune()

    def Preload(self, path, count = 1):
        if path not in self.pooledExplosions:
            self.pooledExplosions[path] = PooledExplosion(path)
        self.pooledExplosions[path].AddRef(count)

    def Cancel(self, path, count = 1):
        if path not in self.pooledExplosions:
            log.LogWarn('ExplosionManager::Cancel ' + path + ' not loaded.')
            return
        self.pooledExplosions[path].DecRef(count)

    @telemetry.ZONE_METHOD
    def GetExplosion(self, path, scale = 1.0, preloaded = False, callback = None):
        if path not in self.pooledExplosions:
            if preloaded:
                log.LogWarn('ExplosionManager::GetExplosion ' + path + ' not loaded.')
            self.Preload(path)
        elif not preloaded:
            self.pooledExplosions[path].AddRef(1)
        explosion = self.pooledExplosions[path].Pop()
        explosion.scaling = (scale, scale, scale)
        explosion.Start()
        self._Append(callback, explosion, self.pooledExplosions[path])
        return explosion

    def GetBoundingSphereRadius(self, path):
        if path not in self.pooledExplosions:
            log.LogWarn('ExplosionManager::GetBoundingSphereRadius ' + path + ' not loaded.')
            self.Preload(path)
        return getattr(self.pooledExplosions[path].resource, 'boundingSphereRadius', -1)

    def _Append(self, callback, model, pool):
        delay = pool.GetDuration()
        if delay > self.ageLimit:
            delay = self.ageLimit
        stamp = blue.os.GetSimTime() + delay
        self.queue.append((stamp,
         callback,
         model,
         pool))
        if len(self.queue) > self.limit:
            self._Delete(self.queue.pop(0))

    def _Prune(self):
        if not len(self.queue) and not len(self.pooledExplosions):
            return
        now = blue.os.GetSimTime()
        if len(self.queue):
            self.queue.sort()
            while True:
                blue.synchro.Yield()
                now = blue.os.GetSimTime()
                if not len(self.queue) or not self.running:
                    break
                if self.queue[0][0] < now:
                    self._Delete(self.queue.pop(0))
                else:
                    break

        delKeys = []
        for val in self.pooledExplosions.itervalues():
            if val.PrunePool(now):
                delKeys.append(val.path)

        for key in delKeys:
            del self.pooledExplosions[key]

    def _Delete(self, item):
        if item is not None:
            stamp, callback, model, pool = item
            if model is None:
                log.LogError('ExplosionManager::_Delete item has no model')
            if pool is None:
                log.LogError('ExplosionManager::_Delete item has no pool')
            if callback is not None:
                callback(model)
            model.Stop()
            pool.Push(model)
            pool.DecRef(1)

    def GetCount(self):
        return len(self.queue)

    def SetLimit(self, limit):
        self.limit = limit

    def Inspect(self):
        print self.queue

    def Start(self):
        self.running = True
        uthread.new(self.Run)

    def Stop(self):
        self.running = False

    @staticmethod
    def SetUpChildExplosion(explosionModel, explosionLocatorSets):
        explosionChildren = explosionModel.Find('trinity.EveChildExplosion', 2)
        if explosionLocatorSets is not None:
            transforms = []
            locators = [ (each[0], each[1]) for each in (explosionLocatorSets.locators if explosionLocatorSets else []) ]
            random.shuffle(locators)
            for position, direction in locators:
                rotation = geo2.QuaternionRotationArc((0, 1, 0), direction)
                transform = geo2.MatrixTransformation((0, 0, 0), (0, 0, 0, 1), (1, 1, 1), (0, 0, 0), rotation, position)
                transforms.append(transform)

            for each in explosionChildren:
                each.SetLocalExplosionTransforms(transforms)

        for each in explosionChildren:
            each.Play()

    @staticmethod
    def PlayClientSideExplosionBall(gfxResPath, worldPos, rotation, explosionLocatorSets = None):
        scene = sm.GetService('space').GetScene()
        clientBall = AddClientBall(worldPos)
        explosionModel = trinity.Load(gfxResPath)
        explosionModel.translationCurve = clientBall
        explosionModel.rotation = rotation
        ExplosionManager.SetUpChildExplosion(explosionModel, explosionLocatorSets)
        scene.objects.append(explosionModel)
        secTillBallRemove = 60.0
        if isinstance(explosionModel, trinity.EveEffectRoot2):
            for child in explosionModel.effectChildren:
                secTillBallRemove = max(secTillBallRemove, child.globalDuration)

        uthread.new(ExplosionManager._DelayedBallRemove, clientBall, explosionModel, secTillBallRemove)

    @staticmethod
    def _DelayedBallRemove(clientBall, explosionModel, secTillBallRemove):
        blue.synchro.Sleep(secTillBallRemove * 1000)
        scene = sm.GetService('space').GetScene()
        scene.objects.fremove(explosionModel)
        RemoveClientBall(clientBall)


def GetLodLevel(position, radius):
    cam = sm.GetService('sceneManager').GetActiveSpaceCamera()
    if cam is None:
        return 1
    distance = geo2.Vec3Distance(cam.eyePosition, position)
    vp = trinity.device.viewport
    aspectRatio = vp.GetAspectRatio()
    fov = cam.fov / camutils.GetARZoomMultiplier(aspectRatio)
    lodQuality = gfxsettings.Get(gfxsettings.GFX_LOD_QUALITY)
    boundingSize = radius / (math.tan(fov / 2) * distance) * vp.height
    if boundingSize < 192 / lodQuality:
        return 1
    return 0


exports = {'util.ExplosionManager': ExplosionManager,
 'util.GetLodLevel': GetLodLevel}
