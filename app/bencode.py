from typing import Union, List, Dict


def unpack(data: str) -> Union[str, int, List, Dict]:
    if not data:
        raise InvalidPattern('data is empty')

    if data[0] == 'i': # Integer
        raise NotImplemented()
    elif data[0] == 'l': # List
        raise NotImplemented()
    elif data[0] == 'd': # Dictionnary
        raise NotImplemented()
    else: # String
        delimiter = data.index(':')
        length = int(data[:delimiter])

        return data[delimiter + 1:delimiter + 1 + length]

    raise ValueError('Unknown data format')
