#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\requests\packages\urllib3\util\connection.py
from __future__ import absolute_import
import socket
try:
    from select import poll, POLLIN
except ImportError:
    poll = False
    try:
        from select import select
    except ImportError:
        select = False

def is_connection_dropped(conn):
    sock = getattr(conn, 'sock', False)
    if sock is False:
        return False
    if sock is None:
        return True
    if not poll:
        if not select:
            return False
        try:
            return select([sock], [], [], 0.0)[0]
        except socket.error:
            return True

    p = poll()
    p.register(sock, POLLIN)
    for fno, ev in p.poll(0.0):
        if fno == sock.fileno():
            return True


def create_connection(address, timeout = socket._GLOBAL_DEFAULT_TIMEOUT, source_address = None, socket_options = None):
    host, port = address
    if host.startswith('['):
        host = host.strip('[]')
    err = None
    for res in socket.getaddrinfo(host, port, 0, socket.SOCK_STREAM):
        af, socktype, proto, canonname, sa = res
        sock = None
        try:
            sock = socket.socket(af, socktype, proto)
            _set_socket_options(sock, socket_options)
            if timeout is not socket._GLOBAL_DEFAULT_TIMEOUT:
                sock.settimeout(timeout)
            if source_address:
                sock.bind(source_address)
            sock.connect(sa)
            return sock
        except socket.error as e:
            err = e
            if sock is not None:
                sock.close()
                sock = None

    if err is not None:
        raise err
    raise socket.error('getaddrinfo returns an empty list')


def _set_socket_options(sock, options):
    if options is None:
        return
    for opt in options:
        sock.setsockopt(*opt)
