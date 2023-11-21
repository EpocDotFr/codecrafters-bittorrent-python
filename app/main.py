from app import bencode
from io import StringIO
import argparse
import json


def main() -> None:
    arg_parser = argparse.ArgumentParser()

    command_arg_parser = arg_parser.add_subparsers(dest='command')

    decode_arg_parser = command_arg_parser.add_parser('decode')
    decode_arg_parser.add_argument('data')

    args = arg_parser.parse_args()

    if args.command == 'decode':
        with StringIO(args.data) as f:
            print(json.dumps(bencode.unpack(f)))


if __name__ == '__main__':
    main()
