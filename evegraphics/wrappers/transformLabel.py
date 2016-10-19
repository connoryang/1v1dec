#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\evegraphics\wrappers\transformLabel.py
import trinity
import carbonui.fontconst as fontConst

def _GetDefaultFont():
    try:
        return uicore.font.GetFontFamilyBasedOnClientLanguageID()[fontConst.STYLE_DEFAULT][2]
    except:
        return 'res:/UI/Fonts/EveSansNeue-ExpandedBold.otf'


class TransformableLabel(object):

    def __init__(self, text, parent, size = 72, shadow = 0, hspace = 8, font = None):
        self.transform = trinity.EveTransform()
        self.transform.mesh = trinity.Tr2Mesh()
        self.transform.mesh.geometryResPath = 'res:/Model/Global/zsprite.gr2'
        self.transform.modifier = 1
        self.measurer = trinity.Tr2FontMeasurer()
        self.measurer.limit = 0
        if font is None:
            font = _GetDefaultFont()
        self.measurer.font = font
        self.measurer.fontSize = size
        self.measurer.letterSpace = hspace
        area = trinity.Tr2MeshArea()
        self.transform.mesh.transparentAreas.append(area)
        area.effect = self.effect = trinity.Tr2Effect()
        sampler = list(self.effect.samplerOverrides.GetDefaultValue())
        sampler[0] = 'DiffuseMapSampler'
        sampler[1] = trinity.TRITADDRESS_CLAMP
        sampler[2] = trinity.TRITADDRESS_CLAMP
        self.effect.samplerOverrides.append(tuple(sampler))
        self.effect.effectFilePath = 'res:/Graphics/Effect/Managed/Space/SpecialFX/TextureColor.fx'
        diffuseColor = trinity.Tr2Vector4Parameter()
        diffuseColor.name = 'DiffuseColor'
        self.effect.parameters.append(diffuseColor)
        self.diffuseColor = diffuseColor
        self.diffuseMap = trinity.TriTextureParameter()
        self.diffuseMap.name = 'DiffuseMap'
        self.effect.resources.append(self.diffuseMap)
        parent.children.append(self.transform)
        trinity.device.RegisterResource(self)
        self.SetText(text)

    def Destroy(self):
        self.measurer.Reset()
        self.measurer = None
        self.transform = None
        self.diffuseMap.SetResource(None)
        self.diffuseMap = None
        self.effect = None
        self.transform = None

    def SetText(self, text):
        self.measurer.Reset()
        self.measurer.AddText(text.upper())
        height = self.measurer.ascender - self.measurer.descender
        width = self.measurer.cursorX
        self.measurer.CommitText(0, self.measurer.ascender)
        self.transform.scaling = (width, height, 0)
        self.RebuildResource()

    def SetDiffuseColor(self, color):
        self.diffuseColor.value = color

    def OverrideText(self):
        pass

    def SetDisplay(self, display):
        self.transform.display = display

    def OnInvalidate(self, level):
        pass

    def RebuildResource(self):
        height = self.measurer.ascender - self.measurer.descender
        width = self.measurer.cursorX
        tr = trinity.TriTextureRes(width, height, 1, trinity.PIXEL_FORMAT.B8G8R8A8_UNORM, trinity.BUFFER_USAGE_FLAGS.CPU_WRITE)
        self.measurer.DrawToTexture(tr)
        self.diffuseMap.SetResource(tr)

    def OnCreate(self, dev):
        if self.diffuseMap is None:
            return
        if self.diffuseMap.resource is not None and self.diffuseMap.resource.isGood:
            return
        self.RebuildResource()


class HoverLabel(TransformableLabel):

    def __init__(self, text, parent, scaling = 1.0, size = 72, shadow = 0, hspace = 8, font = None):
        self.parent = parent
        self.extraTransform = trinity.EveTransform()
        self.extraTransform.useDistanceBasedScale = True
        self.extraTransform.distanceBasedScaleArg1 = 1.0
        self.extraTransform.distanceBasedScaleArg2 = 0.05
        self.extraTransform.scaling = (scaling, scaling, scaling)
        parent.children.append(self.extraTransform)
        TransformableLabel.__init__(self, text, self.extraTransform, size, shadow, hspace, font)
        self.transform.translation = (0, self.transform.scaling[1] * 0.5, 0)

    def SetText(self, text):
        TransformableLabel.SetText(self, text)
        self.transform.translation = (0, self.transform.scaling[1] * 0.5, 0)

    def SetPosition(self, pos):
        self.extraTransform.translation = pos

    def SetDistanceScale2(self, value):
        self.extraTransform.distanceBasedScaleArg2 = value

    def Destroy(self):
        TransformableLabel.Destroy(self)
        del self.extraTransform.children[:]
        self.extraTransform = None
