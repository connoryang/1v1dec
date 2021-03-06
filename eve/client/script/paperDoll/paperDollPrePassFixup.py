#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\paperDoll\paperDollPrePassFixup.py
import trinity
import logging
import eve.common.script.paperDoll.paperDollDefinitions as pdDef
import eve.client.script.paperDoll.commonClientFunctions as pdCcf
import eve.common.script.paperDoll.paperDollConfiguration as pdCfg
SOURCE_AREA_TYPE_OPAQUE = 0
SOURCE_AREA_TYPE_DECAL = 1
SHADOW_ALPHATEST_EFFECT_PATH = 'res:/Graphics/Effect/Managed/Interior/Avatar/ShadowAlphaTest.fx'
SHADOW_OPAQUE_EFFECT_PATH = 'res:/Graphics/Effect/Managed/Interior/Avatar/Shadow.fx'
SHADOW_CLOTH_ALPHATEST_EFFECT_PATH = 'res:/Graphics/Effect/Managed/Interior/Avatar/ShadowClothAlphaTest.fx'
SHADOW_CLOTH_OPAQUE_EFFECT_PATH = 'res:/Graphics/Effect/Managed/Interior/Avatar/ShadowCloth.fx'
COLLAPSED_SHADOW_EFFECT_PATH = 'res:/Graphics/Effect/Managed/Interior/Avatar/ShadowCollapsed.fx'
COLLAPSED_BASIC_EFFECT_PATH = 'res:/Graphics/Effect/Managed/Interior/Avatar/PortraitBasic.fx'
LIGHT_CONTROL_MAP_MALE_PATH = 'res:/Graphics/Character/Global/FaceSetup/MaleLightControlMap.png'
LIGHT_CONTROL_MAP_FEMALE_PATH = 'res:/Graphics/Character/Global/FaceSetup/FemaleLightControlMap.png'
USE_DECAL_PLP_FOR_TRANSPARENT_AREAS = True
MATERIAL_ID_CONVERSION = {(0, 50, 1): 64,
 (0, 20, 11): 66,
 (0, 400, 11): 68,
 (0, 800, 11): 70,
 (5, 20, 11): 71,
 (5, 21, 11): 71,
 (10, 50, 1): 74,
 (10, 100, 1): 76,
 (10, 20, 11): 78,
 (10, 800, 11): 80,
 (11, 800, 11): 80,
 (20, 100, 1): 82,
 (10, 300, 11): 84,
 (13, 100, 1): 86}
MATERIAL_ID_EXACT = {0: 72,
 5: 73,
 10: 74,
 11: 75,
 12: 76,
 13: 77,
 14: 78,
 15: 79,
 16: 80,
 17: 81,
 18: 82,
 19: 83,
 20: 84,
 21: 85,
 22: 86,
 23: 87,
 24: 88,
 25: 89,
 26: 90,
 27: 91,
 28: 92,
 29: 93,
 30: 94,
 31: 95,
 32: 96}
MATERIAL_ID_TRANSPARENT_HACK_EXACT = {0: 74,
 5: 72,
 10: 74,
 11: 74,
 13: 70}

def FindMaterialID(materialID, specPower1, specPower2, materialLookupTable = MATERIAL_ID_EXACT):
    if materialLookupTable is None:
        materialLookupTable = MATERIAL_ID_EXACT
    exact = materialLookupTable.get(materialID, -1)
    if exact != -1:
        return exact
    specPower2 += 1
    for key in MATERIAL_ID_CONVERSION:
        if key == (materialID, specPower1, specPower2):
            return MATERIAL_ID_CONVERSION[key]

    logging.warn('PaperDollPrepassFixup: could not find a match for materialID = %s, specular power = (%s to %s)', materialID, specPower1, specPower2)
    best = None
    bestError = 10000
    for key in MATERIAL_ID_CONVERSION:
        if best is None or key[0] == materialID:
            error = abs(specPower1 - key[1]) + abs(specPower2 - key[1])
            if error < bestError:
                best = MATERIAL_ID_CONVERSION[key]
                bestError = error

    return best


def CopyResource(res):
    if res is None:
        return
    newRes = trinity.TriTextureParameter()
    newRes.name = res.name
    newRes.resourcePath = res.resourcePath
    if res.resourcePath == '' and res.resource is not None:
        newRes.SetResource(res.resource)
    return newRes


def CopyResources(sourceEffect, targetMaterial, resourceNames):
    if hasattr(sourceEffect, 'resources'):
        for res in sourceEffect.resources:
            if res.name not in resourceNames or type(res) != trinity.TriTextureParameter:
                continue
            newParameter = trinity.TriTextureParameter()
            newParameter.name = res.name
            newParameter.resourcePath = res.resourcePath
            if res.resourcePath == '' and res.resource is not None:
                newParameter.SetResource(res.resource)
            if type(targetMaterial) == trinity.Tr2Effect:
                targetMaterial.resources.append(newParameter)
            else:
                targetMaterial.parameters[res.name] = newParameter


def CopyParameters(sourceEffect, targetMaterial, parameterNames):
    if type(sourceEffect) != trinity.Tr2ShaderMaterial:
        for param in sourceEffect.parameters:
            if param.name not in parameterNames:
                continue
            newParameter = type(param)()
            newParameter.name = param.name
            newParameter.value = param.value
            if type(targetMaterial) == trinity.Tr2Effect:
                targetMaterial.parameters.append(newParameter)
            else:
                targetMaterial.parameters[param.name] = newParameter


def CopyAreaForPrePassShadows(area, sourceAreaType = SOURCE_AREA_TYPE_OPAQUE):
    originalEffect = area.effect
    if originalEffect is None or not hasattr(originalEffect, 'effectFilePath'):
        return
    newArea = trinity.Tr2MeshArea()
    newArea.name = area.name
    newArea.index = area.index
    newArea.count = area.count
    newEffect = trinity.Tr2Effect()
    if originalEffect.effectFilePath.lower().find('avatar') == -1:
        if sourceAreaType == SOURCE_AREA_TYPE_DECAL and originalEffect.effectFilePath.lower().find('alphatest') == -1:
            return
    elif originalEffect.effectFilePath.lower().find('cloth') == -1:
        if sourceAreaType == SOURCE_AREA_TYPE_DECAL:
            newEffect.effectFilePath = SHADOW_ALPHATEST_EFFECT_PATH
        else:
            newEffect.effectFilePath = SHADOW_OPAQUE_EFFECT_PATH
    elif sourceAreaType == SOURCE_AREA_TYPE_DECAL:
        newEffect.effectFilePath = SHADOW_CLOTH_ALPHATEST_EFFECT_PATH
    else:
        newEffect.effectFilePath = SHADOW_CLOTH_OPAQUE_EFFECT_PATH
    newEffect.name = originalEffect.name
    CopyResources(originalEffect, newEffect, {'DiffuseMap', 'CutMaskMap'})
    CopyParameters(originalEffect, newEffect, {'TransformUV0',
     'MaterialDiffuseColor',
     'CutMaskInfluence',
     'ArrayOfCutMaskInfluence'})
    newArea.effect = newEffect
    return newArea


def GetEffectParameter(effect, name, default):
    for p in effect.parameters:
        if p.name == name:
            return p

    return default


def CopyAreaForPrePassDepthNormal(area, sourceAreaType = SOURCE_AREA_TYPE_OPAQUE, materialLookupTable = None):
    originalEffect = area.effect
    if originalEffect is None:
        return
    if hasattr(originalEffect, 'effectFilePath') and 'glass' in originalEffect.effectFilePath.lower():
        return
    newArea = trinity.Tr2MeshArea()
    newArea.name = area.name
    newArea.index = area.index
    newArea.count = area.count
    newArea.reversed = area.reversed
    newMaterial = trinity.Tr2ShaderMaterial()
    newMaterial.highLevelShaderName = 'NormalDepth'
    if sourceAreaType == SOURCE_AREA_TYPE_DECAL:
        newMaterial.name = 'Skinned_Cutout_NormalDepth'
        newMaterial.defaultSituation = 'AlphaCutout'
    else:
        newMaterial.name = 'Skinned_Opaque_NormalDepth'
        newMaterial.defaultSituation = ''
    if hasattr(originalEffect, 'effectFilePath') and 'double' in originalEffect.effectFilePath.lower():
        newMaterial.defaultSituation = newMaterial.defaultSituation + ' DoubleMaterial'
    if hasattr(originalEffect, 'name'):
        name = originalEffect.name.lower()
        if name.startswith('c_skin_'):
            newMaterial.defaultSituation = newMaterial.defaultSituation + ' SmoothNormal'
        elif name.startswith('c_eyes'):
            newMaterial.defaultSituation = newMaterial.defaultSituation + ' EyeShader'
    CopyResources(area.effect, newMaterial, {'NormalMap',
     'SpecularMap',
     'DiffuseMap',
     'CutMaskMap'})
    CopyParameters(area.effect, newMaterial, {'TransformUV0',
     'MaterialDiffuseColor',
     'CutMaskInfluence',
     'MaterialSpecularFactors',
     'ArrayOfCutMaskInfluence',
     'ArrayOfMaterialLibraryID',
     'ArrayOfMaterial2LibraryID',
     'ArrayOfMaterialSpecularFactors'})
    if 'MaterialSpecularFactors' in newMaterial.parameters:
        newMaterial.parameters['MaterialSpecularFactors'].z = 2.0
    MaterialLibraryID = pdCcf.FindParameterByName(area.effect, 'MaterialLibraryID')
    if MaterialLibraryID is None:
        MaterialLibraryID = 11
    else:
        MaterialLibraryID = MaterialLibraryID.x
    MaterialSpecularCurve = pdCcf.FindParameterByName(area.effect, 'MaterialSpecularCurve')
    if MaterialSpecularCurve is None:
        MaterialSpecularCurve = (0, 50, 0, 0)
    else:
        MaterialSpecularCurve = (MaterialSpecularCurve.x,
         MaterialSpecularCurve.y,
         MaterialSpecularCurve.z,
         MaterialSpecularCurve.w)
    param = trinity.Tr2FloatParameter()
    param.name = 'MaterialLibraryID'
    param.value = FindMaterialID(MaterialLibraryID, 1 + MaterialSpecularCurve[3], MaterialSpecularCurve[1], materialLookupTable=materialLookupTable)
    newMaterial.parameters['MaterialLibraryID'] = param
    MaterialLibraryID = pdCcf.FindParameterByName(area.effect, 'Material2LibraryID')
    if MaterialLibraryID is not None:
        param = trinity.Tr2FloatParameter()
        param.name = 'Material2LibraryID'
        param.value = FindMaterialID(MaterialLibraryID.x, 1 + MaterialSpecularCurve[3], MaterialSpecularCurve[1])
        newMaterial.parameters['Material2LibraryID'] = param
    newArea.effect = newMaterial
    return newArea


def CopyArea(area):
    newArea = area.CloneTo()
    if newArea.effect is not None:
        if type(newArea.effect) != trinity.Tr2ShaderMaterial:
            newArea.effect.effectFilePath = area.effect.effectFilePath
            newArea.effect.resources.removeAt(-1)
            for r in area.effect.resources:
                newRes = CopyResource(r)
                if newRes is not None:
                    newArea.effect.resources.append(newRes)

    return newArea


def CopyAreaOnly(area):
    newArea = trinity.Tr2MeshArea()
    newArea.name = area.name
    newArea.index = area.index
    newArea.count = area.count
    newArea.reversed = area.reversed
    return newArea


def CopyHairShader(fx):
    newMaterial = trinity.Tr2ShaderMaterial()
    lowPath = fx.effectFilePath.lower()
    newMaterial.highLevelShaderName = 'Hair'
    if 'detailed' in lowPath:
        newMaterial.defaultSituation = 'Detailed'
    if 'dxt5n' in lowPath:
        newMaterial.defaultSituation = newMaterial.defaultSituation + ' OPT_USE_DXT5N'
    CopyCommonAvatarMaterialParams(newMaterial, fx)
    CopyResources(fx, newMaterial, {'TangentSampler'})
    CopyParameters(fx, newMaterial, {'HairParameters',
     'HairSpecularFactors1',
     'HairSpecularFactors2',
     'HairSpecularColor1',
     'HairSpecularColor2',
     'TangentMapParameters',
     'HairDiffuseBias'})
    return newMaterial


def CopyHairShaderDepthNormal(fx):
    newMaterial = trinity.Tr2ShaderMaterial()
    lowPath = fx.effectFilePath.lower()
    newMaterial.highLevelShaderName = 'NormalDepth'
    newMaterial.defaultSituation = 'AlphaCutout TwoSided'
    if 'detailed' in lowPath:
        newMaterial.defaultSituation = newMaterial.defaultSituation + ' Detailed'
    if 'dxt5n' in lowPath:
        newMaterial.defaultSituation = newMaterial.defaultSituation + ' OPT_USE_DXT5N'
    CopyCommonAvatarMaterialParams(newMaterial, fx)
    param = trinity.Tr2FloatParameter()
    param.name = 'MaterialLibraryID'
    param.value = 75
    newMaterial.parameters['MaterialLibraryID'] = param
    param = trinity.Tr2FloatParameter()
    param.name = 'AlphaTestValue'
    param.value = 0.0235
    newMaterial.parameters['AlphaTestValue'] = param
    return newMaterial


def CopyAreaForPrePassHair(area):
    fx = area.effect
    if fx is not None and hasattr(fx, 'effectFilePath') and 'hair' in fx.effectFilePath.lower():
        newArea = CopyArea(area)
        newMaterial = CopyHairShader(fx)
        newArea.effect = newMaterial
        newArea.useSHLighting = True
        return newArea


def CopyAreaForPrePassHairDepthNormal(area):
    fx = area.effect
    if fx is not None and hasattr(fx, 'effectFilePath') and 'hair' in fx.effectFilePath.lower():
        newArea = CopyArea(area)
        newMaterial = CopyHairShaderDepthNormal(fx)
        newArea.effect = newMaterial
        return newArea


def FindShaderMaterialParameter(mat, name):
    for param in mat.parameters:
        if param.name == name:
            return param

    logging.error('%s target param not found in Tr2ShaderMaterial!', name)


def CopyCommonAvatarMaterialParams(mat, fx, meshName = None):
    CopyResources(fx, mat, {'NormalMap',
     'SpecularMap',
     'DiffuseMap',
     'CutMaskMap',
     'FresnelLookupMap',
     'ColorNdotLLookupMap'})
    CopyParameters(fx, mat, {'MaterialDiffuseColor',
     'MaterialSpecularColor',
     'MaterialSpecularCurve',
     'MaterialSpecularFactors',
     'FresnelFactors',
     'MaterialLibraryID',
     'TransformUV0',
     'CutMaskInfluence'})
    cmi = mat.parameters.get('CutMaskInfluence')
    if cmi and cmi.value >= 0.85:
        if meshName and 'drape' in meshName:
            cmi.value = 1.0
        elif cmi.value <= 1.0:
            cmi.value = 0.999
    if 'MaterialSpecularColor' in mat.parameters:
        mat.parameters['MaterialSpecularColor'].x = mat.parameters['MaterialSpecularColor'].x * 1.2
        mat.parameters['MaterialSpecularColor'].y = mat.parameters['MaterialSpecularColor'].y * 1.2
        mat.parameters['MaterialSpecularColor'].z = mat.parameters['MaterialSpecularColor'].z * 1.2
    if 'MaterialDiffuseColor' not in mat.parameters:
        param = trinity.Tr2Vector4Parameter()
        param.name = 'MaterialDiffuseColor'
        param.value = (1, 1, 1, 1)
        mat.parameters['MaterialDiffuseColor'] = param


def ConvertEffectToTr2ShaderMaterial(fx, defaultSituation = None, meshName = None):
    if hasattr(fx, 'effectFilePath'):
        fxpath = fx.effectFilePath.lower()
        newMaterial = trinity.Tr2ShaderMaterial()
        if defaultSituation is not None:
            newMaterial.defaultSituation = defaultSituation
        if hasattr(fx, 'name'):
            name = fx.name.lower()
            if name.startswith('c_eyes'):
                newMaterial.defaultSituation = newMaterial.defaultSituation + ' EyeShader'
        if 'double' in fxpath:
            newMaterial.highLevelShaderName = 'SkinnedAvatarBRDFDouble'
            CopyCommonAvatarMaterialParams(newMaterial, fx, meshName)
            CopyParameters(fx, newMaterial, {'Material2LibraryID',
             'Material2SpecularCurve',
             'Material2SpecularColor',
             'Material2SpecularFactors'})
            if pdCcf.IsSkin(fx):
                newMaterial.defaultSituation = newMaterial.defaultSituation + ' Skin'
        elif 'eyeshader' in fxpath or 'skinnedavatarbrdf' in fxpath or 'portraitbasic' in fxpath:
            newMaterial.highLevelShaderName = 'SkinnedAvatarBrdf'
            CopyCommonAvatarMaterialParams(newMaterial, fx, meshName)
            if pdCcf.IsSkin(fx):
                newMaterial.defaultSituation = newMaterial.defaultSituation + ' Skin'
        elif 'skinnedavatar' in fxpath:
            newMaterial.highLevelShaderName = 'SkinnedAvatar'
            CopyCommonAvatarMaterialParams(newMaterial, fx, meshName)
        elif 'clothavatar' in fxpath:
            newMaterial.highLevelShaderName = 'ClothAvatar'
            CopyCommonAvatarMaterialParams(newMaterial, fx, meshName)
        elif 'glass' in fxpath:
            newMaterial.highLevelShaderName = 'GlassAvatar'
            CopyCommonAvatarMaterialParams(newMaterial, fx, meshName)
            CopyParameters(fx, newMaterial, {'GlassOptions',
             'GlassOptions2',
             'GlowColor',
             'MaterialCubeReflectionControl',
             'MaterialCubeReflection',
             'MaterialCubeReflectionColor',
             'GlassTransparencyColor',
             'GlassTransparencyOptions'})
        else:
            return fx
        return newMaterial
    return fx


def AddDepthNormalAreasToStandardMesh(mesh):
    mesh.depthNormalAreas.removeAt(-1)
    for area in mesh.opaqueAreas:
        newArea = CopyAreaForPrePassDepthNormal(area, SOURCE_AREA_TYPE_OPAQUE)
        if newArea is not None:
            mesh.depthNormalAreas.append(newArea)
            newArea.effect.parameters['TransformUV0'].value = (0, 0, 1, 1)


def IsEyeRelated(areaMesh):
    if areaMesh.effect is None or not hasattr(areaMesh.effect, 'name'):
        return False
    low = areaMesh.effect.name.lower()
    return low.startswith('c_eyes') or low.startswith('c_eyewetness') or 'eyelashes' in low


def IsGlassRelated(areaMesh):
    if areaMesh.effect is None or not hasattr(areaMesh.effect, 'effectFilePath'):
        return False
    low = areaMesh.effect.effectFilePath.lower()
    return 'glass' in low


def AddPrepassAreasToStandardMesh(mesh, processDepthAreas, processDepthNormalAreas, avatar = None, doll = None, useLightControlMap = False):
    opaqueAreas = mesh.opaqueAreas
    processDepthAreas = len(mesh.depthAreas) <= 0
    if processDepthNormalAreas:
        mesh.depthNormalAreas.removeAt(-1)
    mesh.decalPrepassAreas.removeAt(-1)
    mesh.opaquePrepassAreas.removeAt(-1)
    for area in mesh.transparentAreas:
        if area.name[0:8] == 'Prepass_':
            mesh.transparentAreas.remove(area)

    newAreas = []
    for area in opaqueAreas:
        if IsGlassRelated(area):
            newArea = CopyAreaOnly(area)
            if newArea is not None:
                newArea.name = 'Prepass_' + newArea.name
                newArea.effect = ConvertEffectToTr2ShaderMaterial(area.effect, 'SHLighting', mesh.name)
                newArea.useSHLighting = True
                newAreas.append(newArea)
                area.debugIsHidden = True
            if processDepthAreas:
                newArea = CopyAreaForPrePassShadows(area, SOURCE_AREA_TYPE_OPAQUE)
                if newArea is not None:
                    mesh.depthAreas.append(newArea)
            continue
        if area.effect is not None and hasattr(area.effect, 'effectFilePath') and 'hair' in area.effect.effectFilePath.lower():
            continue
        if processDepthNormalAreas:
            newArea = CopyAreaForPrePassDepthNormal(area, SOURCE_AREA_TYPE_OPAQUE)
            if newArea is not None:
                mesh.depthNormalAreas.append(newArea)
        if processDepthAreas:
            newArea = CopyAreaForPrePassShadows(area, SOURCE_AREA_TYPE_OPAQUE)
            if newArea is not None:
                mesh.depthAreas.append(newArea)
        newArea = CopyAreaOnly(area)
        if newArea is not None:
            if mesh.name.startswith('head') and useLightControlMap:
                newArea.effect = ConvertEffectToTr2ShaderMaterial(area.effect, 'Prepass SHLighting', mesh.name)
                useLightControl = trinity.Tr2FloatParameter()
                useLightControl.name = 'UseLightControl'
                useLightControl.value = 0.5
                newArea.effect.parameters[useLightControl.name] = useLightControl
                lightControlMap = trinity.TriTextureParameter()
                lightControlMap.name = 'LightControlMap'
                lcmPath = LIGHT_CONTROL_MAP_FEMALE_PATH
                if doll and doll.gender == pdDef.GENDER.MALE:
                    lcmPath = LIGHT_CONTROL_MAP_MALE_PATH
                lightControlMap.resourcePath = lcmPath
                newArea.effect.parameters[lightControlMap.name] = lightControlMap
                lightControlMatrix = trinity.Tr2Matrix4Parameter()
                lightControlMatrix.name = 'LightControlMatrix'
                newArea.effect.parameters[lightControlMatrix.name] = lightControlMatrix
                newArea.useSHLighting = True
                if avatar:
                    headMatrixCurves = None
                    boneMatrixCurve = None
                    for cs in avatar.curveSets:
                        if cs.name == 'HeadMatrixCurves':
                            headMatrixCurves = cs
                            for curve in headMatrixCurves.curves:
                                if curve.bone == 'Head':
                                    boneMatrixCurve = curve

                            break

                    if not headMatrixCurves:
                        headMatrixCurves = trinity.TriCurveSet()
                        headMatrixCurves.name = 'HeadMatrixCurves'
                        avatar.curveSets.append(headMatrixCurves)
                    if not boneMatrixCurve:
                        boneMatrixCurve = trinity.Tr2BoneMatrixCurve()
                        boneMatrixCurve.bone = 'Head'
                        boneMatrixCurve.name = 'HeadMatrixCurve'
                        boneMatrixCurve.skinnedObject = avatar
                        headMatrixCurves.curves.append(boneMatrixCurve)
                    if len(headMatrixCurves.bindings):
                        bind = headMatrixCurves.bindings[0]
                    else:
                        bind = trinity.TriValueBinding()
                        headMatrixCurves.bindings.append(bind)
                    bind.sourceObject = boneMatrixCurve
                    bind.destinationObject = lightControlMatrix
                    bind.sourceAttribute = 'currentValue'
                    bind.destinationAttribute = 'value'
                    headMatrixCurves.Play()
            else:
                newArea.effect = ConvertEffectToTr2ShaderMaterial(area.effect, 'Prepass', mesh.name)
            mesh.opaquePrepassAreas.append(newArea)

    def FixCutMask(area):
        if area.effect and 'CutMaskInfluence' in area.effect.parameters:
            area.effect.parameters['CutMaskInfluence'].value = 1.0

    def AddAreasForRegularPLP(area, materialLookupTable = None, isTransparent = False):
        if area.effect is not None and hasattr(area.effect, 'effectFilePath') and 'hair' in area.effect.effectFilePath.lower():
            return
        if processDepthNormalAreas:
            newArea = CopyAreaForPrePassDepthNormal(area, SOURCE_AREA_TYPE_DECAL, materialLookupTable=materialLookupTable)
            if newArea is not None:
                if isTransparent:
                    FixCutMask(newArea)
                mesh.depthNormalAreas.append(newArea)
        if processDepthAreas:
            newArea = CopyAreaForPrePassShadows(area, SOURCE_AREA_TYPE_DECAL)
            if newArea is not None:
                if isTransparent:
                    FixCutMask(newArea)
                mesh.depthAreas.append(newArea)
        newArea = CopyAreaOnly(area)
        if newArea is not None:
            newArea.effect = ConvertEffectToTr2ShaderMaterial(area.effect, 'Prepass Decal', mesh.name)
            if isTransparent:
                FixCutMask(newArea)
            mesh.decalPrepassAreas.append(newArea)
        area.debugIsHidden = True

    for area in mesh.decalAreas:
        if IsGlassRelated(area):
            newArea = CopyAreaOnly(area)
            if newArea is not None:
                newArea.name = 'Prepass_' + newArea.name
                newArea.effect = ConvertEffectToTr2ShaderMaterial(area.effect, 'SHLighting', mesh.name)
                newArea.useSHLighting = True
                newAreas.append(newArea)
                area.debugIsHidden = True
            if processDepthAreas:
                newArea = CopyAreaForPrePassShadows(area, SOURCE_AREA_TYPE_DECAL)
                if newArea is not None:
                    mesh.depthAreas.append(newArea)
        else:
            AddAreasForRegularPLP(area)

    for area in mesh.transparentAreas:
        if area.effect is None:
            continue
        if hasattr(area.effect, 'effectFilePath') and 'hair' in area.effect.effectFilePath.lower():
            continue
        if USE_DECAL_PLP_FOR_TRANSPARENT_AREAS and not IsEyeRelated(area) and not IsGlassRelated(area):
            AddAreasForRegularPLP(area, materialLookupTable=MATERIAL_ID_TRANSPARENT_HACK_EXACT, isTransparent=True)
            area.effect = None
        else:
            newArea = CopyAreaOnly(area)
            if newArea is not None:
                if 'C_SkinShiny' in area.effect.name:
                    newArea.effect = ConvertEffectToTr2ShaderMaterial(area.effect, 'Prepass Decal', mesh.name)
                    mesh.decalPrepassAreas.append(newArea)
                else:
                    newArea.effect = ConvertEffectToTr2ShaderMaterial(area.effect, 'SHLighting', mesh.name)
                    newArea.useSHLighting = True
                    newAreas.append(newArea)
                area.debugIsHidden = True

    mesh.transparentAreas.extend(newAreas)


def AddPrepassAreasToHair(mesh, processDepthAreas, processDepthNormalAreas, usePrepassAlphaTestHair):
    if len(mesh.depthAreas) > 0:
        processDepthAreas = False
    if processDepthNormalAreas:
        mesh.depthNormalAreas.removeAt(-1)
    mesh.depthNormalAreas.removeAt(-1)
    mesh.decalPrepassAreas.removeAt(-1)
    mesh.opaquePrepassAreas.removeAt(-1)
    for area in mesh.transparentAreas:
        if area.name[0:6] == 'Decal_' or area.name[0:8] == 'Prepass_':
            mesh.transparentAreas.remove(area)

    result = False
    newDepthAreas = []
    if processDepthAreas:
        for area in mesh.decalAreas:
            newArea = CopyAreaForPrePassShadows(area, SOURCE_AREA_TYPE_DECAL)
            if newArea is not None:
                newDepthAreas.append(newArea)

        for area in mesh.transparentAreas:
            newArea = CopyAreaForPrePassShadows(area, SOURCE_AREA_TYPE_DECAL)
            if newArea is not None:
                newDepthAreas.append(newArea)

    if not usePrepassAlphaTestHair:
        newAreas = []
        for area in mesh.transparentAreas:
            newArea = CopyAreaForPrePassHair(area)
            if newArea is not None:
                newArea.name = 'Decal_' + newArea.name
                newAreas.append(newArea)
                result = True
            area.debugIsHidden = True

        mesh.transparentAreas.extend(newAreas)
        for area in mesh.decalAreas:
            newArea = CopyAreaForPrePassHair(area)
            if newArea is not None:
                newArea.name = 'Decal_' + newArea.name
                mesh.decalPrepassAreas.append(newArea)
                result = True
            area.debugIsHidden = True

    else:
        for area in mesh.transparentAreas:
            if not area.reversed:
                newArea = CopyAreaForPrePassHair(area)
                if newArea is not None:
                    newArea.name = 'Decal_' + newArea.name
                    mesh.decalPrepassAreas.append(newArea)
                    result = True
                newArea = CopyAreaForPrePassHairDepthNormal(area)
                if newArea is not None:
                    newArea.name = 'Decal_' + newArea.name
                    mesh.depthNormalAreas.append(newArea)
                    result = True
            area.debugIsHidden = True

        for area in mesh.decalAreas:
            if not area.reversed:
                newArea = CopyAreaForPrePassHair(area)
                if newArea is not None:
                    newArea.name = 'Decal_' + newArea.name
                    mesh.decalPrepassAreas.append(newArea)
                    result = True
                newArea = CopyAreaForPrePassHairDepthNormal(area)
                if newArea is not None:
                    newArea.name = 'Decal_' + newArea.name
                    mesh.depthNormalAreas.append(newArea)
                    result = True
            area.debugIsHidden = True

    if result:
        mesh.depthAreas.extend(newDepthAreas)
    return result


def AddPrepassAreasToAvatar(avatar, visualModel, doll, clothSimulationActive = True, **kwargs):
    createShadows = doll.overrideLod <= pdCfg.PerformanceOptions.shadowLod
    useLightControlMap = doll.overrideLod < 1
    collapseShadowMesh = kwargs.get('collapseShadowMesh', False)
    collapsePLPMesh = kwargs.get('collapsePLPMesh', False)
    collapseMainMesh = kwargs.get('collapseMainMesh', False)
    for mesh in visualModel.meshes:
        if mesh.name[0:4] == 'hair':
            if AddPrepassAreasToHair(mesh, processDepthAreas=createShadows and not collapseShadowMesh, processDepthNormalAreas=not collapsePLPMesh, usePrepassAlphaTestHair=doll.usePrepassAlphaTestHair):
                continue
        AddPrepassAreasToStandardMesh(mesh, processDepthAreas=createShadows and not collapseShadowMesh, processDepthNormalAreas=not collapsePLPMesh, doll=doll, avatar=avatar, useLightControlMap=useLightControlMap)

    if doll.overrideLod >= pdCfg.PerformanceOptions.singleBoneLod:
        for mesh in visualModel.meshes:
            for dn in mesh.depthNormalAreas:
                dn.effect.defaultSituation = dn.effect.defaultSituation + ' SingleBone'

            for dn in mesh.opaquePrepassAreas:
                if hasattr(dn.effect, 'defaultSituation'):
                    dn.effect.defaultSituation = dn.effect.defaultSituation + ' SingleBone'

            for dn in mesh.decalPrepassAreas:
                dn.effect.defaultSituation = dn.effect.defaultSituation + ' SingleBone'

    if doll.overrideLod == 2:
        for mesh in visualModel.meshes:
            for dn in mesh.depthNormalAreas:
                dn.effect.defaultSituation = dn.effect.defaultSituation + ' OPT_USE_OBJECT_NORMAL'

    if collapseMainMesh:
        for mesh in visualModel.meshes:
            for dn in mesh.opaquePrepassAreas:
                dn.effect.defaultSituation = dn.effect.defaultSituation + ' OPT_COLLAPSED_PLP'

    if doll.useDXT5N:
        for mesh in visualModel.meshes:
            for areas in pdCcf.MeshAreaListIterator(mesh, includePLP=True):
                for area in areas:
                    if hasattr(area.effect, 'defaultSituation'):
                        area.effect.defaultSituation = area.effect.defaultSituation + ' OPT_USE_DXT5N'

    if clothSimulationActive:
        for mesh in avatar.clothMeshes:
            if mesh.effect and mesh.effect.name:
                mesh.depthEffect = None
                newEffect = trinity.Tr2ShaderMaterial()
                newEffect.highLevelShaderName = 'Shadow'
                newEffect.defaultSituation = 'Cloth'
                CopyResources(mesh.effect, newEffect, {'DiffuseMap', 'CutMaskMap'})
                CopyParameters(mesh.effect, newEffect, {'TransformUV0', 'MaterialDiffuseColor', 'CutMaskInfluence'})
                mesh.depthEffect = newEffect
                mesh.depthNormalEffect = None
                isTr2Effect = hasattr(mesh.effect, 'effectFilePath')
                effectIsHairEffect = False
                if isTr2Effect:
                    effectIsHairEffect = 'hair' in mesh.effect.effectFilePath.lower()
                if isTr2Effect and not effectIsHairEffect:
                    newEffect = trinity.Tr2ShaderMaterial()
                    newEffect.highLevelShaderName = 'NormalDepth'
                    newEffect.defaultSituation = 'Cloth'
                    if doll.useDXT5N:
                        newEffect.defaultSituation = newEffect.defaultSituation + ' OPT_USE_DXT5N'
                    CopyResources(mesh.effect, newEffect, {'NormalMap',
                     'SpecularMap',
                     'DiffuseMap',
                     'CutMaskMap'})
                    CopyParameters(mesh.effect, newEffect, {'TransformUV0',
                     'MaterialSpecularCurve',
                     'MaterialLibraryID',
                     'MaterialDiffuseColor',
                     'CutMaskInfluence'})
                    mesh.depthNormalEffect = newEffect
                if isTr2Effect:
                    reversedIsTr2Effect = hasattr(mesh.effectReversed, 'effectFilePath')
                    reversedEffectIsHair = False
                    if reversedIsTr2Effect:
                        reversedEffectIsHair = 'hair' in mesh.effectReversed.effectFilePath.lower()
                    if effectIsHairEffect:
                        newMaterial = CopyHairShader(mesh.effect)
                        newMaterial.name = mesh.effect.name
                        newMaterial.defaultSituation += ' Cloth'
                        newMaterial.defaultSituation += ' Detailed'
                        if doll.useDXT5N:
                            newMaterial.defaultSituation += ' OPT_USE_DXT5N'
                        if not doll.usePrepassAlphaTestHair:
                            mesh.useTransparentBatches = True
                            mesh.useSHLighting = True
                            mesh.depthNormalEffect = None
                            mesh.depthNormalEffectReversed = None
                            if reversedIsTr2Effect and reversedEffectIsHair:
                                newMaterial = CopyHairShader(mesh.effectReversed)
                                newMaterial.name = mesh.effectReversed.name
                                newMaterial.defaultSituation += ' Cloth'
                                newMaterial.defaultSituation += ' Detailed'
                                if doll.useDXT5N:
                                    newMaterial.defaultSituation += ' OPT_USE_DXT5N'
                                mesh.effectReversed = newMaterial
                                mesh.useTransparentBatches = True
                                mesh.useSHLighting = True
                        else:
                            mesh.useTransparentBatches = False
                            mesh.useSHLighting = False
                            mesh.effectReversed = None
                            mesh.depthNormalEffectReversed = None
                            depthNormalMaterial = CopyHairShaderDepthNormal(mesh.effect)
                            depthNormalMaterial.name = mesh.effect.name
                            depthNormalMaterial.defaultSituation += ' Cloth'
                            mesh.depthNormalEffect = depthNormalMaterial
                        mesh.effect = newMaterial
                    else:
                        situation = 'Prepass Cloth'
                        if doll.useDXT5N:
                            situation = situation + ' OPT_USE_DXT5N'
                        newMaterial = ConvertEffectToTr2ShaderMaterial(mesh.effect, situation, mesh.name)
                        newMaterial.name = mesh.effect.name
                        mesh.effect = newMaterial
                        if reversedIsTr2Effect and not reversedEffectIsHair:
                            newMaterial = ConvertEffectToTr2ShaderMaterial(mesh.effectReversed, situation, mesh.name)
                            newMaterial.name = mesh.effectReversed.name
                            mesh.effectReversed = newMaterial
                elif mesh.effect.highLevelShaderName == 'Hair':
                    if not doll.usePrepassAlphaTestHair:
                        mesh.depthNormalEffect = None
                        mesh.useTransparentBatches = True
                        mesh.useSHLighting = True
                        mesh.depthNormalEffect = None
                        mesh.depthNormalEffectReversed = None
                        mesh.effectReversed = mesh.effect.CopyTo()
                    else:
                        mesh.useTransparentBatches = False
                        mesh.useSHLighting = False
                        mesh.effectReversed = None
                        mesh.depthNormalEffectReversed = None
                        depthNormalMaterial = trinity.Tr2ShaderMaterial()
                        depthNormalMaterial.highLevelShaderName = 'NormalDepth'
                        depthNormalMaterial.defaultSituation = 'AlphaCutout TwoSided ' + mesh.effect.defaultSituation
                        for p in mesh.effect.parameters:
                            param = mesh.effect.parameters[p]
                            if type(param) == trinity.TriTextureParameter:
                                newParameter = CopyResource(param)
                            else:
                                newParameter = type(param)()
                                newParameter.name = param.name
                                newParameter.value = param.value
                            depthNormalMaterial.parameters[param.name] = newParameter

                        param = trinity.Tr2FloatParameter()
                        param.name = 'MaterialLibraryID'
                        param.value = 75
                        depthNormalMaterial.parameters['MaterialLibraryID'] = param
                        param = trinity.Tr2FloatParameter()
                        param.name = 'AlphaTestValue'
                        param.value = 0.0235
                        depthNormalMaterial.parameters['AlphaTestValue'] = param
                        depthNormalMaterial.name = mesh.effect.name
                        depthNormalMaterial.defaultSituation += ' Cloth'
                        mesh.depthNormalEffect = depthNormalMaterial

    avatar.BindLowLevelShaders()


exports = {'paperDoll.prePassFixup.AddPrepassAreasToAvatar': AddPrepassAreasToAvatar,
 'paperDoll.prePassFixup.AddDepthNormalAreasToStandardMesh': AddDepthNormalAreasToStandardMesh,
 'paperDoll.prePassFixup.MATERIAL_ID_EXACT': MATERIAL_ID_EXACT,
 'paperDoll.prePassFixup.MATERIAL_ID_TRANSPARENT_HACK_EXACT': MATERIAL_ID_TRANSPARENT_HACK_EXACT,
 'paperDoll.prePassFixup.FindMaterialID': FindMaterialID}
