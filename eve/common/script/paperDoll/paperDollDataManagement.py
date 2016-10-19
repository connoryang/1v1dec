#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\common\script\paperDoll\paperDollDataManagement.py
import os
import uthread
import copy
import types
import hashlib
import blue
import eve.common.script.paperDoll.paperDollDefinitions as pdDef
import eve.common.script.paperDoll.paperDollCommonFunctions as pdCF
from eve.common.script.paperDoll.paperDollResData import ResData, GenderData
import telemetry
import log
import sys
import legacy_r_drive
from .yamlPreloader import YamlPreloader, LoadYamlFileNicely
from .paperDollConfiguration import PerformanceOptions
from .yamlPreloader import AvatarPartMetaData

def ClearAllCachedMaps():
    cachePath = GetMapCachePath()
    fileSystemPath = blue.rot.PathToFilename(cachePath)
    for root, dirs, files in os.walk(fileSystemPath):
        for f in iter(files):
            os.remove(os.path.join(root, f))


def GetMapCachePath():
    avatarCachePath = u''
    try:
        userCacheFolder = blue.paths.ResolvePath(u'cache:')
        avatarCachePath = u'{0}/{1}'.format(userCacheFolder, u'Avatars/cachedMaps')
    except Exception:
        avatarCachePath = u''
        sys.exc_clear()

    return avatarCachePath


def GetCacheFilePath(cachePath, hashKey, textureWidth, mapType):
    cacheFilePath = u''
    try:
        hashKey = str(hashKey).replace('-', '_')
        cacheFilePath = u'{0}/{1}/{2}{3}.dds'.format(cachePath, textureWidth, mapType, hashKey)
    except Exception:
        cacheFilePath = u''
        sys.exc_clear()

    return cacheFilePath


def FindCachedMap(hashKey, textureWidth, mapType):
    cachePath = GetMapCachePath()
    try:
        if cachePath:
            filePath = GetCacheFilePath(cachePath, hashKey, textureWidth, mapType)
            if filePath:
                if blue.paths.exists(filePath):
                    rotPath = blue.rot.FilenameToPath(filePath)
                    os.utime(filePath, None)
                    cachedTexture = blue.resMan.GetResourceW(rotPath)
                    return cachedTexture
    except Exception:
        sys.exc_clear()


def SaveMapsToDisk(hashKey, maps):
    cachePath = GetMapCachePath()
    if not cachePath:
        return
    for i, each in enumerate(maps):
        if each is not None:
            textureWidth = each.width
            filePath = GetCacheFilePath(cachePath, hashKey, textureWidth, i)
            if filePath:
                folder = os.path.split(filePath)[0]
                try:
                    if not os.path.exists(folder):
                        os.makedirs(folder)
                    each.Save(filePath)
                    each.WaitForSave()
                except OSError:
                    pass


class ModifierLoader():
    __guid__ = 'paperDoll.ModifierLoader'
    __sharedLoadSource = False
    __sharedResData = None
    __isLoaded = False

    def setclothSimulationActive(self, value):
        self._clothSimulationActive = value

    clothSimulationActive = property(fget=lambda self: self._clothSimulationActive, fset=lambda self, value: self.setclothSimulationActive(value))

    def __init__(self):
        self.yamlPreloader = YamlPreloader()
        self.resData = None
        self.patterns = []
        self.IsLoaded = False
        self.forceRunTimeOptionGeneration = False
        self._clothSimulationActive = False
        uthread.new(self.LoadData_t)

    def DebugReload(self, forceRunTime = False):
        self.forceRunTimeOptionGeneration = forceRunTime
        ModifierLoader.__sharedLoadSource = False
        ModifierLoader.__sharedResData = None
        ModifierLoader.__isLoaded = False
        YamlPreloader.Clear()
        uthread.new(self.LoadData_t)

    @staticmethod
    @telemetry.ZONE_FUNCTION
    def LoadBlendshapeLimits(limitsResPath):
        data = LoadYamlFileNicely(limitsResPath)
        if data is not None:
            limits = data.get('limits')
            ret = {}
            if limits and type(limits) is dict:
                for k, v in limits.iteritems():
                    ret[k.lower()] = v

                data['limits'] = ret
        return data

    @telemetry.ZONE_METHOD
    def GetWorkingDirectory(self, gender):
        if gender == pdDef.GENDER.FEMALE:
            return pdDef.FEMALE_BASE_PATH
        else:
            return pdDef.MALE_BASE_PATH

    @telemetry.ZONE_METHOD
    def LoadData_t(self):
        try:
            if ModifierLoader.__sharedLoadSource == legacy_r_drive.loadFromContent and ModifierLoader.__sharedResData:
                self.resData = ModifierLoader.__sharedResData
                while not ModifierLoader.__isLoaded:
                    pdCF.Yield()

                self.IsLoaded = True
                return
            self.resData = ResData()
            femPath = pdDef.FEMALE_BASE_PATH
            femPathLOD = pdDef.FEMALE_BASE_LOD_PATH
            femPathGT = pdDef.FEMALE_BASE_GRAPHICS_TEST_PATH
            femPathGTLOD = pdDef.FEMALE_BASE_GRAPHICS_TEST_LOD_PATH
            malePath = pdDef.MALE_BASE_PATH
            malePathLOD = pdDef.MALE_BASE_LOD_PATH
            malePathGT = pdDef.MALE_BASE_GRAPHICS_TEST_PATH
            malePathGTLOD = pdDef.MALE_BASE_GRAPHICS_TEST_LOD_PATH
            if legacy_r_drive.loadFromContent:
                femPath = femPath.replace('res:', 'resPreview:')
                femPathLOD = femPathLOD.replace('res:', 'resPreview:')
                femPathGT = femPathGT.replace('res:', 'resPreview:')
                femPathGTLOD = femPathGTLOD.replace('res:', 'resPreview:')
                malePath = malePath.replace('res:', 'resPreview:')
                malePathLOD = malePathLOD.replace('res:', 'resPreview:')
                malePathGT = malePathGT.replace('res:', 'resPreview:')
                malePathGTLOD = malePathGTLOD.replace('res:', 'resPreview:')
            self.resData.Populate(pdDef.GENDER.FEMALE, femPath)
            self.resData.Populate(pdDef.GENDER.FEMALE, femPathLOD, key=GenderData.LOD_KEY)
            self.resData.Populate(pdDef.GENDER.FEMALE, femPathGT, key=GenderData.TEST_KEY)
            self.resData.Populate(pdDef.GENDER.FEMALE, femPathGTLOD, key=GenderData.TEST_LOD_KEY)
            self.resData.Populate(pdDef.GENDER.MALE, malePath)
            self.resData.Populate(pdDef.GENDER.MALE, malePathLOD, key=GenderData.LOD_KEY)
            self.resData.Populate(pdDef.GENDER.MALE, malePathGT, key=GenderData.TEST_KEY)
            self.resData.Populate(pdDef.GENDER.MALE, malePathGTLOD, key=GenderData.TEST_LOD_KEY)
            while self.resData.IsLoading():
                pdCF.Yield()

            PerformanceOptions.SetEnableYamlCache(True)
            while self.yamlPreloader.IsLoading():
                pdCF.Yield()

            for gender in pdDef.GENDER:
                self.resData.PopulateVirtualModifierFolders(gender)

            self.resData.LinkSiblings(None, GenderData.LOD_KEY)
            self.resData.LinkSiblings(GenderData.TEST_KEY, GenderData.TEST_LOD_KEY)
            self.resData.PropogateLODRules()
            self._LoadPatterns()
            self.IsLoaded = True
        finally:
            ModifierLoader.__sharedLoadSource = legacy_r_drive.loadFromContent
            ModifierLoader.__sharedResData = self.resData
            ModifierLoader.__isLoaded = self.IsLoaded

    @telemetry.ZONE_METHOD
    def WaitUntilLoaded(self):
        while not self.IsLoaded:
            pdCF.Yield()

    @telemetry.ZONE_METHOD
    def _LoadPatterns(self):
        if legacy_r_drive.loadFromContent:
            self.patterns = pdDef.GetPatternList()
        else:
            if pdDef.GENDER_ROOT:
                optionsFile = 'res:/{0}/Character/PatternOptions.yaml'.format(pdDef.BASE_GRAPHICS_FOLDER)
            else:
                optionsFile = 'res:/{0}/Character/Modular/PatternOptions.yaml'.format(pdDef.BASE_GRAPHICS_FOLDER)
            self.patterns = LoadYamlFileNicely(optionsFile)

    def GetPatternDir(self):
        return 'res:/{0}/Character/Patterns'.format(pdDef.BASE_GRAPHICS_FOLDER)

    @telemetry.ZONE_METHOD
    def GetItemType(self, itemTypePath, gender = None):
        if gender and 'res:' not in itemTypePath:
            basePath = ''
            if gender == pdDef.GENDER.MALE:
                basePath = pdDef.MALE_BASE_PATH
            elif gender == pdDef.GENDER.FEMALE:
                basePath = pdDef.FEMALE_BASE_PATH
            if itemTypePath.startswith('/'):
                fmt = '{0}{1}'
            else:
                fmt = '{0}/{1}'
            itemTypePath = fmt.format(basePath, itemTypePath)
        itemType = self.__GetFromYamlCache(itemTypePath)
        return itemType

    def ListTypes(self, gender, cat = None, modifier = None):
        availableTypes = []
        if modifier:
            parentEntry = self.resData.GetEntryByPath(gender, modifier.respath)
            entries = self.resData.GetChildEntries(parentEntry)
        elif cat:
            parentEntry = self.resData.GetEntryByPath(gender, cat)
            entries = self.resData.Traverse(parentEntry, visitFunc=lambda x: not x.dirs)
        else:
            entries = [ entry for entry in self.resData.GetEntriesByGender(gender) if not entry.dirs ]
        for entry in entries:
            fileNames = entry.GetFilesByExt('type')
            for fn in fileNames:
                fullResPath = entry.GetFullResPath(fn)
                availableTypes.append(fullResPath)

        log.LogNotice('paperdollDataMgmt: List types -> (%s, %s, %s, %s)' % (gender,
         cat,
         modifier,
         len(availableTypes)))
        return availableTypes

    def CategoryHasTypes(self, category):

        def Visit(gender, resDataEntry):
            if not resDataEntry:
                return False
            found = False
            if 'types' in resDataEntry.dirs:
                found = True
            if not found:
                for childResDataEntry in self.resData.GetChildEntries(resDataEntry):
                    found = Visit(gender, childResDataEntry)
                    if found:
                        break

            return found

        def CheckTypes(gender):
            entry = self.resData.GetEntryByPath(gender, category)
            return Visit(gender, entry)

        return any(map(lambda x: CheckTypes(x), pdDef.GENDER))

    @telemetry.ZONE_METHOD
    def ListOptions(self, gender, cat = None, showVariations = False):
        results = []
        entries = []
        if cat:
            pathEntry = self.resData.GetEntryByPath(gender, cat)
            if pathEntry:
                entries.extend(self.resData.GetChildEntries(pathEntry))
            pathEntry = self.resData.GetEntryByPath(gender, cat, key=GenderData.TEST_KEY)
            if pathEntry:
                entries.extend(self.resData.GetChildEntries(pathEntry, key=GenderData.TEST_KEY))
            if showVariations:
                for entry in entries:
                    variations = []
                    for childEntry in self.resData.GetChildEntries(entry):
                        if childEntry.isVariationFolder:
                            variations.append(childEntry.leafFolderName)

                    result = (entry.leafFolderName, tuple(variations))
                    results.append(result)

            else:
                for entry in entries:
                    results.append(entry.leafFolderName)

        else:
            results.extend(self.resData.GetPathToEntryByGender(gender).keys())
            results.extend(self.resData.GetPathToEntryByGender(gender, key=GenderData.TEST_KEY).keys())
        results.sort()
        return results

    @telemetry.ZONE_METHOD
    def CollectBuildData(self, gender, path, weight = 1.0, forceLoaded = False):
        currentBuildData = BuildData(path)
        currentBuildData.weight = weight
        self.LoadResource(gender, path, currentBuildData, forceLoaded=forceLoaded)
        return currentBuildData

    @telemetry.ZONE_METHOD
    def LoadResource(self, gender, path, modifier, forceLoaded = False):
        if not self.resData.QueryPathByGender(gender, path):
            log.LogWarn('PaperDoll - Path {0} for gender {1} does not exist that is passed to ModifierLoader::LoadResource!'.format(path, gender))
            return
        if not forceLoaded:
            while not self.IsLoaded:
                pdCF.BeFrameNice()

        resDataEntry = self.resData.GetEntryByPath(gender, path)
        modifier.lodCutoff = resDataEntry.lodCutoff or modifier.lodCutoff
        self._GetFilesForEntry(resDataEntry, modifier)
        parentEntry = self.resData.GetParentEntry(resDataEntry)
        if 'colors' in parentEntry.dirs:
            colorEntry = self.resData.GetEntryByPath(gender, parentEntry.GetResPath('colors'))
            self._PopulateMetaData(modifier, colorEntry)
        matchingVariationEntries = (entry for entry in self.resData.GetChildEntries(resDataEntry) if entry.isVariationFolder)
        for variationResDataEntry in iter(matchingVariationEntries):
            variationModifier = BuildData()
            self._GetFilesForEntry(variationResDataEntry, variationModifier)
            modifier.variations[variationResDataEntry.leafFolderName] = variationModifier

        if len(modifier.variations):
            original = copy.deepcopy(modifier)
            original.variations = {}
            modifier.variations['v0'] = original
        if 'default' in modifier.colorVariations:
            modifier.SetColorVariation('default')
        if modifier.metaData.alternativeTextureSourcePath:
            path = modifier.metaData.alternativeTextureSourcePath.lower()
            altEntry = self.resData.GetEntryByPath(gender, path)
            self._GetFilesForEntry(altEntry, modifier, sourceMapsOnly=True)

    @telemetry.ZONE_METHOD
    def __GetFromYamlCache(self, key):
        inst = self.yamlPreloader.LoadYaml(key)
        return inst

    @telemetry.ZONE_METHOD
    def _PartFromPath(self, path, reverseLookupData = None, rvPart = None):
        for part in pdDef.DOLL_PARTS:
            if part in path:
                return part

        if '_acc_' in path:
            return pdDef.DOLL_PARTS.ACCESSORIES
        if reverseLookupData:
            for part in iter(reverseLookupData):
                if part in path:
                    return rvPart

        return ''

    @telemetry.ZONE_METHOD
    def _PopulateSourceMaps(self, modifier, resDataEntry):
        files = resDataEntry.sourceMaps.keys()
        for f in files:
            partType = self._PartFromPath(f) or self._PartFromPath(resDataEntry.respath, pdDef.BODY_CATEGORIES, pdDef.DOLL_PARTS.BODY)
            if pdDef.MAP_PREFIX_COLORIZE in f:
                modifier.colorize = True
            if pdDef.MAP_SUFFIX_DRGB in f:
                modifier.mapDRGB[partType] = resDataEntry.GetFullResPath(f)
            elif pdDef.MAP_SUFFIX_LRGB in f:
                modifier.mapLRGB[partType] = resDataEntry.GetFullResPath(f)
            elif pdDef.MAP_SUFFIX_LA in f:
                modifier.mapLA[partType] = resDataEntry.GetFullResPath(f)
            elif pdDef.MAP_SUFFIX_DA in f:
                modifier.mapDA[partType] = resDataEntry.GetFullResPath(f)
            elif pdDef.MAP_SUFFIX_L in f:
                modifier.mapL[partType] = resDataEntry.GetFullResPath(f)
            elif pdDef.MAP_SUFFIX_Z in f:
                modifier.mapZ[partType] = resDataEntry.GetFullResPath(f)
            elif pdDef.MAP_SUFFIX_O in f:
                modifier.mapO[partType] = resDataEntry.GetFullResPath(f)
            elif pdDef.MAP_SUFFIX_D in f:
                modifier.mapD[partType] = resDataEntry.GetFullResPath(f)
            elif pdDef.MAP_SUFFIX_N in f:
                modifier.mapN[partType] = resDataEntry.GetFullResPath(f)
            elif pdDef.MAP_SUFFIX_MN in f:
                modifier.mapMN[partType] = resDataEntry.GetFullResPath(f)
            elif pdDef.MAP_SUFFIX_TN in f:
                modifier.mapTN[partType] = resDataEntry.GetFullResPath(f)
            elif pdDef.MAP_SUFFIX_S in f:
                modifier.mapSRG[partType] = resDataEntry.GetFullResPath(f)
            elif pdDef.MAP_SUFFIX_AO in f:
                modifier.mapAO[partType] = resDataEntry.GetFullResPath(f)
            elif pdDef.MAP_SUFFIX_MM in f:
                modifier.mapMaterial[partType] = resDataEntry.GetFullResPath(f)
            elif pdDef.MAP_SUFFIX_MASK in f or pdDef.MAP_SUFFIX_M in f:
                modifier.mapMask[partType] = resDataEntry.GetFullResPath(f)
                modifier.mapAO[partType] = resDataEntry.GetFullResPath(f)

    @telemetry.ZONE_METHOD
    def _PopulateGeometry(self, modifier, resDataEntry):
        modifier.clothPath = resDataEntry.redFiles.get(pdDef.CLOTH_PATH, '')
        modifier.clothOverride = resDataEntry.redFiles.get(pdDef.CLOTH_OVERRIDE, '')
        modifier.stubblePath = resDataEntry.redFiles.get(pdDef.STUBBLE_PATH, '')
        if modifier.stubblePath:
            modifier.colorize = True
        modifier.shaderPath = resDataEntry.redFiles.get(pdDef.SHADER_PATH, '')
        modifier.redfile = resDataEntry.redFiles.get(pdDef.RED_FILE, '')

    @telemetry.ZONE_METHOD
    def _PopulateMetaData(self, modifier, resDataEntry):
        metaDataFn = 'metadata.yaml'
        if metaDataFn in resDataEntry.files:
            resPath = resDataEntry.GetFullResPath(metaDataFn)
            inst = self.__GetFromYamlCache(resPath)
            if inst:
                inst.defaultMetaData = False
                modifier.metaData = inst
        files = resDataEntry.GetFilesByExt('pose')
        if files:
            resPath = resDataEntry.GetFullResPath(files[0])
            inst = self.__GetFromYamlCache(resPath)
            modifier.poseData = inst
        files = resDataEntry.GetFilesByExt('color')
        for f in files:
            resPath = resDataEntry.GetFullResPath(f)
            inst = self.__GetFromYamlCache(resPath)
            varName = f.split('.')[0]
            modifier.colorVariations[varName] = inst

        files = resDataEntry.GetFilesByExt('proj')
        if files:
            resPath = resDataEntry.GetFullResPath(files[0])
            inst = self.__GetFromYamlCache(resPath)
            if inst:
                inst.SetTexturePath(inst.texturePath)
                inst.SetMaskPath(inst.maskPath)
                modifier.decalData = inst

    @telemetry.ZONE_METHOD
    def _GetFilesForEntry(self, resDataEntry, modifier, sourceMapsOnly = False):
        if resDataEntry:
            self._PopulateSourceMaps(modifier, resDataEntry)
            dimExt = [ ext for ext in resDataEntry.extToFiles.keys() if ext.isdigit() ]
            if dimExt:
                dimFn = resDataEntry.extToFiles[dimExt[0]][0]
                modifier.accessoryMapSize = [ int(x) for x in dimFn.split('.')[-2:] ]
            if not sourceMapsOnly:
                self._PopulateGeometry(modifier, resDataEntry)
                self._PopulateMetaData(modifier, resDataEntry)
        return modifier


class BuildDataMaps(object):

    def __init__(self):
        self._isTextureContainingModifier = None
        self._contributesToMapTypes = None
        self._affectedTextureParts = None
        self.mapN = {}
        self.mapMN = {}
        self.mapTN = {}
        self.mapSRG = {}
        self.mapAO = {}
        self.mapMaterial = {}
        self.mapMask = {}
        self.mapD = {}
        self.mapDRGB = {}
        self.mapDA = {}
        self.mapLRGB = {}
        self.mapLA = {}
        self.mapL = {}
        self.mapZ = {}
        self.mapO = {}

    def IsTextureContainingModifier(self):
        if self._isTextureContainingModifier is None:
            self._isTextureContainingModifier = False
            for each in self.__dict__.iterkeys():
                if each.startswith('map'):
                    if self.__dict__[each]:
                        self._isTextureContainingModifier = True
                        break

        return self._isTextureContainingModifier

    def ContributesToMapTypes(self):
        if self._contributesToMapTypes is None:
            mapTypes = list()
            if len(self.mapD.keys()) > 0 or len(self.mapL.keys()) > 0 or len(self.mapZ.keys()) > 0 or len(self.mapO.keys()) > 0:
                mapTypes.append(pdDef.DIFFUSE_MAP)
            if len(self.mapSRG.keys()) > 0 or len(self.mapAO.keys()) > 0 or len(self.mapMaterial.keys()) > 0:
                mapTypes.append(pdDef.SPECULAR_MAP)
            if len(self.mapN.keys()) > 0 or len(self.mapMN.keys()) > 0 or len(self.mapTN.keys()) > 0:
                mapTypes.append(pdDef.NORMAL_MAP)
            if len(self.mapMask.keys()) > 0:
                mapTypes.append(pdDef.MASK_MAP)
            self._contributesToMapTypes = mapTypes
        return self._contributesToMapTypes

    def GetAffectedTextureParts(self):
        if self._affectedTextureParts is None:
            parts = set()
            for each in self.__dict__.iterkeys():
                if each.startswith('map'):
                    parts.update(self.__dict__[each].keys())

            self._affectedTextureParts = parts
        return self._affectedTextureParts


class BuildData(BuildDataMaps):
    __metaclass__ = telemetry.ZONE_PER_METHOD
    __guid__ = 'paperDoll.BuildData'
    DEFAULT_COLORIZEDATA = [pdDef.MID_GRAY] * 3
    DEFAULT_PATTERNDATA = [pdDef.DARK_GRAY,
     pdDef.LIGHT_GRAY,
     pdDef.MID_GRAY,
     pdDef.MID_GRAY,
     pdDef.MID_GRAY,
     (0, 0, 8, 8),
     0.0]
    DEFAULT_SPECULARCOLORDATA = [pdDef.MID_GRAY] * 3

    def __del__(self):
        self.ClearCachedData()

    def __init__(self, pathName = None, name = None, categorie = None):
        BuildDataMaps.__init__(self)
        self.name = ''
        self.categorie = categorie.lower() if categorie else ''
        extPath = None
        splits = None
        if pathName is not None:
            pathName = pathName.lower()
            splits = pathName.split(pdDef.SEPERATOR_CHAR)
            extPath = str(pdDef.SEPERATOR_CHAR.join(splits[1:]))
            self.categorie = str(splits[0])
        self.lodCutoff = pdDef.LOD_99
        self.lodCutin = -pdDef.LOD_99
        self.name = name.lower() if name else extPath
        if self.categorie and self.name:
            self.respath = '{0}/{1}'.format(self.categorie, self.name)
        else:
            self.respath = ''
        if splits and len(splits) > 2:
            self.group = splits[1]
        else:
            self.group = ''
        self.usingMaskedShader = False
        self.redfile = ''
        self.clothPath = ''
        self.clothOverride = ''
        self.meshes = []
        self.__cmpMeshes = []
        self.meshGeometryResPaths = {}
        self.dependantModifiers = {}
        self.__clothData = None
        self.__clothDirty = False
        self.stubblePath = ''
        self.shaderPath = ''
        self.drapePath = ''
        self.accessoryMapSize = None
        self.decalData = None
        self.colorize = False
        self._colorizeData = list(BuildData.DEFAULT_COLORIZEDATA)
        self.__cmpColorizeData = []
        self.__pattern = ''
        self.patternData = list(BuildData.DEFAULT_PATTERNDATA)
        self.__cmpPatternData = []
        self.specularColorData = list(BuildData.DEFAULT_SPECULARCOLORDATA)
        self.__cmpSpecularColorData = []
        self.colorVariations = {}
        self.currentColorVariation = ''
        self.variations = {}
        self.variationTextureHash = ''
        self.currentVariation = ''
        self.lastVariation = ''
        self.__weight = 1.0
        self.hasWeightPulse = False
        self.__useSkin = False
        self.metaData = AvatarPartMetaData()
        self.poseData = None
        self.__tuck = True
        self.ulUVs = (pdDef.DEFAULT_UVS[0], pdDef.DEFAULT_UVS[1])
        self.lrUVs = (pdDef.DEFAULT_UVS[2], pdDef.DEFAULT_UVS[3])
        self.__IsHidden = False
        self.WasHidden = False
        self.__IsDirty = True
        self.__hashValue = None

    def HasWeightPulse(self):
        return self.hasWeightPulse

    def IsVisibleAtLOD(self, lod):
        return self.lodCutin <= lod <= self.lodCutoff

    def GetUVsForCompositing(self, bodyPart):
        if bodyPart != pdDef.DOLL_PARTS.ACCESSORIES:
            if bodyPart == pdDef.DOLL_PARTS.BODY:
                UVs = pdDef.BODY_UVS
            elif bodyPart == pdDef.DOLL_PARTS.HEAD:
                UVs = pdDef.HEAD_UVS
            elif bodyPart == pdDef.DOLL_PARTS.HAIR:
                UVs = pdDef.HAIR_UVS
        else:
            accUVs = pdDef.ACCE_UVS
            width = accUVs[2] - accUVs[0]
            height = accUVs[3] - accUVs[1]
            UVs = list((accUVs[0] + self.ulUVs[0] * width, accUVs[1] + self.ulUVs[1] * height) + (accUVs[0] + self.lrUVs[0] * width, accUVs[1] + self.lrUVs[1] * height))
        return UVs

    def SetColorizeData(self, *args):
        x = args
        depth = 0
        while len(x) == 1 and type(x[0]) in (tuple, list) and depth < 5:
            x = x[0]
            depth += 1

        didChange = False
        for i in xrange(len(x)):
            if len(x) > i and type(x[i]) in (tuple, list):
                if self._colorizeData[i] != tuple(x[i]):
                    self._colorizeData[i] = tuple(x[i])
                    didChange = True

        if didChange:
            self.IsDirty = True

    def GetColorizeData(self):
        return self._colorizeData

    def GetColorVariations(self):
        return self.colorVariations.keys()

    def SetColorVariation(self, variationName):
        if variationName == 'none':
            self.currentColorVariation = 'none'
            return
        if not self.currentColorVariation == 'none' and self.colorVariations and variationName in self.colorVariations:
            currentColorVariation = self.colorVariations[variationName]
            if not currentColorVariation:
                return
            if 'colors' in currentColorVariation:
                for i in xrange(3):
                    self.colorizeData[i] = currentColorVariation['colors'][i]

            if 'pattern' in currentColorVariation:
                self.pattern = currentColorVariation['pattern']
            if 'patternColors' in currentColorVariation:
                arrayLength = len(currentColorVariation['patternColors'])
                for i in xrange(arrayLength):
                    self.patternData[i] = currentColorVariation['patternColors'][i]

            if 'specularColors' in currentColorVariation:
                for i in xrange(3):
                    self.specularColorData[i] = currentColorVariation['specularColors'][i]

            self.currentColorVariation = str(variationName)

    def SetColorVariationDirectly(self, variation):
        if variation is not None and type(variation) is types.DictionaryType:
            if 'colors' in variation:
                for i in xrange(3):
                    self.colorizeData[i] = variation['colors'][i]

            if 'pattern' in variation:
                self.pattern = variation['pattern']
            if 'patternColors' in variation:
                for i in xrange(5):
                    self.patternData[i] = variation['patternColors'][i]

            if 'specularColors' in variation:
                for i in xrange(3):
                    self.specularColorData[i] = variation['specularColors'][i]

    def SetColorVariationSpecularity(self, specularColor):
        self.specularColorData = specularColor

    def GetColorsFromColorVariation(self, variationName):
        if self.colorVariations and self.colorVariations.get(variationName):
            var = self.colorVariations[variationName]
            if var['pattern'] != '':
                return [var['patternColors'][0], var['patternColors'][3], var['patternColors'][4]]
            else:
                return var['colors']

    def GetVariations(self):
        return self.variations.keys()

    def SetVariation(self, variationName):
        variationName = variationName or 'v0'
        if self.variations and variationName in self.variations:
            oldRedFile = self.redfile
            oldClothPath = self.clothPath
            var = self.variations[variationName]
            doNotCopy = ['respath', 'dependantModifiers']
            for member in var.__dict__:
                if member not in doNotCopy:
                    if type(var.__dict__[member]) == str and var.__dict__[member]:
                        self.__dict__[member] = var.__dict__[member]
                    if type(var.__dict__[member]) == dict and len(var.__dict__[member]) > 0:
                        for entry in var.__dict__[member]:
                            self.__dict__[member][entry] = var.__dict__[member][entry]
                            if member.startswith('map'):
                                self.variationTextureHash = var.__dict__[member][entry]

                    if member == 'metaData':
                        if var.metaData and not var.metaData.defaultMetaData:
                            self.metaData = var.metaData

            if oldRedFile != self.redfile:
                del self.meshes[:]
                self.meshGeometryResPaths = {}
            if oldClothPath != self.clothPath:
                self.clothData = None
            self.lastVariation = self.currentVariation
            self.currentVariation = str(variationName)

    def GetVariationMetaData(self, variationName = None):
        if variationName == '':
            variationName = 'v0'
        variationName = variationName or self.currentVariation
        variation = self.variations.get(variationName)
        if variation and variation.metaData and not variation.metaData.defaultMetaData:
            return variation.metaData

    def GetDependantModifiersFullData(self, metaDataOverride = None):
        metaData = metaDataOverride or self.metaData
        if metaData.dependantModifiers:
            parsedValues = []
            for each in metaData.dependantModifiers:
                if '#' in each:
                    tmpList = []
                    for elem in each.split('#'):
                        tmpList.append(elem)

                    while len(tmpList) < 3:
                        tmpList.append('')

                    if len(tmpList) < 4:
                        tmpList.append(1.0)
                    else:
                        tmpList[3] = float(tmpList[3])
                    parsedValues.append(tuple(tmpList))
                else:
                    parsedValues.append((each,
                     '',
                     '',
                     1.0))

            return parsedValues

    def GetDependantModifierResPaths(self):
        if self.metaData.dependantModifiers:
            resPaths = []
            for resPath in self.metaData.dependantModifiers:
                if '#' in resPath:
                    resPaths.append(resPath.split('#')[0])
                else:
                    resPaths.append(resPath)

            return resPaths

    def GetOccludedModifiersFullData(self, metaDataOverride = None):
        if metaDataOverride:
            metaData = metaDataOverride
        else:
            metaData = self.metaData
        if metaData.occludesModifiers:
            parsedValues = []
            for each in metaData.occludesModifiers:
                if '#' in each:
                    tmpList = []
                    for elem in each.split('#'):
                        tmpList.append(elem)

                    if len(tmpList) < 2:
                        tmpList.append(1.0)
                    else:
                        tmpList[1] = float(tmpList[1])
                    tmpList[0] = tmpList[0].lower()
                    parsedValues.append(tuple(tmpList))
                else:
                    parsedValues.append((each.lower(), 1.0))

            return parsedValues

    def GetDependantModifiers(self):
        return self.dependantModifiers.values()

    def AddDependantModifier(self, modifier):
        if self.respath == modifier.respath:
            raise AttributeError('paperDoll:BuildData:AddDependantModifier - Trying to add modifier as dependant of itself!')
        self.dependantModifiers[modifier.respath] = modifier

    def RemoveDependantModifier(self, modifier):
        if modifier.respath in self.dependantModifiers:
            del self.dependantModifiers[modifier.respath]

    def GetMeshSourcePaths(self):
        return [self.clothPath, self.redfile]

    def IsMeshDirty(self):
        return self.__clothDirty or self.clothPath and not self.clothData or self.__cmpMeshes != self.meshes or any(map(lambda mesh: not (mesh.geometry and mesh.geometry.isGood), self.meshes))

    def IsMeshContainingModifier(self):
        return any((self.meshes,
         self.clothData,
         self.clothPath,
         self.redfile))

    def IsBlendshapeModifier(self):
        return self.categorie in pdDef.BLENDSHAPE_CATEGORIES

    def __repr__(self):
        s = 'BuildData instance, ID%s\n' % id(self)
        s = s + 'Name: [%s]\t Category: [%s]\t RedFile: [%s]\n' % (self.name, self.categorie, self.redfile)
        s = s + 'Dirty: [%s]\t Hidden: [%s]\t Respath: [%s]\t' % (self.IsDirty, self.IsHidden, self.GetResPath())
        return s

    def __hash__(self):
        return id(self)

    def getIsDirty(self):
        if self.__IsDirty:
            return True
        if self.lastVariation != self.currentVariation:
            return True
        if self.__cmpPatternData != self.patternData:
            return True
        if self.__cmpColorizeData != self._colorizeData:
            return True
        if self.__cmpSpecularColorData != self.specularColorData:
            return True
        if self.__cmpMeshes != self.meshes:
            return True
        if self.__cmpDecalData != self.decalData:
            return True
        return False

    def setIsDirty(self, value):
        if value == False:
            self.__cmpColorizeData = list(self._colorizeData)
            self.__cmpSpecularColorData = list(self.specularColorData)
            self.__cmpPatternData = list(self.patternData)
            self.__cmpMeshes = list(self.meshes)
            if self.decalData is not None:
                self.__cmpDecalData = copy.deepcopy(self.decalData)
            else:
                self.__cmpDecalData = None
            self.lastVariation = self.currentVariation
            self.WasHidden = False
            self.WasShown = False
            self.__clothDirty = False
        else:
            self.__hashValue = None
            self._isTextureContainingModifier = None
            self._contributesToMapTypes = None
            self._affectedTextureParts = None
        self.__IsDirty = value

    IsDirty = property(fget=getIsDirty, fset=setIsDirty)

    def dirtDeco(fun):

        def new(*args):
            args[0].__IsDirty = True
            return fun(*args)

        return new

    colorizeData = property(fset=SetColorizeData, fget=GetColorizeData)

    @dirtDeco
    def setisHidden(self, value):
        self.WasShown = value and not self.__IsHidden
        self.WasHidden = not value and self.__IsHidden
        self.__IsHidden = value

    IsHidden = property(fget=lambda self: self.__IsHidden, fset=setisHidden)

    @property
    def clothData(self):
        return self.__clothData

    @clothData.setter
    def clothData(self, value):
        self.__clothDirty = True
        self.__clothData = value

    @dirtDeco
    def settuck(self, value):
        self.__tuck = value

    tuck = property(fget=lambda self: self.__tuck, fset=settuck)

    @dirtDeco
    def setpattern(self, value):
        self.__pattern = value

    pattern = property(fget=lambda self: self.__pattern, fset=setpattern)

    def setweight(self, value):
        if self.__weight == value:
            return
        if value > 0 and self.__weight <= 0:
            self.hasWeightPulse = True
        elif self.__weight > 0 and value <= 0:
            self.hasWeightPulse = True
        self.__weight = value
        self.__IsDirty = True

    weight = property(fget=lambda self: self.__weight, fset=setweight)

    @dirtDeco
    def setuseSkin(self, value):
        self.__useSkin = value

    useSkin = property(fget=lambda self: self.__useSkin, fset=setuseSkin)

    def GetTypeData(self):
        return (self.respath, self.currentVariation, self.currentColorVariation)

    def ClearCachedData(self):
        del self.meshes[:]
        del self.__cmpMeshes[:]
        self.clothData = None
        self.meshGeometryResPaths = {}

    def GetResPath(self):
        return self.respath

    def GetFootPrint(self, preserveTypes = False, occlusionWeight = None):
        colorsOutput = self.colorizeData if preserveTypes else str(self.colorizeData)
        colorsSource = self.colorizeData
        if self.pattern:
            colorsOutput = self.patternData if preserveTypes else str(self.patternData)
            colorsSource = self.patternData
        data = {}
        data[pdDef.DNA_STRINGS.PATH] = self.GetResPath()
        serializationWeight = self.weight if not occlusionWeight else self.weight + occlusionWeight
        data[pdDef.DNA_STRINGS.WEIGHT] = serializationWeight
        data[pdDef.DNA_STRINGS.CATEGORY] = self.categorie
        if colorsSource != BuildData.DEFAULT_COLORIZEDATA:
            data[pdDef.DNA_STRINGS.COLORS] = colorsOutput
        if self.specularColorData != BuildData.DEFAULT_SPECULARCOLORDATA:
            data[pdDef.DNA_STRINGS.SPECULARCOLORS] = self.specularColorData
        if self.pattern:
            data[pdDef.DNA_STRINGS.PATTERN] = self.pattern
        if self.decalData:
            data[pdDef.DNA_STRINGS.DECALDATA] = self.decalData
        if self.currentColorVariation:
            data[pdDef.DNA_STRINGS.COLORVARIATION] = self.currentColorVariation
        if self.currentVariation:
            data[pdDef.DNA_STRINGS.VARIATION] = self.currentVariation
        return data

    def CompareFootPrint(self, other):
        if isinstance(other, BuildData):
            otherFP = other.GetFootPrint()
        else:
            otherFP = other

        def doCompare(sfp, ofp):
            ret = 1
            for k, v in sfp.iteritems():
                if ofp.get(k) != v:
                    if k != pdDef.DNA_STRINGS.VARIATION:
                        return 0
                    ret = -1

            return ret

        selfFP = self.GetFootPrint(preserveTypes=True)
        cmpResult = doCompare(selfFP, otherFP)
        if cmpResult < 1:
            selfFP = self.GetFootPrint(preserveTypes=False)
            cmpResult = doCompare(selfFP, otherFP)
        return cmpResult

    def Hash(self):
        return hash(self)


class BuildDataManager(object):
    __metaclass__ = telemetry.ZONE_PER_METHOD
    __guid__ = 'paperDoll.BuildDataManager'

    def getmodifiers(self):
        if self.__filterHidden:
            modifiersdata = {}
            for part in self.__modifiers.iterkeys():
                modifiers = [ modifier for modifier in self.__modifiers[part] if not modifier._BuildData__IsHidden ]
                modifiersdata[part] = modifiers

            return modifiersdata
        else:
            return self.__modifiers

    def setmodifiers(self, value):
        raise AttributeError('Cannot directly set modifiers!')

    modifiersdata = property(fget=getmodifiers, fset=setmodifiers)

    def __del__(self):
        del self.__sortedList
        del self.__dirtyModifiersAdded
        del self.__dirtyModifiersRemoved
        del self.__modifiers

    def __init__(self):
        object.__init__(self)
        self.__modifiers = {pdDef.DOLL_PARTS.BODY: [],
         pdDef.DOLL_PARTS.HEAD: [],
         pdDef.DOLL_PARTS.HAIR: [],
         pdDef.DOLL_PARTS.ACCESSORIES: [],
         pdDef.DOLL_EXTRA_PARTS.BODYSHAPES: [],
         pdDef.DOLL_EXTRA_PARTS.UTILITYSHAPES: [],
         pdDef.DOLL_EXTRA_PARTS.UNDEFINED: []}
        self.desiredOrder = pdDef.DESIRED_ORDER[:]
        self.desiredOrderChanged = False
        self.__sortedList = []
        self.__dirty = False
        self.modifierLimits = {}
        self.occludeRules = {}
        self.__dirtyModifiersAdded = []
        self.__dirtyModifiersRemoved = []
        self.currentLOD = pdDef.LOD_0
        self.__locked = False
        self.__pendingModifiersToAdd = []
        self.__pendingModifiersToRemove = []
        self.__filterHidden = True
        self._parentModifiers = {}

    def AddBlendshapeLimitsFromFile(self, resPath):
        data = ModifierLoader.LoadBlendshapeLimits(resPath)
        if data:
            limits = data['limits']
            self.AddModifierLimits(limits)

    def AddModifierLimits(self, modifierLimits):
        self.modifierLimits.update(modifierLimits)

    def ApplyLimitsToModifierWeights(self):
        for modifier in self.GetModifiersAsList(includeFuture=True, showHidden=True):
            limit = self.modifierLimits.get(modifier.name)
            if limit:
                minLimit, maxLimit = limit
                modifier.weight = min(max(minLimit, modifier.weight), maxLimit)

    def GetMorphTargets(self):
        modifierList = self.GetModifiersAsList()
        removedModifiers = list(self.__dirtyModifiersRemoved)
        morphTargets = {}

        def Qualifier(modifier):
            return modifier.IsBlendshapeModifier()

        for modifier in iter(removedModifiers):
            if Qualifier(modifier):
                morphTargets[modifier.name] = 0

        for modifier in iter(modifierList):
            if Qualifier(modifier):
                weight = modifier.weight if modifier.weight < 1.0 else 1.0
                limit = self.modifierLimits.get(modifier.name)
                if limit:
                    minLimit, maxLimit = limit
                    weight = min(max(minLimit, weight), maxLimit)
                morphTargets[modifier.name] = weight

        return morphTargets

    def AddParentModifier(self, modifier, parentModifier):
        parentModifiers = self.GetParentModifiers(modifier)
        if parentModifier not in parentModifiers:
            parentModifiers.append(parentModifier)
        self._parentModifiers[modifier] = parentModifiers

    def GetParentModifiers(self, modifier):
        return self._parentModifiers.get(modifier, [])

    def RemoveParentModifier(self, modifier, dependantModifier = None):
        if dependantModifier:
            parentModifiers = self.GetParentModifiers(dependantModifier)
            if modifier in parentModifiers:
                parentModifiers.remove(modifier)
        else:
            for parentModifiers in self._parentModifiers.itervalues():
                if modifier in parentModifiers:
                    parentModifiers.remove(modifier)

    def GetSoundTags(self):
        soundTags = []
        for modifier in iter(self.GetSortedModifiers()):
            soundTag = modifier.metaData.soundTag
            if soundTag and soundTag not in soundTags:
                soundTags.append(soundTag)

        return soundTags

    def Lock(self):
        self.__locked = True

    def UnLock(self):
        self.__locked = False
        for modifier in self.__pendingModifiersToRemove:
            self.RemoveModifier(modifier)

        self.__pendingModifiersToRemove = []
        for modifier in self.__pendingModifiersToAdd:
            self.AddModifier(modifier)

        self.__pendingModifiersToAdd = []

    def HashForMaps(self, hashableElements = None):
        hasher = hashlib.md5()
        if hashableElements:
            for he in iter(hashableElements):
                hasher.update(str(he))

        for part, modifiers in self.modifiersdata.iteritems():
            hasher.update(part)
            for modifier in iter(modifiers):
                if not (modifier.IsTextureContainingModifier() or modifier.metaData.hidesBootShin or modifier.metaData.forcesLooseTop or modifier.metaData.swapTops or modifier.metaData.swapBottom or modifier.metaData.swapSocks):
                    continue
                modString = '{0}{1}{2}{3}{4}{5}{6}{7}{8}{9}'.format(modifier.name, modifier.categorie, modifier.weight, modifier.colorizeData, modifier.specularColorData, modifier.pattern, modifier.patternData, modifier.decalData, modifier.useSkin, modifier.variationTextureHash)
                if modifier.metaData.hidesBootShin or modifier.metaData.forcesLooseTop or modifier.metaData.swapTops or modifier.metaData.swapBottom or modifier.metaData.swapSocks:
                    modString = '{0}{1}{2}'.format(modString, modifier.metaData.hidesBootShin, modifier.metaData.forcesLooseTop, modifier.metaData.swapTops, modifier.metaData.swapBottom, modifier.metaData.swapSocks)
                hasher.update(modString)

            pdCF.BeFrameNice()

        return hasher.hexdigest()

    def GetDirtyModifiers(self, changedBit = False, addedBit = False, removedBit = False, getWeightless = True):
        ret = list()
        masking = changedBit or addedBit or removedBit
        if addedBit or not masking:
            if getWeightless:
                ret.extend(self.__dirtyModifiersAdded)
            else:
                ret.extend((modifier for modifier in self.__dirtyModifiersAdded if modifier.weight > 0))
        if removedBit or not masking:
            if getWeightless:
                ret.extend(self.__dirtyModifiersRemoved)
            else:
                ret.extend((modifier for modifier in self.__dirtyModifiersRemoved if modifier.weight > 0))
        if changedBit or not masking:
            self.__filterHidden = False
            changedModifiers = []
            for modifiers in self.modifiersdata.itervalues():
                if getWeightless:
                    changedModifiers.extend((modifier for modifier in modifiers if modifier.IsDirty and modifier not in self.__dirtyModifiersAdded))
                else:
                    changedModifiers.extend((modifier for modifier in modifiers if modifier.IsDirty and modifier.weight > 0 and modifier not in self.__dirtyModifiersAdded))

            self.__filterHidden = True
            for modifier in changedModifiers:
                if modifier not in ret:
                    ret.append(modifier)

        ret = self.SortParts(ret)
        return ret

    @telemetry.ZONE_METHOD
    def NotifyUpdate(self):
        del self.__dirtyModifiersAdded[:]
        for modifier in iter(self.__dirtyModifiersRemoved):
            modifier.ClearCachedData()

        del self.__dirtyModifiersRemoved[:]
        for modifier in iter(self.GetModifiersAsList(showHidden=True)):
            modifier.IsDirty = False

        self.desiredOrderChanged = False
        self.__dirty = False

    def SetAllAsDirty(self, clearMeshes = False):
        for part in self.modifiersdata.iterkeys():
            for modifier in self.modifiersdata[part]:
                modifier.IsDirty = True
                if clearMeshes:
                    modifier.ClearCachedData()

        self.__dirty = True

    def SetLOD(self, newLod):
        self.currentLOD = newLod
        modifiers = self.GetModifiersAsList(showHidden=True)
        for modifier in modifiers:
            if not modifier.IsVisibleAtLOD(self.currentLOD):
                self.HideModifier(modifier)
            elif modifier.IsHidden:
                self.ShowModifier(modifier)

    def RemoveMeshContainingModifiers(self, category, privilegedCaller = False):
        for modifier in self.GetModifiersByCategory(category):
            if modifier.IsMeshContainingModifier() and not self.GetParentModifiers(modifier):
                self.RemoveModifier(modifier, privilegedCaller=privilegedCaller)

    def AddModifier(self, modifier, privilegedCaller = False):
        if self.__locked and not privilegedCaller:
            self.__pendingModifiersToAdd.append(modifier)
        else:
            part = self.CategoryToPart(modifier.categorie)
            for existingModifier in iter(self.__modifiers[part]):
                if existingModifier.respath == modifier.respath:
                    if existingModifier.IsVisibleAtLOD(self.currentLOD):
                        if existingModifier.IsHidden:
                            self.ShowModifier(existingModifier)
                    else:
                        self.HideModifier(existingModifier)
                    if modifier.weight > existingModifier.weight:
                        existingModifier.weight = modifier.weight
                        self.ApplyOccludeRules(existingModifier)
                    return

            if not modifier.IsVisibleAtLOD(self.currentLOD):
                self.HideModifier(modifier)
            self.ApplyOccludeRules(modifier)
            if modifier.weight > 0:
                if modifier.categorie == pdDef.BODY_CATEGORIES.TOPOUTER:
                    self.RemoveMeshContainingModifiers(pdDef.BODY_CATEGORIES.TOPINNER, privilegedCaller=privilegedCaller)
                elif modifier.categorie == pdDef.BODY_CATEGORIES.BOTTOMOUTER:
                    self.RemoveMeshContainingModifiers(pdDef.BODY_CATEGORIES.BOTTOMINNER, privilegedCaller=privilegedCaller)
                if modifier.IsMeshContainingModifier() and modifier.categorie not in (pdDef.DOLL_PARTS.ACCESSORIES, pdDef.DOLL_EXTRA_PARTS.DEPENDANTS):
                    self.RemoveMeshContainingModifiers(modifier.categorie, privilegedCaller=privilegedCaller)
            self.OccludeModifiersByModifier(modifier)
            self.__dirtyModifiersAdded.append(modifier)
            resPaths = modifier.GetDependantModifierResPaths()
            if resPaths:
                for resPath in iter(resPaths):
                    dependantModifier = self.GetModifierByResPath(resPath)
                    if dependantModifier:
                        modifier.AddDependantModifier(dependantModifier)
                        self.AddParentModifier(dependantModifier, modifier)

            for dependantModifier in iter(modifier.GetDependantModifiers()):
                self.AddModifier(dependantModifier, privilegedCaller=privilegedCaller)
                self.AddParentModifier(dependantModifier, modifier)

            if modifier in self.__dirtyModifiersRemoved:
                self.__dirtyModifiersRemoved.remove(modifier)
            self.__modifiers[part].append(modifier)
            self.__dirty = True

    def OccludeModifiersByModifier(self, modifier):
        occludeData = modifier.GetOccludedModifiersFullData()
        if occludeData:
            for resPath, weightSubtraction in occludeData:
                self.UpdateOccludeRule(resPath, weightSubtraction)
                occlusionTargets = []
                if pdDef.SEPERATOR_CHAR not in resPath:
                    occlusionTargets.extend(self.GetModifiersByCategory(resPath))
                elif resPath.count(pdDef.SEPERATOR_CHAR) == 1 and resPath.split(pdDef.SEPERATOR_CHAR)[0] in pdDef.CATEGORIES_CONTAINING_GROUPS:
                    category, group = resPath.split(pdDef.SEPERATOR_CHAR)[:2]
                    groupCandidateModifiers = self.GetModifiersByCategory(category)
                    for groupCandidateModifier in groupCandidateModifiers:
                        if group == groupCandidateModifier.group:
                            occlusionTargets.append(groupCandidateModifier)

                else:
                    targetToOcclude = self.GetModifierByResPath(resPath, includeFuture=True)
                    if targetToOcclude:
                        occlusionTargets.append(targetToOcclude)
                for targetToOcclude in occlusionTargets:
                    targetToOcclude.weight -= weightSubtraction

    def GetOcclusionWeight(self, modifier):
        occlusionWeight = 0
        for resPath in self.occludeRules.iterkeys():
            if resPath in modifier.respath:
                occlusionWeight += self.occludeRules[resPath]

        return occlusionWeight

    def ApplyOccludeRules(self, modifier):
        modifier.weight -= self.GetOcclusionWeight(modifier)

    def IsCategoryOccluded(self, category):
        for resPath, weight in self.occludeRules.iteritems():
            if weight >= 1.0 and resPath == category:
                return True

        return False

    def UpdateOccludeRule(self, resPath, weight):
        occludeRule = self.occludeRules.get(resPath, 0)
        occludeRule += weight
        if occludeRule <= 0.0:
            try:
                del self.occludeRules[resPath]
            except KeyError:
                pass

        else:
            self.occludeRules[resPath] = occludeRule

    def ReverseOccludeModifiersByModifier(self, modifier, useVariation = None):
        occludeData = None
        if useVariation is not None:
            metaData = modifier.GetVariationMetaData(useVariation)
            occludeData = modifier.GetOccludedModifiersFullData(metaData)
        else:
            occludeData = modifier.GetOccludedModifiersFullData()
        if occludeData:
            for resPath, weightSubtraction in occludeData:
                self.UpdateOccludeRule(resPath, -weightSubtraction)
                modifiersToReverseOcclude = []
                if pdDef.SEPERATOR_CHAR not in resPath:
                    for occludedModifier in self.GetModifiersByCategory(resPath):
                        modifiersToReverseOcclude.append(occludedModifier)

                elif resPath.count(pdDef.SEPERATOR_CHAR) == 1 and resPath.split(pdDef.SEPERATOR_CHAR)[0] in pdDef.CATEGORIES_CONTAINING_GROUPS:
                    category, group = resPath.split(pdDef.SEPERATOR_CHAR)[:2]
                    groupCandidateModifiers = self.GetModifiersByCategory(category)
                    for groupCandidateModifier in groupCandidateModifiers:
                        if group == groupCandidateModifier.group:
                            modifiersToReverseOcclude.append(groupCandidateModifier)

                else:
                    occludedModifier = self.GetModifierByResPath(resPath)
                    if occludedModifier:
                        modifiersToReverseOcclude.append(occludedModifier)
                for target in modifiersToReverseOcclude:
                    oldWeight = target.weight
                    target.weight += weightSubtraction
                    if oldWeight <= 0 and target.weight > 0:
                        self.AddModifier(target, privilegedCaller=True)

    def RemoveModifier(self, modifier, privilegedCaller = False, occludingCall = False):
        if self.__locked and not privilegedCaller:
            self.__pendingModifiersToRemove.append(modifier)
        else:
            if self.GetParentModifiers(modifier) and not occludingCall:
                log.LogWarn('paperDoll::BuildDataManager::RemoveModifier - Attempting to remove a modifier that has parent modifiers', modifier)
                return
            if modifier in self.__dirtyModifiersRemoved:
                return
            part = self.CategoryToPart(modifier.categorie)
            if modifier in self.__modifiers[part]:
                self.__modifiers[part].remove(modifier)
            if modifier in self.__dirtyModifiersAdded:
                self.__dirtyModifiersAdded.remove(modifier)
            self.__dirtyModifiersRemoved.append(modifier)
            replacementPaths = (modifier.metaData.lod1Replacement, modifier.metaData.lod2Replacement)
            for replacementPath in replacementPaths:
                if replacementPath:
                    lodReplacementModifier = self.GetModifierByResPath(replacementPath)
                    if lodReplacementModifier:
                        self.RemoveModifier(lodReplacementModifier)

            self.ReverseOccludeModifiersByModifier(modifier)
            self.RemoveParentModifier(modifier)
            for dependantModifier in iter(modifier.GetDependantModifiers()):
                parentModifiers = self.GetParentModifiers(dependantModifier)
                if parentModifiers:
                    dependantModifier.weight = 0
                    for modifier in iter(parentModifiers):
                        for entry in modifier.GetDependantModifiersFullData():
                            if entry[0] == dependantModifier.respath and entry[3] > dependantModifier.weight:
                                dependantModifier.weight = entry[3]

                    self.ApplyOccludeRules(dependantModifier)
                if occludingCall or len(parentModifiers) == 0:
                    self.RemoveModifier(dependantModifier, privilegedCaller=privilegedCaller)

            self.__dirty = True

    def SetModifiersByCategory(self, category, modifiers, privilegedCaller = False):
        self.__dirty = True
        if type(modifiers) == BuildData:
            modifiers = [modifiers]
        removeModifiers = self.GetModifiersByCategory(category)
        for modifier in iter(removeModifiers):
            self.RemoveModifier(modifier, privilegedCaller=privilegedCaller)

        for modifier in iter(modifiers):
            self.AddModifier(modifier, privilegedCaller=privilegedCaller)

    def GetModifiersByCategory(self, category, showHidden = False, includeFuture = False):
        filterHiddenState = self.__filterHidden
        if showHidden:
            self.__filterHidden = False
        part = self.CategoryToPart(category)
        modifiers = self.modifiersdata.get(part, [])
        modifiers = [ modifier for modifier in modifiers if modifier.categorie == category ]
        if includeFuture:
            for modifier in self.__pendingModifiersToAdd:
                if modifier.categorie == category:
                    modifiers.insert(0, modifier)

        self.__filterHidden = filterHiddenState
        return modifiers

    def GetModifiersByPart(self, part, showHidden = False):
        filterHiddenState = self.__filterHidden
        if showHidden:
            self.__filterHidden = False
        modifiers = self.modifiersdata.get(part, [])
        self.__filterHidden = filterHiddenState
        return modifiers

    def GetModifierByResPath(self, resPath, includeFuture = False, showHidden = False):
        for modifier in self.GetModifiersAsList(includeFuture=includeFuture, showHidden=showHidden):
            if modifier.respath == resPath:
                return modifier

    def GetMeshSourcePaths(self, modifiers = None):
        meshSourcePaths = list()
        if modifiers is None:
            modifiers = self.GetSortedModifiers()
        for modifier in iter(modifiers):
            meshSourcePaths.extend(modifier.GetMeshSourcePaths())

        while None in meshSourcePaths:
            meshSourcePaths.remove(None)

        while '' in meshSourcePaths:
            meshSourcePaths.remove('')

        return meshSourcePaths

    def GetMapsToComposite(self, modifiers = None):
        mapTypes = set()
        if modifiers is None:
            modifiers = self.GetSortedModifiers()
        modGenerator = (modifier for modifier in iter(modifiers) if modifier.weight > 0)
        for modifier in modGenerator:
            mapTypes.update(modifier.ContributesToMapTypes())

        return mapTypes

    def GetPartsFromMaps(self, modifiers = None):
        parts = set()
        if modifiers is None:
            modifiers = self.GetSortedModifiers()
        modGenerator = (modifier for modifier in iter(modifiers) if modifier.weight > 0)
        for modifier in modGenerator:
            parts.update(modifier.GetAffectedTextureParts())

        return list(parts)

    def GetParts(self, modifiers = None):
        parts = set()
        if modifiers is None:
            modifiers = self.GetSortedModifiers()
        for modifier in iter(modifiers):
            part = self.CategoryToPart(modifier.categorie)
            parts.add(part)

        return list(parts)

    def HideModifiersByCategory(self, category):
        for modifier in self.GetModifiersByCategory(category):
            self.HideModifier(modifier)

    def HideModifiersByPart(self, part):
        for modifier in self.GetModifiersByPart(part):
            self.HideModifier(modifier)

    def HideModifier(self, modifier):
        self.__dirty = True
        modifier.IsHidden = True
        self.__dirtyModifiersRemoved.append(modifier)
        if modifier in self.__dirtyModifiersAdded:
            self.__dirtyModifiersAdded.remove(modifier)

    def ShowModifiersByCategory(self, category):
        self.__filterHidden = False
        for modifier in self.GetModifiersByCategory(category):
            self.ShowModifier(modifier)

        self.__filterHidden = True

    def ShowModifiersByPart(self, part):
        self.__filterHidden = False
        for modifier in self.GetModifiersByPart(part):
            self.ShowModifier(modifier)

        self.__filterHidden = True

    def ShowModifier(self, modifier):
        self.__dirty = True
        modifier.IsHidden = False
        self.__dirtyModifiersAdded.append(modifier)
        if modifier in self.__dirtyModifiersRemoved:
            self.__dirtyModifiersRemoved.remove(modifier)

    def GetHiddenModifiers(self):
        self.__filterHidden = False
        modifiers = []
        for modifier in iter(self.GetModifiersAsList()):
            if modifier.IsHidden:
                modifiers.append(modifier)

        self._filterHidden = True
        return modifiers

    def GetBodyModifiers(self, remapToPart = False):
        return self.GetModifiersByPart(pdDef.DOLL_PARTS.BODY)

    def GetHeadModifiers(self, remapToPart = False):
        category = pdDef.DOLL_PARTS.HEAD
        if remapToPart:
            category = self.CategoryToPart(category, pdDef.DOLL_PARTS.HEAD)
        return self.GetModifiersByCategory(category)

    def GetHairModifiers(self, remapToPart = False):
        category = pdDef.DOLL_PARTS.HAIR
        if remapToPart:
            category = self.CategoryToPart(category, pdDef.DOLL_PARTS.HAIR)
        return self.GetModifiersByCategory(category)

    def GetAccessoriesModifiers(self, remapToPart = False):
        category = pdDef.DOLL_PARTS.ACCESSORIES
        if remapToPart:
            category = self.CategoryToPart(category, pdDef.DOLL_PARTS.ACCESSORIES)
        return self.GetModifiersByCategory(category)

    def GetModifiersAsList(self, includeFuture = False, showHidden = False):
        filterHiddenState = self.__filterHidden
        if showHidden:
            self.__filterHidden = False
        ret = []
        if includeFuture:
            ret = list(self.__pendingModifiersToAdd)
        for each in self.modifiersdata.itervalues():
            ret.extend(each)

        self.__filterHidden = filterHiddenState
        return ret

    @telemetry.ZONE_METHOD
    def GetSortedModifiers(self, showHidden = False, includeFuture = False):
        if showHidden:
            modifiers = self.SortParts(self.GetModifiersAsList(includeFuture=includeFuture, showHidden=True))
            return modifiers
        if self.__dirty or not self.__sortedList:
            self.__sortedList = self.SortParts(self.GetModifiersAsList())
        if includeFuture:
            ret = list(self.__pendingModifiersToAdd)
            ret.extend(self.__sortedList)
        return list(self.__sortedList)

    def _SortPartFunc(self, modifier, dso):
        try:
            dsoIdx = dso.index(modifier.categorie) * 1000
            groups = pdDef.GROUPS.get(modifier.categorie, [])
            try:
                subIdx = groups.index(modifier.group)
            except ValueError:
                subIdx = 999

            dsoIdx += subIdx
        except ValueError:
            dsoIdx = -1

        return dsoIdx

    def SortParts(self, modifiersList):
        dso = self.desiredOrder
        retList = list(modifiersList)
        retList.sort(key=lambda x: self._SortPartFunc(x, dso))
        return retList

    def ChangeDesiredOrder(self, categoryA, categoryB):
        aIdx = self.desiredOrder.index(categoryA)
        bIdx = self.desiredOrder.index(categoryB)
        if aIdx > bIdx:
            self.desiredOrderChanged = True
            self.__sortedList = None
            self.desiredOrder[bIdx], self.desiredOrder[aIdx] = self.desiredOrder[aIdx], self.desiredOrder[bIdx]

    def GetMeshes(self, part = None, alternativeModifierList = None, includeClothMeshes = False):
        meshes = []
        parts = [part] if part else pdDef.DOLL_PARTS

        def CollectMeshsFrom(fromIter):
            for each in iter(fromIter):
                if each.weight > 0:
                    if part in (None, self.CategoryToPart(each.categorie)):
                        for mesh in iter(each.meshes):
                            meshes.insert(0, mesh)

                        if includeClothMeshes and each.clothData:
                            meshes.insert(0, each.clothData)

        if alternativeModifierList is not None:
            CollectMeshsFrom(alternativeModifierList)
        elif part is not None:
            for p in parts:
                CollectMeshsFrom(self.GetModifiersByPart(p))

        else:
            CollectMeshsFrom(self.GetSortedModifiers())
        return list(meshes)

    def RemapMeshes(self, destinationMeshes):
        for modifier in iter(self.GetModifiersAsList()):
            for mesh in iter(modifier.meshes):
                for destMesh in iter(destinationMeshes):
                    if mesh.name == destMesh.name:
                        mesh = destMesh
                        break

    def CategoryToPart(self, category, partFilter = None):
        if category in pdDef.DOLL_PARTS:
            return category
        if category in pdDef.BODY_CATEGORIES and partFilter in (None, pdDef.DOLL_PARTS.BODY):
            return pdDef.DOLL_PARTS.BODY
        if category in pdDef.HEAD_CATEGORIES and partFilter in (None, pdDef.DOLL_PARTS.HEAD):
            return pdDef.DOLL_PARTS.HEAD
        if category in pdDef.HAIR_CATEGORIES and partFilter in (None, pdDef.DOLL_PARTS.HAIR):
            return pdDef.DOLL_PARTS.HAIR
        if category in pdDef.ACCESSORIES_CATEGORIES and partFilter in (None, pdDef.DOLL_PARTS.ACCESSORIES):
            return pdDef.DOLL_PARTS.ACCESSORIES
        if category in pdDef.DOLL_EXTRA_PARTS.BODYSHAPES:
            return pdDef.DOLL_EXTRA_PARTS.BODYSHAPES
        if category in pdDef.DOLL_EXTRA_PARTS.UTILITYSHAPES:
            return pdDef.DOLL_EXTRA_PARTS.UTILITYSHAPES
        if category in pdDef.DOLL_EXTRA_PARTS.DEPENDANTS:
            return pdDef.DOLL_PARTS.BODY
        return pdDef.DOLL_EXTRA_PARTS.UNDEFINED


exports = {'paperDoll.SaveMapsToDisk': SaveMapsToDisk,
 'paperDoll.ClearAllCachedMaps': ClearAllCachedMaps,
 'paperDoll.FindCachedMap': FindCachedMap}
