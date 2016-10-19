#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\crates\storage.py
import collections
import fsdlite
_crateAttributes = ['animatedSplash',
 'descriptionID',
 'nameID',
 'staticSplash',
 'typeID']
Crate = collections.namedtuple('Crate', _crateAttributes)

class Texture(object):

    def __new__(cls, *args, **kwargs):
        obj = object.__new__(cls)
        obj.height = None
        obj.resPath = None
        obj.width = None
        obj._color = None
        return obj

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, value):
        if len(value) == 3:
            self._color = (value[0], value[1], value[2])
        elif len(value) == 4:
            self._color = (value[0],
             value[1],
             value[2],
             value[3])


MAPPING = [('$', Crate), ('staticSplash$', Texture), ('animatedSplash$', Texture)]

def CrateStorage():
    try:
        return CrateStorage._storage
    except AttributeError:
        CrateStorage._storage = fsdlite.EveStorage(data='crates', cache='crates.static', mapping=MAPPING, coerce=int)
        return CrateStorage._storage
