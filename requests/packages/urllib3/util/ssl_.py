#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\requests\packages\urllib3\util\ssl_.py
from __future__ import absolute_import
import errno
import warnings
import hmac
from binascii import hexlify, unhexlify
from hashlib import md5, sha1, sha256
from ..exceptions import SSLError, InsecurePlatformWarning, SNIMissingWarning
SSLContext = None
HAS_SNI = False
create_default_context = None
IS_PYOPENSSL = False
HASHFUNC_MAP = {32: md5,
 40: sha1,
 64: sha256}

def _const_compare_digest_backport(a, b):
    result = abs(len(a) - len(b))
    for l, r in zip(bytearray(a), bytearray(b)):
        result |= l ^ r

    return result == 0


_const_compare_digest = getattr(hmac, 'compare_digest', _const_compare_digest_backport)
try:
    import ssl
    from ssl import wrap_socket, CERT_NONE, PROTOCOL_SSLv23
    from ssl import HAS_SNI
except ImportError:
    pass

try:
    from ssl import OP_NO_SSLv2, OP_NO_SSLv3, OP_NO_COMPRESSION
except ImportError:
    OP_NO_SSLv2, OP_NO_SSLv3 = (16777216, 33554432)
    OP_NO_COMPRESSION = 131072

DEFAULT_CIPHERS = 'ECDH+AESGCM:DH+AESGCM:ECDH+AES256:DH+AES256:ECDH+AES128:DH+AES:ECDH+HIGH:DH+HIGH:ECDH+3DES:DH+3DES:RSA+AESGCM:RSA+AES:RSA+HIGH:RSA+3DES:!aNULL:!eNULL:!MD5'
try:
    from ssl import SSLContext
except ImportError:
    import sys

    class SSLContext(object):
        supports_set_ciphers = (2, 7) <= sys.version_info < (3,) or (3, 2) <= sys.version_info

        def __init__(self, protocol_version):
            self.protocol = protocol_version
            self.check_hostname = False
            self.verify_mode = ssl.CERT_NONE
            self.ca_certs = None
            self.options = 0
            self.certfile = None
            self.keyfile = None
            self.ciphers = None

        def load_cert_chain(self, certfile, keyfile):
            self.certfile = certfile
            self.keyfile = keyfile

        def load_verify_locations(self, cafile = None, capath = None):
            self.ca_certs = cafile
            if capath is not None:
                raise SSLError('CA directories not supported in older Pythons')

        def set_ciphers(self, cipher_suite):
            if not self.supports_set_ciphers:
                raise TypeError('Your version of Python does not support setting a custom cipher suite. Please upgrade to Python 2.7, 3.2, or later if you need this functionality.')
            self.ciphers = cipher_suite

        def wrap_socket(self, socket, server_hostname = None, server_side = False):
            warnings.warn('A true SSLContext object is not available. This prevents urllib3 from configuring SSL appropriately and may cause certain SSL connections to fail. You can upgrade to a newer version of Python to solve this. For more information, see https://urllib3.readthedocs.org/en/latest/security.html#insecureplatformwarning.', InsecurePlatformWarning)
            kwargs = {'keyfile': self.keyfile,
             'certfile': self.certfile,
             'ca_certs': self.ca_certs,
             'cert_reqs': self.verify_mode,
             'ssl_version': self.protocol,
             'server_side': server_side}
            if self.supports_set_ciphers:
                return wrap_socket(socket, ciphers=self.ciphers, **kwargs)
            else:
                return wrap_socket(socket, **kwargs)


def assert_fingerprint(cert, fingerprint):
    fingerprint = fingerprint.replace(':', '').lower()
    digest_length = len(fingerprint)
    hashfunc = HASHFUNC_MAP.get(digest_length)
    if not hashfunc:
        raise SSLError('Fingerprint of invalid length: {0}'.format(fingerprint))
    fingerprint_bytes = unhexlify(fingerprint.encode())
    cert_digest = hashfunc(cert).digest()
    if not _const_compare_digest(cert_digest, fingerprint_bytes):
        raise SSLError('Fingerprints did not match. Expected "{0}", got "{1}".'.format(fingerprint, hexlify(cert_digest)))


def resolve_cert_reqs(candidate):
    if candidate is None:
        return CERT_NONE
    if isinstance(candidate, str):
        res = getattr(ssl, candidate, None)
        if res is None:
            res = getattr(ssl, 'CERT_' + candidate)
        return res
    return candidate


def resolve_ssl_version(candidate):
    if candidate is None:
        return PROTOCOL_SSLv23
    if isinstance(candidate, str):
        res = getattr(ssl, candidate, None)
        if res is None:
            res = getattr(ssl, 'PROTOCOL_' + candidate)
        return res
    return candidate


def create_urllib3_context(ssl_version = None, cert_reqs = None, options = None, ciphers = None):
    context = SSLContext(ssl_version or ssl.PROTOCOL_SSLv23)
    cert_reqs = ssl.CERT_REQUIRED if cert_reqs is None else cert_reqs
    if options is None:
        options = 0
        options |= OP_NO_SSLv2
        options |= OP_NO_SSLv3
        options |= OP_NO_COMPRESSION
    context.options |= options
    if getattr(context, 'supports_set_ciphers', True):
        context.set_ciphers(ciphers or DEFAULT_CIPHERS)
    context.verify_mode = cert_reqs
    if getattr(context, 'check_hostname', None) is not None:
        context.check_hostname = False
    return context


def ssl_wrap_socket(sock, keyfile = None, certfile = None, cert_reqs = None, ca_certs = None, server_hostname = None, ssl_version = None, ciphers = None, ssl_context = None, ca_cert_dir = None):
    context = ssl_context
    if context is None:
        context = create_urllib3_context(ssl_version, cert_reqs, ciphers=ciphers)
    if ca_certs or ca_cert_dir:
        try:
            context.load_verify_locations(ca_certs, ca_cert_dir)
        except IOError as e:
            raise SSLError(e)
        except OSError as e:
            if e.errno == errno.ENOENT:
                raise SSLError(e)
            raise

    if certfile:
        context.load_cert_chain(certfile, keyfile)
    if HAS_SNI:
        return context.wrap_socket(sock, server_hostname=server_hostname)
    warnings.warn('An HTTPS request has been made, but the SNI (Subject Name Indication) extension to TLS is not available on this platform. This may cause the server to present an incorrect TLS certificate, which can cause validation failures. You can upgrade to a newer version of Python to solve this. For more information, see https://urllib3.readthedocs.org/en/latest/security.html#snimissingwarning.', SNIMissingWarning)
    return context.wrap_socket(sock)
