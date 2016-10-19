#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\evegraphics\wrappers\runtimeInstancedMesh.py
import trinity
INSTANCE_TYPE_1LAYERV2 = '1layerv2'
INSTANCE_TYPE_CIRCLE_FALLOFF = 'simple'
_DEFAULT_TEXTURE = 'res:/texture/hringur.dds'
_DEFAULT_GEOMETRY = 'res:/Graphics/Generic/UnitPlane/UnitPlane.gr2'
INSTANCE_DEFAULT_PATH = {}
INSTANCE_EFFECTS = {INSTANCE_TYPE_CIRCLE_FALLOFF: 'res:/graphics/effect/managed/space/specialfx/particles/static/SimpleCircularFalloff.fx',
 INSTANCE_TYPE_1LAYERV2: 'res:/graphics/effect/managed/space/specialfx/particles/static/1LayerV2.fx'}
_ELEMENT_TYPE_CUSTOM = trinity.PARTICLE_ELEMENT_TYPE.CUSTOM
_ELEMENT_TYPE_POSITION = trinity.PARTICLE_ELEMENT_TYPE.POSITION
INSTANCE_ELEMENT_DECLARATIONS = {INSTANCE_TYPE_1LAYERV2: ([(_ELEMENT_TYPE_POSITION, 0, 3),
                           (_ELEMENT_TYPE_CUSTOM, 0, 1),
                           (_ELEMENT_TYPE_CUSTOM, 1, 1),
                           (_ELEMENT_TYPE_CUSTOM, 2, 4),
                           (_ELEMENT_TYPE_CUSTOM, 3, 1),
                           (_ELEMENT_TYPE_CUSTOM, 4, 4)], (('position', (0.0, 0.0, 0.0)),
                           ('size', 1.0),
                           ('rotation', 0.0),
                           ('color0', (1.0, 1.0, 1.0, 1.0)),
                           ('atlasID', 0.0),
                           ('color1', (1.0, 1.0, 1.0, 1.0)))),
 INSTANCE_TYPE_CIRCLE_FALLOFF: ([(_ELEMENT_TYPE_POSITION, 0, 3),
                                 (_ELEMENT_TYPE_CUSTOM, 0, 1),
                                 (_ELEMENT_TYPE_CUSTOM, 1, 4),
                                 (_ELEMENT_TYPE_CUSTOM, 2, 2)], (('position', (0.0, 0.0, 0.0)),
                                 ('size', 1.0),
                                 ('color', (1.0, 1.0, 1.0, 1.0)),
                                 ('falloffRange', (0.0, 0.0))))}

def _CreateRuntimeInstanceMesh(instanceType, additive = False):
    effect = ''
    if instanceType in INSTANCE_EFFECTS:
        effect = INSTANCE_EFFECTS[instanceType]
    mesh = trinity.Tr2InstancedMesh()
    mesh.instanceGeometryResPath = ''
    mesh.geometryResPath = _DEFAULT_GEOMETRY
    mesh.instanceGeometryResource = trinity.Tr2RuntimeInstanceData()
    area = trinity.Tr2MeshArea()
    area.effect = trinity.Tr2Effect()
    area.effect.effectFilePath = effect
    trinity.WaitForResourceLoads()
    area.effect.PopulateParameters()
    for each in area.effect.resources:
        each.resourcePath = _DEFAULT_TEXTURE

    if additive:
        mesh.additiveAreas.append(area)
    else:
        mesh.transparentAreas.append(area)
    return mesh


class ParticleInstance:

    def __init__(self, declaration, **kwargs):
        self.fields = declaration[1]
        for fieldName, defaultValue in self.fields:
            setattr(self, fieldName, defaultValue)

        for key, val in kwargs.items():
            setattr(self, key, val)

    def GetData(self):
        data = []
        for fieldName, _ in self.fields:
            data.append(getattr(self, fieldName))

        return tuple(data)


class EffectParameterList:

    def __init__(self, effect):
        for param in effect.parameters:
            setattr(self, param.name, param)

        for tex in effect.resources:
            setattr(self, tex.name, tex)


class RuntimeInstancedMesh:

    def __init__(self, instanceType, **defaults):
        if instanceType in INSTANCE_DEFAULT_PATH:
            self.mesh = trinity.Load(INSTANCE_DEFAULT_PATH[instanceType])
        else:
            self.mesh = _CreateRuntimeInstanceMesh(instanceType)
        self.instanceData = self.mesh.instanceGeometryResource
        self.declaration = INSTANCE_ELEMENT_DECLARATIONS[instanceType]
        self.instanceData.SetElementLayout(self.declaration[0])
        self.effectParameters = EffectParameterList(self.mesh.Find('trinity.Tr2Effect')[0])
        self.fieldDefaults = defaults
        self.particles = []
        self.data = []

    def AddParticle(self, **fields):
        attribs = {}
        for each in self.fieldDefaults:
            if each not in fields:
                attribs[each] = self.fieldDefaults[each]

        for key, val in fields.items():
            attribs[key] = val

        particle = ParticleInstance(self.declaration, **attribs)
        self.particles.append(particle)
        self.data.append(particle.GetData())
        return len(self.particles)

    def Submit(self):
        self.instanceData.SetData(self.data)
        self.instanceData.UpdateData()
        self.instanceData.UpdateBoundingBox()
        self.mesh.minBounds = self.instanceData.aabbMin
        self.mesh.maxBounds = self.instanceData.aabbMax
