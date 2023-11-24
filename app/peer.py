from typing import Tuple, Optional
from app.torrent import Torrent
import app.messages as messages
import socket
import struct


class Peer:
    my_peer_id: bytes
    torrent: Torrent
    address: Tuple[str, int]
    socket: socket.socket

    def __init__(self, my_peer_id: bytes, torrent: Torrent, address: Tuple[str, int]):
        self.my_peer_id = my_peer_id
        self.torrent = torrent
        self.address = address

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(2)

    def download_piece(self, piece_number: int, output: str) -> None:
        if not self.handshake():
            return

        message = self.receive()

        if not isinstance(message, messages.BitfieldMessage):
            return

        self.send(messages.InterestedMessage())

        message = self.receive()

        if not isinstance(message, messages.UnchokeMessage):
            return

        # self.send_message(RequestMessage()) TODO

    def receive(self) -> Optional[messages.Message]:
        message_length = int.from_bytes(self.socket.recv(4), byteorder='big')

        if message_length is None:
            return None

        if message_length == 0:
            return messages.KeepAliveMessage()

        return messages.TypedMessage.from_bytes(self.socket.recv(message_length))

    def send(self, message: messages.Message) -> None:
        self.socket.sendall(message.serialize())

    def handshake(self) -> Optional[messages.HandshakeMessage]:
        self.socket.sendall(messages.HandshakeMessage(
            info_hash=self.torrent.info_hash.digest(),
            peer_id=self.my_peer_id
        ).serialize())

        response = messages.HandshakeMessage.unserialize(
            self.socket.recv(messages.HandshakeMessage.size())
        )

        if not isinstance(response, messages.HandshakeMessage):
            return None

        return response

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
