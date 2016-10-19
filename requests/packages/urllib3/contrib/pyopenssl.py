#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\requests\packages\urllib3\contrib\pyopenssl.py
from __future__ import absolute_import
try:
    from ndg.httpsclient.ssl_peer_verification import SUBJ_ALT_NAME_SUPPORT
    from ndg.httpsclient.subj_alt_name import SubjectAltName as BaseSubjectAltName
except SyntaxError as e:
    raise ImportError(e)

import OpenSSL.SSL
from pyasn1.codec.der import decoder as der_decoder
from pyasn1.type import univ, constraint
from socket import timeout, error as SocketError
try:
    from socket import _fileobject
except ImportError:
    _fileobject = None
    from urllib3.packages.backports.makefile import backport_makefile

import ssl
import select
import six
from .. import connection
from .. import util
__all__ = ['inject_into_urllib3', 'extract_from_urllib3']
HAS_SNI = SUBJ_ALT_NAME_SUPPORT
_openssl_versions = {ssl.PROTOCOL_SSLv23: OpenSSL.SSL.SSLv23_METHOD,
 ssl.PROTOCOL_TLSv1: OpenSSL.SSL.TLSv1_METHOD}
if hasattr(ssl, 'PROTOCOL_TLSv1_1') and hasattr(OpenSSL.SSL, 'TLSv1_1_METHOD'):
    _openssl_versions[ssl.PROTOCOL_TLSv1_1] = OpenSSL.SSL.TLSv1_1_METHOD
if hasattr(ssl, 'PROTOCOL_TLSv1_2') and hasattr(OpenSSL.SSL, 'TLSv1_2_METHOD'):
    _openssl_versions[ssl.PROTOCOL_TLSv1_2] = OpenSSL.SSL.TLSv1_2_METHOD
try:
    _openssl_versions.update({ssl.PROTOCOL_SSLv3: OpenSSL.SSL.SSLv3_METHOD})
except AttributeError:
    pass

_openssl_verify = {ssl.CERT_NONE: OpenSSL.SSL.VERIFY_NONE,
 ssl.CERT_OPTIONAL: OpenSSL.SSL.VERIFY_PEER,
 ssl.CERT_REQUIRED: OpenSSL.SSL.VERIFY_PEER + OpenSSL.SSL.VERIFY_FAIL_IF_NO_PEER_CERT}
DEFAULT_SSL_CIPHER_LIST = util.ssl_.DEFAULT_CIPHERS.encode('ascii')
SSL_WRITE_BLOCKSIZE = 16384
orig_util_HAS_SNI = util.HAS_SNI
orig_connection_ssl_wrap_socket = connection.ssl_wrap_socket

def inject_into_urllib3():
    connection.ssl_wrap_socket = ssl_wrap_socket
    util.HAS_SNI = HAS_SNI
    util.IS_PYOPENSSL = True


def extract_from_urllib3():
    connection.ssl_wrap_socket = orig_connection_ssl_wrap_socket
    util.HAS_SNI = orig_util_HAS_SNI
    util.IS_PYOPENSSL = False


class SubjectAltName(BaseSubjectAltName):
    sizeSpec = univ.SequenceOf.sizeSpec + constraint.ValueSizeConstraint(1, 1024)


def get_subj_alt_name(peer_cert):
    dns_name = []
    if not SUBJ_ALT_NAME_SUPPORT:
        return dns_name
    general_names = SubjectAltName()
    for i in range(peer_cert.get_extension_count()):
        ext = peer_cert.get_extension(i)
        ext_name = ext.get_short_name()
        if ext_name != 'subjectAltName':
            continue
        ext_dat = ext.get_data()
        decoded_dat = der_decoder.decode(ext_dat, asn1Spec=general_names)
        for name in decoded_dat:
            if not isinstance(name, SubjectAltName):
                continue
            for entry in range(len(name)):
                component = name.getComponentByPosition(entry)
                if component.getName() != 'dNSName':
                    continue
                dns_name.append(str(component.getComponent()))

    return dns_name


class WrappedSocket(object):

    def __init__(self, connection, socket, suppress_ragged_eofs = True):
        self.connection = connection
        self.socket = socket
        self.suppress_ragged_eofs = suppress_ragged_eofs
        self._makefile_refs = 0
        self._closed = False

    def fileno(self):
        return self.socket.fileno()

    def _decref_socketios(self):
        if self._makefile_refs > 0:
            self._makefile_refs -= 1
        if self._closed:
            self.close()

    def recv(self, *args, **kwargs):
        try:
            data = self.connection.recv(*args, **kwargs)
        except OpenSSL.SSL.SysCallError as e:
            if self.suppress_ragged_eofs and e.args == (-1, 'Unexpected EOF'):
                return ''
            raise SocketError(str(e))
        except OpenSSL.SSL.ZeroReturnError as e:
            if self.connection.get_shutdown() == OpenSSL.SSL.RECEIVED_SHUTDOWN:
                return ''
            raise
        except OpenSSL.SSL.WantReadError:
            rd, wd, ed = select.select([self.socket], [], [], self.socket.gettimeout())
            if not rd:
                raise timeout('The read operation timed out')
            else:
                return self.recv(*args, **kwargs)
        else:
            return data

    def recv_into(self, *args, **kwargs):
        try:
            return self.connection.recv_into(*args, **kwargs)
        except OpenSSL.SSL.SysCallError as e:
            if self.suppress_ragged_eofs and e.args == (-1, 'Unexpected EOF'):
                return 0
            raise SocketError(str(e))
        except OpenSSL.SSL.ZeroReturnError as e:
            if self.connection.get_shutdown() == OpenSSL.SSL.RECEIVED_SHUTDOWN:
                return 0
            raise
        except OpenSSL.SSL.WantReadError:
            rd, wd, ed = select.select([self.socket], [], [], self.socket.gettimeout())
            if not rd:
                raise timeout('The read operation timed out')
            else:
                return self.recv_into(*args, **kwargs)

    def settimeout(self, timeout):
        return self.socket.settimeout(timeout)

    def _send_until_done(self, data):
        while True:
            try:
                return self.connection.send(data)
            except OpenSSL.SSL.WantWriteError:
                _, wlist, _ = select.select([], [self.socket], [], self.socket.gettimeout())
                if not wlist:
                    raise timeout()
                continue

    def sendall(self, data):
        total_sent = 0
        while total_sent < len(data):
            sent = self._send_until_done(data[total_sent:total_sent + SSL_WRITE_BLOCKSIZE])
            total_sent += sent

    def shutdown(self):
        self.connection.shutdown()

    def close(self):
        if self._makefile_refs < 1:
            try:
                self._closed = True
                return self.connection.close()
            except OpenSSL.SSL.Error:
                return

        else:
            self._makefile_refs -= 1

    def getpeercert(self, binary_form = False):
        x509 = self.connection.get_peer_certificate()
        if not x509:
            return x509
        if binary_form:
            return OpenSSL.crypto.dump_certificate(OpenSSL.crypto.FILETYPE_ASN1, x509)
        return {'subject': ((('commonName', x509.get_subject().CN),),),
         'subjectAltName': [ ('DNS', value) for value in get_subj_alt_name(x509) ]}

    def _reuse(self):
        self._makefile_refs += 1

    def _drop(self):
        if self._makefile_refs < 1:
            self.close()
        else:
            self._makefile_refs -= 1


if _fileobject:

    def makefile(self, mode, bufsize = -1):
        self._makefile_refs += 1
        return _fileobject(self, mode, bufsize, close=True)


else:
    makefile = backport_makefile
WrappedSocket.makefile = makefile

def _verify_callback(cnx, x509, err_no, err_depth, return_code):
    return err_no == 0


def ssl_wrap_socket(sock, keyfile = None, certfile = None, cert_reqs = None, ca_certs = None, server_hostname = None, ssl_version = None, ca_cert_dir = None):
    ctx = OpenSSL.SSL.Context(_openssl_versions[ssl_version])
    if certfile:
        keyfile = keyfile or certfile
        ctx.use_certificate_file(certfile)
    if keyfile:
        ctx.use_privatekey_file(keyfile)
    if cert_reqs != ssl.CERT_NONE:
        ctx.set_verify(_openssl_verify[cert_reqs], _verify_callback)
    if ca_certs or ca_cert_dir:
        try:
            ctx.load_verify_locations(ca_certs, ca_cert_dir)
        except OpenSSL.SSL.Error as e:
            raise ssl.SSLError('bad ca_certs: %r' % ca_certs, e)

    else:
        ctx.set_default_verify_paths()
    OP_NO_COMPRESSION = 131072
    ctx.set_options(OP_NO_COMPRESSION)
    ctx.set_cipher_list(DEFAULT_SSL_CIPHER_LIST)
    cnx = OpenSSL.SSL.Connection(ctx, sock)
    if isinstance(server_hostname, six.text_type):
        server_hostname = server_hostname.encode('utf-8')
    cnx.set_tlsext_host_name(server_hostname)
    cnx.set_connect_state()
    while True:
        try:
            cnx.do_handshake()
        except OpenSSL.SSL.WantReadError:
            rd, _, _ = select.select([sock], [], [], sock.gettimeout())
            if not rd:
                raise timeout('select timed out')
            continue
        except OpenSSL.SSL.Error as e:
            raise ssl.SSLError('bad handshake: %r' % e)

        break

    return WrappedSocket(cnx, sock)
