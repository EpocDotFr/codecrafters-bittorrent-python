from hashlib import sha1
from app import bencode
from io import BytesIO
import argparse
import json


def _bytes_to_str(obj) -> str:
    if isinstance(obj, bytes):
        return obj.decode()

    raise TypeError()


def main() -> None:
    arg_parser = argparse.ArgumentParser()

    command_arg_parser = arg_parser.add_subparsers(dest='command')

    decode_arg_parser = command_arg_parser.add_parser('decode')
    decode_arg_parser.add_argument('data')

    info_arg_parser = command_arg_parser.add_parser('info')
    info_arg_parser.add_argument('filename')

    args = arg_parser.parse_args()

    if args.command == 'decode':
        with BytesIO(args.data.encode()) as f:
            print(json.dumps(bencode.unpack(f), default=_bytes_to_str))
    elif args.command == 'info':
        with open(args.filename, 'rb') as f:
            info = bencode.unpack(f)

        tracker_url = info['announce'].decode()
        length = info['info']['length']

        with BytesIO() as f:
            bencode.pack(f, info['info'])

            f.seek(0)

            info_hash = sha1(f.read()).hexdigest()

        piece_length =  info['info']['piece length']

        pieces = info['info']['pieces']

        piece_hashes = [
            pieces[i:i + 20].hex() for i in range(0, len(pieces), 20)
        ]

        print(f'Tracker URL: {tracker_url}')
        print(f'Length: {length}')
        print(f'Info Hash: {info_hash}')
        print(f'Piece Length: {piece_length}')
        print(f'Piece Hashes:')

        for piece_hash in piece_hashes:
            print(piece_hash)


if __name__ == '__main__':
    main()
