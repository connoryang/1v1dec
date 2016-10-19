#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\fsd\schemas\path.py


class FsdDataPathObject(object):

    def __init__(self, name, parent = None):
        self.name = name
        self.parent = parent

    def __str__(self):
        if self.parent is not None:
            return self.parent.__str__() + self.name
        else:
            return self.name
