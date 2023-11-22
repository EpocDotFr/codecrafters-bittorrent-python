from typing import BinaryIO, OrderedDict, List, Any
from hashlib import sha1
from app import bencode
from io import BytesIO


class Torrent:
    data: OrderedDict
    tracker_url: str
    length: int
    piece_length: int
    piece_hashes: List[str]
    info_hash: Any

    def __init__(self, info: OrderedDict):
        self.data = info

        self.tracker_url = self.data['announce'].decode()
        self.length = self.data['info']['length']
        self.piece_length = self.data['info']['piece length']

        self.piece_hashes = Torrent.parse_piece_hashes(self.data['info']['pieces'])

        with BytesIO() as f:
            bencode.pack(f, self.data['info'])

            f.seek(0)

            self.info_hash = sha1(f.read())

    @classmethod
    def load(cls, f: BinaryIO):
        return cls(bencode.unpack(f))

    @staticmethod
    def parse_piece_hashes(pieces: bytes) -> List:
        return [
            pieces[i:i + 20].hex() for i in range(0, len(pieces), 20)
        ]
