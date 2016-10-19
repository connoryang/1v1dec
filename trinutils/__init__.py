#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\trinutils\__init__.py


def ReloadTextures(obj):
    reloadedpaths = set()
    for texresource in obj.Find('trinity.TriTextureParameter'):
        if texresource.resource and texresource.resourcePath.lower() not in reloadedpaths:
            texresource.resource.Reload()
            reloadedpaths.add(texresource.resourcePath.lower())


def TrinObjectHasCurves(trinObject):
    if hasattr(trinObject, 'translationCurve') and trinObject.translationCurve is not None:
        return True
    if hasattr(trinObject, 'rotationCurve') and trinObject.rotationCurve is not None:
        return True
    return False
