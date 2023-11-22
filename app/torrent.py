from typing import BinaryIO, OrderedDict, List
from hashlib import sha1
from app import bencode
from io import BytesIO


class Torrent:
    data: OrderedDict

    def __init__(self, info: OrderedDict):
        self.data = info

    @classmethod
    def load(cls, f: BinaryIO):
        return cls(bencode.unpack(f))

    @property
    def tracker_url(self) -> str:
        return self.data['announce'].decode()

    @property
    def length(self) -> int:
        return self.data['info']['length']

    @property
    def piece_length(self) -> int:
        return self.data['info']['piece length']

    @property
    def piece_hashes(self) -> List:
        pieces = self.data['info']['pieces']

        return [
            pieces[i:i + 20].hex() for i in range(0, len(pieces), 20)
        ]

    @property
    def info_hash(self) -> str:
        with BytesIO() as f:
            bencode.pack(f, self.data['info'])

            f.seek(0)

            return sha1(f.read()).hexdigest()
