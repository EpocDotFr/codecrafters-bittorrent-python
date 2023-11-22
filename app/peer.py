from typing import Tuple, Optional
from app.torrent import Torrent
import socket
import struct

PSTR = b'BitTorrent protocol'
PSTRLEN = len(PSTR)


class Peer:
    my_peer_id: str
    torrent: Torrent
    address: Tuple[str, int]
    socket: socket.socket

    def __init__(self, my_peer_id: str, torrent: Torrent, address: Tuple[str, int]):
        self.my_peer_id = my_peer_id
        self.torrent = torrent
        self.address = address

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def handshake(self) -> Optional[Tuple]:
        handshake_fmt = f'H{PSTRLEN}s8s20s20s'

        self.send(
            handshake_fmt,
            PSTRLEN,
            PSTR,
            b'0' * 8,
            self.torrent.info_hash.digest(),
            self.my_peer_id.encode()
        )

        return self.receive(handshake_fmt)

    def receive(self, fmt) -> Optional[Tuple]:
        fmt = f'>{fmt}'

        data = self.socket.recv(
            struct.calcsize(fmt)
        )

        if not data:
            return None

        return struct.unpack(f'>{fmt}', data)

    def send(self, fmt, *args) -> None:
        self.socket.sendall(
            struct.pack(f'>{fmt}', *args)
        )

    def connect(self) -> None:
        self.socket.connect(self.address)

    def disconnect(self) -> None:
        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()

    def __enter__(self):
        self.connect()

        return self

    def __exit__(self, exc_type, exc_value, exc_traceback) -> None:
        self.disconnect()
