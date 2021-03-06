#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\charactercreator\const.py
CHARACTER_CREATION_NETWORK = 'res:/Animation/MorphemeIncarna/Export/CharCreation_runtimeBinary/CharacterCreation.mor'
GENDERID_FEMALE = 0
GENDERID_MALE = 1
NUM_PORTRAITS = 4
BODYGROUP = 0
SKINGROUP = 1
HAIRGROUP = 2
EYESGROUP = 3
MAKEUPGROUP = 4
SKINDETAILSGROUP = 5
CLOTHESGROUP = 6
BACKGROUNDGROUP = 7
POSESGROUP = 8
LIGHTSGROUP = 9
PIERCINGGROUP = 10
TATTOOGROUP = 11
SCARSGROUP = 12
PROSTHETICS = 13
AUGMENTATIONS = 14
MAINFRAME = ('ui_105_32_1', 8, -4)
MAINFRAME_INV = ('ui_105_32_10', 8, -4)
MAINFRAME_WITHTABS = ('ui_105_32_9', 8, -4)
FRAME_SOFTSHADE = ('ui_105_32_26', 15, 0)
FILL_BEVEL = ('ui_105_32_31', 0, 0)
ICON_EXPANDED = 'ui_105_32_4'
ICON_COLLAPSED = 'ui_105_32_5'
ICON_EXPANDEDSINGLE = 'ui_105_32_20'
ICON_COLLAPSEDSINGLE = 'ui_105_32_21'
ICON_RANDOMSMALL = 'ui_105_32_6'
ICON_RANDOM = 'ui_105_32_7'
ICON_FOCUSFRAME = 'ui_105_32_36'
ICON_CLOSE = 'ui_105_32_12'
ICON_NEXT = 'ui_105_32_16'
ICON_BACK = 'ui_105_32_15'
ICON_CAM_PRESSED = 'ui_105_32_23'
ICON_CAM_IDLE = 'ui_105_32_24'
ICON_TOGGLECLOTHES = 'ui_105_32_8'
ICON_HELP = 'ui_105_32_32'
POSERANGE = 6
TEXTURE_RESOLUTIONS = [(4096, 2048), (2048, 1024), (512, 256)]
DOLL_VIEWER_TEXTURE_RESOLUTIONS = [(2048, 1024), (1024, 512), (512, 256)]
eyes = 'makeup/eyes'
eyeshadow = 'makeup/eyeshadow'
eyelashes = 'makeup/eyelashes'
eyeliner = 'makeup/eyeliner'
lipstick = 'makeup/lipstick'
blush = 'makeup/blush'
skintype = 'skintype'
hair = 'hair'
eyebrows = 'makeup/eyebrows'
beard = 'beard'
bottomouter = 'bottomouter'
topmiddle = 'topmiddle'
topouter = 'topouter'
feet = 'feet'
outer = 'outer'
bottominner = 'bottominner'
bottommiddle = 'bottommiddle'
topinner = 'topinner'
tattoo = 'tattoo'
skintone = 'skintone'
skinaging = 'makeup/aging'
scarring = 'makeup/scarring'
freckles = 'makeup/freckles'
glasses = 'accessories/glasses'
muscle = 'bodyshapes/muscularshape'
weight = 'bodyshapes/fatshape'
bottomunderwear = 'bottomunderwear'
topunderwear = 'topunderwear'
p_earslow = 'accessories/earslow'
p_earshigh = 'accessories/earshigh'
p_nose = 'accessories/nose'
p_nostril = 'accessories/nostril'
p_brow = 'accessories/brow'
p_lips = 'accessories/lips'
p_chin = 'accessories/chin'
s_head = 'scars/head'
t_head = 'tattoo/head'
t_armleft = 'tattoo/armleft'
t_armright = 'tattoo/armright'
pr_armleft = 'makeup/armleft'
pr_armright = 'makeup/armright'
augm_face = 'makeup/augmentations'
BASEBEARD = 'beard/stubble'
MASTER_COLORS = [hair, eyes]
invisibleModifiers = ['feet_nude', 'blank']
maleRandomizeItems = {eyes: EYESGROUP,
 eyeshadow: SKINDETAILSGROUP,
 eyeliner: SKINDETAILSGROUP,
 lipstick: SKINDETAILSGROUP,
 blush: SKINDETAILSGROUP,
 hair: HAIRGROUP,
 eyebrows: HAIRGROUP,
 beard: HAIRGROUP,
 skinaging: SKINGROUP,
 scarring: SKINGROUP,
 freckles: SKINGROUP,
 muscle: BODYGROUP,
 weight: BODYGROUP,
 bottomouter: CLOTHESGROUP,
 topmiddle: CLOTHESGROUP,
 topouter: CLOTHESGROUP,
 feet: CLOTHESGROUP,
 outer: CLOTHESGROUP,
 topinner: CLOTHESGROUP,
 glasses: CLOTHESGROUP,
 p_earslow: PIERCINGGROUP,
 p_earshigh: PIERCINGGROUP,
 p_nose: PIERCINGGROUP,
 p_nostril: PIERCINGGROUP,
 p_brow: PIERCINGGROUP,
 p_lips: PIERCINGGROUP,
 p_chin: PIERCINGGROUP,
 t_head: TATTOOGROUP,
 s_head: SCARSGROUP}
femaleRandomizeItems = {eyes: EYESGROUP,
 eyeshadow: MAKEUPGROUP,
 eyeliner: MAKEUPGROUP,
 lipstick: MAKEUPGROUP,
 blush: MAKEUPGROUP,
 hair: HAIRGROUP,
 eyebrows: HAIRGROUP,
 skinaging: SKINGROUP,
 freckles: SKINGROUP,
 scarring: SKINGROUP,
 muscle: BODYGROUP,
 weight: BODYGROUP,
 bottomouter: CLOTHESGROUP,
 topmiddle: CLOTHESGROUP,
 topouter: CLOTHESGROUP,
 feet: CLOTHESGROUP,
 outer: CLOTHESGROUP,
 glasses: CLOTHESGROUP,
 p_earslow: PIERCINGGROUP,
 p_earshigh: PIERCINGGROUP,
 p_nose: PIERCINGGROUP,
 p_nostril: PIERCINGGROUP,
 p_brow: PIERCINGGROUP,
 p_lips: PIERCINGGROUP,
 p_chin: PIERCINGGROUP,
 t_head: TATTOOGROUP,
 s_head: SCARSGROUP}
randomizerBlacklist = {'makeup/eyes': ['eyes_10']}
recustomizationRandomizerBlacklist = [skintone,
 skinaging,
 freckles,
 scarring,
 muscle,
 weight]
randomizerCategoryBlacklist = [p_earslow,
 p_earshigh,
 p_nose,
 p_nostril,
 p_brow,
 p_lips,
 p_chin,
 t_head,
 t_armleft,
 t_armright,
 s_head,
 pr_armright,
 pr_armleft,
 augm_face]
maleOddsOfSelectingNone = {glasses: 0.75,
 beard: 0.5,
 topouter: 0.5,
 outer: 0.5,
 t_head: 0.0,
 s_head: 0.0}
maleOddsOfSelectingNoneFullRandomize = {eyeshadow: 0.95,
 eyeliner: 0.95,
 lipstick: 0.95,
 blush: 0.95,
 skinaging: 0.95,
 scarring: 0.95,
 freckles: 0.95,
 glasses: 0.95}
femaleOddsOfSelectingNone = {glasses: 0.75,
 topouter: 0.5,
 outer: 0.5,
 p_earslow: 0.8,
 p_earshigh: 0.8,
 p_nose: 0.8,
 p_nostril: 0.8,
 p_brow: 0.8,
 p_lips: 0.8,
 p_chin: 0.8,
 t_head: 0.0,
 s_head: 0.0}
femaleOddsOfSelectingNoneFullRandomize = {eyeshadow: 0.9,
 eyeliner: 0.9,
 lipstick: 0.9,
 blush: 0.9,
 skinaging: 0.95,
 freckles: 0.95,
 glasses: 0.95}
addWeightToCategories = [eyeshadow,
 eyeliner,
 lipstick,
 blush,
 skinaging]
RACESTEP = 1
BLOODLINESTEP = 2
CUSTOMIZATIONSTEP = 3
PORTRAITSTEP = 4
NAMINGSTEP = 5
MINIMALNAMINGSTEP = 6
COLORMAPPING = {eyes: (False, False),
 hair: (False, False),
 eyeshadow: (True, False),
 eyeliner: (True, False),
 blush: (True, False),
 lipstick: (True, True),
 t_head: (True, False)}
TUCKMAPPING = {topmiddle: ('dependants/drape', (topmiddle,), 'standard'),
 outer: ('dependants/hood', (outer,), 'robeam1'),
 feet: ('dependants/boottucking', (bottomouter,), 'standard'),
 bottomouter: ('dependants/waisttucking', (topmiddle, topouter), 'standard')}
TUCKCATEGORIES = ['dependants/drape',
 'dependants/hood',
 'dependants/boottucking',
 'dependants/waisttucking']
HELPTEXTS = {BODYGROUP: 'UI/CharacterCreation/HelpTexts/BodyShape',
 SKINGROUP: 'UI/CharacterCreation/HelpTexts/Skin',
 HAIRGROUP: 'UI/CharacterCreation/HelpTexts/Hair',
 EYESGROUP: 'UI/CharacterCreation/HelpTexts/Eyes',
 MAKEUPGROUP: 'UI/CharacterCreation/HelpTexts/Makeup',
 SKINDETAILSGROUP: 'UI/CharacterCreation/HelpTexts/SkinDetails',
 CLOTHESGROUP: 'UI/CharacterCreation/HelpTexts/Clothes',
 BACKGROUNDGROUP: 'UI/CharacterCreation/HelpTexts/Backgrounds',
 POSESGROUP: 'UI/CharacterCreation/HelpTexts/Poses',
 LIGHTSGROUP: 'UI/CharacterCreation/HelpTexts/Light',
 PIERCINGGROUP: 'UI/CharacterCreation/HelpTexts/Piercings',
 TATTOOGROUP: 'UI/CharacterCreation/HelpTexts/Tattoo',
 SCARSGROUP: 'UI/CharacterCreation/HelpTexts/Scars'}
PICKMAPPING = {('sculpt', 12): eyes,
 ('hair', 0): hair,
 ('hair', 1): eyebrows,
 ('hair', 2): beard,
 ('makeup', 0): eyeshadow,
 ('makeup', 1): blush,
 ('makeup', 2): lipstick,
 ('clothes', 0): topmiddle,
 ('clothes', 1): topmiddle,
 ('clothes', 2): bottomouter,
 ('clothes', 3): bottomouter,
 ('clothes', 4): feet}
REMOVEABLE = (glasses,
 topouter,
 topmiddle,
 outer,
 eyebrows,
 beard,
 eyeshadow,
 eyeliner,
 blush,
 lipstick,
 bottomouter,
 feet,
 bottommiddle,
 p_earslow,
 p_earshigh,
 p_nose,
 p_nostril,
 p_brow,
 p_lips,
 p_chin,
 t_head,
 t_armright,
 t_armleft,
 s_head,
 pr_armleft,
 pr_armright,
 augm_face)
SKINTYPECOLORS = {'c1': (0.678431, 0.580392, 0.552941, 1.0),
 'c2': (0.721569, 0.556863, 0.470588, 1.0),
 'c3': (0.631373, 0.52549, 0.415686, 1.0),
 'c4': (0.560784, 0.458824, 0.407843, 1.0),
 'c5': (0.580392, 0.443137, 0.356863, 1.0),
 'c6': (0.509804, 0.4, 0.337255, 1.0),
 'c7': (0.505882, 0.372549, 0.32549, 1.0),
 'c8': (0.466667, 0.360784, 0.286275, 1.0),
 'c9': (0.407843, 0.309804, 0.247059, 1.0),
 'c10': (0.34902, 0.254902, 0.227451, 1.0),
 'c11': (0.278431, 0.2, 0.180392, 1.0),
 'c12': (0.227451, 0.160784, 0.141176, 1.0),
 'c13': (0.180392, 0.137255, 0.121569, 1.0),
 'c14': (0.156863, 0.117647, 0.113725, 1.0)}
DEFAULSKINCOLORFORBLOODLINE = {1: 'c7',
 2: 'c6',
 3: 'c4',
 4: 'c12',
 5: 'c4',
 6: 'c9',
 7: 'c7',
 8: 'c4',
 11: 'c5',
 12: 'c8',
 13: 'c3',
 14: 'c8'}
SCENE_PATH_CUSTOMIZATION = 'res:/Graphics/Interior/characterCreation/Customization.red'
SCENE_PATH_RACE_SELECTION = 'res:/Graphics/Interior/characterCreation/RaceSelection.red'
CUSTOMIZATION_FLOOR = 'res:/Graphics/Interior/characterCreation/Plane/Floor.red'
COLOR = (1.0, 1.0, 1.0)
COLOR50 = (1.0, 1.0, 1.0, 0.5)
COLOR75 = (1.0, 1.0, 1.0, 0.75)
COLOR100 = (1.0, 1.0, 1.0, 1.0)
LIGHT_SETTINGS_ID = [10866,
 10742,
 10743,
 10744,
 10745,
 10746,
 10747]
LIGHT_COLOR_SETTINGS_ID = [10866,
 10748,
 10749,
 10750,
 10751,
 10752,
 10753]
backgroundOptions = ['res:/UI/Texture/CharacterCreation/backdrops/Background_1.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_2.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_3.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_4.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_5.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_6.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_7.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_8.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_9.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_10.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_11.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_12.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_13.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_14.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_15.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_16.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_17.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_18.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_19.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_20.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_21.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_22.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_23.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_24.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_25.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_26.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_27.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_28.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_29.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_30.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_31.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_32.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_33.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_34.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_35.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_36.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_37.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_38.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_39.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_40.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_41.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_42.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_43.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_44.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_45.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_46.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_47.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_48.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_49.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_50.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_51.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_52.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_53.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_54.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_55.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_56.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_57.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_58.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_59.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_60.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_61.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_62.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_63.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_64.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_65.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_66.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_67.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_68.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_69.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_70.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_71.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_72.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_73.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_74.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_75.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_76.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_77.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_78.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_79.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_80.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_81.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_82.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_83.dds',
 'res:/UI/Texture/CharacterCreation/backdrops/Background_84.dds']
greenscreenBackgroundOptions = ['res:/UI/Texture/CharacterCreation/backdrops/Background_1001.dds']
BASE_HAIR_COLOR_FEMALE = 'res:/Graphics/Character/Female/Paperdoll/hair/Colors/BaseColor.base'
BASE_HAIR_COLOR_MALE = 'res:/Graphics/Character/Male/Paperdoll/hair/Colors/BaseColor.base'
HAIRCOLOR_RESTRICTION_FEMALE = 'res:/Graphics/Character/Female/Paperdoll/hair/Colors/restrictions'
HAIRCOLOR_RESTRICTION_MALE = 'res:/Graphics/Character/Male/Paperdoll/hair/Colors/restrictions'
HAIRCOLORS = ['res:/Graphics/Character/Female/Paperdoll/hair/Colors/', 'res:/Graphics/Character/Male/Paperdoll/hair/Colors/']
BASE_HAIR_TYPE_FEMALE = 'res:/Graphics/Character/Female/Paperdoll/hair/Hair_Stubble_01/Types/Hair_Stubble_01.type'
BASE_HAIR_TYPE_MALE = 'res:/Graphics/Character/Male/Paperdoll/hair/Hair_Stubble_02/Types/Hair_Stubble_02.type'
EYESHADOWCOLOR_RESTRICTION_FEMALE = 'res:/Graphics/Character/Female/Paperdoll/Makeup/EyeShadow/Colors/restrictions'
EYESHADOWCOLORS = ['res:/Graphics/Character/Female/Paperdoll/Makeup/EyeShadow/Colors/', 'res:/Graphics/Character/Male/Paperdoll/Makeup/EyeShadow/Colors/']
HEADTATTOOCOLOR_RESTRICTION_FEMALE = 'res:/Graphics/Character/Female/Paperdoll/Tattoo/Head/Colors/restrictions'
HEADTATTOOCOLOR_RESTRICTION_MALE = 'res:/Graphics/Character/Male/Paperdoll/Tattoo/Head/Colors/restrictions'
HEADTATTOOCOLORS = ['res:/Graphics/Character/Female/Paperdoll/Tattoo/Head/Colors/', 'res:/Graphics/Character/Male/Paperdoll/Tattoo/Head/Colors/']
weightLimits = {t_head: {'default': [0.62, 0.91],
          ('white_A', None): [0.44, 0.73]}}
defaultIntensity = {t_head: 1.0}
FACE_POSE_CONTROLPARAMS = [['ControlParameters|BrowLeftCurl', 0.5],
 ['ControlParameters|BrowRightCurl', 0.5],
 ['ControlParameters|BrowLeftUpDown', 0.5],
 ['ControlParameters|BrowRightUpDown', 0.5],
 ['ControlParameters|BrowLeftTighten', 0.5],
 ['ControlParameters|BrowRightTighten', 0.5],
 ['ControlParameters|SquintLeft', 0.0],
 ['ControlParameters|SquintRight', 0.0],
 ['ControlParameters|FrownLeft', 0.0],
 ['ControlParameters|FrownRight', 0.0],
 ['ControlParameters|SmileLeft', 0.0],
 ['ControlParameters|SmileRight', 0.0],
 ['ControlParameters|HeadTilt', 0.0],
 ['ControlParameters|JawSideways', 0.5],
 ['ControlParameters|JawUp', 1.0],
 ['ControlParameters|EyesLookVertical', 0.5],
 ['ControlParameters|EyesLookHorizontal', 0.5],
 ['ControlParameters|EyeClose', 0.0],
 ['ControlParameters|OrientChar', 0.5]]
MODE_FULLINITIAL_CUSTOMIZATION = 1
MODE_LIMITED_RECUSTOMIZATION = 2
MODE_FULL_RECUSTOMIZATION = 3
MODE_FULL_BLOODLINECHANGE = 4
MODE_INITIAL_MINI_CUSTOMIZATION = 5
CAMERA_MODE_DEFAULT = 0
CAMERA_MODE_FACE = 1
CAMERA_MODE_BODY = 2
CAMERA_MODE_PORTRAIT = 3
