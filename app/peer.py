from app.custom_types import KeepAliveMessage, ChokeMessage, UnchokeMessage, InterestedMessage, NotInterestedMessage, \
    BitfieldMessage, HaveMessage, RequestMessage, PieceMessage, CancelMessage
from typing import Tuple, Optional, Union, Any
from app.torrent import Torrent
import socket
import struct

PSTR = b'BitTorrent protocol'
PSTRLEN = len(PSTR)


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

        message = self.receive_message()

        if not isinstance(message, BitfieldMessage):
            return

        self.send_message(InterestedMessage())

        message = self.receive_message()

        if not isinstance(message, UnchokeMessage):
            return

        # self.send_message(RequestMessage()) TODO

    def receive_message(self) -> Optional[Union[KeepAliveMessage, ChokeMessage, UnchokeMessage, InterestedMessage, NotInterestedMessage, HaveMessage, BitfieldMessage, RequestMessage, PieceMessage, CancelMessage]]:
        message_length = self.unpack('I')

        if message_length is None:
            return None

        if message_length == 0:
            return KeepAliveMessage()

        message_type = self.unpack('B')

        if message_type is None:
            return None

        message_payload = self.socket.recv(message_length - 1) if message_length - 1 != 0 else b''

        if message_type == 0:
            return ChokeMessage()
        elif message_type == 1:
            return UnchokeMessage()
        elif message_type == 2:
            return InterestedMessage()
        elif message_type == 3:
            return NotInterestedMessage()
        elif message_type == 4:
            return HaveMessage(piece_index=struct.unpack('>I', message_payload)[0])
        elif message_type == 5:
            return BitfieldMessage(bits=Peer.bytes_to_bits(message_payload))
        elif message_type == 6:
            index, begin, length = struct.unpack('>III', message_payload)

            return RequestMessage(index=index, begin=begin, length=length)
        elif message_type == 7:
            index, begin = struct.unpack('>II', message_payload[:8])

            return PieceMessage(index=index, begin=begin, block=message_payload[8:])
        elif message_type == 8:
            index, begin, length = struct.unpack('>III', message_payload)

            return CancelMessage(index=index, begin=begin, length=length)

        raise ValueError(f'Unknown message type: {message_type}')

    def send_message(self, message: Union[KeepAliveMessage, ChokeMessage, UnchokeMessage, InterestedMessage, NotInterestedMessage, HaveMessage, BitfieldMessage, RequestMessage, PieceMessage, CancelMessage]) -> None:
        message_payload = b''

        if isinstance(message, ChokeMessage):
            message_type = 0
        elif isinstance(message, UnchokeMessage):
            message_type = 1
        elif isinstance(message, InterestedMessage):
            message_type = 2
        elif isinstance(message, NotInterestedMessage):
            message_type = 3
        elif isinstance(message, HaveMessage):
            message_type = 4
            message_payload = struct.pack('>I', message.piece_index)
        elif isinstance(message, BitfieldMessage):
            message_type = 5
            message_payload = Peer.bits_to_bytes(message.bits)
        elif isinstance(message, RequestMessage):
            message_type = 6
            message_payload = struct.pack('>III', message.index, message.begin, message.length)
        elif isinstance(message, PieceMessage):
            message_type = 7
            message_payload = struct.pack('>II', message.index, message.begin) + message.block
        elif isinstance(message, CancelMessage):
            message_type = 8
            message_payload = struct.pack('>III', message.index, message.begin, message.length)
        else:
            raise ValueError(f'Unknown message: {type(message)}')

        self.pack(
            'IB',
            1 + len(message_payload),
            message_type
        )

        if message_payload:
            self.socket.sendall(message_payload)

    def handshake(self) -> Optional[Tuple]:
        handshake_fmt = f'B{PSTRLEN}s8s20s20s'

        self.pack(
            handshake_fmt,
            PSTRLEN,
            PSTR,
            b'0' * 8,
            self.torrent.info_hash.digest(),
            self.my_peer_id
        )

        return self.unpack(handshake_fmt)

    def unpack(self, fmt) -> Any:
        fmt = f'>{fmt}'

        data = self.socket.recv(
            struct.calcsize(fmt)
        )

        if not data:
            return None

        ret = struct.unpack(fmt, data)

        return ret[0] if len(ret) == 1 else ret

    def pack(self, fmt, *args) -> None:
        self.socket.sendall(
            struct.pack(f'>{fmt}', *args)
        )

    def connect(self) -> None:
        self.socket.connect(self.address)

    def disconnect(self) -> None:
        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()

    @staticmethod
    def bytes_to_bits(b: bytes) -> str:
        return format(int.from_bytes(b, byteorder='big'), '08b')

    @staticmethod
    def bits_to_bytes(b: str) -> bytes:
        return int(b, 2).to_bytes(4, byteorder='big')

    def __enter__(self):
        self.connect()

        return self

    def __exit__(self, exc_type, exc_value, exc_traceback) -> None:
        self.disconnect()
