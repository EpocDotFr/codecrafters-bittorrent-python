from typing import Tuple
import struct

PSTR = b'BitTorrent protocol'
PSTRLEN = len(PSTR)


class HasStructMixin:
    _format: str

    def pack(self, *data) -> bytes:
        return struct.pack(f'>{self._format}', *data)

    @classmethod
    def unpack(cls, data: bytes) -> Tuple:
        return struct.unpack(f'>{cls._format}', data)


class Message:
    def serialize(self) -> bytes:
        return b''

    @classmethod
    def unserialize(cls, data: bytes):
        return cls()


class TypedMessage(Message):
    _type: int

    def serialize(self) -> bytes:
        message_payload = super().serialize()

        return struct.pack('>IB', 1 + len(message_payload), self._type) + message_payload

    @classmethod
    def unserialize(cls, data: bytes):
        message_type, message_payload = data[0], data[1:]

        if message_type == 0:
            class_ = ChokeMessage
        elif message_type == 1:
            class_ = UnchokeMessage
        elif message_type == 2:
            class_ = InterestedMessage
        elif message_type == 3:
            class_ = NotInterestedMessage
        elif message_type == 4:
            class_ = HaveMessage
        elif message_type == 5:
            class_ = BitfieldMessage
        elif message_type == 6:
            class_ = RequestMessage
        elif message_type == 7:
            class_ = PieceMessage
        elif message_type == 8:
            class_ = CancelMessage
        else:
            raise ValueError(f'Unknown message type: {message_type}')

        return class_.unserialize(message_payload)


class HandshakeMessage(HasStructMixin, Message):
    info_hash: bytes
    peer_id: bytes
    reserved: bytes

    _format: str = f'B{PSTRLEN}s8s20s20s'

    def __init__(self, info_hash: bytes, peer_id: bytes, reserved: bytes = b'0' * 8):
        self.info_hash = info_hash
        self.peer_id = peer_id
        self.reserved = reserved

    def serialize(self) -> bytes:
        return self.pack(
            PSTRLEN,
            PSTR,
            self.reserved,
            self.info_hash,
            self.peer_id
        )

    @classmethod
    def unserialize(cls, data: bytes):
        pstrlen, pstr, reserved, info_hash, peer_id = cls.unpack(data)

        if pstrlen != PSTRLEN or pstr != PSTR:
            raise ValueError()

        return cls(info_hash=info_hash, peer_id=peer_id, reserved=reserved)


class KeepAliveMessage(Message):
    pass


class ChokeMessage(TypedMessage):
    _type: int = 0


class UnchokeMessage(TypedMessage):
    _type: int = 1


class InterestedMessage(TypedMessage):
    _type: int = 2


class NotInterestedMessage(TypedMessage):
    _type: int = 3


class HaveMessage(HasStructMixin, TypedMessage):
    piece_index: int

    _format = 'I'
    _type: int = 4

    def __init__(self, piece_index: int):
        self.piece_index = piece_index

    def serialize(self) -> bytes:
        return self.pack(
            self.piece_index
        )

    @classmethod
    def unserialize(cls, data: bytes):
        piece_index, = cls.unpack(data)

        return cls(piece_index=piece_index)


class BitfieldMessage(TypedMessage):
    bits: bytes

    _type: int = 5

    def __init__(self, bits: bytes):
        self.bits = bits

    def serialize(self) -> bytes:
        return self.bits

    @classmethod
    def unserialize(cls, data: bytes):
        return cls(bits=data)

    @staticmethod
    def bytes_to_bits(b: bytes) -> str:
        return format(int.from_bytes(b, byteorder='big'), '08b')

    @staticmethod
    def bits_to_bytes(b: str) -> bytes:
        return int(b, 2).to_bytes(4, byteorder='big')


class RequestMessage(HasStructMixin, TypedMessage):
    index: int
    begin: int
    length: int

    _format = 'III'
    _type: int = 6

    def __init__(self, index: int, begin: int, length: int):
        self.index = index
        self.begin = begin
        self.length = length

    def serialize(self) -> bytes:
        return self.pack(
            self.index,
            self.begin,
            self.length
        )

    @classmethod
    def unserialize(cls, data: bytes):
        index, begin, length = cls.unpack(data)

        return cls(index=index, begin=begin, length=length)


class PieceMessage(HasStructMixin, TypedMessage):
    index: int
    begin: int
    block: bytes

    _format = 'II'
    _type: int = 7

    def __init__(self, index: int, begin: int, block: bytes):
        self.index = index
        self.begin = begin
        self.block = block

    def serialize(self) -> bytes:
        return self.pack(
            self.index,
            self.begin
        ) + self.block

    @classmethod
    def unserialize(cls, data: bytes):
        index, begin = cls.unpack(data[:8])

        return cls(index=index, begin=begin, block=data[8:])


class CancelMessage(HasStructMixin, TypedMessage):
    index: int
    begin: int
    length: int

    _format = 'III'
    _type: int = 8

    def __init__(self, index: int, begin: int, length: int):
        self.index = index
        self.begin = begin
        self.length = length

    def serialize(self) -> bytes:
        return self.pack(
            self.index,
            self.begin,
            self.length
        )

    @classmethod
    def unserialize(cls, data: bytes):
        index, begin, length = cls.unpack(data)

        return cls(index=index, begin=begin, length=length)
