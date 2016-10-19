#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\trinity\postprocess.py
import ast
import logging
import math
import re
import blue
import trinity
import yamlext

def _GetValueType(value):
    if isinstance(value, (str, unicode)):
        return 'texture'
    if isinstance(value, (tuple, list)):
        if len(value) == 2:
            return 'vector2'
        if len(value) == 3:
            return 'vector3'
        if len(value) == 4:
            return 'vector4'
        raise ValueError()
    if isinstance(value, bool):
        return 'bool'
    if isinstance(value, (float, int, long)):
        return 'float'
    raise ValueError()


def _GetParameterType(data):
    if 'type' in data:
        return data['type']
    return _GetValueType(data['value'])


def _GetConditionDependencies(condition):
    dependencies = []
    for node in ast.walk(ast.parse(condition)):
        if isinstance(node, ast.Name):
            dependencies.append(node.id)

    return dependencies


def _FindNamedItem(items, name):
    for each in items:
        if each.name == name:
            return each

    raise KeyError()


class _LazyParameters(object):

    def __init__(self, parameters):
        self._parameters = parameters

    def __getitem__(self, item):
        return self._parameters[item].GetValue()


def _EvaluateString(expression, parameters):
    try:
        return eval(expression, {'platform': trinity.platform,
         'math': math}, _LazyParameters(parameters))
    except BaseException as e:
        params = []
        for k, v in parameters.iteritems():
            try:
                params.append('%s = %s' % (k, v.GetValue()))
            except:
                params.append('%s = ???' % k)

        logging.exception('Exception when evaluating expression %s with parameters %s', expression, '\n'.join(params))
        raise e


class Parameter(object):

    def __init__(self, name, data):
        self.name = name
        self.group = data.get('group')
        self.description = data.get('description', '')
        self._type = _GetParameterType(data)
        self._bindings = {}

    def UpdateValue(self, parameters):
        self._UpdateBindings()

    def GetValue(self):
        pass

    def GetExposedValue(self):
        return self.GetValue()

    def SetValue(self, value):
        pass

    def SetExposedValue(self, value):
        self.SetValue(value)

    def _GetEffectParameter(self, effect, name):
        raise NotImplementedError()

    def _ApplyToObject(self, obj, name):
        setattr(obj, name, self.GetValue())

    def _ApplyToEffect(self, obj, name):
        self._ApplyToObject(obj, name)

    def Bind(self, obj, name):
        if isinstance(obj, trinity.Tr2Effect):
            self._bindings[obj, name] = self._GetEffectParameter(obj, name) + (self._ApplyToEffect,)
        else:
            self._bindings[obj, name] = (obj, name, self._ApplyToObject)

    def Unbind(self, obj, name):
        try:
            del self._bindings[obj, name]
        except KeyError:
            pass

    def GetDependencies(self):
        return ()

    def _UpdateBindings(self):
        for obj, name, applyFunc in self._bindings.itervalues():
            applyFunc(obj, name)

    def UpdateUsage(self, usage):
        usage[self.name] = True

    def Load(self, parameters):
        pass

    def Unload(self):
        pass


class NumericParameter(Parameter):

    def __init__(self, name, data):
        super(NumericParameter, self).__init__(name, data)
        self.value = data['value']
        if isinstance(self.value, list):
            self.value = tuple(self.value)
        self.currentValue = self.value
        if self._type == 'float':
            self.paramType = trinity.Tr2FloatParameter
        elif self._type == 'vector2':
            self.paramType = trinity.Tr2Vector2Parameter
        elif self._type == 'vector3':
            self.paramType = trinity.Tr2Vector3Parameter
        elif self._type == 'vector4':
            self.paramType = trinity.Tr2Vector4Parameter
        else:
            raise RuntimeError()
        self._dependencies = _GetConditionDependencies(self.value) if isinstance(self.value, basestring) else []

    def _GetEffectParameter(self, effect, name):
        try:
            param = _FindNamedItem(effect.parameters, name)
        except KeyError:
            param = self.paramType()
            param.name = name
            effect.parameters.append(param)

        return (param, 'value')

    def _ApplyToEffect(self, obj, name):
        obj.value = self.currentValue

    def GetValue(self):
        return self.currentValue

    def SetValue(self, value):
        self.value = value

    def UpdateValue(self, parameters):
        if isinstance(self.value, (str, unicode)):
            self.currentValue = _EvaluateString(self.value, parameters)
        else:
            self.currentValue = self.value
        super(NumericParameter, self).UpdateValue(parameters)

    def GetDependencies(self):
        return self._dependencies


class BooleanParameter(Parameter):

    def __init__(self, name, data):
        super(BooleanParameter, self).__init__(name, data)
        self.value = data['value']
        self.paramType = trinity.Tr2FloatParameter

    def GetValue(self):
        return self.value

    def SetValue(self, value):
        self.value = value

    def _GetEffectParameter(self, effect, name):
        try:
            param = _FindNamedItem(effect.parameters, name)
        except KeyError:
            param = trinity.Tr2FloatParameter()
            param.name = name
            effect.parameters.append(param)

        return (param, 'value')

    def _ApplyToEffect(self, obj, name):
        obj.value = 1 if self.value else 0


class TextureParameter(Parameter):

    def __init__(self, name, data):
        super(TextureParameter, self).__init__(name, data)
        if self._type != 'texture':
            raise RuntimeError()
        self.resourcePath = data['value']
        self.resource = blue.resMan.GetResource(self.resourcePath)
        self.resource.name = name

    def GetValue(self):
        return self.resource

    def SetValue(self, value):
        self.resourcePath = value
        self.resource = blue.resMan.GetResource(self.resourcePath)
        self.resource.name = self.name

    def GetExposedValue(self):
        return self.resourcePath

    def _GetEffectParameter(self, effect, name):
        try:
            param = _FindNamedItem(effect.resources, name)
        except KeyError:
            param = trinity.TriTextureParameter()
            param.name = name
            effect.resources.append(param)

        return (param, 'resourcePath')

    def _ApplyToEffect(self, obj, name):
        obj.resourcePath = self.resourcePath


class GpuBufferParameter(Parameter):

    def __init__(self, name, data):
        super(GpuBufferParameter, self).__init__(name, data)
        if self._type != 'gpubuffer':
            raise RuntimeError()
        reader = blue.DictReader()
        self.buffer = reader.CreateObject(data['buffer'])

    def GetValue(self):
        return self.buffer

    def SetValue(self, value):
        self.buffer = value

    def _GetEffectParameter(self, effect, name):
        try:
            param = _FindNamedItem(effect.resources, name)
        except KeyError:
            param = trinity.Tr2GeometryBufferParameter()
            param.name = name
            effect.resources.append(param)

        return (param, 'gpuBuffer')

    def _ApplyToEffect(self, obj, name):
        obj.gpuBuffer = self.buffer


class BuiltinRenderTargetParameter(Parameter):

    def __init__(self, name, rt):
        super(BuiltinRenderTargetParameter, self).__init__(name, {'type': 'rendertarget'})
        self.rt = rt
        self.texture = trinity.TriTextureRes()
        self.texture.name = self.name
        self.texture.SetFromRenderTarget(self.rt)

    def GetValue(self):
        return self.rt

    def SetValue(self, value):
        self.rt = value
        self.texture.SetFromRenderTarget(self.rt)

    def _GetEffectParameter(self, effect, name):
        try:
            param = _FindNamedItem(effect.resources, name)
        except KeyError:
            param = trinity.TriTextureParameter()
            param.name = name
            effect.resources.append(param)

        return (param, 'resourcePath')

    def _ApplyToEffect(self, obj, name):
        obj.SetResource(self.texture)


class RenderTargetParameter(Parameter):

    def __init__(self, name, data):
        super(RenderTargetParameter, self).__init__(name, data)
        if self._type != 'rendertarget':
            raise RuntimeError()
        self._data = data
        self.rt = None
        self.texture = trinity.TriTextureRes()
        self.texture.name = self.name

    def UpdateValue(self, parameters):
        if 'copyFrom' in self._data:
            copyFrom = parameters[self._data['copyFrom']].GetValue()
            if copyFrom:
                if 'width' in self._data:
                    if isinstance(self._data['width'], float):
                        width = int(self._data['width'] * copyFrom.width)
                    else:
                        width = self._data['width']
                else:
                    width = copyFrom.width
                if 'height' in self._data:
                    if isinstance(self._data['height'], float):
                        height = int(self._data['height'] * copyFrom.height)
                    else:
                        height = self._data['height']
                else:
                    height = copyFrom.height
                self.rt = trinity.Tr2RenderTarget()
                self.rt.CreateEx(width, height, self._data.get('mipCount', copyFrom.mipCount), self._data.get('format', copyFrom.format), self._data.get('multiSampleType', copyFrom.multiSampleType), self._data.get('multiSampleQuality', copyFrom.multiSampleQuality), trinity.EX_FLAG.BIND_UNORDERED_ACCESS if self._data.get('uav', False) else 0)
                self.rt.name = self.name
            else:
                self.rt = None
        else:
            self.rt = trinity.Tr2RenderTarget()
            self.rt.CreateEx(self._data['width'], self._data['height'], self._data.get('mipCount', 1), self._data['format'], self._data.get('multiSampleType', 1), self._data.get('multiSampleQuality', 1), trinity.EX_FLAG.BIND_UNORDERED_ACCESS if self._data.get('uav', False) else 0)
            self.rt.name = self.name
        self.texture.SetFromRenderTarget(self.rt)
        self._UpdateBindings()

    def GetValue(self):
        return self.rt

    def _GetEffectParameter(self, effect, name):
        try:
            param = _FindNamedItem(effect.resources, name)
        except KeyError:
            param = trinity.TriTextureParameter()
            param.name = name
            effect.resources.append(param)

        return (param, 'resourcePath')

    def _ApplyToObject(self, obj, name):
        setattr(obj, name, self.GetValue())

    def _ApplyToEffect(self, obj, name):
        obj.SetResource(self.texture)

    def GetDependencies(self):
        if 'copyFrom' in self._data:
            return (self._data['copyFrom'],)
        return ()

    def UpdateUsage(self, usage):
        super(RenderTargetParameter, self).UpdateUsage(usage)
        if 'copyFrom' in self._data:
            usage[self._data['copyFrom']] = True

    def Load(self, parameters):
        if not self.rt:
            self.UpdateValue(parameters)

    def Unload(self):
        self.rt = None
        self._UpdateBindings()


class ConditionParameter(Parameter):

    def __init__(self, name, data):
        super(ConditionParameter, self).__init__(name, data)
        if self._type != 'condition':
            raise RuntimeError()
        self.condition = data['condition']
        self.true = data[True]
        self.false = data[False]
        self.active = None
        self._dependencies = [self.true, self.false] + _GetConditionDependencies(data['condition'])

    def UpdateValue(self, parameters):
        if _EvaluateString(self.condition, parameters):
            active = parameters[self.true]
        else:
            active = parameters[self.false]
        if self.active != active:
            for obj, name in self._bindings:
                self.active.Unbind(obj, name)

            self.active = active
            for obj, name in self._bindings:
                self.active.Bind(obj, name)

        self.active.UpdateValue(parameters)

    def GetValue(self):
        return self.active.GetValue()

    def GetDependencies(self):
        return self._dependencies

    def Bind(self, obj, name):
        super(ConditionParameter, self).Bind(obj, name)
        if self.active:
            self.active.Bind(obj, name)

    def Unbind(self, obj, name):
        super(ConditionParameter, self).Unbind(obj, name)
        if self.active:
            self.active.Bind(obj, name)

    def _GetEffectParameter(self, effect, name):
        return (None, None)

    def UpdateUsage(self, usage):
        super(ConditionParameter, self).UpdateUsage(usage)
        if self.active:
            self.active.UpdateUsage(usage)


PARAMETER_TYPES = {'condition': ConditionParameter,
 'rendertarget': RenderTargetParameter,
 'texture': TextureParameter,
 'vector2': NumericParameter,
 'vector3': NumericParameter,
 'vector4': NumericParameter,
 'float': NumericParameter,
 'bool': BooleanParameter,
 'gpubuffer': GpuBufferParameter}

def TopoSort(dependencies):
    if not dependencies:
        raise StopIteration()
    data = dict(dependencies)
    for k, v in data.items():
        v.discard(k)

    extra_items_in_deps = reduce(set.union, data.values()) - set(data.keys())
    data.update({item:set() for item in extra_items_in_deps})
    while True:
        ordered = set((item for item, dep in data.items() if not dep))
        if not ordered:
            break
        for each in ordered:
            yield each

        data = {item:dep - ordered for item, dep in data.items() if item not in ordered}

    if data:
        raise RuntimeError('A cyclic dependency exists amongst %r' % dependencies)


def _IsIdentifier(s):
    return re.match('^[_A-Za-z][_a-zA-Z0-9]*$', s)


class PostProcess(object):

    def __init__(self):
        super(PostProcess, self).__setattr__('renderJob', trinity.TriRenderJob())
        self.renderJob.name = 'Post Process'
        self.renderJob.enabled = False
        super(PostProcess, self).__setattr__('source', None)
        super(PostProcess, self).__setattr__('dest', None)
        super(PostProcess, self).__setattr__('_data', None)
        super(PostProcess, self).__setattr__('_rj', trinity.TriRenderJob())
        super(PostProcess, self).__setattr__('_parameters', {'__sourcert__': BuiltinRenderTargetParameter('__sourcert__', self.source),
         '__destrt__': BuiltinRenderTargetParameter('__sourcert__', self.dest)})
        super(PostProcess, self).__setattr__('_dependencies', {})
        super(PostProcess, self).__setattr__('_stepDependencies', [])
        super(PostProcess, self).__setattr__('_builtInParameters', self._parameters.keys())
        super(PostProcess, self).__setattr__('__members__', [])
        super(PostProcess, self).__setattr__('_loadPending', False)
        self.Clear()

    def LoadParameters(self, path):
        params = yamlext.load(blue.paths.GetFileContentsWithYield(path))
        for name, value in params.iteritems():
            self._parameters[name].SetValue(value)

        self._UpdateParameters()

    def SaveParameters(self, path):
        params = {}
        for name, param in self._parameters.iteritems():
            value = param.GetValue()
            if isinstance(value, (int,
             long,
             float,
             tuple,
             bool)):
                params[name] = value

        yamlext.dumpfile(params, blue.paths.ResolvePathForWriting(path))

    def Clear(self):
        data = '\nparameters:\n    _source:\n        type: condition\n        condition: __sourcert__ and __sourcert__.multiSampleType > 1\n        true: _sourceCopy\n        false: __sourcert__\n    _sourceCopy:\n        type: rendertarget\n        multiSampleType: 1\n        multiSampleQuality: 0\n        copyFrom: __sourcert__\nsteps:\n-   type: Resolve\n    name: Resolve Source into Dest\n    condition: __sourcert__.multiSampleType > 1 and __destrt__\n    parameters:\n        destination: __destrt__\n        source: __sourcert__\n-   type: Resolve\n    name: Resolve Source into a Temp RT\n    condition: __sourcert__.multiSampleType > 1 and not __destrt__\n    parameters:\n        destination: _sourceCopy\n        source: __sourcert__\n\n-   type: PushDepthStencil\n    name: Push NULL DS\n    parameters:\n        pushCurrent: False\n-   type: PushRenderTarget\n    name: Backup RT 0\n    parameters:\n        renderTarget: __destrt__\n\n-   type: RenderTexture\n    name: Render to Dest\n    condition: not __destrt__\n    parameters:\n        renderTarget: _source\n\n-   type: PopDepthStencil\n    name: Restore DS\n-   type: PopRenderTarget\n    name: Restore RT 0\n'
        self._data = yamlext.loads(data)
        del self.renderJob.steps[:]
        if self.source:
            self._LoadData(self._data)
            super(PostProcess, self).__setattr__('_loadPending', False)
        else:
            super(PostProcess, self).__setattr__('_loadPending', True)

    def _SetVariable(self, name, value):
        self._parameters[name].SetExposedValue(value)
        self._UpdateParameters((name,))

    def SetSource(self, source):
        super(PostProcess, self).__setattr__('source', source)
        self._SetVariable('__sourcert__', source)
        self.renderJob.enabled = True if source else False
        if self.source and self._loadPending:
            self._LoadData(self._data)
            super(PostProcess, self).__setattr__('_loadPending', False)

    def SetDest(self, dest):
        super(PostProcess, self).__setattr__('dest', dest)
        self._SetVariable('__destrt__', dest)

    def _ExpandChangedParams(self, changedParams = None):
        if changedParams is None:
            changedParams = self._parameters.keys()
        cp = set(changedParams)
        for each in changedParams:
            cp = cp.union({k for k, v in self._dependencies.iteritems() if each in v})

        return cp

    def _UpdateParameters(self, changedParams = None):
        changedParams = self._ExpandChangedParams(changedParams)
        for p in TopoSort(self._dependencies):
            if p in changedParams:
                self._parameters[p].UpdateValue(self._parameters)

        used = {k:False for k in self._parameters.iterkeys()}
        for params, condition, steps in self._stepDependencies:
            if condition:
                enabled = True if _EvaluateString(condition, self._parameters) else False
            else:
                enabled = True
            if params.intersection(changedParams):
                for step in steps:
                    step.enabled = enabled

            if enabled:
                for name in params:
                    self._parameters[name].UpdateUsage(used)

        for name, is_used in used.iteritems():
            if is_used:
                self._parameters[name].Load(self._parameters)
            else:
                self._parameters[name].Unload()

    def Load(self, path):
        self.Clear()
        self._data = yamlext.load(blue.paths.GetFileContentsWithYield(path))
        if self.source:
            self._LoadData(self._data)
            super(PostProcess, self).__setattr__('_loadPending', False)
        else:
            super(PostProcess, self).__setattr__('_loadPending', True)

    def _LoadData(self, data):
        del self.__members__[:]
        self._dependencies.clear()
        del self._stepDependencies[:]
        for k in list(self._parameters.keys()):
            if k not in self._builtInParameters:
                del self._parameters[k]

        for key, value in data.get('parameters', {}).iteritems():
            self._AddVariable(key, value)

        self.__members__.sort()
        self._UpdateParameters()
        tempVars = self._CreateTempVariables(data)
        self._UpdateParameters()
        del self.renderJob.steps[:]
        for each in data.get('steps', []):
            usedParameters = set()
            step = getattr(trinity, 'TriStep%s' % each['type'])()
            for key, value in each.iteritems():
                if key not in ('type', 'parameters', 'effectParameters', 'condition', 'renderTargets'):
                    if isinstance(value, dict):
                        reader = blue.DictReader()
                        value = reader.CreateObject(value)
                    setattr(step, key, value)

            if 'parameters' in each:
                for key, value in each['parameters'].iteritems():
                    if isinstance(value, basestring):
                        if value in tempVars:
                            value = tempVars[value]
                        self._parameters[value].Bind(step, key)
                        usedParameters.add(value)
                    else:
                        setattr(step, key, value)

            if 'effectParameters' in each:
                for key, value in each['effectParameters'].iteritems():
                    if value in tempVars:
                        value = tempVars[value]
                    self._parameters[value].Bind(step.effect, key)
                    usedParameters.add(value)

            steps = [step]
            if 'condition' in each:
                if not _EvaluateString(each['condition'], self._parameters):
                    step.enabled = False
            for indx, rt in each.get('renderTargets', {}).iteritems():
                setrt = trinity.TriStepSetRenderTarget(self._parameters[rt].GetValue())
                self._parameters[rt].Bind(setrt, 'renderTarget')
                setrt.name = 'Set RT %s for %s' % (indx, each.get('name', ''))
                setrt.enabled = step.enabled
                self.renderJob.steps.append(setrt)
                steps.append(setrt)
                usedParameters.add(rt)

            self.renderJob.steps.append(step)
            if 'condition' in each:
                self._stepDependencies.append((usedParameters.union(_GetConditionDependencies(each['condition'])), each['condition'], steps))
            else:
                self._stepDependencies.append((usedParameters, None, steps))

        self._UpdateParameters()

    def _CreateTempVariables(self, data):
        tempVars = {}
        for each in data.get('steps', []):
            for key, value in each.get('parameters', {}).iteritems():
                if isinstance(value, basestring) and not _IsIdentifier(value) and value not in tempVars:
                    name = '_ppTemp%s' % len(tempVars)
                    val = _EvaluateString(value, self._parameters)
                    self._AddVariable(name, {'value': value,
                     'type': _GetValueType(val)})
                    tempVars[value] = name

            for key, value in each.get('effectParameters', {}).iteritems():
                if isinstance(value, basestring) and not _IsIdentifier(value) and value not in tempVars:
                    name = '_ppTemp%s' % len(tempVars)
                    val = _EvaluateString(value, self._parameters)
                    self._AddVariable(name, {'value': value,
                     'type': _GetValueType(val)})
                    tempVars[value] = name

        return tempVars

    def _AddVariable(self, name, description):
        pt = PARAMETER_TYPES[_GetParameterType(description)]
        self._parameters[name] = pt(name, description)
        self._dependencies[name] = set()
        for each in self._parameters[name].GetDependencies():
            self._dependencies[name].add(each)

        self.__members__.append(name)

    def __getattr__(self, item):
        if item in self._parameters:
            return self._parameters[item].GetExposedValue()
        raise AttributeError()

    def __setattr__(self, key, value):
        if key == 'source':
            self.SetSource(value)
        elif key == 'dest':
            self.SetDest(value)
        elif key == '_data':
            super(PostProcess, self).__setattr__('_data', value)
        elif key in self._parameters:
            self._SetVariable(key, value)
        else:
            raise AttributeError()

    def _JessicaGetGroup(self, attribute):
        if attribute in self._parameters:
            return self._parameters[attribute].group

    def _JessicaGetDescription(self, attribute):
        if attribute in self._parameters:
            return self._parameters[attribute].description
