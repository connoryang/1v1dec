#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\evegraphics\fsd\graphicIDs.py
from evegraphics.fsd.base import BuiltDataLoader

class GraphicIDs(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/graphicIDs.static'
    __autobuildBuiltFile__ = 'eve/autobuild/staticdata/client/graphicIDs.static'


def GetGraphicIDDictionary():
    return GraphicIDs.GetData()


def GetGraphic(graphicID):
    return GraphicIDs.GetData().get(graphicID, None)


def GetGraphicAttribute(graphicID, attributeName, default = None):
    if isinstance(graphicID, (int, long)):
        return getattr(GetGraphic(graphicID), attributeName, default)
    return getattr(graphicID, attributeName, default)


def GetGraphicFile(graphicID, default = None):
    return GetGraphicAttribute(graphicID, 'graphicFile', default)


def GetExplosionBucketID(graphicID, default = None):
    return GetGraphicAttribute(graphicID, 'explosionBucketID', default)


def GetSofRaceName(graphicID, default = None):
    return GetGraphicAttribute(graphicID, 'sofRaceName', default)


def GetSofHullName(graphicID, default = None):
    return GetGraphicAttribute(graphicID, 'sofHullName', default)


def GetSofFactionName(graphicID, default = None):
    return GetGraphicAttribute(graphicID, 'sofFactionName', default)


def GetCollisionFile(graphicID, default = None):
    return GetGraphicAttribute(graphicID, 'collisionFile', default)


def GetIconFolder(graphicID, default = None):
    return GetGraphicAttribute(graphicID, 'iconFolder', default)


def GetAnimationStates(graphicID, default = None):
    return GetGraphicAttribute(graphicID, 'animationStates', default)


def GetAnimationStateObjects(graphicID, default = None):
    return GetGraphicAttribute(graphicID, 'animationStateObjects', default)


def GetAmmoColor(graphicID, default = None):
    return GetGraphicAttribute(graphicID, 'ammoColor', default)


def GetAlbedoColor(graphicID, default = None):
    return GetGraphicAttribute(graphicID, 'albedoColor', default)


def GetEmissiveColor(graphicID, default = None):
    return GetGraphicAttribute(graphicID, 'emissiveColor', default)
