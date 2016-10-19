#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\localization\propertyHandlers\basePropertyHandler.py
from .. import const as locconst
from ..logger import LogError
from ..uiutil import PrepareLocalizationSafeString
import re
methodNameRE = re.compile('[A-Z][^A-Z]*|[^A-Z]+')

class Singleton(object):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Singleton, cls).__new__(cls, *args, **kwargs)
        return cls._instance


class BasePropertyHandler(Singleton):
    PROPERTIES = {}

    def __init__(self):
        self._SetUpProperties()

    def GetProperty(self, propertyName, identifierID, languageID, *args, **kwargs):
        if propertyName is None:
            method = self._GetDefault
            isUniversal = True
        else:
            isUniversal = False
            method = self._propertyMethods.get((languageID, propertyName), None)
            if method is None:
                method = self._propertyMethods.get((locconst.CODE_UNIVERSAL, propertyName), None)
                isUniversal = True
        if method is None:
            expectedUniversalMethodName = self._GeneratePropertyMethodName(propertyName, locconst.CODE_UNIVERSAL)
            expectedLangaugeSpecificMethodName = self._GeneratePropertyMethodName(propertyName, languageID)
            message = ''.join(("No method defined on '",
             str(self.__class__),
             "' to handle property '",
             propertyName,
             "'.  Tried methods'",
             expectedUniversalMethodName,
             "' and '",
             expectedLangaugeSpecificMethodName,
             "'."))
            raise AttributeError(message)
        try:
            if isUniversal:
                return method(identifierID, languageID, *args, **kwargs)
            return method(identifierID, *args, **kwargs)
        except TypeError:
            print '---- TYPE ERROR ----'
            print method
            print propertyName, identifierID, languageID
            print args
            print kwargs

    def _PrepareLocalizationSafeString(self, textString, messageID = None):
        return PrepareLocalizationSafeString(textString, messageID=messageID)

    def _SetUpProperties(self):
        self._propertyMethods = {}
        for languageID in self.PROPERTIES:
            propertyNames = self.PROPERTIES[languageID]
            for propertyName in propertyNames:
                methodName = self._GeneratePropertyMethodName(propertyName, languageID)
                isUniversal = True if languageID == locconst.CODE_UNIVERSAL else False
                if not hasattr(self, methodName):
                    if isUniversal:
                        LogError("Class '", self.__class__.__name__, "' must implement the function '", methodName, "' to use the property '", propertyName, "'.")
                        setattr(self, methodName, BasePropertyHandler._NotImplementedUniversalPropertyFactory(methodName))
                    else:
                        LogError("Class '", self.__class__.__name__, "' must implement the function '", methodName, "' to use the property '", propertyName, "' in language '", languageID, "'.")
                        setattr(self, methodName, BasePropertyHandler._NotImplementedPropertyFactory(methodName))
                method = getattr(self, methodName)
                self._propertyMethods[languageID, propertyName] = method

    @staticmethod
    def _NotImplementedUniversalPropertyFactory(methodName):
        return lambda identifierID, languageID, *args, **kwargs: BasePropertyHandler._NotImplementedProperty(methodName)

    @staticmethod
    def _NotImplementedPropertyFactory(methodName):
        return lambda identifierID, *args, **kwargs: BasePropertyHandler._NotImplementedProperty(methodName)

    @staticmethod
    def _NotImplementedProperty(methodName):
        raise NotImplementedError, 'The property method (%s) is missing an implementation.' % methodName

    def _GeneratePropertyMethodName(self, propertyName, languageID):
        methodName = '_Get' + ''.join([ part.title() for part in methodNameRE.findall(propertyName) ])
        if languageID != locconst.CODE_UNIVERSAL:
            methodName = methodName + languageID.replace('-', '_').upper()
        return methodName

    def _GetDefault(self, value, languageID, *args, **kwargs):
        return value

    def Linkify(self, value, linkText):
        raise NotImplementedError, 'This variable type cannot be converted into a link until a Linkify function is defined in its property handler.'
