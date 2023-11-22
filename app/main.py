from app.torrent import Torrent
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

    peers_arg_parser = command_arg_parser.add_parser('peers')
    peers_arg_parser.add_argument('filename')

    args = arg_parser.parse_args()

    if args.command == 'decode':
        with BytesIO(args.data.encode()) as f:
            print(json.dumps(bencode.unpack(f), default=_bytes_to_str))
    elif args.command == 'info':
        with open(args.filename, 'rb') as f:
            torrent = Torrent.load(f)

        print(f'Tracker URL: {torrent.tracker_url}')
        print(f'Length: {torrent.length}')
        print(f'Info Hash: {torrent.info_hash}')
        print(f'Piece Length: {torrent.piece_length}')
        print(f'Piece Hashes:')

        for piece_hash in torrent.piece_hashes:
            print(piece_hash)
    elif args.command == 'peers':
        pass


if __name__ == '__main__':
    main()
