from typing import Union, List, Dict, Optional
from io import StringIO


def unpack(f: StringIO) -> Optional[Union[str, int, List, Dict]]:
    type_ = f.read(1)

    if type_ == 'i': # Integer
        integer = ''
        char = ''

        while char != 'e':
            integer += char

            char = f.read(1)

        return int(integer)
    elif type_ == 'l': # List
        list_ = []

        while True:
            value = unpack(f)

            if value is None:
                return list_

            list_.append(value)
    elif type_ == 'd': # Dictionary
        raise NotImplementedError()
    elif type_ == 'e': # End of list or dictionary
        return None
    else: # String
        length = type_
        char = ''

        while char != ':':
            length += char

            char = f.read(1)

        length = int(length)

        return f.read(length)
