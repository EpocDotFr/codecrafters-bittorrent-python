from typing import Union, List, Optional
from collections import OrderedDict
from io import StringIO


def unpack(f: StringIO) -> Optional[Union[str, int, List, OrderedDict]]:
    type_ = f.read(1)

    if type_ == 'i': # Integer
        integer = ''

        while True:
            char = f.read(1)

            if not char or char == 'e':
                break

            integer += char

        return int(integer)
    elif type_ == 'l': # List
        list_ = []

        while True:
            value = unpack(f)

            if value is None:
                return list_

            list_.append(value)
    elif type_ == 'd': # Dictionary
        dict_ = OrderedDict()

        while True:
            key = unpack(f)

            if key is None:
                return dict_

            value = unpack(f)

            dict_[key] = value
    elif type_ == 'e': # End of list or dictionary
        return None
    else: # String
        length = type_
        while True:
            char = f.read(1)

            if not char or char == ':':
                break

            length += char

        return f.read(int(length))
