#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\evegraphics\fsd\explosionBuckets.py
import itertools
import random
import evetypes
from evegraphics.fsd.base import BuiltDataLoader
from evegraphics.fsd.graphicIDs import GetExplosionBucketID
import logging
log = logging.getLogger(__file__)

class ExplosionBucketsLoader(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/explosionBuckets.static'
    __autobuildBuiltFile__ = 'eve/autobuild/staticdata/client/explosionBuckets.static'


def GetExplosionBuckets():
    return ExplosionBucketsLoader.GetData()


def GetExplosionBucketIDByTypeID(typeID):
    explosionBucketIdByGraphicID = GetExplosionBucketID(evetypes.GetGraphicID(typeID))
    explosionBucketIdByGroup = evetypes.GetExplosionBucketIDByGroup(evetypes.GetGroupID(typeID))
    return explosionBucketIdByGraphicID or explosionBucketIdByGroup


def GetExplosionBucketByTypeID(typeID):
    return GetExplosionBucket(GetExplosionBucketIDByTypeID(typeID))


def GetExplosionBucket(explosionBucketID):
    return GetExplosionBuckets().get(explosionBucketID, None)


def GetExplosionAttribute(explosionBucketID, attributeName, default = None):
    if isinstance(explosionBucketID, (int, long)):
        return getattr(GetExplosionBucket(explosionBucketID), attributeName, default)
    return getattr(explosionBucketID, attributeName, default)


def GetExplosionRaces(explosionBucketID):
    explosions = GetExplosionAttribute(explosionBucketID, 'explosions', None)
    if explosions is None:
        log.error("ExplosionBucket '%s' has no explosions" % explosionBucketID)
        return
    return explosions


def GetExplosionsForRace(explosionBucketID, raceName):
    explosions = GetExplosionAttribute(explosionBucketID, 'explosions', None)
    if explosions is None:
        log.error("ExplosionBucket '%s' has no explosions" % explosionBucketID)
        return
    return explosions.get(raceName, explosions.get('default', None))


def GetRandomExplosion(explosionBucketID, raceName):
    listOfExplosionsToPick = GetExplosionsForRace(explosionBucketID, raceName)
    if listOfExplosionsToPick is None:
        log.error("ExplosionBucket '%s' has no explosions for race '%s' or race 'default'" % (explosionBucketID, raceName))
        return
    return random.choice(listOfExplosionsToPick)
