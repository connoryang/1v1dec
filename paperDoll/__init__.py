#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\common\modules\nice\client\_nastyspace\paperDoll\__init__.py
from carbon.client.script.graphics.paperDollClient import PaperDollClientComponent
from eve.common.script.paperDoll.paperDollDefinitions import USE_PNG
from eve.common.script.paperDoll.paperDollDefinitions import TEXTURE_STUB
from eve.common.script.paperDoll.paperDollDefinitions import TEXTURE_PRELOAD_PATHS
from eve.common.script.paperDoll.paperDollDefinitions import SculptingRow
from eve.common.script.paperDoll.paperDollDefinitions import STUBBLE_PATH
from eve.common.script.paperDoll.paperDollDefinitions import SPECULAR_MAP
from eve.common.script.paperDoll.paperDollDefinitions import SPECIAL_HANDLE_SHAPES
from eve.common.script.paperDoll.paperDollDefinitions import SKIN_GENERIC_PATH
from eve.common.script.paperDoll.paperDollDefinitions import SKINNED_AVATAR_TONGUE_SHADER
from eve.common.script.paperDoll.paperDollDefinitions import SKINNED_AVATAR_TEETH_SHADER
from eve.common.script.paperDoll.paperDollDefinitions import SKINNED_AVATAR_SINGLEPASS_SINGLE_PATH
from eve.common.script.paperDoll.paperDollDefinitions import SKINNED_AVATAR_SINGLEPASS_DOUBLE_PATH
from eve.common.script.paperDoll.paperDollDefinitions import SKINNED_AVATAR_HAIR_DETAILED
from eve.common.script.paperDoll.paperDollDefinitions import SKINNED_AVATAR_GLASS_SHADER
from eve.common.script.paperDoll.paperDollDefinitions import SKINNED_AVATAR_EYE_SHADER
from eve.common.script.paperDoll.paperDollDefinitions import SKINNED_AVATAR_EYEWETNESS_SHADER
from eve.common.script.paperDoll.paperDollDefinitions import SKINNED_AVATAR_CLOTH_HAIR_DETAILED
from eve.common.script.paperDoll.paperDollDefinitions import SKINNED_AVATAR_BRDF_LINEAR
from eve.common.script.paperDoll.paperDollDefinitions import SKINNED_AVATAR_BRDF_DOUBLE_LINEAR
from eve.common.script.paperDoll.paperDollDefinitions import SHADER_PATH
from eve.common.script.paperDoll.paperDollDefinitions import SHADERS_TO_ENABLE_DXT5N
from eve.common.script.paperDoll.paperDollDefinitions import SHADERS_THAT_CAN_SWITCH_TO_FAST_SHADER_MODE
from eve.common.script.paperDoll.paperDollDefinitions import SEPERATOR_CHAR
from eve.common.script.paperDoll.paperDollDefinitions import RESIZABLE_MAPS
from eve.common.script.paperDoll.paperDollDefinitions import RED_FILE
from eve.common.script.paperDoll.paperDollDefinitions import Property
from eve.common.script.paperDoll.paperDollDefinitions import PROJECTED_TATTOO
from eve.common.script.paperDoll.paperDollDefinitions import OUTSOURCING_JESSICA_PATH
from eve.common.script.paperDoll.paperDollDefinitions import NORMAL_MAP
from eve.common.script.paperDoll.paperDollDefinitions import ModifierRow
from eve.common.script.paperDoll.paperDollDefinitions import MODULAR_TEST_CASES_FOLDER
from eve.common.script.paperDoll.paperDollDefinitions import MODIFIERNAMEFILE
from eve.common.script.paperDoll.paperDollDefinitions import MID_GRAY
from eve.common.script.paperDoll.paperDollDefinitions import MASK_MAP
from eve.common.script.paperDoll.paperDollDefinitions import MASKING_CATEGORIES
from eve.common.script.paperDoll.paperDollDefinitions import MAP_TYPE_SUFFIXES
from eve.common.script.paperDoll.paperDollDefinitions import MAP_SUFFIX_Z
from eve.common.script.paperDoll.paperDollDefinitions import MAP_SUFFIX_TN
from eve.common.script.paperDoll.paperDollDefinitions import MAP_SUFFIX_S
from eve.common.script.paperDoll.paperDollDefinitions import MAP_SUFFIX_O
from eve.common.script.paperDoll.paperDollDefinitions import MAP_SUFFIX_N
from eve.common.script.paperDoll.paperDollDefinitions import MAP_SUFFIX_MN
from eve.common.script.paperDoll.paperDollDefinitions import MAP_SUFFIX_MM
from eve.common.script.paperDoll.paperDollDefinitions import MAP_SUFFIX_MASK
from eve.common.script.paperDoll.paperDollDefinitions import MAP_SUFFIX_M
from eve.common.script.paperDoll.paperDollDefinitions import MAP_SUFFIX_LRGB
from eve.common.script.paperDoll.paperDollDefinitions import MAP_SUFFIX_LA
from eve.common.script.paperDoll.paperDollDefinitions import MAP_SUFFIX_L
from eve.common.script.paperDoll.paperDollDefinitions import MAP_SUFFIX_DRGB
from eve.common.script.paperDoll.paperDollDefinitions import MAP_SUFFIX_DA
from eve.common.script.paperDoll.paperDollDefinitions import MAP_SUFFIX_D
from eve.common.script.paperDoll.paperDollDefinitions import MAP_SUFFIX_AO
from eve.common.script.paperDoll.paperDollDefinitions import MAP_SUFFIX_512
from eve.common.script.paperDoll.paperDollDefinitions import MAP_SUFFIX_4K
from eve.common.script.paperDoll.paperDollDefinitions import MAP_SUFFIX_256
from eve.common.script.paperDoll.paperDollDefinitions import MAP_SIZE_SUFFIXES
from eve.common.script.paperDoll.paperDollDefinitions import MAP_PREFIX_COLORIZE
from eve.common.script.paperDoll.paperDollDefinitions import MAP_FORMAT_TGA
from eve.common.script.paperDoll.paperDollDefinitions import MAP_FORMAT_PNG
from eve.common.script.paperDoll.paperDollDefinitions import MAP_FORMAT_DDS
from eve.common.script.paperDoll.paperDollDefinitions import MAP_FORMATS
from eve.common.script.paperDoll.paperDollDefinitions import MAPS
from eve.common.script.paperDoll.paperDollDefinitions import MAPNAMES
from eve.common.script.paperDoll.paperDollDefinitions import MAPMARKERS
from eve.common.script.paperDoll.paperDollDefinitions import MALE_PATH_SUFFIX
from eve.common.script.paperDoll.paperDollDefinitions import MALE_OPTION_FILE_PATH
from eve.common.script.paperDoll.paperDollDefinitions import MALE_LOD_PATH_SUFFIX
from eve.common.script.paperDoll.paperDollDefinitions import MALE_DECAL_BINDPOSE
from eve.common.script.paperDoll.paperDollDefinitions import MALE_BASE_PATH
from eve.common.script.paperDoll.paperDollDefinitions import MALE_BASE_LOD_PATH
from eve.common.script.paperDoll.paperDollDefinitions import MALE_BASE_GRAPHICS_TEST_PATH
from eve.common.script.paperDoll.paperDollDefinitions import MALE_BASE_GRAPHICS_TEST_LOD_PATH
from eve.common.script.paperDoll.paperDollDefinitions import MAKEUP_GROUPS
from eve.common.script.paperDoll.paperDollDefinitions import MAKEUP_EYES
from eve.common.script.paperDoll.paperDollDefinitions import MAKEUP_EYELASHES
from eve.common.script.paperDoll.paperDollDefinitions import MAKEUP_EYEBROWS
from eve.common.script.paperDoll.paperDollDefinitions import LOD_SKIN
from eve.common.script.paperDoll.paperDollDefinitions import LOD_SCATTER_SKIN
from eve.common.script.paperDoll.paperDollDefinitions import LOD_A
from eve.common.script.paperDoll.paperDollDefinitions import LOD_99
from eve.common.script.paperDoll.paperDollDefinitions import LOD_3
from eve.common.script.paperDoll.paperDollDefinitions import LOD_2
from eve.common.script.paperDoll.paperDollDefinitions import LOD_1
from eve.common.script.paperDoll.paperDollDefinitions import LOD_0
from eve.common.script.paperDoll.paperDollDefinitions import LIGHT_GRAY
from eve.common.script.paperDoll.paperDollDefinitions import INTERIOR_AVATAR_EFFECT_FILE_PATH
from eve.common.script.paperDoll.paperDollDefinitions import HashDecalList
from eve.common.script.paperDoll.paperDollDefinitions import HEAD_UVS
from eve.common.script.paperDoll.paperDollDefinitions import HEAD_CATEGORIES
from eve.common.script.paperDoll.paperDollDefinitions import HEAD_BLENDSHAPE_ZONES
from eve.common.script.paperDoll.paperDollDefinitions import HAIR_UVS
from eve.common.script.paperDoll.paperDollDefinitions import HAIR_CATEGORIES
from eve.common.script.paperDoll.paperDollDefinitions import GetPatternList
from eve.common.script.paperDoll.paperDollDefinitions import GetMorphsFromGr2
from eve.common.script.paperDoll.paperDollDefinitions import GetDNAConverter
from eve.common.script.paperDoll.paperDollDefinitions import GetCategorizedBlendShapeNames
from eve.common.script.paperDoll.paperDollDefinitions import GROUPS
from eve.common.script.paperDoll.paperDollDefinitions import GLASS_SHADER_REFLECTION_CUBE_PATH
from eve.common.script.paperDoll.paperDollDefinitions import GEO_SUFFIX_LODA
from eve.common.script.paperDoll.paperDollDefinitions import GEO_SUFFIX_LOD3
from eve.common.script.paperDoll.paperDollDefinitions import GEO_SUFFIX_LOD2
from eve.common.script.paperDoll.paperDollDefinitions import GEO_SUFFIX_LOD1
from eve.common.script.paperDoll.paperDollDefinitions import GEO_SUFFIX_LOD0
from eve.common.script.paperDoll.paperDollDefinitions import GEO_LOD_SUFFIXES
from eve.common.script.paperDoll.paperDollDefinitions import GEO_FORMAT_RED
from eve.common.script.paperDoll.paperDollDefinitions import GEO_FORMAT_GR2
from eve.common.script.paperDoll.paperDollDefinitions import GEO_FORMATS
from eve.common.script.paperDoll.paperDollDefinitions import GENDER_ROOT
from eve.common.script.paperDoll.paperDollDefinitions import GENDER
from eve.common.script.paperDoll.paperDollDefinitions import FRESNEL_LOOKUP_MAP
from eve.common.script.paperDoll.paperDollDefinitions import FIXED_SIZE_MAPS
from eve.common.script.paperDoll.paperDollDefinitions import FEMALE_WRINKLE_FACEZONE_PREFIX
from eve.common.script.paperDoll.paperDollDefinitions import FEMALE_PATH_SUFFIX
from eve.common.script.paperDoll.paperDollDefinitions import FEMALE_OPTION_FILE_PATH
from eve.common.script.paperDoll.paperDollDefinitions import FEMALE_LOD_PATH_SUFFIX
from eve.common.script.paperDoll.paperDollDefinitions import FEMALE_DECAL_BINDPOSE
from eve.common.script.paperDoll.paperDollDefinitions import FEMALE_BASE_PATH
from eve.common.script.paperDoll.paperDollDefinitions import FEMALE_BASE_LOD_PATH
from eve.common.script.paperDoll.paperDollDefinitions import FEMALE_BASE_GRAPHICS_TEST_PATH
from eve.common.script.paperDoll.paperDollDefinitions import FEMALE_BASE_GRAPHICS_TEST_LOD_PATH
from eve.common.script.paperDoll.paperDollDefinitions import EYE_SHADER_REFLECTION_CUBE_PATH
from eve.common.script.paperDoll.paperDollDefinitions import EXTERIOR_AVATAR_EFFECT_FILE_PATH
from eve.common.script.paperDoll.paperDollDefinitions import EFFECT_PRELOAD_PATHS
from eve.common.script.paperDoll.paperDollDefinitions import DumpYaml
from eve.common.script.paperDoll.paperDollDefinitions import DumpBlendshapes
from eve.common.script.paperDoll.paperDollDefinitions import DUMP_MODULAR_TEST_CASES_TO_OPTIONS
from eve.common.script.paperDoll.paperDollDefinitions import DOLL_PART_TO_CATEGORIES
from eve.common.script.paperDoll.paperDollDefinitions import DOLL_PARTS
from eve.common.script.paperDoll.paperDollDefinitions import DOLL_EXTRA_PARTS
from eve.common.script.paperDoll.paperDollDefinitions import DNA_STRINGS
from eve.common.script.paperDoll.paperDollDefinitions import DNAConverter
from eve.common.script.paperDoll.paperDollDefinitions import DIFFUSE_MAP
from eve.common.script.paperDoll.paperDollDefinitions import DESIRED_ORDER
from eve.common.script.paperDoll.paperDollDefinitions import DEFAULT_UVS
from eve.common.script.paperDoll.paperDollDefinitions import DEFAULT_NUDE_TORSO
from eve.common.script.paperDoll.paperDollDefinitions import DEFAULT_NUDE_SLEEVESUPPER
from eve.common.script.paperDoll.paperDollDefinitions import DEFAULT_NUDE_SLEEVESLOWER
from eve.common.script.paperDoll.paperDollDefinitions import DEFAULT_NUDE_PARTS
from eve.common.script.paperDoll.paperDollDefinitions import DEFAULT_NUDE_LEGS
from eve.common.script.paperDoll.paperDollDefinitions import DEFAULT_NUDE_HEAD
from eve.common.script.paperDoll.paperDollDefinitions import DEFAULT_NUDE_HANDS
from eve.common.script.paperDoll.paperDollDefinitions import DEFAULT_NUDE_FEET
from eve.common.script.paperDoll.paperDollDefinitions import DEFAULT_NUDE_EYELASHES
from eve.common.script.paperDoll.paperDollDefinitions import DARK_GRAY
from eve.common.script.paperDoll.paperDollDefinitions import CreateEntries
from eve.common.script.paperDoll.paperDollDefinitions import ConvertDNAForDB
from eve.common.script.paperDoll.paperDollDefinitions import ColorSelectionRow
from eve.common.script.paperDoll.paperDollDefinitions import CLOTH_PATH
from eve.common.script.paperDoll.paperDollDefinitions import CLOTH_OVERRIDE
from eve.common.script.paperDoll.paperDollDefinitions import CLOTH_AVATAR_LINEAR
from eve.common.script.paperDoll.paperDollDefinitions import CATEGORIES_THATCLEAN_MATERIALMAP
from eve.common.script.paperDoll.paperDollDefinitions import CATEGORIES_CONTAINING_GROUPS
from eve.common.script.paperDoll.paperDollDefinitions import BODY_UVS
from eve.common.script.paperDoll.paperDollDefinitions import BODY_CATEGORIES
from eve.common.script.paperDoll.paperDollDefinitions import BODY_BLENDSHAPE_ZONES
from eve.common.script.paperDoll.paperDollDefinitions import BLENDSHAPE_CATEGORIES
from eve.common.script.paperDoll.paperDollDefinitions import BLENDSHAPE_AXIS_PAIRS
from eve.common.script.paperDoll.paperDollDefinitions import BLENDSHAPE_AXIS
from eve.common.script.paperDoll.paperDollDefinitions import BASE_GRAPHICS_TEST_FOLDER
from eve.common.script.paperDoll.paperDollDefinitions import BASE_GRAPHICS_FOLDER
from eve.common.script.paperDoll.paperDollDefinitions import AppearanceRow
from eve.common.script.paperDoll.paperDollDefinitions import AddBlendshapeEntries
from eve.common.script.paperDoll.paperDollDefinitions import AXIS_DIRECTIONS
from eve.common.script.paperDoll.paperDollDefinitions import AVATAR_TYPES
from eve.common.script.paperDoll.paperDollDefinitions import ALL_BLENDSHAPE_ZONES
from eve.common.script.paperDoll.paperDollDefinitions import ACCE_UVS
from eve.common.script.paperDoll.paperDollDefinitions import ACCESSORIES_CATEGORIES
from eve.common.script.paperDoll.paperDollCommonFunctions import AddToDictList
from eve.common.script.paperDoll.paperDollCommonFunctions import BeFrameNice
from eve.common.script.paperDoll.paperDollCommonFunctions import GetFromDictList
from eve.common.script.paperDoll.paperDollCommonFunctions import NastyYamlLoad
from eve.common.script.paperDoll.paperDollCommonFunctions import WaitForAll
from eve.common.script.paperDoll.paperDollCommonFunctions import Yield
from eve.common.script.paperDoll.paperDollConfiguration import PerformanceOptions
from eve.common.script.paperDoll.paperDollDataManagement import BuildData
from eve.common.script.paperDoll.paperDollDataManagement import BuildDataManager
from eve.common.script.paperDoll.paperDollDataManagement import ClearAllCachedMaps
from eve.common.script.paperDoll.paperDollDataManagement import FindCachedMap
from eve.common.script.paperDoll.paperDollDataManagement import ModifierLoader
from eve.common.script.paperDoll.paperDollDataManagement import SaveMapsToDisk
from eve.common.script.paperDoll.paperDollRandomizer import AbstractRandomizer
from eve.common.script.paperDoll.paperDollRandomizer import DollRandomizer
from eve.common.script.paperDoll.paperDollTestUtils import RandomModifierManager as RandomModifierMananger
from eve.common.script.paperDoll.yamlPreloader import AvatarPartMetaData
from eve.common.script.paperDoll.yamlPreloader import LoadYamlFileNicely
from eve.common.script.paperDoll.yamlPreloader import YamlPreloader
from eve.client.script.paperDoll.commonClientFunctions import TRANSLATION
from eve.client.script.paperDoll.commonClientFunctions import StripDigits
from eve.client.script.paperDoll.commonClientFunctions import SetOrAddMap
from eve.client.script.paperDoll.commonClientFunctions import ROTATION
from eve.client.script.paperDoll.commonClientFunctions import PutMeshToLookup
from eve.client.script.paperDoll.commonClientFunctions import MoveAreas
from eve.client.script.paperDoll.commonClientFunctions import MeshAreaListIterator
from eve.client.script.paperDoll.commonClientFunctions import MeshAreaIterator
from eve.client.script.paperDoll.commonClientFunctions import IsSkin
from eve.client.script.paperDoll.commonClientFunctions import IsGlasses
from eve.client.script.paperDoll.commonClientFunctions import IsBeard
from eve.client.script.paperDoll.commonClientFunctions import INTERIOR_MALE_GEOMETRY_RESPATH
from eve.client.script.paperDoll.commonClientFunctions import INTERIOR_FEMALE_GEOMETRY_RESPATH
from eve.client.script.paperDoll.commonClientFunctions import HAIR_MESH_SHAPE
from eve.client.script.paperDoll.commonClientFunctions import GetHighLevelShaderByName
from eve.client.script.paperDoll.commonClientFunctions import GetEffectsFromMesh
from eve.client.script.paperDoll.commonClientFunctions import GetEffectsFromAreaList
from eve.client.script.paperDoll.commonClientFunctions import FindResourceByName
from eve.client.script.paperDoll.commonClientFunctions import FindParameterByName
from eve.client.script.paperDoll.commonClientFunctions import FindOrAddVec4
from eve.client.script.paperDoll.commonClientFunctions import FindOrAddMat4
from eve.client.script.paperDoll.commonClientFunctions import DestroyWeakBlueDict
from eve.client.script.paperDoll.commonClientFunctions import DRAPE_TUCK_NAMES
from eve.client.script.paperDoll.commonClientFunctions import DEFAULT_FEMALE_ANIMATION_RESPATH
from eve.client.script.paperDoll.commonClientFunctions import CreateRandomDoll
from eve.client.script.paperDoll.commonClientFunctions import CheckDuplicateMeshes
from eve.client.script.paperDoll.commonClientFunctions import AddWeakBlue
from eve.client.script.paperDoll.commonClientFunctions import GetSkinTypeOrToneColorVariation
from eve.client.script.paperDoll.AvatarGhost import AvatarGhost
from eve.client.script.paperDoll.SkinLightmapRenderer import SkinLightmapRenderer
from eve.client.script.paperDoll.SkinSpotLightShadows import SkinSpotLightShadows
from eve.client.script.paperDoll.paperDollImpl import CompressionSettings
from eve.client.script.paperDoll.paperDollImpl import Doll
from eve.client.script.paperDoll.paperDollImpl import Factory
from eve.client.script.paperDoll.paperDollImpl import MapBundle
from eve.client.script.paperDoll.paperDollImpl import OutOfVideoMemoryException
from eve.client.script.paperDoll.paperDollImpl import RedundantUpdateException
from eve.client.script.paperDoll.paperDollImpl import UpdateRuleBundle
from eve.client.script.paperDoll.paperDollLOD import AbortAllLod
from eve.client.script.paperDoll.paperDollLOD import LoadingStubPath
from eve.client.script.paperDoll.paperDollLOD import LodQueue
from eve.client.script.paperDoll.paperDollLOD import SetupLODFromPaperdoll
from eve.client.script.paperDoll.paperDollPortrait import PortraitTools
from eve.client.script.paperDoll.paperDollSpawnWrappers import PaperDollCharacter
from eve.client.script.paperDoll.paperDollSpawnWrappers import PaperDollManager
from eve.client.script.paperDoll.projectedDecals import BK_SHADERRES
from eve.client.script.paperDoll.projectedDecals import DECAL_PROJECTION_CAMERA
from eve.client.script.paperDoll.projectedDecals import DECAL_PROJECTION_CYLINDRICAL
from eve.client.script.paperDoll.projectedDecals import DECAL_PROJECTION_DISABLED
from eve.client.script.paperDoll.projectedDecals import DECAL_PROJECTION_EO_LOD_THRESHOLD
from eve.client.script.paperDoll.projectedDecals import DECAL_PROJECTION_PLANAR
from eve.client.script.paperDoll.projectedDecals import DecalBaker
from eve.client.script.paperDoll.projectedDecals import EO_SHADERRES
from eve.client.script.paperDoll.projectedDecals import INV_SHADERRES
from eve.client.script.paperDoll.projectedDecals import MASK_SHADERRES
from eve.client.script.paperDoll.projectedDecals import ProjectedDecal
from eve.client.script.paperDoll.projectedDecals import RT_SHADERRES
from eve.client.script.paperDoll.projectedDecals import ST_SHADERRES
from eve.client.script.paperDoll.projectedDecals import ShowTexture
from eve.client.script.ui.login.charcreation.eveDollRandomizer import EveDollRandomizer
