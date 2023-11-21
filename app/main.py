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

        print(f'Tracker URL: {tracker_url}')
        print(f'Length: {length}')


if __name__ == '__main__':
    main()
