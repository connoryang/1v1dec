#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\lib\pyasn1_modules\rfc4210.py
from pyasn1.type import tag, namedtype, namedval, univ, constraint, char, useful
from pyasn1_modules import rfc2459, rfc2511, rfc2314
MAX = 64

class KeyIdentifier(univ.OctetString):
    pass


class CMPCertificate(rfc2459.Certificate):
    pass


class OOBCert(CMPCertificate):
    pass


class CertAnnContent(CMPCertificate):
    pass


class PKIFreeText(univ.SequenceOf):
    componentType = char.UTF8String()
    subtypeSpec = univ.SequenceOf.subtypeSpec + constraint.ValueSizeConstraint(1, MAX)


class PollRepContent(univ.SequenceOf):

    class CertReq(univ.Sequence):
        componentType = namedtype.NamedTypes(namedtype.NamedType('certReqId', univ.Integer()), namedtype.NamedType('checkAfter', univ.Integer()), namedtype.OptionalNamedType('reason', PKIFreeText()))

    componentType = CertReq()


class PollReqContent(univ.SequenceOf):

    class CertReq(univ.Sequence):
        componentType = namedtype.NamedTypes(namedtype.NamedType('certReqId', univ.Integer()))

    componentType = CertReq()


class InfoTypeAndValue(univ.Sequence):
    componentType = namedtype.NamedTypes(namedtype.NamedType('infoType', univ.ObjectIdentifier()), namedtype.OptionalNamedType('infoValue', univ.Any()))


class GenRepContent(univ.SequenceOf):
    componentType = InfoTypeAndValue()


class GenMsgContent(univ.SequenceOf):
    componentType = InfoTypeAndValue()


class PKIConfirmContent(univ.Null):
    pass


class CRLAnnContent(univ.SequenceOf):
    componentType = rfc2459.CertificateList()


class CAKeyUpdAnnContent(univ.Sequence):
    componentType = namedtype.NamedTypes(namedtype.NamedType('oldWithNew', CMPCertificate()), namedtype.NamedType('newWithOld', CMPCertificate()), namedtype.NamedType('newWithNew', CMPCertificate()))


class RevDetails(univ.Sequence):
    componentType = namedtype.NamedTypes(namedtype.NamedType('certDetails', rfc2511.CertTemplate()), namedtype.OptionalNamedType('crlEntryDetails', rfc2459.Extensions()))


class RevReqContent(univ.SequenceOf):
    componentType = RevDetails()


class CertOrEncCert(univ.Choice):
    componentType = namedtype.NamedTypes(namedtype.NamedType('certificate', CMPCertificate().subtype(explicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatConstructed, 0))), namedtype.NamedType('encryptedCert', rfc2511.EncryptedValue().subtype(explicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatConstructed, 1))))


class CertifiedKeyPair(univ.Sequence):
    componentType = namedtype.NamedTypes(namedtype.NamedType('certOrEncCert', CertOrEncCert()), namedtype.OptionalNamedType('privateKey', rfc2511.EncryptedValue().subtype(explicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatConstructed, 0))), namedtype.OptionalNamedType('publicationInfo', rfc2511.PKIPublicationInfo().subtype(explicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatConstructed, 1))))


class POPODecKeyRespContent(univ.SequenceOf):
    componentType = univ.Integer()


class Challenge(univ.Sequence):
    componentType = namedtype.NamedTypes(namedtype.OptionalNamedType('owf', rfc2459.AlgorithmIdentifier()), namedtype.NamedType('witness', univ.OctetString()), namedtype.NamedType('challenge', univ.OctetString()))


class PKIStatus(univ.Integer):
    namedValues = namedval.NamedValues(('accepted', 0), ('grantedWithMods', 1), ('rejection', 2), ('waiting', 3), ('revocationWarning', 4), ('revocationNotification', 5), ('keyUpdateWarning', 6))


class PKIFailureInfo(univ.BitString):
    namedValues = namedval.NamedValues(('badAlg', 0), ('badMessageCheck', 1), ('badRequest', 2), ('badTime', 3), ('badCertId', 4), ('badDataFormat', 5), ('wrongAuthority', 6), ('incorrectData', 7), ('missingTimeStamp', 8), ('badPOP', 9), ('certRevoked', 10), ('certConfirmed', 11), ('wrongIntegrity', 12), ('badRecipientNonce', 13), ('timeNotAvailable', 14), ('unacceptedPolicy', 15), ('unacceptedExtension', 16), ('addInfoNotAvailable', 17), ('badSenderNonce', 18), ('badCertTemplate', 19), ('signerNotTrusted', 20), ('transactionIdInUse', 21), ('unsupportedVersion', 22), ('notAuthorized', 23), ('systemUnavail', 24), ('systemFailure', 25), ('duplicateCertReq', 26))


class PKIStatusInfo(univ.Sequence):
    componentType = namedtype.NamedTypes(namedtype.NamedType('status', PKIStatus()), namedtype.OptionalNamedType('statusString', PKIFreeText()), namedtype.OptionalNamedType('failInfo', PKIFailureInfo()))


class ErrorMsgContent(univ.Sequence):
    componentType = namedtype.NamedTypes(namedtype.NamedType('pKIStatusInfo', PKIStatusInfo()), namedtype.OptionalNamedType('errorCode', univ.Integer()), namedtype.OptionalNamedType('errorDetails', PKIFreeText()))


class CertStatus(univ.Sequence):
    componentType = namedtype.NamedTypes(namedtype.NamedType('certHash', univ.OctetString()), namedtype.NamedType('certReqId', univ.Integer()), namedtype.OptionalNamedType('statusInfo', PKIStatusInfo()))


class CertConfirmContent(univ.SequenceOf):
    componentType = CertStatus()


class RevAnnContent(univ.Sequence):
    componentType = namedtype.NamedTypes(namedtype.NamedType('status', PKIStatus()), namedtype.NamedType('certId', rfc2511.CertId()), namedtype.NamedType('willBeRevokedAt', useful.GeneralizedTime()), namedtype.NamedType('badSinceDate', useful.GeneralizedTime()), namedtype.OptionalNamedType('crlDetails', rfc2459.Extensions()))


class RevRepContent(univ.Sequence):
    componentType = namedtype.NamedTypes(namedtype.NamedType('status', PKIStatusInfo()), namedtype.OptionalNamedType('revCerts', univ.SequenceOf(componentType=rfc2511.CertId()).subtype(subtypeSpec=constraint.ValueSizeConstraint(1, MAX), explicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatConstructed, 0))), namedtype.OptionalNamedType('crls', univ.SequenceOf(componentType=rfc2459.CertificateList()).subtype(subtypeSpec=constraint.ValueSizeConstraint(1, MAX), explicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatConstructed, 1))))


class KeyRecRepContent(univ.Sequence):
    componentType = namedtype.NamedTypes(namedtype.NamedType('status', PKIStatusInfo()), namedtype.OptionalNamedType('newSigCert', CMPCertificate().subtype(explicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatConstructed, 0))), namedtype.OptionalNamedType('caCerts', univ.SequenceOf(componentType=CMPCertificate()).subtype(explicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatConstructed, 1), subtypeSpec=constraint.ValueSizeConstraint(1, MAX))), namedtype.OptionalNamedType('keyPairHist', univ.SequenceOf(componentType=CertifiedKeyPair()).subtype(explicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatConstructed, 2), subtypeSpec=constraint.ValueSizeConstraint(1, MAX))))


class CertResponse(univ.Sequence):
    componentType = namedtype.NamedTypes(namedtype.NamedType('certReqId', univ.Integer()), namedtype.NamedType('status', PKIStatusInfo()), namedtype.OptionalNamedType('certifiedKeyPair', CertifiedKeyPair()), namedtype.OptionalNamedType('rspInfo', univ.OctetString()))


class CertRepMessage(univ.Sequence):
    componentType = namedtype.NamedTypes(namedtype.OptionalNamedType('caPubs', univ.SequenceOf(componentType=CMPCertificate()).subtype(subtypeSpec=constraint.ValueSizeConstraint(1, MAX), explicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatConstructed, 1))), namedtype.NamedType('response', univ.SequenceOf(componentType=CertResponse())))


class POPODecKeyChallContent(univ.SequenceOf):
    componentType = Challenge()


class OOBCertHash(univ.Sequence):
    componentType = namedtype.NamedTypes(namedtype.OptionalNamedType('hashAlg', rfc2459.AlgorithmIdentifier().subtype(explicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatConstructed, 0))), namedtype.OptionalNamedType('certId', rfc2511.CertId().subtype(explicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatConstructed, 1))), namedtype.NamedType('hashVal', univ.BitString()))


class NestedMessageContent(univ.SequenceOf):
    componentType = univ.Any()


class DHBMParameter(univ.Sequence):
    componentType = namedtype.NamedTypes(namedtype.NamedType('owf', rfc2459.AlgorithmIdentifier()), namedtype.NamedType('mac', rfc2459.AlgorithmIdentifier()))


id_DHBasedMac = univ.ObjectIdentifier('1.2.840.113533.7.66.30')

class PBMParameter(univ.Sequence):
    componentType = namedtype.NamedTypes(namedtype.NamedType('salt', univ.OctetString().subtype(subtypeSpec=constraint.ValueSizeConstraint(0, 128))), namedtype.NamedType('owf', rfc2459.AlgorithmIdentifier()), namedtype.NamedType('iterationCount', univ.Integer()), namedtype.NamedType('mac', rfc2459.AlgorithmIdentifier()))


id_PasswordBasedMac = univ.ObjectIdentifier('1.2.840.113533.7.66.13')

class PKIProtection(univ.BitString):
    pass


nestedMessageContent = NestedMessageContent().subtype(explicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatConstructed, 20))

class PKIBody(univ.Choice):
    componentType = namedtype.NamedTypes(namedtype.NamedType('ir', rfc2511.CertReqMessages().subtype(explicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatConstructed, 0))), namedtype.NamedType('ip', CertRepMessage().subtype(explicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatConstructed, 1))), namedtype.NamedType('cr', rfc2511.CertReqMessages().subtype(explicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatConstructed, 2))), namedtype.NamedType('cp', CertRepMessage().subtype(explicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatConstructed, 3))), namedtype.NamedType('p10cr', rfc2314.CertificationRequest().subtype(explicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatConstructed, 4))), namedtype.NamedType('popdecc', POPODecKeyChallContent().subtype(explicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatConstructed, 5))), namedtype.NamedType('popdecr', POPODecKeyRespContent().subtype(explicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatConstructed, 6))), namedtype.NamedType('kur', rfc2511.CertReqMessages().subtype(explicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatConstructed, 7))), namedtype.NamedType('kup', CertRepMessage().subtype(explicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatConstructed, 8))), namedtype.NamedType('krr', rfc2511.CertReqMessages().subtype(explicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatConstructed, 9))), namedtype.NamedType('krp', KeyRecRepContent().subtype(explicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatConstructed, 10))), namedtype.NamedType('rr', RevReqContent().subtype(explicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatConstructed, 11))), namedtype.NamedType('rp', RevRepContent().subtype(explicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatConstructed, 12))), namedtype.NamedType('ccr', rfc2511.CertReqMessages().subtype(explicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatConstructed, 13))), namedtype.NamedType('ccp', CertRepMessage().subtype(explicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatConstructed, 14))), namedtype.NamedType('ckuann', CAKeyUpdAnnContent().subtype(explicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatConstructed, 15))), namedtype.NamedType('cann', CertAnnContent().subtype(explicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatConstructed, 16))), namedtype.NamedType('rann', RevAnnContent().subtype(explicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatConstructed, 17))), namedtype.NamedType('crlann', CRLAnnContent().subtype(explicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatConstructed, 18))), namedtype.NamedType('pkiconf', PKIConfirmContent().subtype(explicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatConstructed, 19))), namedtype.NamedType('nested', nestedMessageContent), namedtype.NamedType('genm', GenMsgContent().subtype(explicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatConstructed, 21))), namedtype.NamedType('gen', GenRepContent().subtype(explicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatConstructed, 22))), namedtype.NamedType('error', ErrorMsgContent().subtype(explicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatConstructed, 23))), namedtype.NamedType('certConf', CertConfirmContent().subtype(explicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatConstructed, 24))), namedtype.NamedType('pollReq', PollReqContent().subtype(explicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatConstructed, 25))), namedtype.NamedType('pollRep', PollRepContent().subtype(explicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatConstructed, 26))))


class PKIHeader(univ.Sequence):
    componentType = namedtype.NamedTypes(namedtype.NamedType('pvno', univ.Integer(namedValues=namedval.NamedValues(('cmp1999', 1), ('cmp2000', 2)))), namedtype.NamedType('sender', rfc2459.GeneralName()), namedtype.NamedType('recipient', rfc2459.GeneralName()), namedtype.OptionalNamedType('messageTime', useful.GeneralizedTime().subtype(explicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatSimple, 0))), namedtype.OptionalNamedType('protectionAlg', rfc2459.AlgorithmIdentifier().subtype(explicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatConstructed, 1))), namedtype.OptionalNamedType('senderKID', rfc2459.KeyIdentifier().subtype(explicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatSimple, 2))), namedtype.OptionalNamedType('recipKID', rfc2459.KeyIdentifier().subtype(explicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatSimple, 3))), namedtype.OptionalNamedType('transactionID', univ.OctetString().subtype(explicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatSimple, 4))), namedtype.OptionalNamedType('senderNonce', univ.OctetString().subtype(explicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatSimple, 5))), namedtype.OptionalNamedType('recipNonce', univ.OctetString().subtype(explicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatSimple, 6))), namedtype.OptionalNamedType('freeText', PKIFreeText().subtype(explicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatConstructed, 7))), namedtype.OptionalNamedType('generalInfo', univ.SequenceOf(componentType=InfoTypeAndValue().subtype(subtypeSpec=constraint.ValueSizeConstraint(1, MAX), explicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatSimple, 8)))))


class ProtectedPart(univ.Sequence):
    componentType = namedtype.NamedTypes(namedtype.NamedType('header', PKIHeader()), namedtype.NamedType('infoValue', PKIBody()))


class PKIMessage(univ.Sequence):
    componentType = namedtype.NamedTypes(namedtype.NamedType('header', PKIHeader()), namedtype.NamedType('body', PKIBody()), namedtype.OptionalNamedType('protection', PKIProtection().subtype(explicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatSimple, 0))), namedtype.OptionalNamedType('extraCerts', univ.SequenceOf(componentType=CMPCertificate()).subtype(subtypeSpec=constraint.ValueSizeConstraint(1, MAX), explicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatConstructed, 1))))


class PKIMessages(univ.SequenceOf):
    componentType = PKIMessage()
    subtypeSpec = univ.SequenceOf.subtypeSpec + constraint.ValueSizeConstraint(1, MAX)


NestedMessageContent.componentType = PKIMessages()
nestedMessageContent.componentType = PKIMessages()
