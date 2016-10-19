#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\environment\spaceObject\harvestableGasCloud.py
import math
import random
import geo2
import trinity
from eve.client.script.environment.spaceObject.cloud import Cloud
from eve.client.script.environment.spaceObject.spaceObject import SpaceObject

class HarvestableGasCloud(Cloud):

    def LoadModel(self, fileName = None, loadedModel = None):
        if trinity.platform != 'dx11':
            fileName = self.typeData.get('graphicFile')
            fileName = fileName.replace('.red', '_fallback.red')
        SpaceObject.LoadModel(self, fileName, loadedModel)

    def Assemble(self):
        Cloud.Assemble(self)
        self.model.rotation = geo2.QuaternionRotationSetYawPitchRoll(random.random() * math.pi * 2.0, random.random() * math.pi, random.random() * math.pi)
