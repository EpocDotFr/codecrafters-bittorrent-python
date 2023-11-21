from typing import Union, List, Optional, BinaryIO
from collections import OrderedDict


def unpack(f: BinaryIO) -> Optional[Union[bytes, int, List, OrderedDict]]:
    type_ = f.read(1)

    if type_ == b'i': # Integer
        integer = b''

        while True:
            char = f.read(1)

            if not char or char == b'e':
                break

            integer += char

        return int(integer)
    elif type_ == b'l': # List
        list_ = []

        while True:
            value = unpack(f)

            if value is None:
                return list_

            list_.append(value)
    elif type_ == b'd': # Dictionary
        dict_ = OrderedDict()

        while True:
            key = unpack(f)

            if key is None:
                return dict_

            value = unpack(f)

            dict_[key.decode()] = value
    elif type_ == b'e': # End of list or dictionary
        return None
    else: # String
        length = type_

        while True:
            char = f.read(1)

            if not char or char == b':':
                break

            length += char

        return f.read(int(length.decode()))
